# Holdem API Server Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create log directories with proper permissions
RUN mkdir -p logs/{api,agent,dashboard,holdemctl} && \
    chmod -R 755 logs/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Default environment variables
ENV LOG_LEVEL=info
ENV LOG_FORMAT=standard
ENV HOLDEM_API_PORT=8000

# Start API server
CMD ["python", "live_agent_server.py"]