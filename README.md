# File Finder RAG System

A powerful file search and summarization system that uses RAG (Retrieval-Augmented Generation) to help you find and understand files in your system. The system features a modern web interface with AI-powered chat capabilities and supports multiple concurrent users.

## Features

### Core Functionality
- 🔍 **Semantic file search** using natural language queries
- 📝 **Automatic file summarization** using local LLM (Ollama)
- 💬 **Interactive chat interface** for direct communication with AI
- 🌐 **Web-based interface** accessible from any device on your network
- 👥 **Multi-user support** with thread-safe operations

### Modern UI & UX
- 🎨 **Sleek black & white design** with glass morphism effects
- 📱 **Responsive design** that works on desktop and mobile
- ⚡ **Real-time status indicators** for system and Ollama connection
- 🔄 **Smooth animations** and transitions
- 📊 **Visual feedback** for all operations

### AI Integration
- 🤖 **Ollama integration** with configurable server settings
- 📋 **Markdown rendering** for formatted AI responses
- ⚙️ **Custom model configuration** through web interface
- 🔧 **Connection testing** with real-time feedback
- 💾 **Persistent settings** using browser localStorage

### File Support
- 📄 **Multiple file types**:
  - Text files (.txt, .md, .py, .js, etc.)
  - PDF documents
  - Word documents (.docx)
  - PowerPoint presentations (.pptx)
- 🔍 **Smart content extraction** and indexing
- 📊 **Relevance scoring** for search results

### User Experience
- ❓ **Built-in help system** with step-by-step instructions
- ⚙️ **Settings panel** for Ollama configuration
- 🔔 **Toast notifications** for user feedback
- 📜 **Scrollable chat history** with message bubbles
- 🎯 **Floating action buttons** for quick navigation

## Prerequisites

- Python 3.8 or higher
- Ollama server with a compatible model (recommended: llama3.1:8b)
- Required Python packages (listed in requirements.txt)

## Installation

### Option 1: Docker Deployment (Recommended)

**Quick Start:**
```bash
git clone <repository-url>
cd local_rag_system
mkdir -p data files
docker-compose up -d
```

The Docker setup includes:
- ✅ **Complete environment** with all dependencies
- ✅ **Automatic Ollama setup** with model download
- ✅ **Production-ready configuration** options
- ✅ **Easy scaling** and management

**Access the application:**
- Web Interface: http://localhost:5000
- Ollama API: http://localhost:11434

For detailed Docker deployment instructions, see [docker-deployment.md](docker-deployment.md).

### Option 2: Manual Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd local_rag_system
```

2. **Install the required packages:**
```bash
pip install -r requirements.txt
```

3. **Install and setup Ollama:**
```bash
# Install Ollama from https://ollama.ai
# Start the Ollama server
ollama serve

# Pull the recommended model
ollama pull llama3.1:8b
```

## Usage

### Starting the System

#### Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# Monitor startup (first time will download models)
docker-compose logs -f

# Check service status
docker-compose ps
```

#### Manual Setup
1. **Start the Flask server:**
```bash
python app.py
```

2. **Access the web interface:**
   - On the same machine: `http://localhost:5000`
   - From other devices on the network: `http://<your-ip-address>:5000`

### Using the Interface

1. **Configure Ollama (if needed):**
   - Click the settings button (⚙️) in the top-left corner
   - Enter your Ollama server URL (default: `http://localhost:11434`)
   - Specify the model name (default: `llama3.1:8b`)
   - Test the connection and save settings

2. **Initialize the system:**
   - Enter a root directory path (or use "." for current directory)
   - Click "Initialize" and wait for completion
   - Monitor the system status indicator

3. **Search for files:**
   - Enter your search query in natural language
   - Select the number of results you want
   - Click "Search" to find relevant files

4. **Get AI summaries:**
   - Click "Summarize" on any search result
   - View the AI-generated summary in the chat interface
   - Continue the conversation by typing additional questions

5. **Chat with AI:**
   - Use the chat input at the bottom to ask questions
   - Get responses with markdown formatting support
   - View conversation history in the scrollable chat area

### Help System

Click the help button (❓) in the top-right corner for:
- Step-by-step usage instructions
- Tips for better search results
- Troubleshooting guidance

## Configuration

### Ollama Settings

The system supports flexible Ollama configuration:

- **Server URL**: Default is `http://localhost:11434`
- **Model**: Default is `llama3.1:8b`
- **Custom configurations**: Set through the web interface
- **Connection testing**: Built-in test functionality
- **Persistent storage**: Settings saved in browser localStorage

### Supported Models

