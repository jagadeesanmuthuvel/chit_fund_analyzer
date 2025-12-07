# Chit Fund Analyzer - Docker Quick Start

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Download from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Navigate to docker directory
cd docker

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access at: **http://localhost:8501**

### Option 2: Docker CLI

```bash
# Build image
docker build -t chit-fund-analyzer .

# Run container
docker run -d -p 8501:8501 --name chit-fund-app chit-fund-analyzer

# View logs
docker logs -f chit-fund-app

# Stop
docker stop chit-fund-app
```

### Option 3: Helper Scripts

**Windows (PowerShell)**:
```powershell
.\docker.ps1 build
.\docker.ps1 run
```

**Linux/Mac**:
```bash
make build
make run
```

## Development

For local development with hot reload, run directly (not in Docker):

```bash
# Activate virtual environment
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run with hot reload
streamlit run streamlit_app/main.py
```

**Note**: The simplified Docker setup is optimized for production. For development, run locally for faster iteration.

## Production Deployment

```bash
# Configure environment (from project root)
cp .env.example .env
# Edit .env with your settings

# Deploy
docker-compose -f docker/docker-compose.prod.yml up -d
```

## Common Commands

```bash
# View logs
docker logs -f chit-fund-app

# Stop container
docker stop chit-fund-app

# Remove container
docker rm chit-fund-app

# Shell access
docker exec -it chit-fund-app bash

# Health check
curl http://localhost:8501/_stcore/health
```

## Troubleshooting

**Port in use?**
```bash
# Use different port
docker run -d -p 8502:8501 --name chit-fund-app chit-fund-analyzer
```

**Container won't start?**
```bash
docker logs chit-fund-app
```

**Permission errors?** (Linux/Mac)
```bash
sudo chown -R 1000:1000 ./data
```

## Next Steps

- See [DOCKER.md](DOCKER.md) for detailed documentation
- Configure Google Sheets: Mount `oauth_credentials.json`
- Production: Use `docker/docker-compose.prod.yml`
- For hot reload development: Run locally with `streamlit run streamlit_app/main.py`
