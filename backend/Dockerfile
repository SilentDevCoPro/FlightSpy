FROM python:3.11-slim

ARG UID=1000
ARG GID=1000

# Create user with fixed UID/GID first to maximize cache stability
RUN groupadd -g ${GID} celeryuser && \
    useradd -u ${UID} -g celeryuser -m celeryuser

# Install system dependencies
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    iputils-ping && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# Install Python dependencies with cache optimization
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copy application code with proper ownership
COPY --chown=celeryuser:celeryuser . .

USER celeryuser

CMD ["celery", "-A", "backend", "worker", "-l", "info"]