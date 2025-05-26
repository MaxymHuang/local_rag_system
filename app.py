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

def test_ollama_connection():
    """Test Ollama connection with a simple prompt."""
    try:
        response = ollama.chat(
            model='hf.co/bartowski/Dolphin3.0-Llama3.2-3B-GGUF:Q4_K_M',
            messages=[{
                'role': 'user',
                'content': 'hello'
            }]
        )
        return True, response['message']['content']
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-ollama', methods=['GET'])
def test_ollama():
    """Test endpoint for Ollama connection."""
    success, response = test_ollama_connection()
    return jsonify({
        'status': 'success' if success else 'error',
        'message': response
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
    global rag, current_root_dir
    data = request.json
    root_dir = data.get('root_dir', '.')
    
    # Use lock to prevent concurrent initialization
    if not rag_lock.acquire(blocking=False):
        return jsonify({
            'status': 'error',
            'message': 'Another initialization is in progress. Please try again in a moment.'
        }), 409
    
    try:
        # Test Ollama connection before initialization
        success, response = test_ollama_connection()
        if not success:
            return jsonify({
                'status': 'error',
                'message': f'Ollama test failed: {response}'
            }), 500

        rag = FileSystemRAG(root_dir=root_dir)
        rag.build_index()
        current_root_dir = os.path.abspath(root_dir)
        return jsonify({
            'status': 'success',
            'message': f'Successfully initialized with directory: {current_root_dir}'
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
    
    if not file_path:
        return jsonify({
            'status': 'error',
            'message': 'No file path provided'
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
        success, response = test_ollama_connection()
        if not success:
            return jsonify({
                'status': 'error',
                'message': f'Ollama test failed: {response}'
            }), 500
            
        try:
            summary = rag.summarize_file(file_path)
            # Check if the summary is an error message
            if summary.startswith('Error'):
                return jsonify({
                    'status': 'error',
                    'message': summary
                }), 500
            return jsonify({
                'status': 'success',
                'summary': summary
            })
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