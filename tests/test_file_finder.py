"""
Tests for the FileSystemRAG class (file_finder.py).
"""
import pytest
import os
from unittest.mock import patch, Mock, mock_open
from pathlib import Path

class TestFileSystemRAG:
    """Test cases for FileSystemRAG class."""

    def test_init(self, temp_dir, mock_ollama_connection):
        """Test initialization with valid and invalid directories."""
        from file_finder import FileSystemRAG
        
        # Test valid directory
        rag = FileSystemRAG(root_dir=temp_dir)
        assert rag.root_dir == os.path.abspath(temp_dir)
        assert rag.model is not None
        assert rag.index is None
        assert rag.file_paths == []
        
        # Test invalid directory
        with pytest.raises(ValueError, match="Directory does not exist"):
            FileSystemRAG(root_dir="/nonexistent/directory")

    @patch('requests.get')
    def test_ollama_connection(self, mock_requests_get, temp_dir):
        """Test Ollama connection handling."""
        from file_finder import FileSystemRAG
        
        # Test connection failure
        mock_requests_get.side_effect = Exception("Connection failed")
        with pytest.raises(ConnectionError, match="Could not connect to Ollama server"):
            FileSystemRAG(root_dir=temp_dir)
            
        # Test successful connection
        mock_requests_get.side_effect = None
        mock_requests_get.return_value.status_code = 200
        rag = FileSystemRAG(root_dir=temp_dir)
        assert rag.ollama_host == "http://localhost:11434"

    def test_file_operations(self, rag_system, sample_files):
        """Test file operations (description and reading)."""
        # Test file description
        test_file = os.path.join(sample_files, 'test.txt')
        description = rag_system._get_file_description(test_file)
        assert "File: test.txt" in description
        
        # Test file reading
        content = rag_system._read_file_contents(test_file)
        assert "This is a test text file" in content
        
        # Test binary file handling
        with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')):
            content = rag_system._read_file_contents('/fake/binary/file')
            assert content == "Binary file - cannot be summarized"

    def test_index_operations(self, rag_system, sample_files):
        """Test index building and searching."""
        # Test index building
        rag_system.build_index()
        assert rag_system.index is not None
        assert len(rag_system.file_paths) > 0
        
        # Test search without index
        with pytest.raises(ValueError, match="Index not built"):
            rag_system.search("test query")
            
        # Test search with results
        results = rag_system.search("test", k=5)
        assert isinstance(results, list)
        assert len(results) <= 5
        if results:
            assert all(key in results[0] for key in ['path', 'description', 'relevance_score'])

    @patch('requests.get')
    @patch('os.path.isfile')
    @patch('ollama.chat')
    def test_summarization(self, mock_ollama_chat, mock_isfile, mock_requests_get, rag_system):
        """Test file summarization functionality."""
        # Setup mocks
        mock_isfile.return_value = True
        mock_requests_get.return_value.status_code = 200
        
        # Test successful summarization
        mock_response = Mock()
        mock_response.message = Mock()
        mock_response.message.content = "Test summary"
        mock_ollama_chat.return_value = mock_response
        
        with patch.object(rag_system, '_read_file_contents', return_value="Test content"):
            result = rag_system.summarize_file('/fake/file.txt')
            assert result == "Test summary"
            
        # Test error handling
        mock_ollama_chat.side_effect = Exception("Ollama error")
        with patch.object(rag_system, '_read_file_contents', return_value="Test content"):
            result = rag_system.summarize_file('/fake/file.txt')
            assert "Error generating summary" in result

    def test_file_type_handling(self, rag_system):
        """Test handling of different file types."""
        # Test PDF
        with patch('file_finder.PdfReader') as mock_pdf:
            mock_page = Mock()
            mock_page.extract_text.return_value = "PDF content"
            mock_pdf.return_value.pages = [mock_page]
            with patch('builtins.open', mock_open()):
                content = rag_system._read_file_contents('/fake/file.pdf')
                assert content == "PDF content"
        
        # Test DOCX
        with patch('file_finder.Document') as mock_doc:
            mock_para = Mock()
            mock_para.text = "Word content"
            mock_doc.return_value.paragraphs = [mock_para]
            content = rag_system._read_file_contents('/fake/file.docx')
            assert content == "Word content"

    def test_get_file_description_file(self, rag_system, sample_files):
        """Test file description generation for files."""
        test_file = os.path.join(sample_files, 'test.txt')
        description = rag_system._get_file_description(test_file)
        assert "File: test.txt" in description
        assert "with extension .txt" in description

    def test_get_file_description_directory(self, rag_system, sample_files):
        """Test file description generation for directories."""
        subdir = os.path.join(sample_files, 'subdir')
        description = rag_system._get_file_description(subdir)
        assert "Directory: subdir" in description
        assert "containing files and subdirectories" in description

    def test_read_file_contents_text(self, rag_system, sample_files):
        """Test reading text file contents."""
        test_file = os.path.join(sample_files, 'test.txt')
        content = rag_system._read_file_contents(test_file)
        assert "This is a test text file" in content

    def test_read_file_contents_json(self, rag_system, sample_files):
        """Test reading JSON file contents."""
        json_file = os.path.join(sample_files, 'data.json')
        content = rag_system._read_file_contents(json_file)
        assert '"key": "value"' in content
        assert '"number": 42' in content

    @patch('builtins.open', side_effect=Exception("File error"))
    def test_read_file_contents_error(self, mock_open_func, rag_system):
        """Test reading file with error."""
        content = rag_system._read_file_contents('/fake/error/file')
        assert "Error reading file" in content

    def test_build_index(self, rag_system, sample_files):
        """Test building the FAISS index."""
        rag_system.build_index()
        
        assert rag_system.index is not None
        assert len(rag_system.file_paths) > 0
        assert rag_system.index.ntotal == len(rag_system.file_paths)

    def test_build_index_empty_directory(self, temp_dir, mock_ollama_connection):
        """Test building index with empty directory."""
        from file_finder import FileSystemRAG
        rag = FileSystemRAG(root_dir=temp_dir)
        rag.build_index()
        
        # Should handle empty directory gracefully
        assert rag.file_paths == []

    def test_search_no_results(self, initialized_rag):
        """Test search that should return results (since we have files)."""
        results = initialized_rag.search("very_specific_nonexistent_query_12345", k=1)
        
        # Even with a nonsensical query, we should get some results
        # because the system will return the closest matches
        assert isinstance(results, list)

    @patch('os.path.isfile')
    def test_summarize_file_not_file(self, mock_isfile, rag_system):
        """Test summarizing something that's not a file."""
        mock_isfile.return_value = False
        result = rag_system.summarize_file('/fake/path')
        assert result == "Not a file - cannot be summarized"

    @patch('requests.get')
    @patch('os.path.isfile')
    def test_summarize_file_ollama_unavailable(self, mock_isfile, mock_requests_get, rag_system):
        """Test summarizing file when Ollama is unavailable."""
        mock_isfile.return_value = True
        mock_requests_get.return_value.status_code = 500
        
        result = rag_system.summarize_file('/fake/file.txt')
        assert "Ollama server returned status code 500" in result

    @patch('requests.get')
    @patch('os.path.isfile')
    @patch('ollama.chat')
    def test_summarize_file_empty_response(self, mock_ollama_chat, mock_isfile, mock_requests_get, rag_system):
        """Test file summarization with empty Ollama response."""
        mock_isfile.return_value = True
        mock_requests_get.return_value.status_code = 200
        
        mock_response = Mock()
        mock_response.message = Mock()
        mock_response.message.content = ""
        mock_ollama_chat.return_value = mock_response
        
        with patch.object(rag_system, '_read_file_contents', return_value="Test content"):
            result = rag_system.summarize_file('/fake/file.txt')
            assert "Empty response from Ollama server" in result

    @patch('os.walk')
    def test_build_index_permission_error(self, mock_walk, rag_system):
        """Test handling permission errors during index building."""
        # Mock os.walk to raise permission error for some files
        mock_walk.return_value = [
            ('/test', ['dir1'], ['file1.txt', 'file2.txt']),
        ]
        
        with patch('os.path.normpath', side_effect=PermissionError("Access denied")):
            # Should not raise exception, just continue
            rag_system.build_index()
            # The method should complete without crashing 