# Dockerfile for Chit Fund Analyzer
FROM python:3.13-slim

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=7860 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create non-root user
RUN useradd -m -u 1000 chitfund && \
    mkdir -p /app/data /app/.streamlit && \
    chown -R chitfund:chitfund /app

WORKDIR /app

# Copy application files (before switching to non-root user)
COPY --chown=chitfund:chitfund . .

# Install Python dependencies using uv (while still root so uv is accessible)
RUN uv pip install --system --no-cache -e .

# Create Streamlit config
RUN echo '[server]\n\
port = 7860\n\
address = "0.0.0.0"\n\
headless = true\n\
enableCORS = true\n\
enableXsrfProtection = false\n\
\n\
[browser]\n\
gatherUsageStats = false' > /app/.streamlit/config.toml && \
    chown chitfund:chitfund /app/.streamlit/config.toml

USER chitfund

EXPOSE 7860

# Health check (Note: Only works with Docker format, not OCI/Podman)
# For Podman, use: podman build --format docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "streamlit_app/main.py"]