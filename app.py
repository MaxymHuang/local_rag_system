from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from file_finder import FileSystemRAG
import os
from threading import Lock
import ollama

app = Flask(__name__)
CORS(app)

# Initialize the RAG system with thread safety
rag = None
rag_lock = Lock()
current_root_dir = None
current_ollama_url = 'http://localhost:11434'
current_ollama_model = 'llama3.1:8b'

# Available sentence transformer models
available_sentence_models = [
    {
        'name': 'paraphrase-MiniLM-L3-v2',
        'display_name': 'Ultra-Fast (L3)',
        'description': 'Smallest and fastest model (61MB). Perfect for laptops with limited resources.',
        'size': '61MB',
        'speed': '⚡⚡⚡',
        'quality': '⭐⭐'
    },
    {
        'name': 'all-MiniLM-L6-v2',
        'display_name': 'Balanced (L6)',
        'description': 'Good balance of speed and quality (90MB). Recommended for most users.',
        'size': '90MB',
        'speed': '⚡⚡',
        'quality': '⭐⭐⭐'
    },
    {
        'name': 'all-MiniLM-L12-v2',
        'display_name': 'High Quality (L12)',
        'description': 'Better quality with slightly larger size (120MB). For better search accuracy.',
        'size': '120MB',
        'speed': '⚡',
        'quality': '⭐⭐⭐⭐'
    }
]

def test_ollama_connection(url=None, model=None):
    """Test Ollama connection with a simple prompt."""
    try:
        # Use provided settings or defaults
        url = url or current_ollama_url
        model = model or current_ollama_model
        
        # Configure ollama client for this test
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': 'hello'
            }],
            options={'host': url}
        )
        
        # Extract content from response - don't assume it's a dictionary
        try:
            # First try to get the message attribute/key
            if hasattr(response, 'message'):
                msg = response.message
            elif isinstance(response, dict) and 'message' in response:
                msg = response['message']
            else:
                return False, "No message found in Ollama response"
            
            # Now extract content from the message
            if hasattr(msg, 'content'):
                content = msg.content
            elif isinstance(msg, dict) and 'content' in msg:
                content = msg['content']
            elif isinstance(msg, str):
                content = msg
            else:
                return False, "Message object missing content attribute"
                
            return True, content
            
        except Exception as e:
            return False, f"Failed to extract message from response: {str(e)}"
            
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sentence-models', methods=['GET'])
def get_sentence_models():
    """Get available sentence transformer models."""
    return jsonify({
        'status': 'success',
        'models': available_sentence_models
    })

@app.route('/test-ollama', methods=['GET'])
def test_ollama():
    """Test endpoint for Ollama connection."""
    success, response = test_ollama_connection()
    return jsonify({
        'status': 'success' if success else 'error',
        'message': response
    })

@app.route('/test-ollama-custom', methods=['POST'])
def test_ollama_custom():
    """Test endpoint for custom Ollama connection."""
    data = request.json
    url = data.get('url', 'http://localhost:11434')
    model = data.get('model', 'llama3.1:8b')
    
    try:
        # Test connection to custom URL
        import requests
        response = requests.get(f"{url}/api/tags", timeout=10)
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'Server returned status code {response.status_code}'
            })
        
        # Test model availability
        success, response = test_ollama_connection(url, model)
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Connection successful! Model {model} is working.'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': response
            })
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'status': 'error',
            'message': f'Could not connect to {url}. Make sure Ollama is running.'
        })
    except requests.exceptions.Timeout:
        return jsonify({
            'status': 'error',
            'message': f'Connection to {url} timed out.'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Connection error: {str(e)}'
        })

@app.route('/status', methods=['GET'])
def status():
    global rag, current_root_dir
    return jsonify({
        'status': 'success',
        'initialized': rag is not None,
        'root_dir': current_root_dir if current_root_dir else None
    })

@app.route('/initialize', methods=['POST'])
def initialize():
    global rag, current_root_dir, current_ollama_url, current_ollama_model
    data = request.json
    root_dir = data.get('root_dir', '.')
    ollama_url = data.get('ollama_url', 'http://localhost:11434')
    ollama_model = data.get('ollama_model', 'llama3.1:8b')
    enable_ai_summary = data.get('enable_ai_summary', True)
    sentence_model = data.get('sentence_model', 'all-MiniLM-L6-v2')
    
    # Update current Ollama settings
    current_ollama_url = ollama_url
    current_ollama_model = ollama_model
    
    # Use lock to prevent concurrent initialization
    if not rag_lock.acquire(blocking=False):
        return jsonify({
            'status': 'error',
            'message': 'Another initialization is in progress. Please try again in a moment.'
        }), 409
    
    try:
        # Only test Ollama connection if AI summary is enabled
        if enable_ai_summary:
            success, response = test_ollama_connection(ollama_url, ollama_model)
            if not success:
                return jsonify({
                    'status': 'error',
                    'message': f'Ollama test failed: {response}'
                }), 500

        rag = FileSystemRAG(root_dir=root_dir, sentence_model=sentence_model)
        rag.build_index()
        current_root_dir = os.path.abspath(root_dir)
        return jsonify({
            'status': 'success',
            'message': f'Successfully initialized with directory: {current_root_dir} using model: {sentence_model}'
        })
    except Exception as e:
        rag = None
        current_root_dir = None
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        rag_lock.release()

