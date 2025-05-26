"""
Tests for the Flask application (app.py).
"""
import pytest
import json
from unittest.mock import patch, Mock
import requests


class TestFlaskApp:
    """Test cases for Flask application endpoints."""

    def test_index_route(self, client):
        """Test the index route returns the main page."""
        response = client.get('/')
        assert response.status_code == 200

    def test_status_route_not_initialized(self, client):
        """Test status route when RAG system is not initialized."""
        response = client.get('/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['initialized'] is False
        assert data['root_dir'] is None

    @patch('app.test_ollama_connection')
    def test_test_ollama_success(self, mock_test_ollama, client):
        """Test successful Ollama connection test."""
        mock_test_ollama.return_value = (True, "Hello! How can I help you today?")
        
        response = client.get('/test-ollama')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'Hello' in data['message']

    @patch('app.test_ollama_connection')
    def test_test_ollama_failure(self, mock_test_ollama, client):
        """Test failed Ollama connection test."""
        mock_test_ollama.return_value = (False, "Connection failed")
        
        response = client.get('/test-ollama')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == "Connection failed"

    @patch('requests.get')
    @patch('ollama.chat')
    def test_test_ollama_custom_success(self, mock_ollama_chat, mock_requests_get, client):
        """Test custom Ollama connection test with success."""
        # Mock successful server response
        mock_requests_get.return_value.status_code = 200
        
        # Mock successful Ollama chat
        mock_response = Mock()
        mock_response.message = Mock()
        mock_response.message.content = "Hello!"
        mock_ollama_chat.return_value = mock_response
        
        response = client.post('/test-ollama-custom', 
                             json={'url': 'http://localhost:11434', 'model': 'llama3.1:8b'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

    @patch('requests.get')
    def test_test_ollama_custom_connection_error(self, mock_requests_get, client):
        """Test custom Ollama connection test with connection error."""
        mock_requests_get.side_effect = requests.exceptions.ConnectionError()
        
        response = client.post('/test-ollama-custom', 
                             json={'url': 'http://localhost:11434', 'model': 'llama3.1:8b'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Could not connect' in data['message']

    @patch('app.test_ollama_connection')
    @patch('app.FileSystemRAG')
    def test_initialize_success(self, mock_rag_class, mock_test_ollama, client, temp_dir):
        """Test successful RAG system initialization."""
        mock_test_ollama.return_value = (True, "Connection successful")
        mock_rag_instance = Mock()
        mock_rag_class.return_value = mock_rag_instance
        
        response = client.post('/initialize', json={'root_dir': temp_dir})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'Successfully initialized' in data['message']

    @patch('app.test_ollama_connection')
    def test_initialize_ollama_failure(self, mock_test_ollama, client, temp_dir):
        """Test initialization failure due to Ollama connection."""
        mock_test_ollama.return_value = (False, "Ollama not available")
        
        response = client.post('/initialize', json={'root_dir': temp_dir})
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Ollama test failed' in data['message']

    def test_search_not_initialized(self, client):
        """Test search endpoint when RAG system is not initialized."""
        response = client.post('/search', json={'query': 'test query'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not initialized' in data['message']

    def test_search_no_query(self, client):
        """Test search endpoint without providing a query."""
        with patch('app.rag', Mock()):  # Mock initialized RAG
            response = client.post('/search', json={})
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'No query provided' in data['message']

    @patch('app.rag')
    def test_search_success(self, mock_rag, client):
        """Test successful search operation."""
        mock_rag.search.return_value = [
            {'path': '/test/file.txt', 'description': 'Test file', 'relevance_score': 0.9}
        ]
        
        response = client.post('/search', json={'query': 'test', 'num_results': 5})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['results']) == 1
        assert data['results'][0]['path'] == '/test/file.txt'

    @patch('app.rag')
    def test_search_exception(self, mock_rag, client):
        """Test search endpoint with exception."""
        mock_rag.search.side_effect = Exception("Search failed")
        
        response = client.post('/search', json={'query': 'test'})
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Search failed' in data['message']

    def test_summarize_not_initialized(self, client):
        """Test summarize endpoint when RAG system is not initialized."""
        response = client.post('/summarize', json={'file_path': '/test/file.txt'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not initialized' in data['message']

    @patch('app.rag')
    @patch('ollama.chat')
    def test_summarize_chat_message(self, mock_ollama_chat, mock_rag, client):
        """Test summarize endpoint with chat message."""
        mock_response = Mock()
        mock_response.message = Mock()
        mock_response.message.content = "This is a chat response."
        mock_ollama_chat.return_value = mock_response
        
        response = client.post('/summarize', json={'message': 'Hello, how are you?'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['summary'] == "This is a chat response."

    def test_summarize_no_input(self, client):
        """Test summarize endpoint without file path or message."""
        with patch('app.rag', Mock()):  # Mock initialized RAG
            response = client.post('/summarize', json={})
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['status'] == 'error'
            assert 'No file path or message provided' in data['message']

    @patch('app.rag')
    @patch('app.current_root_dir', '/test/root')
    @patch('os.path.isfile')
    @patch('os.access')
    @patch('app.test_ollama_connection')
    def test_summarize_file_success(self, mock_test_ollama, mock_access, mock_isfile, mock_rag, client):
        """Test successful file summarization."""
        mock_isfile.return_value = True
        mock_access.return_value = True
        mock_test_ollama.return_value = (True, "Connection successful")
        mock_rag.summarize_file.return_value = "This is a file summary."
        
        with patch('builtins.open', Mock()):
            response = client.post('/summarize', json={'file_path': 'test.txt'})
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert data['summary'] == "This is a file summary."

    @patch('app.rag')
    @patch('app.current_root_dir', '/test/root')
    def test_summarize_file_not_found(self, mock_rag, client):
        """Test file summarization with non-existent file."""
        response = client.post('/summarize', json={'file_path': 'nonexistent.txt'})
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'File does not exist' in data['message']


class TestOllamaConnection:
    """Test cases for Ollama connection functionality."""

    @patch('ollama.chat')
    def test_test_ollama_connection_success(self, mock_ollama_chat):
        """Test successful Ollama connection."""
        from app import test_ollama_connection
        
        mock_response = Mock()
        mock_response.message = Mock()
        mock_response.message.content = "Hello!"
        mock_ollama_chat.return_value = mock_response
        
        success, response = test_ollama_connection()
        assert success is True
        assert response == "Hello!"

    @patch('ollama.chat')
    def test_test_ollama_connection_failure(self, mock_ollama_chat):
        """Test failed Ollama connection."""
        from app import test_ollama_connection
        
        mock_ollama_chat.side_effect = Exception("Connection failed")
        
        success, response = test_ollama_connection()
        assert success is False
        assert "Connection failed" in response

    @patch('ollama.chat')
    def test_test_ollama_connection_no_message(self, mock_ollama_chat):
        """Test Ollama connection with no message in response."""
        from app import test_ollama_connection
        
        mock_response = Mock()
        del mock_response.message  # Remove message attribute
        mock_ollama_chat.return_value = mock_response
        
        success, response = test_ollama_connection()
        assert success is False
        assert "No message found" in response 