# Podman Setup Guide

This project fully supports **Podman** as an alternative to Docker. All container commands work seamlessly with Podman.

## Current Setup

✓ **Podman 5.7.0** detected  
✓ **Docker Compose v5.0.0** available (as external provider)  
✓ Helper scripts configured for auto-detection

## Podman vs Docker

Podman is a daemonless container engine that's compatible with Docker commands:

- **Rootless by default** - Enhanced security
- **Compatible** - Uses same OCI images and commands
- **No daemon** - Direct fork/exec model
- **Pod support** - Kubernetes-like pod management

## Usage

All commands work exactly as documented. The helper scripts automatically detect Podman:

### Windows (PowerShell)

```powershell
.\docker.ps1 run      # Start container with Podman
.\docker.ps1 stop     # Stop container
.\docker.ps1 logs     # View logs
.\docker.ps1 build    # Build image
.\docker.ps1 clean    # Clean up containers/images
```

### Direct Podman Commands

You can also use Podman directly:

```powershell
# Build image
podman build -t chitfund-analyzer .

# Run container
podman run -d -p 8501:8501 --name chitfund chitfund-analyzer

# Use compose files
podman compose -f docker/docker-compose.yml up -d
podman compose -f docker/docker-compose.prod.yml up -d

# Stop and remove
podman stop chitfund
podman rm chitfund
```

## Compose Support

Podman integrates with Docker Compose:

```powershell
# Development
podman compose -f docker/docker-compose.yml up -d

# Production
podman compose -f docker/docker-compose.prod.yml up -d

# View logs
podman compose -f docker/docker-compose.yml logs -f

# Stop
podman compose -f docker/docker-compose.yml down
```

## Key Differences

### Networking

Podman uses different network modes:
- Default: **slirp4netns** (rootless)
- Alternative: **CNI** (Container Network Interface)

The compose files work with both.

### Storage

Podman stores images/containers in:
- Windows: `%LOCALAPPDATA%\containers\`
- Linux: `~/.local/share/containers/`

### Compatibility

All project features work identically:
- ✓ Image builds
- ✓ Container execution
- ✓ Volume mounts
- ✓ Port forwarding
- ✓ Environment variables
- ✓ Health checks
- ✓ Compose deployments

## Verification

Check your setup:

```powershell
# Version
podman --version

# Info
podman info

# Test build
podman build -t test-chitfund .

# Test run
podman run --rm test-chitfund python -c "import chit_fund_analyzer; print('OK')"
```

## Troubleshooting

### Port Already in Use

```powershell
# Find process using port
netstat -ano | findstr :8501

# Or use different port
podman run -p 8502:8501 chitfund-analyzer
```

### Permission Issues

Podman is rootless by default, which avoids most permission issues.

If you encounter file permission errors with volumes:
```powershell
# Check SELinux labels (Linux)
podman run -v ./data:/app/data:Z chitfund-analyzer
```

### Compose Not Found

If `podman compose` doesn't work:

1. Install docker-compose:
   ```powershell
   # Windows
   choco install docker-compose
   
   # Or download from GitHub releases
   ```

2. Or use podman-compose:
   ```powershell
   pip install podman-compose
   podman-compose -f docker/docker-compose.yml up
   ```

## Migration from Docker

No migration needed! Podman uses the same:
- Image format (OCI)
- Compose file format
- Command syntax
- Dockerfile syntax

Simply install Podman and the scripts will auto-detect it.

## Performance

Podman typically offers:
- **Faster startup** (no daemon)
- **Lower memory** usage
- **Better security** (rootless)
- **Same runtime** performance

## Resources

- [Podman Documentation](https://docs.podman.io/)
- [Podman Desktop](https://podman-desktop.io/) - GUI alternative
- [Migration Guide](https://podman.io/whatis.html)
- [Docker Compatibility](https://docs.podman.io/en/latest/markdown/podman.1.html#docker-compatibility)

## Next Steps

Your setup is ready! Try:

```powershell
# Build and run
.\docker.ps1 build
.\docker.ps1 run

# Access application
# http://localhost:8501
```

See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for deployment guide (works with Podman).
