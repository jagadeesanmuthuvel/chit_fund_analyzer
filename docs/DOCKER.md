# Docker Deployment Guide

This guide covers deploying the Chit Fund Analyzer application using Docker.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start production service
docker-compose up -d

# Start development service with hot reload
docker-compose --profile dev up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Makefile

```bash
# Build and run production
make build
make run

# Build and run development
make build-dev
make run-dev

# View logs
make logs

# Stop containers
make stop

# Clean up
make clean
```

## Docker Images

### Production Image
- **Target**: `production`
- **Tag**: `chit-fund-analyzer:latest`
- **Size**: ~400MB (optimized multi-stage build)
- **Features**:
  - Minimal runtime dependencies
  - Non-root user (chitfund)
  - Health checks enabled
  - Production-ready configuration

### Development Image
- **Target**: `development`
- **Tag**: `chit-fund-analyzer:dev`
- **Features**:
  - Hot reload enabled
  - Test dependencies included
  - Playwright browsers
  - Development tools (git, vim)

## Configuration

### Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Key variables:
- `APP_PORT`: Application port (default: 8501)
- `VERSION`: Docker image version tag
- `CREDENTIALS_PATH`: Path to Google OAuth credentials
- `ENABLE_CORS`: Enable CORS (true/false)

### Volumes

**Data Persistence**:
```yaml
volumes:
  - ./data:/app/data
```

**Hot Reload (Development)**:
```yaml
volumes:
  - ./chit_fund_analyzer:/app/chit_fund_analyzer
  - ./streamlit_app:/app/streamlit_app
```

**Credentials**:
```yaml
volumes:
  - ./oauth_credentials.json:/app/oauth_credentials.json:ro
```

## Building Images

### Build Production Image
```bash
docker build --target production -t chit-fund-analyzer:latest .
```

### Build Development Image
```bash
docker build --target development -t chit-fund-analyzer:dev .
```

### Build with Version Tag
```bash
docker build --target production -t chit-fund-analyzer:1.0.0 .
```

## Running Containers

### Production Container
```bash
docker run -d \
  --name chit-fund-app \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  chit-fund-analyzer:latest
```

### Development Container
```bash
docker run -d \
  --name chit-fund-dev \
  -p 8502:8501 \
  -v $(pwd)/chit_fund_analyzer:/app/chit_fund_analyzer \
  -v $(pwd)/streamlit_app:/app/streamlit_app \
  -v $(pwd)/data:/app/data \
  -e STREAMLIT_SERVER_RUN_ON_SAVE=true \
  chit-fund-analyzer:dev
```

## Docker Compose Services

### Production Service
```bash
docker-compose up -d chit-fund-app
```

Access at: http://localhost:8501

### Development Service
```bash
docker-compose --profile dev up -d
```

Access at: http://localhost:8502

### Production with Nginx (Optional)
```bash
docker-compose -f docker-compose.prod.yml --profile with-nginx up -d
```

## Health Checks

The container includes a health check:
```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' chit-fund-app

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' chit-fund-app
```

## Logs and Debugging

### View Logs
```bash
# Follow logs
docker logs -f chit-fund-app

# Last 100 lines
docker logs --tail 100 chit-fund-app

# With docker-compose
docker-compose logs -f
```

### Shell Access
```bash
# Production container
docker exec -it chit-fund-app /bin/bash

# Development container
docker exec -it chit-fund-dev /bin/bash
```

### Run Tests
```bash
# In development container
docker exec -it chit-fund-dev pytest tests/ -v

# Or with make
make test
```

## Production Deployment

### Step 1: Configure Environment
```bash
cp .env.example .env
# Edit .env with production values
```

### Step 2: Build Production Image
```bash
VERSION=1.0.0 make build
```

### Step 3: Deploy
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Step 4: Verify Deployment
```bash
# Check health
curl http://localhost:8501/_stcore/health

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Resource Limits

Production deployment includes resource limits:
- **CPU**: 2 cores (limit), 0.5 cores (reservation)
- **Memory**: 2GB (limit), 512MB (reservation)

Adjust in `docker-compose.prod.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

## Security Best Practices

1. **Non-root User**: App runs as `chitfund` user (UID 1000)
2. **Read-only Credentials**: Mount credentials as read-only
3. **XSRF Protection**: Enabled by default
4. **Minimal Image**: Production image uses slim Python base
5. **No Secrets in Image**: Use volume mounts or secrets management

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs chit-fund-app

# Inspect container
docker inspect chit-fund-app
```

### Port Already in Use
```bash
# Change port in .env or docker-compose
APP_PORT=8502 docker-compose up -d
```

### Permission Issues
```bash
# Fix data directory permissions
sudo chown -R 1000:1000 ./data
```

### Out of Memory
```bash
# Increase memory limit in docker-compose.prod.yml
memory: 4G
```

## Updating the Application

### Pull Latest Code
```bash
git pull origin main
```

### Rebuild and Redeploy
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Rolling Update (Production)
```bash
# Build new version
docker build --target production -t chit-fund-analyzer:1.1.0 .

# Update docker-compose.prod.yml with new version
VERSION=1.1.0 docker-compose -f docker-compose.prod.yml up -d
```

## Backup and Restore

### Backup Data
```bash
# Create backup
docker run --rm \
  -v $(pwd)/data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/data-$(date +%Y%m%d).tar.gz /data
```

### Restore Data
```bash
# Restore from backup
docker run --rm \
  -v $(pwd)/data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/data-20251207.tar.gz -C /
```

## Monitoring

### Resource Usage
```bash
# Real-time stats
docker stats chit-fund-app

# With docker-compose
docker-compose stats
```

### Health Monitoring
```bash
# Automated health check
watch -n 5 'docker inspect --format="{{.State.Health.Status}}" chit-fund-app'
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Build Docker Image
  run: docker build --target production -t chit-fund-analyzer:${{ github.sha }} .

- name: Push to Registry
  run: |
    docker tag chit-fund-analyzer:${{ github.sha }} registry.example.com/chit-fund-analyzer:latest
    docker push registry.example.com/chit-fund-analyzer:latest
```

## Further Reading

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Streamlit Docker Deployment](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