@app.route('/search', methods=['POST'])
def search():
    if not rag:
        return jsonify({
            'status': 'error',
            'message': 'RAG system not initialized. Please initialize first.'
        }), 400
        
    data = request.json
    query = data.get('query')
    num_results = data.get('num_results', 10)  # Default to 10 results
    
    if not query:
        return jsonify({
            'status': 'error',
            'message': 'No query provided'
        }), 400
        
    try:
        results = rag.search(query, k=num_results)
        return jsonify({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    if not rag:
        return jsonify({
            'status': 'error',
            'message': 'RAG system not initialized. Please initialize first.'
        }), 400
        
    data = request.json
    file_path = data.get('file_path')
    message = data.get('message')
    ollama_url = data.get('ollama_url', current_ollama_url)
    ollama_model = data.get('ollama_model', current_ollama_model)
    
    # Handle general chat messages
    if message and not file_path:
        try:
            import ollama
            response = ollama.chat(
                model=ollama_model,
                messages=[{
                    'role': 'user',
                    'content': message
                }],
                options={'host': ollama_url}
            )
            
            # Extract content from response - don't assume it's a dictionary
            summary = None
            
            try:
                # First try to get the message attribute/key
                if hasattr(response, 'message'):
                    msg = response.message
                elif isinstance(response, dict) and 'message' in response:
                    msg = response['message']
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'No message found in Ollama response'
                    }), 500
                
                # Now extract content from the message
                if hasattr(msg, 'content'):
                    summary = msg.content
                elif isinstance(msg, dict) and 'content' in msg:
                    summary = msg['content']
                elif isinstance(msg, str):
                    summary = msg
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Message object missing content attribute'
                    }), 500
                    
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Failed to extract message from response: {str(e)}'
                }), 500
                
            if not summary:
                return jsonify({
                    'status': 'error',
                    'message': 'Empty response from Ollama server'
                }), 500
                
            return jsonify({
                'status': 'success',
                'summary': summary
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error communicating with Ollama: {str(e)}'
            }), 500
    
    # Handle file summarization
    if not file_path:
        return jsonify({
            'status': 'error',
            'message': 'No file path or message provided'
        }), 400
    
    # Normalize and resolve the file path relative to root directory
    try:
        # First normalize the path
        file_path = os.path.normpath(file_path)
        
        # If the path is not absolute, make it relative to the root directory
        if not os.path.isabs(file_path):
            file_path = os.path.join(current_root_dir, file_path)
            
        # Normalize again after joining paths
        file_path = os.path.normpath(file_path)
        
        print(f"Root directory: {current_root_dir}")  # Debug log
        print(f"Attempting to summarize file: {file_path}")  # Debug log
        
        # Check if file exists using a more robust method
        try:
            # Try to open the file to verify it exists and is accessible
            with open(file_path, 'rb') as f:
                # Just open and close to verify access
                pass
        except FileNotFoundError:
            return jsonify({
                'status': 'error',
                'message': f'File does not exist: {file_path}'
            }), 404
        except PermissionError:
            return jsonify({
                'status': 'error',
                'message': f'Permission denied: {file_path}'
            }), 403
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error accessing file: {str(e)}'
            }), 500
            
        # Check if it's a file
        if not os.path.isfile(file_path):
            return jsonify({
                'status': 'error',
                'message': f'Path is not a file: {file_path}'
            }), 400
            
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            return jsonify({
                'status': 'error',
                'message': f'File is not readable: {file_path}'
            }), 403
    
        # Test Ollama connection before summarization
        success, response = test_ollama_connection(ollama_url, ollama_model)
        if not success:
            return jsonify({
                'status': 'error',
                'message': f'Ollama test failed: {response}'
            }), 500
            
        try:
            summary = rag.summarize_file(file_path, ollama_url=ollama_url, ollama_model=ollama_model)
            print(f"Debug: Generated summary: {summary[:100]}...")  # Log first 100 chars of summary
            # Check if the summary is an error message
            if summary.startswith('Error'):
                print(f"Debug: Summary is an error message: {summary}")
                return jsonify({
                    'status': 'error',
                    'message': summary
                }), 500
            print("Debug: Sending successful response to frontend")
            response = jsonify({
                'status': 'success',
                'summary': summary
            })
            print(f"Debug: Response content: {response.get_data(as_text=True)[:100]}...")  # Log first 100 chars of response
            return response
        except Exception as e:
            print(f"Error during summarization: {str(e)}")  # Debug log
            return jsonify({
                'status': 'error',
                'message': f'Error during summarization: {str(e)}'
            }), 500
    except Exception as e:
        print(f"Error processing file path: {str(e)}")  # Debug log
        return jsonify({
            'status': 'error',
            'message': f'Error processing file path: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000) 