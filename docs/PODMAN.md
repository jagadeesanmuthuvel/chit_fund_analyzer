# Using Podman with Chit Fund Analyzer

Podman is a daemonless container engine that is compatible with Docker. This guide shows how to use Podman instead of Docker.

## Prerequisites

### Install Podman

**Windows**:
```powershell
# Using Winget
winget install RedHat.Podman

# Or download from: https://podman.io/getting-started/installation
```

**Linux**:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install podman

# Fedora/RHEL
sudo dnf install podman

# Arch
sudo pacman -S podman
```

**macOS**:
```bash
brew install podman
```

### Install Podman Compose

```bash
# Using pip
pip install podman-compose

# Or using system package manager (Linux)
sudo apt-get install podman-compose  # Ubuntu/Debian
sudo dnf install podman-compose      # Fedora/RHEL
```

## Automatic Detection

The helper scripts (`docker.ps1` and `Makefile`) automatically detect whether you're using Docker or Podman:

```powershell
# Windows - automatically uses podman-compose
.\docker.ps1 run

# Linux/Mac - automatically uses podman-compose
make up
```

You'll see: `Using: podman` when running the scripts.

## Manual Usage

### Building the Image

```bash
# Build image with Podman
podman build -t chitfund-analyzer .

# Or use Podman Compose
podman-compose -f docker/docker-compose.yml build
```

### Running Containers

```bash
# Start with Podman Compose
podman-compose -f docker/docker-compose.yml up -d

# Or run directly
podman run -d \
  -p 8501:8501 \
  -v ./data:/app/data \
  --name chitfund-analyzer \
  chitfund-analyzer
```

### Managing Containers

```bash
# List running containers
podman ps

# Stop container
podman stop chitfund-analyzer

# Remove container
podman rm chitfund-analyzer

# View logs
podman logs -f chitfund-analyzer
```

## Key Differences from Docker

### 1. Rootless by Default

Podman runs containers without root privileges:

```bash
# No sudo required (unlike Docker)
podman run -d -p 8501:8501 chitfund-analyzer
```

### 2. No Daemon

Podman doesn't require a background daemon:

```bash
# No need to start a service like Docker Desktop
podman ps  # Works immediately
```

### 3. Pod Support

Podman can manage groups of containers as "pods":

```bash
# Create a pod (similar to Kubernetes)
podman pod create --name chitfund-pod -p 8501:8501

# Run container in the pod
podman run -d --pod chitfund-pod chitfund-analyzer
```

### 4. Compatibility

Most Docker commands work with Podman:

```bash
# Docker command
docker ps

# Equivalent Podman command
podman ps

# Or create an alias
alias docker=podman
```

## Using Podman Desktop (Optional)

Podman Desktop provides a GUI similar to Docker Desktop:

**Installation**:
```bash
# Download from: https://podman-desktop.io/downloads
```

**Features**:
- Visual container management
- Image building and inspection
- Pod management
- Docker compatibility layer

## Compose File Compatibility

The existing compose files work with Podman Compose:

```bash
# Development
podman-compose -f docker/docker-compose.yml up -d

# Production
podman-compose -f docker/docker-compose.prod.yml up -d
```

## Troubleshooting

### Port Binding Issues

If you get permission errors on ports < 1024:

```bash
# Allow binding to privileged ports
sudo sysctl net.ipv4.ip_unprivileged_port_start=80
```

### SELinux Issues (Linux)

If volumes don't mount correctly:

```bash
# Add :Z flag to volume mounts
podman run -v ./data:/app/data:Z chitfund-analyzer
```

Or update `docker-compose.yml`:
```yaml
volumes:
  - ./data:/app/data:Z  # SELinux label
```

### Podman Compose Not Found

```bash
# Install via pip
pip install podman-compose

# Or use podman-compose wrapper
curl -o /usr/local/bin/podman-compose \
  https://raw.githubusercontent.com/containers/podman-compose/main/podman_compose.py
chmod +x /usr/local/bin/podman-compose
```

### Docker Compatibility Mode

If you need full Docker CLI compatibility:

```bash
# Create Docker alias
alias docker=podman
alias docker-compose=podman-compose

# Or add to ~/.bashrc or ~/.zshrc
echo "alias docker=podman" >> ~/.bashrc
echo "alias docker-compose=podman-compose" >> ~/.bashrc
```

## Performance

Podman typically has similar or better performance than Docker:

- **Startup**: Faster (no daemon)
- **Resource Usage**: Lower overhead
- **Security**: Better (rootless, no daemon)

## Migration from Docker

### Using Existing Docker Images

```bash
# Pull from Docker Hub
podman pull streamlit/streamlit:latest

# Import Docker save archives
docker save chitfund-analyzer | podman load
```

### Converting Docker Compose

The compose files work as-is with `podman-compose`. No changes needed!

## Helper Script Usage

Both helper scripts work automatically with Podman:

### Windows (PowerShell)

```powershell
# Automatically detects and uses Podman
.\docker.ps1 run       # Uses podman-compose
.\docker.ps1 stop
.\docker.ps1 logs
.\docker.ps1 prod-run
```

### Unix/Linux (Make)

```bash
# Automatically detects and uses Podman
make runtime          # Shows detected runtime
make up               # Uses podman-compose
make down
make logs
make prod-up
```

## Additional Resources

- **Official Documentation**: https://podman.io/
- **Podman Desktop**: https://podman-desktop.io/
- **Podman Compose**: https://github.com/containers/podman-compose
- **Migration Guide**: https://podman.io/getting-started/migration

## Advantages of Podman

1. **Rootless**: Run containers without root privileges
2. **Daemonless**: No background service required
3. **Compatible**: Works with Docker images and commands
4. **Secure**: Better security model
5. **Lightweight**: Lower resource overhead
6. **Kubernetes-ready**: Native pod support

Your Chit Fund Analyzer application works seamlessly with both Docker and Podman!
