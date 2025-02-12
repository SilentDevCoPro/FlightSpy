# In your backend/Dockerfile
FROM python:3.11-slim

# Create system user and group first
RUN groupadd -r celeryuser && \
    useradd -r -g celeryuser celeryuser

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    apt-get install -y libpq-dev gcc python3-dev && \
    apt-get install -y iputils-ping && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set ownership BEFORE switching user
RUN chown -R celeryuser:celeryuser /app

# Switch to non-root user
USER celeryuser

# Default command (can be overridden in compose)
CMD ["celery", "-A", "backend", "worker", "-l", "info"]