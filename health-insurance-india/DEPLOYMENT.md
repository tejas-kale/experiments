# 🚀 Deployment Guide

Complete guide for deploying Health Insurance India CLI in various environments.

## Table of Contents

- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Management](#database-management)
- [Monitoring and Logging](#monitoring-and-logging)

---

## 📦 Local Development

### Prerequisites

- Python 3.11 or higher
- pip and virtualenv
- Git
- Anthropic API key

### Setup Steps

```bash
# 1. Clone repository
git clone <repository-url>
cd health-insurance-india

# 2. Create virtual environment
python3.11 -m venv venv

# 3. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 6. Initialize database
python cli.py db init

# 7. Collect initial data (optional)
python cli.py collect --all

# 8. Run CLI
python cli.py --help

# 9. Start API server (optional)
python cli.py serve --reload
```

### Troubleshooting

#### ImportError: No module named 'X'

```bash
pip install -r requirements.txt --upgrade
```

#### Database errors

```bash
# Reset database
python cli.py db reset
python cli.py db init
```

#### PDF extraction fails

```bash
# Install system dependencies for PyMuPDF
# On Ubuntu/Debian:
sudo apt-get install python3-dev

# On MacOS:
brew install mupdf-tools
```

---

## 🏭 Production Deployment

### Option 1: systemd Service (Linux)

1. **Create service file**: `/etc/systemd/system/health-insurance-api.service`

```ini
[Unit]
Description=Health Insurance India API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/health-insurance-india
Environment="PATH=/opt/health-insurance-india/venv/bin"
Environment="ANTHROPIC_API_KEY=your_key_here"
ExecStart=/opt/health-insurance-india/venv/bin/python cli.py serve --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Enable and start service**:

```bash
sudo systemctl enable health-insurance-api
sudo systemctl start health-insurance-api
sudo systemctl status health-insurance-api
```

3. **View logs**:

```bash
sudo journalctl -u health-insurance-api -f
```

### Option 2: Gunicorn + Nginx

1. **Install Gunicorn**:

```bash
pip install gunicorn
```

2. **Create Gunicorn config**: `gunicorn.conf.py`

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 120
timeout = 120
accesslog = "/var/log/health-insurance/access.log"
errorlog = "/var/log/health-insurance/error.log"
loglevel = "info"
```

3. **Run with Gunicorn**:

```bash
gunicorn api:app -c gunicorn.conf.py
```

4. **Nginx configuration**: `/etc/nginx/sites-available/health-insurance`

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Increase max upload size for document uploads
    client_max_body_size 50M;
}
```

5. **Enable site and restart Nginx**:

```bash
sudo ln -s /etc/nginx/sites-available/health-insurance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🐳 Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p data/documents data/metadata logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "cli.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: health-insurance-api
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=sqlite:///./data/policies.db
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: health-insurance-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker-compose build

# Run services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Docker Commands

```bash
# Initialize database inside container
docker-compose exec api python cli.py db init

# Collect documents
docker-compose exec api python cli.py collect --all

# Access shell
docker-compose exec api bash

# View API logs
docker-compose logs -f api
```

---

## ☁️ Cloud Deployment

### AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04, t2.medium or larger)

2. **Connect and setup**:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Clone repository
git clone <your-repo-url>
cd health-insurance-india

# Follow production deployment steps
```

3. **Configure security group**:
   - Allow inbound traffic on port 80 (HTTP)
   - Allow inbound traffic on port 443 (HTTPS)
   - Allow SSH (port 22) from your IP only

4. **Set up SSL with Let's Encrypt**:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Google Cloud Run

1. **Build and push Docker image**:

```bash
# Build
docker build -t gcr.io/YOUR_PROJECT_ID/health-insurance:latest .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/health-insurance:latest
```

2. **Deploy to Cloud Run**:

```bash
gcloud run deploy health-insurance \
  --image gcr.io/YOUR_PROJECT_ID/health-insurance:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=your_key_here \
  --memory 2Gi \
  --timeout 300
```

### Heroku

1. **Create `Procfile`**:

```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

2. **Deploy**:

```bash
# Login
heroku login

# Create app
heroku create your-app-name

# Set config vars
heroku config:set ANTHROPIC_API_KEY=your_key_here

# Deploy
git push heroku main

# Open app
heroku open
```

### Railway

1. **Create `railway.json`**:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python cli.py serve --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. **Deploy**: Connect your GitHub repo in Railway dashboard

---

## ⚙️ Environment Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | Your Anthropic API key |
| `DATABASE_URL` | No | `sqlite:///./data/policies.db` | Database connection string |
| `API_HOST` | No | `0.0.0.0` | API host address |
| `API_PORT` | No | `8000` | API port |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Production Recommendations

```env
# Production .env
ANTHROPIC_API_KEY=sk-ant-xxx
DATABASE_URL=sqlite:///./data/policies.db
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Performance tuning
WORKERS=4
TIMEOUT=120
KEEPALIVE=5
```

---

## 🗄️ Database Management

### Backup Database

```bash
# Backup SQLite database
cp data/policies.db data/backups/policies_$(date +%Y%m%d).db

# Backup with compression
tar -czf data/backups/policies_$(date +%Y%m%d).tar.gz data/
```

### Restore Database

```bash
# Restore from backup
cp data/backups/policies_20240101.db data/policies.db

# Restore and initialize
python cli.py db reset
python cli.py collect --all
```

### Database Migrations

If you modify models, recreate the database:

```bash
python cli.py db reset
python cli.py db init
python cli.py collect --all
```

For production with data, use Alembic:

```bash
# Install
pip install alembic

# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

---

## 📊 Monitoring and Logging

### Application Logs

Logs are stored in `logs/` directory:

```bash
# View today's logs
tail -f logs/$(date +%Y%m%d).log

# Search logs
grep "ERROR" logs/*.log

# Monitor in real-time
tail -f logs/*.log
```

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check with details
curl http://localhost:8000/ | jq
```

### Metrics

Monitor these metrics in production:

- Request count
- Response times
- Error rates
- Database size
- Memory usage
- CPU usage

### Prometheus + Grafana (Optional)

1. **Add prometheus client**:

```bash
pip install prometheus-client
```

2. **Add metrics endpoint in `api.py`**:

```python
from prometheus_client import make_asgi_app

# Mount metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

3. **Configure Prometheus** to scrape `/metrics`

---

## 🔒 Security

### API Key Management

**Never** commit API keys to version control:

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
```

Use environment variables or secret managers:

- AWS Secrets Manager
- Google Secret Manager
- HashiCorp Vault
- Kubernetes Secrets

### Rate Limiting

Add rate limiting to API:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/chat")
@limiter.limit("10/minute")
def chat_endpoint():
    ...
```

### HTTPS

Always use HTTPS in production:

```bash
# Let's Encrypt with Certbot
sudo certbot --nginx -d your-domain.com
```

---

## 🔧 Troubleshooting

### Common Issues

#### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### Permission errors

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Fix permissions
chmod +x cli.py
```

#### Out of memory

Increase Docker memory limit or EC2 instance size.

```bash
# Check memory usage
docker stats

# Limit memory in docker-compose.yml
services:
  api:
    mem_limit: 2g
```

---

## 📞 Support

For deployment issues:

1. Check application logs in `logs/`
2. Check system logs: `journalctl -xe`
3. Verify environment variables
4. Test database connection
5. Check network/firewall settings

---

## ✅ Pre-Deployment Checklist

- [ ] Environment variables set correctly
- [ ] Database initialized
- [ ] API key configured
- [ ] Logs directory writable
- [ ] Port 8000 accessible
- [ ] HTTPS configured (production)
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Health checks passing
- [ ] Documentation updated

---

**Happy Deploying! 🚀**
