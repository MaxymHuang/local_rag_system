import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pathlib import Path
import sys
import argparse
import time

class FileSystemRAG:
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)  # Get absolute path
        # Check if path exists and is accessible
        if not os.path.exists(self.root_dir):
            raise ValueError(f"Directory does not exist: {self.root_dir}")
        if not os.access(self.root_dir, os.R_OK):
            raise ValueError(f"No read access to directory: {self.root_dir}")
            
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.file_paths = []
        
    def _get_file_description(self, file_path: str) -> str:
        """Generate a description for a file or directory."""
        path = Path(file_path)
        if path.is_dir():
            return f"Directory: {path.name} containing files and subdirectories"
        else:
            return f"File: {path.name} with extension {path.suffix}"
    
    def build_index(self):
        """Build the FAISS index from the file system."""
        # Collect all files and directories
        self.file_paths = []
        start_time = time.time()
        files_processed = 0
        
        try:
            print("Scanning directory structure...")
            for root, dirs, files in os.walk(self.root_dir):
                # Skip hidden directories (starting with .)
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # Add directories
                for dir_name in dirs:
                    try:
                        full_path = os.path.normpath(os.path.join(root, dir_name))
                        self.file_paths.append(full_path)
                        files_processed += 1
                        if files_processed % 1000 == 0:
                            print(f"Processed {files_processed} items...")
                    except (PermissionError, OSError) as e:
                        print(f"Warning: Could not access {dir_name}: {str(e)}")
                        continue
                
                # Add files
                for file_name in files:
                    try:
                        if not file_name.startswith('.'):  # Skip hidden files
                            full_path = os.path.normpath(os.path.join(root, file_name))
                            self.file_paths.append(full_path)
                            files_processed += 1
                            if files_processed % 1000 == 0:
                                print(f"Processed {files_processed} items...")
                    except (PermissionError, OSError) as e:
                        print(f"Warning: Could not access {file_name}: {str(e)}")
                        continue
            
            if not self.file_paths:
                print("Warning: No files or directories found in the specified path.")
                return
            
            print(f"\nFound {len(self.file_paths)} files and directories.")
            print("Generating embeddings...")
            
            # Generate descriptions and embeddings
            descriptions = [self._get_file_description(path) for path in self.file_paths]
            embeddings = self.model.encode(descriptions)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))
            
            end_time = time.time()
            print(f"\nIndex built successfully in {end_time - start_time:.2f} seconds!")
            
        except Exception as e:
            print(f"Error building index: {str(e)}")
            raise
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, str]]:
        """Search for files/directories based on natural language query."""
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Return results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.file_paths):  # Ensure index is valid
                results.append({
                    'path': self.file_paths[idx],
                    'description': self._get_file_description(self.file_paths[idx]),
                    'relevance_score': float(1 / (1 + distances[0][i]))  # Convert distance to similarity score
                })
        
        return results

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='File Finder RAG System')
    parser.add_argument('--root-dir', type=str, default='.',
                      help='Root directory to search in (default: current directory)')
    args = parser.parse_args()

    try:
        # Initialize the RAG system with specified root directory
        print(f"Initializing file finder for directory: {os.path.abspath(args.root_dir)}")
        rag = FileSystemRAG(root_dir=args.root_dir)
        
        # Build the index
        print("Building index...")
        rag.build_index()
        
        # Interactive search loop
        while True:
            try:
                query = input("\nEnter your search query (or 'quit' to exit): ")
                if query.lower() == 'quit':
                    break
                    
                results = rag.search(query)
                if not results:
                    print("\nNo results found.")
                    continue
                    
                print("\nSearch Results:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result['description']}")
                    print(f"   Path: {result['path']}")
                    print(f"   Relevance Score: {result['relevance_score']:.2f}")
            except KeyboardInterrupt:
                print("\nSearch interrupted. Type 'quit' to exit.")
                continue
            except Exception as e:
                print(f"\nError during search: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 