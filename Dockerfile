# Dockerfile for Chit Fund Analyzer
FROM python:3.13-slim

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 chitfund && \
    mkdir -p /app/data /app/.streamlit && \
    chown -R chitfund:chitfund /app

WORKDIR /app

# Copy application files
COPY --chown=chitfund:chitfund . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create Streamlit config
RUN echo '[server]\n\
port = 8501\n\
address = "0.0.0.0"\n\
headless = true\n\
enableCORS = false\n\
enableXsrfProtection = true\n\
\n\
[browser]\n\
gatherUsageStats = false\n' > /app/.streamlit/config.toml

USER chitfund

EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "streamlit_app/main.py"]
