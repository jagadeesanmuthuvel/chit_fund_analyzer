# Docker/Podman Configuration

This directory contains all container configuration files for the Chit Fund Analyzer application.

> **Note**: This project supports both Docker and Podman container runtimes. All commands work with either runtime - the helper scripts automatically detect which one you have installed.

## Files

- **docker-compose.yml** - Standard Docker Compose configuration for local development/testing
- **docker-compose.prod.yml** - Production-optimized Docker Compose configuration
- **nginx/** - Nginx reverse proxy configuration (optional)

## Quick Start

### Local Development/Testing

```bash
# From this directory
docker-compose up -d

# Or from project root
docker-compose -f docker/docker-compose.yml up -d
```

Access at: http://localhost:8501

### Production Deployment

```bash
# Configure environment (from project root)
cp .env.example .env
# Edit .env with your settings

# Deploy
docker-compose -f docker/docker-compose.prod.yml up -d
```

## Helper Scripts

From the project root:

**Windows**:
```powershell
.\docker.ps1 run    # Start container
.\docker.ps1 stop   # Stop container
.\docker.ps1 logs   # View logs
```

**Linux/Mac**:
```bash
make up             # Start container
make down           # Stop container
make logs           # View logs
```

## Documentation

See the [docs](../docs/) directory for detailed documentation:

- [DOCKER_QUICKSTART.md](../docs/DOCKER_QUICKSTART.md) - Quick start guide
- [DOCKER.md](../docs/DOCKER.md) - Comprehensive deployment guide
- [DOCKER_CONFIG.md](../docs/DOCKER_CONFIG.md) - Configuration reference
- [DOCKER_COMPLETE.md](../docs/DOCKER_COMPLETE.md) - Complete setup overview

## Dockerfile Location

The main `Dockerfile` is located in the project root directory for standard Docker build conventions.

## Nginx Configuration

The `nginx/` directory contains:
- `nginx.conf` - Reverse proxy configuration
- WebSocket support for Streamlit
- Rate limiting and security headers
- SSL/HTTPS template (commented out)

To use Nginx in production:
```bash
docker-compose -f docker/docker-compose.prod.yml --profile with-nginx up -d
```

## Environment Variables

See `.env.example` in the project root for available configuration options.

## Network and Volumes

- **Network**: `chitfund-network` (bridge)
- **Volumes**: 
  - `chitfund-data` - Persistent data storage
  - Bind mounts for source code (development)
  - Read-only mounts for credentials

## Health Checks

All containers include health checks:
- Endpoint: `http://localhost:8501/_stcore/health`
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

## Resource Limits (Production)

- CPU: 2 cores (limit), 0.5 cores (reservation)
- Memory: 2GB (limit), 512MB (reservation)

Adjust in `docker-compose.prod.yml` as needed.