Any Ollama-compatible model can be used, but recommended models include:
- `llama3.1:8b` (default, good balance of speed and quality)
- `llama3.1:70b` (higher quality, requires more resources)
- `codellama:7b` (optimized for code analysis)
- `mistral:7b` (fast and efficient)

## Multi-User Support

The system supports multiple concurrent users with:
- **Thread-safe operations** for all core functions
- **Shared index** for efficient resource usage
- **Real-time status updates** every 5 seconds
- **Visual indicators** for system state
- **Independent chat sessions** per user

## API Endpoints

### Core Endpoints
- `GET /`: Web interface
- `GET /status`: Check system initialization status
- `POST /initialize`: Initialize the system with a root directory
- `POST /search`: Search for files using a natural language query
- `POST /summarize`: Generate AI summary or chat response

### Ollama Integration
- `GET /test-ollama`: Test default Ollama connection
- `POST /test-ollama-custom`: Test custom Ollama configuration

### Request/Response Examples

**Initialize System:**
```json
POST /initialize
{
  "root_dir": "/path/to/your/files"
}
```

**Search Files:**
```json
POST /search
{
  "query": "Python scripts for data analysis",
  "num_results": 10
}
```

**Get Summary:**
```json
POST /summarize
{
  "file_path": "/path/to/file.py"
}
```

**Chat with AI:**
```json
POST /summarize
{
  "message": "Explain how machine learning works"
}
```

## Security Considerations

### Development vs Production

**Development (current setup):**
- Accessible to all devices on local network
- Debug mode enabled
- No authentication required

**For Production Use:**
1. Set `debug=False` in app.py
2. Implement proper authentication
3. Configure firewall rules for port 5000
4. Consider using HTTPS with SSL certificates
5. Set up proper logging and monitoring
6. Use environment variables for sensitive configuration

### Network Security
- The system binds to `0.0.0.0:5000` for network access
- Consider using a reverse proxy (nginx) for production
- Implement rate limiting for API endpoints
- Monitor for unusual activity patterns

## Troubleshooting

### Ollama Connection Issues

1. **Server not responding:**
   - Ensure Ollama is running: `ollama serve`
   - Check the server URL in settings
   - Verify firewall settings

2. **Model not found:**
   - Pull the model: `ollama pull llama3.1:8b`
   - Check model name spelling in settings
   - List available models: `ollama list`

3. **Connection timeout:**
   - Check network connectivity
   - Verify Ollama server is accessible
   - Try a different model

### System Issues

1. **Initialization fails:**
   - Check directory path validity
   - Ensure read permissions for the directory
   - Verify no other user is initializing
   - Check available disk space

2. **Search not working:**
   - Ensure system is initialized
   - Try rephrasing your query
   - Check if files are in supported formats
   - Verify file permissions

3. **UI not loading:**
   - Check browser console for errors
   - Clear browser cache
   - Ensure JavaScript is enabled
   - Try a different browser

### Performance Issues

1. **Slow initialization:**
   - Large directories take longer to process
   - Consider excluding unnecessary file types
   - Monitor system resources

2. **Slow search results:**
   - Reduce number of results requested
   - Use more specific queries
   - Check system memory usage

3. **Slow AI responses:**
   - Try a smaller/faster model
   - Check Ollama server resources
   - Verify network connection to Ollama

## Development

### Project Structure
```
local_rag_system/
├── app.py                    # Flask web server
├── file_finder.py            # Core RAG functionality
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Web interface
├── Dockerfile               # Docker container definition
├── docker-compose.yml       # Development Docker setup
├── docker-compose.prod.yml  # Production Docker setup
├── nginx.conf               # Nginx reverse proxy config
├── docker-deployment.md     # Docker deployment guide
└── README.md               # This file
```

### Key Components

- **Flask Server** (`app.py`): Web interface and API endpoints
- **RAG Engine** (`file_finder.py`): File indexing, search, and AI integration
- **Frontend** (`templates/index.html`): Modern web interface with chat capabilities

### Adding New Features

1. **Backend**: Modify `app.py` for new endpoints or `file_finder.py` for core functionality
2. **Frontend**: Update `templates/index.html` for UI changes
3. **Dependencies**: Add new packages to `requirements.txt`

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

### Areas for Contribution

- Additional file format support
- Enhanced AI model integration
- Improved search algorithms
- Better error handling
- Performance optimizations
- Security enhancements

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- **Faiss** for embedding and vector DB indexing
- **Ollama** for providing the local LLM infrastructure
- **Sentence Transformers** for semantic search capabilities
- **Flask** for the web framework
- **Tailwind CSS** for the modern UI styling 