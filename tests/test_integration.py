"""
Integration tests for the local RAG system.
Tests the full workflow from initialization to search and summarization.
"""
import pytest
import json
import os
from unittest.mock import patch, Mock


class TestIntegration:
    """Integration tests for the complete RAG system workflow."""

    @patch('app.test_ollama_connection')
    @patch('requests.get')
    def test_full_workflow_success(self, mock_requests_get, mock_test_ollama, client, sample_files):
        """Test the complete workflow: initialize -> search -> summarize."""
        # Mock Ollama connection
        mock_test_ollama.return_value = (True, "Connection successful")
        mock_requests_get.return_value.status_code = 200
        
        # Step 1: Initialize the system
        response = client.post('/initialize', json={'root_dir': sample_files})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        # Step 2: Check status
        response = client.get('/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['initialized'] is True
        assert data['root_dir'] is not None
        
        # Step 3: Perform search
        response = client.post('/search', json={'query': 'test file', 'num_results': 5})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'results' in data
        assert isinstance(data['results'], list)
        
        # Step 4: Test chat functionality
        with patch('ollama.chat') as mock_ollama_chat:
            mock_response = Mock()
            mock_response.message = Mock()
            mock_response.message.content = "This is a chat response."
            mock_ollama_chat.return_value = mock_response
            
            response = client.post('/summarize', json={'message': 'Hello, how are you?'})
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert data['summary'] == "This is a chat response."

    @patch('app.test_ollama_connection')
    def test_workflow_ollama_failure(self, mock_test_ollama, client, sample_files):
        """Test workflow when Ollama is not available."""
        mock_test_ollama.return_value = (False, "Ollama not available")
        
        # Try to initialize - should fail
        response = client.post('/initialize', json={'root_dir': sample_files})
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Ollama test failed' in data['message']
        
        # Status should show not initialized
        response = client.get('/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['initialized'] is False

    def test_workflow_invalid_directory(self, client):
        """Test workflow with invalid directory."""
        response = client.post('/initialize', json={'root_dir': '/nonexistent/directory'})
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'

    @patch('app.test_ollama_connection')
    @patch('requests.get')
    def test_search_before_initialization(self, mock_requests_get, mock_test_ollama, client):
        """Test that search fails before initialization."""
        response = client.post('/search', json={'query': 'test'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not initialized' in data['message']

    @patch('app.test_ollama_connection')
    @patch('requests.get')
    def test_summarize_before_initialization(self, mock_requests_get, mock_test_ollama, client):
        """Test that file summarization fails before initialization."""
        response = client.post('/summarize', json={'file_path': '/test/file.txt'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not initialized' in data['message']

    @patch('app.test_ollama_connection')
    @patch('requests.get')
    @patch('app.rag_lock')
    def test_concurrent_initialization(self, mock_lock, mock_requests_get, mock_test_ollama, client, sample_files):
        """Test that concurrent initialization is handled properly."""
        # Mock lock to simulate another initialization in progress
        mock_lock.acquire.return_value = False
        
        response = client.post('/initialize', json={'root_dir': sample_files})
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Another initialization is in progress' in data['message']

    @patch('app.test_ollama_connection')
    @patch('requests.get')
    def test_file_summarization_workflow(self, mock_requests_get, mock_test_ollama, client, sample_files):
        """Test the file summarization workflow."""
        # Setup mocks
        mock_test_ollama.return_value = (True, "Connection successful")
        mock_requests_get.return_value.status_code = 200
        
        # Initialize the system
        response = client.post('/initialize', json={'root_dir': sample_files})
        assert response.status_code == 200
        
        # Mock file summarization
        with patch('app.rag') as mock_rag:
            mock_rag.summarize_file.return_value = "This is a summary of the test file."
            
            # Test file summarization
            test_file = os.path.join(sample_files, 'test.txt')
            response = client.post('/summarize', json={'file_path': test_file})
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert data['summary'] == "This is a summary of the test file."

    def test_error_handling_workflow(self, client):
        """Test error handling throughout the workflow."""
        # Test with malformed JSON
        response = client.post('/initialize', data='invalid json')
        assert response.status_code == 400
        
        # Test with missing required fields
        response = client.post('/search', json={})
        assert response.status_code == 400
        
        response = client.post('/summarize', json={})
        assert response.status_code == 400


class TestEndToEndScenarios:
    """End-to-end test scenarios simulating real user workflows."""

    @patch('app.test_ollama_connection')
    @patch('requests.get')
    def test_researcher_workflow(self, mock_requests_get, mock_test_ollama, client, sample_files):
        """Simulate a researcher using the system to find and analyze files."""
        # Setup
        mock_test_ollama.return_value = (True, "Connection successful")
        mock_requests_get.return_value.status_code = 200
        
        # 1. Researcher initializes the system with their document directory
        response = client.post('/initialize', json={'root_dir': sample_files})
        assert response.status_code == 200
        
        # 2. Researcher searches for Python files
        response = client.post('/search', json={'query': 'python script', 'num_results': 10})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        # 3. Researcher asks a general question
        with patch('ollama.chat') as mock_ollama_chat:
            mock_response = Mock()
            mock_response.message = Mock()
            mock_response.message.content = "Python is a programming language."
            mock_ollama_chat.return_value = mock_response
            
            response = client.post('/summarize', json={'message': 'What is Python?'})
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'

    @patch('app.test_ollama_connection')
    @patch('requests.get')
    def test_developer_workflow(self, mock_requests_get, mock_test_ollama, client, sample_files):
        """Simulate a developer using the system to understand a codebase."""
        # Setup
        mock_test_ollama.return_value = (True, "Connection successful")
        mock_requests_get.return_value.status_code = 200
        
        # 1. Developer initializes with project directory
        response = client.post('/initialize', json={'root_dir': sample_files})
        assert response.status_code == 200
        
        # 2. Developer searches for configuration files
        response = client.post('/search', json={'query': 'configuration json', 'num_results': 5})
        assert response.status_code == 200
        
        # 3. Developer wants to understand a specific file
        with patch('app.rag') as mock_rag:
            mock_rag.summarize_file.return_value = "This JSON file contains configuration settings."
            
            test_file = os.path.join(sample_files, 'data.json')
            response = client.post('/summarize', json={'file_path': test_file})
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'

    @patch('app.test_ollama_connection')
    @patch('requests.get')
    def test_system_recovery_workflow(self, mock_requests_get, mock_test_ollama, client, sample_files):
        """Test system recovery from various error states."""
        # Setup
        mock_test_ollama.return_value = (True, "Connection successful")
        mock_requests_get.return_value.status_code = 200
        
        # 1. Initialize successfully
        response = client.post('/initialize', json={'root_dir': sample_files})
        assert response.status_code == 200
        
        # 2. Simulate Ollama going down during operation
        mock_test_ollama.return_value = (False, "Connection lost")
        
        # 3. Try to use chat - should fail gracefully
        response = client.post('/summarize', json={'message': 'test'})
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        
        # 4. Search should still work (doesn't require Ollama)
        response = client.post('/search', json={'query': 'test'})
        assert response.status_code == 200
        
        # 5. Ollama comes back online
        mock_test_ollama.return_value = (True, "Connection restored")
        
        # 6. Re-initialize should work
        response = client.post('/initialize', json={'root_dir': sample_files})
        assert response.status_code == 200 