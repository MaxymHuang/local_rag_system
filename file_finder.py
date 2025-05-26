"""
# File Finder RAG System
# Copyright (C) 2024 [Maxym (Yu-Chia) Huang]
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
"""

import os
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pathlib import Path
import sys
import argparse
import time
import ollama
import json
from docx import Document
from PyPDF2 import PdfReader
from pptx import Presentation
import requests

class FileSystemRAG:
    def __init__(self, root_dir: str = ".", ollama_host: str = "http://localhost:11434"):
        self.root_dir = os.path.abspath(root_dir)  # Get absolute path
        # Check if path exists and is accessible
        if not os.path.exists(self.root_dir):
            raise ValueError(f"Directory does not exist: {self.root_dir}")
        if not os.access(self.root_dir, os.R_OK):
            raise ValueError(f"No read access to directory: {self.root_dir}")
            
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.file_paths = []
        
        # Configure Ollama client
        self.ollama_host = ollama_host
        self.ollama_model = "hf.co/bartowski/Dolphin3.0-Llama3.2-3B-GGUF:Q4_K_M"  # Full model name
        
        # Test Ollama connection
        try:
            response = requests.get(f"{ollama_host}/api/tags")
            if response.status_code != 200:
                raise ConnectionError(f"Ollama server returned status code {response.status_code}")
            print("Successfully connected to Ollama server")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Could not connect to Ollama server at {ollama_host}. Make sure Ollama is running.")
        
    def _get_file_description(self, file_path: str) -> str:
        """Generate a description for a file or directory."""
        path = Path(file_path)
        if path.is_dir():
            return f"Directory: {path.name} containing files and subdirectories"
        else:
            return f"File: {path.name} with extension {path.suffix}"
    
    def _read_file_contents(self, file_path: str) -> str:
        """Read the contents of a file."""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        try:
            # Handle PDF files
            if ext == '.pdf':
                with open(file_path, 'rb') as file:
                    pdf = PdfReader(file)
                    text = []
                    for page in pdf.pages:
                        text.append(page.extract_text())
                    return "\n".join(text)
            
            # Handle Word documents
            elif ext == '.docx':
                doc = Document(file_path)
                text = []
                for para in doc.paragraphs:
                    text.append(para.text)
                return "\n".join(text)
            
            # Handle PowerPoint files
            elif ext == '.pptx':
                prs = Presentation(file_path)
                text = []
                for slide in prs.slides:
                    slide_text = []
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            slide_text.append(shape.text)
                    if slide_text:
                        text.append("Slide: " + " | ".join(slide_text))
                return "\n".join(text)
            
            # Handle text files
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
        except UnicodeDecodeError:
            return "Binary file - cannot be summarized"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def summarize_file(self, file_path: str) -> str:
        """Summarize a file using Ollama."""
        if not os.path.isfile(file_path):
            return "Not a file - cannot be summarized"
            
        content = self._read_file_contents(file_path)
        if content.startswith("Error") or content.startswith("Binary"):
            return content
            
        try:
            # Get file type for context
            file_type = Path(file_path).suffix.lower()
            file_name = Path(file_path).name
            
            # Prepare context-aware prompt
            if file_type == '.pdf':
                context = "PDF document"
            elif file_type == '.docx':
                context = "Word document"
            elif file_type == '.pptx':
                context = "PowerPoint presentation"
            else:
                context = "file"
                
            prompt = f"""Please provide a concise summary of this {context} named '{file_name}':

{content[:4000]}  # Limit content length

Focus on the main content and key points."""
            
            # Use Ollama to generate a summary
            try:
                response = ollama.chat(
                    model=self.ollama_model,
                    messages=[{
                        'role': 'user',
                        'content': prompt
                    }]
                )
                return response['message']['content']
            except requests.exceptions.ConnectionError:
                return f"Error: Could not connect to Ollama server at {self.ollama_host}. Make sure Ollama is running."
            except Exception as e:
                return f"Error generating summary: {str(e)}"
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
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
    parser.add_argument('--ollama-host', type=str, default='http://localhost:11434',
                      help='Ollama server host (default: http://localhost:11434)')
    parser.add_argument('--ollama-model', type=str, default='1d35e3661de3',
                      help='Ollama model ID (default: 1d35e3661de3)')
    args = parser.parse_args()

    try:
        # Initialize the RAG system with specified root directory and Ollama host
        print(f"Initializing file finder for directory: {os.path.abspath(args.root_dir)}")
        rag = FileSystemRAG(root_dir=args.root_dir, ollama_host=args.ollama_host)
        
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
                
                # Ask if user wants to summarize a file
                summarize = input("\nWould you like to summarize any of these files? (y/n/q to quit): ").lower().strip()
                if summarize == 'q' or summarize == 'quit':
                    break
                if summarize != 'y':
                    continue
                
                # Ask user to select a file for summarization
                while True:
                    try:
                        selection = input("\nEnter the number of the file you want to summarize (or 'q' to quit, Enter to search again): ")
                        if not selection.strip():
                            break
                        if selection.lower() in ['q', 'quit']:
                            break
                            
                        idx = int(selection) - 1
                        if 0 <= idx < len(results):
                            selected_file = results[idx]['path']
                            print(f"\nGenerating summary for: {selected_file}")
                            summary = rag.summarize_file(selected_file)
                            print("\nSummary:")
                            print(summary)
                            break
                        else:
                            print("Invalid selection. Please enter a number from the list.")
                    except ValueError:
                        print("Please enter a valid number.")
                    except KeyboardInterrupt:
                        print("\nSelection cancelled.")
                        break
                        
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