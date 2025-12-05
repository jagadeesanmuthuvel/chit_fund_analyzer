# Chit Fund Analyzer - Setup Guide

A comprehensive setup guide for deploying the Chit Fund Analyzer application in both development and production environments.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Production Setup](#production-setup)
4. [Environment Configuration](#environment-configuration)
5. [Deployment Options](#deployment-options)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

## Prerequisites

### System Requirements
- **Python**: 3.13+ (recommended 3.13.2)
- **Memory**: Minimum 2GB RAM, 4GB+ recommended for production
- **Storage**: At least 1GB free space
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)

### Required Tools
- **Git**: For version control and cloning the repository
- **UV Package Manager**: For dependency management (recommended)
- **Alternative**: pip + virtualenv (if UV is not available)

---

## Development Setup

### 🚀 Quick Start (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/jagadeesanmuthuvel/chit_fund_analyzer.git
cd chit_fund_analyzer

# 2. Install UV package manager (if not already installed)
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Create virtual environment and install dependencies
uv venv
uv sync

# 4. Activate virtual environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 5. Run the application
python run_app.py
```

### 📦 Alternative Setup (Using pip)

```bash
# 1. Clone the repository
git clone https://github.com/jagadeesanmuthuvel/chit_fund_analyzer.git
cd chit_fund_analyzer

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
streamlit run streamlit_app.py
```

### 🧪 Verify Development Setup

```bash
# Test module functionality
python test_module.py

# Test Streamlit app components
python test_streamlit.py

# Run demo notebook (requires Jupyter)
jupyter lab chit_fund_analyzer_demo.ipynb
```

---

## Production Setup

### 🌐 Docker Deployment (Recommended for Production)

#### Create Dockerfile
```dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

#### Create docker-compose.yml
```yaml
version: '3.8'

services:
  chit-fund-analyzer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - PYTHONPATH=/app
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_HEADLESS=true
    volumes:
      - ./data:/app/data  # For persistent data storage
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### Deploy with Docker
```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### ☁️ Cloud Deployment Options

#### 1. Streamlit Cloud (Free Tier)
```bash
# 1. Push code to GitHub
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main

# 2. Visit https://share.streamlit.io/
# 3. Connect GitHub repository
# 4. Deploy from main branch
```

#### 2. Heroku Deployment
Create `Procfile`:
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

Create `requirements.txt`:
```bash
# Generate requirements file
pip freeze > requirements.txt
```

Deploy:
```bash
# Install Heroku CLI and login
heroku create chit-fund-analyzer-app
git push heroku main
heroku open
```

#### 3. AWS EC2 Deployment
```bash
# 1. Launch EC2 instance (Ubuntu 20.04 LTS)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3.13 python3.13-venv nginx -y

# 4. Clone and setup application
git clone https://github.com/jagadeesanmuthuvel/chit_fund_analyzer.git
cd chit_fund_analyzer
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 5. Create systemd service
sudo nano /etc/systemd/system/chit-fund-analyzer.service
```

SystemD service file:
```ini
[Unit]
Description=Chit Fund Analyzer Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/chit_fund_analyzer
Environment=PATH=/home/ubuntu/chit_fund_analyzer/.venv/bin
ExecStart=/home/ubuntu/chit_fund_analyzer/.venv/bin/streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable chit-fund-analyzer
sudo systemctl start chit-fund-analyzer
```

### 🔒 Nginx Reverse Proxy (Production Security)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
}
```

---

## Environment Configuration

### 🔧 Development Environment Variables
Create `.env` file:
```bash
# Development settings
ENVIRONMENT=development
DEBUG=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### 🔐 Production Environment Variables
```bash
# Production settings
ENVIRONMENT=production
DEBUG=false
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
```

### ⚙️ Configuration Files

#### Development Config (`config/development.toml`)
```toml
[server]
port = 8501
host = "localhost"
headless = false

[browser]
gatherUsageStats = false

[logger]
level = "debug"

[theme]
base = "light"
```

#### Production Config (`config/production.toml`)
```toml
[server]
port = 8501
host = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200

[browser]
gatherUsageStats = false

[logger]
level = "warning"

[theme]
base = "light"
```

---

## Deployment Options

### 🔄 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy Chit Fund Analyzer

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python test_module.py
        python test_streamlit.py

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to production
      run: |
        # Add your deployment commands here
        echo "Deploying to production..."
```

### 🐳 Kubernetes Deployment

#### Deployment manifest (`k8s/deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chit-fund-analyzer
spec:
  replicas: 2
  selector:
    matchLabels:
      app: chit-fund-analyzer
  template:
    metadata:
      labels:
        app: chit-fund-analyzer
    spec:
      containers:
      - name: app
        image: chit-fund-analyzer:latest
        ports:
        - containerPort: 8501
        env:
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: chit-fund-analyzer-service
spec:
  selector:
    app: chit-fund-analyzer
  ports:
  - port: 80
    targetPort: 8501
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl get services
```

---

## Troubleshooting

### 🔍 Common Issues and Solutions

#### Issue: Import Errors
```bash
# Problem: Module not found errors
# Solution: Ensure virtual environment is activated and dependencies installed
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Issue: Port Already in Use
```bash
# Problem: Port 8501 is already in use
# Solution: Use a different port
streamlit run streamlit_app.py --server.port 8502
```

#### Issue: Permission Denied (Linux/macOS)
```bash
# Problem: Permission errors
# Solution: Fix file permissions
chmod +x run_app.py
sudo chown -R $USER:$USER .
```

#### Issue: Memory Issues
```bash
# Problem: Out of memory errors
# Solution: Increase system memory or optimize configuration
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=50
export STREAMLIT_SERVER_MAX_MESSAGE_SIZE=50
```

### 📊 Performance Optimization

#### For Large Datasets
```python
# In streamlit_app.py, add caching
@st.cache_data
def load_large_scenario_analysis(bid_range, num_scenarios):
    # Cache expensive operations
    pass

@st.cache_resource
def get_analyzer_instance():
    # Cache resource-intensive objects
    pass
```

#### Memory Management
```bash
# Monitor memory usage
htop  # or Task Manager on Windows

# Limit Python memory
export PYTHONMALLOC=malloc
export MALLOC_ARENA_MAX=2
```

### 🐛 Debugging

#### Enable Debug Mode
```python
# Add to streamlit_app.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug information
if st.sidebar.checkbox("Debug Mode"):
    st.write("Debug info:", st.session_state)
```

#### Log Analysis
```bash
# View application logs
tail -f logs/app.log

# Docker logs
docker logs container-name -f

# Systemd logs
journalctl -u chit-fund-analyzer -f
```

---

## Maintenance

### 🔄 Updates and Upgrades

#### Regular Maintenance
```bash
# 1. Update dependencies
pip list --outdated
pip install --upgrade package-name

# 2. Update requirements
pip freeze > requirements.txt

# 3. Test after updates
python test_module.py
python test_streamlit.py
```

#### Security Updates
```bash
# 1. Check for security vulnerabilities
pip audit

# 2. Update to latest secure versions
pip install --upgrade pip setuptools

# 3. Review and update dependencies
pip-review --auto
```

### 📊 Monitoring

#### Health Checks
```python
# Add to streamlit_app.py
def health_check():
    try:
        # Test core functionality
        from chit_fund_analyzer import ChitFundConfig
        return {"status": "healthy", "timestamp": datetime.now()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

#### Performance Monitoring
```bash
# Monitor resource usage
# CPU and memory
top -p $(pgrep -f streamlit)

# Network
netstat -tulpn | grep 8501

# Disk usage
df -h
du -sh chit_fund_analyzer/
```

### 🔐 Security Checklist

- [ ] Use HTTPS in production
- [ ] Enable XSRF protection
- [ ] Disable CORS in production
- [ ] Regular dependency updates
- [ ] Monitor for vulnerabilities
- [ ] Secure environment variables
- [ ] Regular backups
- [ ] Access logging
- [ ] Rate limiting (if needed)
- [ ] Firewall configuration

### 📋 Backup Strategy

```bash
# 1. Backup application code
git push origin main

# 2. Backup configuration files
tar -czf config-backup-$(date +%Y%m%d).tar.gz config/ .env

# 3. Backup user data (if any)
cp -r data/ backup/data-$(date +%Y%m%d)/

# 4. Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/chit-fund-analyzer"
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/backup-$DATE.tar.gz" \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    .
```

---

## 📞 Support

### Getting Help
- **Documentation**: Check `README.md` and `STREAMLIT_README.md`
- **Issues**: Open GitHub issues for bugs or feature requests
- **Testing**: Run test scripts to verify functionality
- **Logs**: Check application logs for error details

### Performance Tuning
- **Memory**: Adjust `STREAMLIT_SERVER_MAX_UPLOAD_SIZE`
- **Caching**: Implement `@st.cache_data` for expensive operations
- **Connection**: Use `@st.cache_resource` for database connections
- **Optimization**: Profile code and optimize bottlenecks

---

## 📝 Quick Reference

### Development Commands
```bash
python run_app.py                    # Start development server
python test_module.py                # Test core functionality
python test_streamlit.py             # Test Streamlit components
streamlit run streamlit_app.py       # Direct Streamlit run
```

### Production Commands
```bash
docker-compose up -d                 # Start with Docker
systemctl start chit-fund-analyzer   # Start systemd service
kubectl apply -f k8s/                # Deploy to Kubernetes
nginx -s reload                      # Reload Nginx config
```

### Useful URLs
- **Local Development**: http://localhost:8501
- **Health Check**: http://localhost:8501/_stcore/health
- **Metrics**: http://localhost:8501/_stcore/metrics (if enabled)

This setup guide provides comprehensive instructions for deploying the Chit Fund Analyzer in various environments, from local development to enterprise production deployments.