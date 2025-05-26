# File Finder RAG System

A powerful file search and summarization system using RAG (Retrieval-Augmented Generation) with a modern web interface, AI-powered chat, and Docker deployment support.

## ✨ Features

- 🔍 **Semantic file search** with natural language queries
- 📝 **AI summarization** using local Ollama models
- 💬 **Interactive chat interface** with markdown rendering
- 🎨 **Modern UI** with black/white design and real-time status
- ⚙️ **Configurable Ollama settings** through web interface
- 🐳 **Docker deployment** with production-ready setup
- 👥 **Multi-user support** with thread-safe operations
- 📄 **Multiple file types**: Text, PDF, Word, PowerPoint

## 🚀 Quick Start

### Docker (Recommended)
```bash
git clone <repository-url>
cd local_rag_system
mkdir -p data files
docker-compose up -d
```

Access: http://localhost:5000

### Manual Installation
```bash
git clone <repository-url>
cd local_rag_system
pip install -r requirements.txt

# Install Ollama from https://ollama.ai
ollama serve
ollama pull llama3.1:8b

python app.py
```

## 📖 Usage

1. **Configure Ollama** (⚙️ settings button) - set server URL and model
2. **Initialize system** - enter directory path and click "Initialize"
3. **Search files** - use natural language queries
4. **Get AI summaries** - click "Summarize" on any result
5. **Chat with AI** - ask questions in the chat interface

## 🔧 Configuration

### Ollama Settings
- **Default URL**: `http://localhost:11434`
- **Default Model**: `llama3.1:8b`
- **Supported Models**: llama3.1:8b/70b, codellama:7b, mistral:7b

### Docker Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://ollama:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1:8b` | Default model name |
| `FLASK_ENV` | `production` | Flask environment |

## 🏭 Production Deployment

```bash
# Production with resource limits and security
docker-compose -f docker-compose.prod.yml up -d

# With nginx reverse proxy and SSL
docker-compose -f docker-compose.prod.yml --profile with-proxy up -d
```

Features: Resource limits, security hardening, health checks, rate limiting, SSL support.

## 📁 Project Structure
```
local_rag_system/
├── app.py                    # Flask web server
├── file_finder.py            # Core RAG functionality
├── templates/index.html      # Web interface
├── Dockerfile               # Container definition
├── docker-compose.yml       # Development setup
├── docker-compose.prod.yml  # Production setup
├── nginx.conf               # Reverse proxy config
└── docker-deployment.md     # Detailed deployment guide
```

## 🛠️ API Endpoints

- `GET /` - Web interface
- `GET /status` - System status
- `POST /initialize` - Initialize with directory
- `POST /search` - Search files
- `POST /summarize` - AI summary/chat
- `GET /test-ollama` - Test Ollama connection

## 🚨 Troubleshooting

**Ollama Issues:**
- Ensure Ollama is running: `ollama serve`
- Check model availability: `ollama list`
- Test connection in settings panel

**Docker Issues:**
- Monitor logs: `docker-compose logs -f`
- Check service status: `docker-compose ps`
- See detailed guide: [docker-deployment.md](docker-deployment.md)

**Performance:**
- Use smaller models for faster responses
- Increase Docker resource limits for production
- Monitor system resources

## 🔒 Security

**Development:** Local access, debug mode enabled
**Production:** Use nginx proxy, SSL, rate limiting, read-only mounts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

Areas for contribution: file format support, AI integration, search algorithms, security enhancements.

## 📞 Support

- **Documentation**: [docker-deployment.md](docker-deployment.md) for detailed deployment
- **Issues**: Check logs and GitHub issues
- **Author**: [Maxym](https://github.com/MaxymHuang) | [LinkedIn](https://www.linkedin.com/in/maxymhuang/)

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama** - Local LLM infrastructure
- **Sentence Transformers** - Semantic search
- **Flask** - Web framework
- **Tailwind CSS** - UI styling 