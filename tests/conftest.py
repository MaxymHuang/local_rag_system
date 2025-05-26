"""
Pytest configuration and fixtures for the local RAG system tests.
"""
import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from file_finder import FileSystemRAG


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing."""
    # Create some test files
    test_files = {
        'test.txt': 'This is a test text file with some content.',
        'readme.md': '# Test README\nThis is a markdown file.',
        'data.json': '{"key": "value", "number": 42}',
        'script.py': 'print("Hello, World!")\ndef test_function():\n    return True'
    }
    
    # Create subdirectory
    subdir = os.path.join(temp_dir, 'subdir')
    os.makedirs(subdir)
    
    for filename, content in test_files.items():
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Create a file in subdirectory
    with open(os.path.join(subdir, 'nested.txt'), 'w', encoding='utf-8') as f:
        f.write('This is a nested file.')
    
    return temp_dir


@pytest.fixture
def mock_ollama():
    """Mock Ollama responses."""
    mock_response = Mock()
    mock_response.message = Mock()
    mock_response.message.content = "This is a mocked summary of the file content."
    
    with patch('ollama.chat', return_value=mock_response):
        yield mock_response


@pytest.fixture
def mock_ollama_connection():
    """Mock Ollama connection test."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        yield mock_get


@pytest.fixture
def rag_system(temp_dir, mock_ollama_connection):
    """Create a FileSystemRAG instance for testing."""
    return FileSystemRAG(root_dir=temp_dir)


@pytest.fixture
def initialized_rag(rag_system, sample_files):
    """Create an initialized RAG system with sample files."""
    rag_system.build_index()
    return rag_system 