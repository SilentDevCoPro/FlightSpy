#!/bin/bash

echo "Waiting for Docker containers to be healthy..."
docker-compose wait
WAIT_EXIT_CODE=$?
if [ "$WAIT_EXIT_CODE" -ne 0 ]; then
    echo "Error waiting for services to become healthy. Docker Compose wait exited with an error."
    echo "Please check the Docker Compose logs to diagnose startup issues."
    exit 1
else
    echo "All services are healthy."
fi

exit 0