# SE-QPT Backend Dockerfile
# Optimized for 2GB DigitalOcean Droplet
# Build context: src/backend/ (all dependencies are now co-located)

FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn for production
RUN pip install --no-cache-dir gunicorn

# Copy application code (includes config/ and data/ directories)
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run with gunicorn
# - 2 workers (handles concurrent users on 1-vCPU droplet)
# - 4 threads per worker (for I/O-bound OpenAI API calls)
# - max-requests 200: recycle workers after 200 requests to prevent memory leaks
# - timeout 600: long timeout for Phase 4 GenAI export endpoints
# - graceful-timeout 30: allow in-flight requests to finish on worker recycle
# - keep-alive 5: close idle connections after 5s to free resources
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "600", "--graceful-timeout", "30", "--keep-alive", "5", "--max-requests", "200", "--max-requests-jitter", "50", "--preload", "run:app"]
