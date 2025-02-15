FROM python:3.11-slim

ARG UID=1000
ARG GID=1000

RUN groupadd -g ${GID} celeryuser && \
    useradd -u ${UID} -g celeryuser -m celeryuser

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev iputils-ping && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=celeryuser:celeryuser . .

USER celeryuser

CMD ["celery", "-A", "backend", "worker", "-l", "info"]