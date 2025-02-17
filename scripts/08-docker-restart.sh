#!/bin/bash

echo "Restarting Docker Compose (down then up)..."
docker-compose down
if [ $? -ne 0 ]; then
    echo "Error running docker-compose down."
    exit 1
fi
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "Error running docker-compose up -d after down."
    exit 1
fi

exit 0