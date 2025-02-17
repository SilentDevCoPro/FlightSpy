#!/bin/bash

echo "Starting Docker Compose (initial up) in detached mode..."
docker-compose up
if [ $? -ne 0 ]; then
    echo "Error starting Docker Compose (initial up)."
    exit 1
fi

exit 0