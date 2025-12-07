# Docker Configuration Summary

This document provides an overview of all Docker-related files in the project.

## File Structure

```
chit_fund_analyzer/
├── Dockerfile                      # Multi-stage Docker build
├── .dockerignore                   # Files to exclude from Docker context
├── docker-compose.yml              # Development and production services
├── docker-compose.prod.yml         # Production-optimized deployment
├── .env.example                    # Environment variable template
├── docker.ps1                      # Windows PowerShell helper script
├── Makefile                        # Unix/Linux helper commands
├── DOCKER.md                       # Comprehensive deployment guide
├── DOCKER_QUICKSTART.md            # Quick start guide
├── nginx/
│   └── nginx.conf                  # Nginx reverse proxy configuration
└── .github/
    └── workflows/
        └── docker-build.yml        # CI/CD pipeline for Docker builds
```

## File Descriptions

### 1. Dockerfile

**Purpose**: Multi-stage build for optimized production and development images

**Stages**:
- `base`: Base Python 3.13-slim with system dependencies
- `builder`: Installs Python dependencies using uv
- `production`: Minimal runtime image (~400MB)
- `development`: Includes dev tools and test dependencies

**Key Features**:
- Non-root user (chitfund, UID 1000)
- Health checks
- Optimized layer caching
- Security hardening
- Streamlit configuration

**Build Targets**:
```bash
# Production (default)
docker build --target production -t chit-fund-analyzer:latest .

# Development
docker build --target development -t chit-fund-analyzer:dev .
```

### 2. .dockerignore

**Purpose**: Exclude unnecessary files from Docker build context

**Excludes**:
- Python cache files (`__pycache__`, `*.pyc`)
- Virtual environments (`.venv`, `venv`)
- Git files and history
- Test artifacts and logs
- IDE configurations
- Credentials and secrets
- Documentation files

**Benefits**:
- Faster builds
- Smaller build context
- Better security (no secrets in image)

### 3. docker-compose.yml

**Purpose**: Development and basic production deployment

**Services**:
- `chit-fund-app`: Production service (port 8501)
- `chit-fund-dev`: Development service with hot reload (port 8502, profile: dev)

**Features**:
- Volume mounts for data persistence
- Health checks
- Network isolation
- Automatic restart policies

**Usage**:
```bash
# Production
docker-compose up -d

# Development
docker-compose --profile dev up -d
```

### 4. docker-compose.prod.yml

**Purpose**: Production-optimized deployment with advanced features

**Services**:
- `chit-fund-app`: Production application with resource limits
- `nginx`: Reverse proxy (optional, profile: with-nginx)

**Features**:
- Resource limits (CPU: 2 cores, Memory: 2GB)
- Environment variable configuration via .env
- Persistent volume for data
- Logging configuration
- Nginx reverse proxy support

**Usage**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 5. .env.example

**Purpose**: Template for environment variables

**Variables**:
- `VERSION`: Docker image version tag
- `APP_PORT`: Application port (default: 8501)
- `NGINX_PORT`: Nginx HTTP port
- `NGINX_SSL_PORT`: Nginx HTTPS port
- `ENABLE_CORS`: CORS configuration
- `CREDENTIALS_PATH`: Path to OAuth credentials
- `LOG_LEVEL`: Logging level

**Setup**:
```bash
cp .env.example .env
# Edit .env with your values
```

### 6. docker.ps1

**Purpose**: PowerShell helper script for Windows users

**Commands**:
- `.\docker.ps1 build` - Build production image
- `.\docker.ps1 run` - Run production container
- `.\docker.ps1 dev` - Run development container
- `.\docker.ps1 stop` - Stop all containers
- `.\docker.ps1 logs` - View logs
- `.\docker.ps1 test` - Run tests
- `.\docker.ps1 clean` - Clean up resources
- `.\docker.ps1 prod` - Deploy production environment

**Features**:
- Color-coded output
- Automatic browser opening
- Interactive cleanup
- Environment validation

### 7. Makefile

**Purpose**: Unix/Linux/Mac command shortcuts

**Targets**:
- `make build` - Build production image
- `make run` - Run production container
- `make build-dev` - Build development image
- `make run-dev` - Run development container
- `make up` - Start with docker-compose
- `make down` - Stop docker-compose services
- `make test` - Run tests in container
- `make logs` - Show container logs
- `make shell` - Open shell in container
- `make clean` - Remove containers and images

### 8. nginx/nginx.conf

**Purpose**: Nginx reverse proxy configuration

**Features**:
- WebSocket support for Streamlit
- Rate limiting (10 req/s)
- Security headers
- Health check endpoint
- SSL/HTTPS support (commented template)
- Increased timeouts for long-running requests

**Usage**:
```bash
docker-compose -f docker-compose.prod.yml --profile with-nginx up -d
```

