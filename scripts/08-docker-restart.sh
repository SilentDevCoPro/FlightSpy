#!/bin/bash

echo "Restarting Docker Compose (down then up)..."
docker-compose down
if [ $? -ne 0 ]; then
    echo "Error running docker-compose down."
    exit 1
fi
docker-compose up
if [ $? -ne 0 ]; then
    echo "Error running docker-compose up after down."
    exit 1
fi

exit 0