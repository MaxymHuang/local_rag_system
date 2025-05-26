# File Finder RAG System

A powerful file search and summarization system that uses RAG (Retrieval-Augmented Generation) to help you find and understand files in your system. The system features a modern web interface and supports multiple concurrent users.

## Features

- 🔍 Semantic file search using natural language queries
- 📝 Automatic file summarization using local LLM (Ollama)
- 🌐 Web-based interface accessible from any device on your network
- 👥 Support for multiple concurrent users
- 📄 Support for various file types:
  - Text files
  - PDF documents
  - Word documents (.docx)
  - PowerPoint presentations (.pptx)
- 🔒 Thread-safe operations for multi-user environments

## Prerequisites

- Python 3.8 or higher
- Ollama server running locally with a compatible model
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd local_rag_system
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Make sure Ollama is running with your preferred model. The system is configured to use the model ID "1d35e3661de3" by default.

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Access the web interface:
   - On the same machine: `http://localhost:5000`
   - From other devices on the network: `http://<your-ip-address>:5000`

3. Using the interface:
   - Initialize the system by providing a root directory path
   - Wait for the initialization to complete
   - Enter your search query in natural language
   - View search results with relevance scores
   - Click "Summarize" on any file to generate a summary

## Multi-User Support

The system supports multiple concurrent users with the following features:
- Real-time system status updates
- Thread-safe initialization
- Shared index for efficient resource usage
- Visual indicators for system state
- Automatic status checks every 5 seconds

## API Endpoints

- `GET /`: Web interface
- `GET /status`: Check system status
- `POST /initialize`: Initialize the system with a root directory
- `POST /search`: Search for files using a query
- `POST /summarize`: Generate a summary for a specific file

## Security Considerations

1. The system is accessible to all devices on your local network
2. For production use:
   - Set `debug=False` in app.py
   - Implement proper authentication
   - Configure your firewall to allow access to port 5000
   - Consider using HTTPS for secure communication

## Troubleshooting

1. If you can't connect to the Ollama server:
   - Ensure Ollama is running
   - Check if the model ID is correct
   - Verify the Ollama server URL (default: http://localhost:11434)

2. If initialization fails:
   - Check if the directory path is valid
   - Ensure you have read permissions for the directory
   - Check if another user is currently initializing the system

3. If search results are not as expected:
   - Try rephrasing your query
   - Check if the file types are supported
   - Verify that the files are readable

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 