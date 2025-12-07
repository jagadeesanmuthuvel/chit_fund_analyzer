# Makefile for Chit Fund Analyzer Container operations
# Auto-detects Docker or Podman

# Detect container runtime
CONTAINER_RUNTIME := $(shell command -v podman 2>/dev/null || command -v docker 2>/dev/null)
COMPOSE_CMD := $(shell command -v podman-compose 2>/dev/null || command -v docker-compose 2>/dev/null)

ifeq ($(CONTAINER_RUNTIME),)
$(error Neither Docker nor Podman is installed. Please install one of them.)
endif

.PHONY: help build build-dev run run-dev stop clean test logs shell install runtime

# Default target
help:
	@echo "Chit Fund Analyzer - Container Commands"
	@echo "========================================"
	@echo "Using: $(CONTAINER_RUNTIME)"
	@echo ""
	@echo "build          - Build production container image"
	@echo "build-dev      - Build development container image"
	@echo "run            - Run production container"
	@echo "run-dev        - Run development container with hot reload"
	@echo "stop           - Stop all containers"
	@echo "clean          - Remove containers and images"
	@echo "test           - Run tests in container"
	@echo "logs           - Show container logs"
	@echo "shell          - Open shell in running container"
	@echo "install        - Install dependencies locally"
	@echo "up             - Start with compose"
	@echo "down           - Stop compose services"
	@echo "runtime        - Show detected container runtime"

# Show detected runtime
runtime:
	@echo "Container Runtime: $(CONTAINER_RUNTIME)"
	@echo "Compose Command: $(COMPOSE_CMD)"

# Build production image
build:
	$(CONTAINER_RUNTIME) build -t chit-fund-analyzer:latest .

# Build development image
build-dev:
	@echo "Using same image for dev and prod. For hot reload, run: streamlit run streamlit_app/main.py"
	$(CONTAINER_RUNTIME) build -t chit-fund-analyzer:latest .

# Run production container
run:
	$(CONTAINER_RUNTIME) run -d \
		--name chit-fund-app \
		-p 8501:8501 \
		-v $$(pwd)/data:/app/data \
		--restart unless-stopped \
		chit-fund-analyzer:latest
# Run development container with hot reload
run-dev:
	@echo "For hot reload, run locally: streamlit run streamlit_app/main.py"
	$(CONTAINER_RUNTIME) run -d \
		--name chit-fund-app \
		-p 8501:8501 \
		-v $$(pwd)/data:/app/data \
		chit-fund-analyzer:latest

# Start with compose
up:
	$(COMPOSE_CMD) -f docker/docker-compose.yml up -d

# Start development environment
up-dev:
	$(COMPOSE_CMD) -f docker/docker-compose.yml up -d

# Stop compose services
down:
	$(COMPOSE_CMD) -f docker/docker-compose.yml down

# Stop containers
stop:
	$(CONTAINER_RUNTIME) stop chit-fund-app 2>/dev/null || true
	$(CONTAINER_RUNTIME) stop chit-fund-dev 2>/dev/null || true

# Clean up containers and images
clean: stop
	$(CONTAINER_RUNTIME) rm chit-fund-app 2>/dev/null || true
	$(CONTAINER_RUNTIME) rmi chit-fund-analyzer:latest 2>/dev/null || true

# Run tests in container
test:
	$(CONTAINER_RUNTIME) run --rm \
		-v $$(pwd):/app \
		chit-fund-analyzer:latest \
		bash -c "pip install pytest && pytest tests/ -v"

# Show container logs
logs:
	$(CONTAINER_RUNTIME) logs -f chit-fund-app

# Open shell in running container
shell:
	$(CONTAINER_RUNTIME) exec -it chit-fund-app /bin/bash

# Install dependencies locally
install:
	pip install -e ".[dev,test]"

# Production deployment
prod-up:
	$(COMPOSE_CMD) -f docker/docker-compose.prod.yml up -d

prod-down:
	$(COMPOSE_CMD) -f docker/docker-compose.prod.yml down