### 9. DOCKER.md

**Purpose**: Comprehensive Docker deployment documentation

**Contents**:
- Detailed installation instructions
- Configuration guide
- Building and running containers
- Docker Compose usage
- Health checks and monitoring
- Logs and debugging
- Production deployment steps
- Security best practices
- Troubleshooting guide
- Backup and restore procedures
- CI/CD integration examples

### 10. DOCKER_QUICKSTART.md

**Purpose**: Quick reference for common Docker commands

**Contents**:
- Prerequisites
- Quick start commands (Windows/Linux/Mac)
- Common tasks
- Production deployment steps
- Troubleshooting tips
- Next steps and resources

### 11. .github/workflows/docker-build.yml

**Purpose**: GitHub Actions CI/CD pipeline

**Triggers**:
- Push to main/develop branches
- Pull requests to main
- Release publications

**Jobs**:
1. Build production and development images
2. Run tests in container
3. Health check verification
4. Push to GitHub Container Registry (ghcr.io)
5. Generate deployment summary

**Features**:
- Multi-platform support
- Docker layer caching
- Automated testing
- Image versioning with tags
- Security scanning (can be added)

**Registry**:
- Images pushed to `ghcr.io/<owner>/chit-fund-analyzer`
- Tags: branch name, PR number, semver, commit SHA

## Image Sizes

- **Production**: ~400MB
  - Python 3.13-slim base
  - Core dependencies only
  - No dev tools

- **Development**: ~800MB
  - Includes pytest, playwright
  - Chromium browser
  - Development tools

## Security Features

1. **Non-root User**: Runs as `chitfund` (UID 1000)
2. **Read-only Credentials**: Mounted volumes are read-only
3. **No Secrets in Image**: Secrets via volumes or environment
4. **Security Headers**: Configured in nginx
5. **XSRF Protection**: Enabled by default
6. **Resource Limits**: Prevent DoS attacks
7. **Health Checks**: Automatic container monitoring

## Network Configuration

- **Default Network**: Bridge network `chitfund-network`
- **Ports**:
  - 8501: Production application
  - 8502: Development application (with hot reload)
  - 80: Nginx HTTP (optional)
  - 443: Nginx HTTPS (optional)

## Volume Configuration

### Development
```yaml
volumes:
  - ./chit_fund_analyzer:/app/chit_fund_analyzer  # Code hot reload
  - ./streamlit_app:/app/streamlit_app            # Code hot reload
  - ./data:/app/data                              # Data persistence
```

### Production
```yaml
volumes:
  - chitfund-data:/app/data                       # Named volume
  - ./oauth_credentials.json:/app/oauth_credentials.json:ro  # Credentials
```

## Deployment Scenarios

### 1. Local Development
```bash
docker-compose --profile dev up -d
```
- Hot reload enabled
- Source code mounted
- Port 8502

### 2. Local Production Testing
```bash
docker-compose up -d
```
- Production configuration
- Data persistence
- Port 8501

### 3. Production Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```
- Resource limits
- Production logging
- Health monitoring
- Optional Nginx proxy

### 4. CI/CD Pipeline
```bash
# Automated via GitHub Actions
# Builds, tests, and publishes on push/PR
```

## Maintenance Commands

### Update Application
```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Data
```bash
docker run --rm \
  -v $(pwd)/data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/data-$(date +%Y%m%d).tar.gz /data
```

### View Resource Usage
```bash
docker stats chit-fund-app
```

### Inspect Container
```bash
docker inspect chit-fund-app
```

## Troubleshooting Reference

| Issue | Solution |
|-------|----------|
| Port in use | Change `APP_PORT` in .env |
| Permission denied | Fix data dir: `chown -R 1000:1000 ./data` |
| Out of memory | Increase limits in docker-compose.prod.yml |
| Container won't start | Check logs: `docker logs chit-fund-app` |
| Health check failing | Inspect: `docker inspect chit-fund-app` |

## Best Practices

1. **Use .env for configuration**: Never hardcode sensitive values
2. **Mount credentials as read-only**: Prevent accidental modification
3. **Use named volumes for data**: Better management and backup
4. **Enable health checks**: Automatic container monitoring
5. **Set resource limits**: Prevent resource exhaustion
6. **Use multi-stage builds**: Smaller production images
7. **Run as non-root**: Enhanced security
8. **Keep logs manageable**: Configure log rotation
9. **Test locally first**: Validate before production
10. **Document changes**: Update this file when adding features

## Future Enhancements

- [ ] Multi-architecture builds (ARM64 support)
- [ ] Database integration (PostgreSQL)
- [ ] Redis caching layer
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Automated security scanning
- [ ] Kubernetes deployment manifests
- [ ] Helm charts
