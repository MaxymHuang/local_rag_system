from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from file_finder import FileSystemRAG
import os
from threading import Lock

app = Flask(__name__)
CORS(app)

# Initialize the RAG system with thread safety
rag = None
rag_lock = Lock()
current_root_dir = None

@app.route('/')
def index():
    return render_template('index.html')

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
    
    if not query:
        return jsonify({
            'status': 'error',
            'message': 'No query provided'
        }), 400
        
    try:
        results = rag.search(query)
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
        
    try:
        summary = rag.summarize_file(file_path)
        return jsonify({
            'status': 'success',
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000) 