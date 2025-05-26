# Docker Deployment Guide

This guide explains how to deploy the File Finder RAG System using Docker for both development and production environments.

## 📋 Prerequisites

- Docker Engine 20.10+ 
- Docker Compose 2.0+
- At least 4GB RAM (8GB+ recommended for production)
- 10GB+ free disk space for models and data

## 🚀 Quick Start (Development)

### 1. Basic Setup

```bash
# Clone the repository
git clone <repository-url>
cd local_rag_system

# Create directories for data and files
mkdir -p data files

# Start the services
docker-compose up -d
```

### 2. Wait for Model Download

The first startup will take several minutes as it downloads the `llama3.1:8b` model (~4.7GB):

```bash
# Monitor the model download progress
docker-compose logs -f ollama-init

# Check when services are ready
docker-compose ps
```

### 3. Access the Application

- **Web Interface**: http://localhost:5000
- **Ollama API**: http://localhost:11434

## 🏗️ File Structure

```
local_rag_system/
├── Dockerfile                 # Main application container
├── docker-compose.yml         # Development setup
├── docker-compose.prod.yml    # Production setup
├── .dockerignore             # Docker build exclusions
├── nginx.conf                # Nginx reverse proxy config
├── docker-deployment.md      # This guide
├── data/                     # Application data (mounted)
├── files/                    # Your files to search (mounted)
└── ssl/                      # SSL certificates (production)
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `FLASK_DEBUG` | `0` | Debug mode (0/1) |
| `OLLAMA_URL` | `http://ollama:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1:8b` | Default model name |

### Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./data` | `/app/data` | Application data & indexes |
| `./files` | `/app/files` | Files to search through |
| `ollama-data` | `/root/.ollama` | Ollama models & config |

## 🏭 Production Deployment

### 1. Production Setup

```bash
# Use the production compose file
docker-compose -f docker-compose.prod.yml up -d

# Or with nginx reverse proxy
docker-compose -f docker-compose.prod.yml --profile with-proxy up -d
```

### 2. SSL Configuration (Optional)

```bash
# Create SSL directory
mkdir -p ssl

# Add your SSL certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem

# Update nginx.conf with your domain
# Uncomment the HTTPS server block
```

### 3. Production Features

- **Resource Limits**: CPU and memory constraints
- **Security**: No new privileges, read-only mounts
- **Health Checks**: Comprehensive service monitoring
- **Nginx Proxy**: Load balancing and SSL termination
- **Rate Limiting**: API protection

## 🛠️ Management Commands

### Service Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a specific service
docker-compose restart rag-system

# View logs
docker-compose logs -f rag-system
docker-compose logs -f ollama

# Check service status
docker-compose ps
```

### Model Management

```bash
# Pull a different model
docker-compose exec ollama ollama pull mistral:7b

# List available models
docker-compose exec ollama ollama list

# Remove a model
docker-compose exec ollama ollama rm llama3.1:8b
```

### Data Management

```bash
# Backup application data
docker run --rm -v local_rag_system_ollama-data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-backup.tar.gz -C /data .

# Restore application data
docker run --rm -v local_rag_system_ollama-data:/data -v $(pwd):/backup alpine tar xzf /backup/ollama-backup.tar.gz -C /data

# Clean up unused volumes
docker volume prune
```

## 🔍 Monitoring & Debugging

### Health Checks

```bash
# Check application health
curl http://localhost:5000/

# Check Ollama health
curl http://localhost:11434/api/tags

# Check nginx health (if using proxy)
curl http://localhost/health
```

### Performance Monitoring

```bash
# Monitor resource usage
docker stats

# View detailed container info
docker-compose exec rag-system top
docker-compose exec ollama nvidia-smi  # If using GPU
```

### Debugging

```bash
# Access container shell
docker-compose exec rag-system bash
docker-compose exec ollama bash

# View application logs
docker-compose logs --tail=100 rag-system

# Debug network connectivity
docker-compose exec rag-system curl http://ollama:11434/api/tags
```

## 🚨 Troubleshooting

### Common Issues

1. **Model Download Fails**
   ```bash
   # Check internet connectivity
   docker-compose exec ollama curl -I https://ollama.ai
   
   # Manually pull model
   docker-compose exec ollama ollama pull llama3.1:8b
   ```

2. **Out of Memory**
   ```bash
   # Check available memory
   free -h
   
   # Use a smaller model
   docker-compose exec ollama ollama pull llama3.1:8b
   ```

3. **Permission Issues**
   ```bash
   # Fix data directory permissions
   sudo chown -R $USER:$USER data files
   chmod -R 755 data files
   ```

4. **Port Conflicts**
   ```bash
   # Check what's using the ports
   sudo netstat -tulpn | grep :5000
   sudo netstat -tulpn | grep :11434
   
   # Modify ports in docker-compose.yml
   ```

### Performance Optimization

1. **For Better Performance**
   ```yaml
   # In docker-compose.yml, increase resources:
   deploy:
     resources:
       limits:
         memory: 4G
         cpus: '2.0'
   ```

2. **For GPU Support** (if available)
   ```yaml
   # Add to ollama service:
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: 1
             capabilities: [gpu]
   ```

## 🔒 Security Considerations

### Development
- Services accessible on localhost only
- No authentication required
- Debug mode available

### Production
- Use nginx reverse proxy
- Enable SSL/TLS encryption
- Implement rate limiting
- Use read-only file mounts
- Enable security headers
- Monitor access logs

### Best Practices
- Regularly update base images
- Use specific image tags (not `latest`)
- Implement proper backup strategies
- Monitor resource usage
- Set up log rotation

## 📊 Scaling

### Horizontal Scaling
```yaml
# Scale the RAG system
docker-compose up -d --scale rag-system=3

# Use nginx for load balancing
upstream rag_backend {
    server rag-system_1:5000;
    server rag-system_2:5000;
    server rag-system_3:5000;
}
```

### Vertical Scaling
```yaml
# Increase resources per container
deploy:
  resources:
    limits:
      memory: 8G
      cpus: '4.0'
```

## 🔄 Updates & Maintenance

### Updating the Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

### Updating Models
```bash
# Pull newer model version
docker-compose exec ollama ollama pull llama3.1:8b

# Update environment variable
# Edit docker-compose.yml and restart
```

### Cleanup
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Complete cleanup
docker system prune -a --volumes
```

## 📞 Support

For issues and questions:
- Check the logs: `docker-compose logs`
- Review this guide
- Check the main README.md
- Open an issue on GitHub

## 🎯 Next Steps

After successful deployment:
1. Configure your file directories in `./files/`
2. Initialize the system through the web interface
3. Test search and summarization features
4. Set up monitoring and backups
5. Configure SSL for production use 