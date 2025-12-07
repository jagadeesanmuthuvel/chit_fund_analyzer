# Chit Fund Analyzer - Container Helper Script for Windows
# PowerShell script for managing Docker/Podman containers

param(
    [Parameter(Position=0)]
    [ValidateSet('build', 'run', 'stop', 'logs', 'clean', 'test', 'dev', 'prod', 'help')]
    [string]$Command = 'help'
)

# Auto-detect container runtime
$CONTAINER_RUNTIME = if (Get-Command podman -ErrorAction SilentlyContinue) { 
    "podman" 
} elseif (Get-Command docker -ErrorAction SilentlyContinue) { 
    "docker" 
} else { 
    $null 
}

$COMPOSE_CMD = if ($CONTAINER_RUNTIME -eq "podman") { 
    "podman-compose" 
} else { 
    "docker-compose" 
}

if (-not $CONTAINER_RUNTIME) {
    Write-Host "Error: Neither Docker nor Podman is installed." -ForegroundColor Red
    Write-Host "Please install Docker Desktop or Podman." -ForegroundColor Yellow
    Write-Host "  Docker: https://docs.docker.com/get-docker/" -ForegroundColor Cyan
    Write-Host "  Podman: https://podman.io/getting-started/installation" -ForegroundColor Cyan
    exit 1
}

Write-Host "Using container runtime: $CONTAINER_RUNTIME" -ForegroundColor Cyan

function Show-Help {
    Write-Host "Chit Fund Analyzer - Docker Management" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\docker.ps1 <command>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Green
    Write-Host "  build    - Build production Docker image"
    Write-Host "  dev      - Run development container with hot reload"
    Write-Host "  run      - Run production container"
    Write-Host "  prod     - Deploy production environment with docker-compose"
    Write-Host "  stop     - Stop all containers"
    Write-Host "  logs     - Show container logs"
    Write-Host "  test     - Run tests in container"
    Write-Host "  clean    - Remove containers and images"
    Write-Host "  help     - Show this help message"
    Write-Host ""
}

function Build-Production {
    Write-Host "Building container image..." -ForegroundColor Green
    & $CONTAINER_RUNTIME build -t chit-fund-analyzer:latest .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Container image built successfully" -ForegroundColor Green
    }
}

function Run-Development {
    Write-Host "Starting development environment..." -ForegroundColor Green
    Write-Host "Note: For hot reload, run locally with 'streamlit run streamlit_app/main.py'" -ForegroundColor Yellow
    & $COMPOSE_CMD -f docker/docker-compose.yml up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Container started" -ForegroundColor Green
        Write-Host "Access the app at: http://localhost:8501" -ForegroundColor Cyan
        Start-Process "http://localhost:8501"
    }
}

function Run-Production {
    Write-Host "Starting production container..." -ForegroundColor Green
    & $COMPOSE_CMD -f docker/docker-compose.yml up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Production container started" -ForegroundColor Green
        Write-Host "Access the app at: http://localhost:8501" -ForegroundColor Cyan
        Start-Process "http://localhost:8501"
    }
}

function Deploy-Production {
    Write-Host "Deploying production environment..." -ForegroundColor Green
    
    # Check if .env exists
    if (-not (Test-Path ".env")) {
        Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "⚠ Please configure .env file before proceeding" -ForegroundColor Yellow
        return
    }
    
    & $COMPOSE_CMD -f docker/docker-compose.prod.yml up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Production environment deployed" -ForegroundColor Green
        Write-Host "Access the app at: http://localhost:8501" -ForegroundColor Cyan
    }
}

function Stop-Containers {
    Write-Host "Stopping containers..." -ForegroundColor Yellow
    & $COMPOSE_CMD -f docker/docker-compose.yml down
    & $COMPOSE_CMD -f docker/docker-compose.prod.yml down 2>$null
    Write-Host "✓ Containers stopped" -ForegroundColor Green
}

function Show-Logs {
    Write-Host "Showing container logs (Ctrl+C to exit)..." -ForegroundColor Cyan
    & $COMPOSE_CMD -f docker/docker-compose.yml logs -f
}

function Run-Tests {
    Write-Host "Running tests in container..." -ForegroundColor Green
    & $CONTAINER_RUNTIME run --rm `
        -v "${PWD}:/app" `
        chit-fund-analyzer:latest `
        bash -c 'pip install pytest pytest-playwright; pytest tests/ -v'
}

function Clean-All {
    Write-Host "Cleaning up container resources..." -ForegroundColor Yellow
    
    # Stop containers
    & $COMPOSE_CMD -f docker/docker-compose.yml down 2>$null
    & $COMPOSE_CMD -f docker/docker-compose.prod.yml down 2>$null
    
    # Remove containers
    & $CONTAINER_RUNTIME rm chit-fund-app 2>$null
    & $CONTAINER_RUNTIME rm chit-fund-dev 2>$null
    
    # Remove images
    $response = Read-Host "Remove container images? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        & $CONTAINER_RUNTIME rmi chit-fund-analyzer:latest 2>$null
        & $CONTAINER_RUNTIME rmi chit-fund-analyzer:dev 2>$null
    }
    
    Write-Host "✓ Cleanup complete" -ForegroundColor Green
}

# Main execution
switch ($Command) {
    'build' { Build-Production }
    'dev' { Run-Development }
    'run' { Run-Production }
    'prod' { Deploy-Production }
    'stop' { Stop-Containers }
    'logs' { Show-Logs }
    'test' { Run-Tests }
    'clean' { Clean-All }
    'help' { Show-Help }
    default { Show-Help }
}
