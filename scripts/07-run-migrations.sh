#!/bin/bash

BACKEND_CONTAINER_NAME="flightspy_backend"
echo "Running Django migrations inside ${BACKEND_CONTAINER_NAME} container..."

docker exec "${BACKEND_CONTAINER_NAME}" python manage.py makemigrations dump1090_collector
MIGRATIONS_MAKEMIGRATIONS_EXIT_CODE=$?
if [ "$MIGRATIONS_MAKEMIGRATIONS_EXIT_CODE" -ne 0 ]; then
    echo "Error running 'makemigrations' command. Check the output above for errors."
    echo "Migrations may not have been created successfully."
    exit 1
else
    echo "'makemigrations' command completed."
    docker exec "${BACKEND_CONTAINER_NAME}" python manage.py migrate
    MIGRATIONS_MIGRATE_EXIT_CODE=$?
    if [ "$MIGRATIONS_MIGRATE_EXIT_CODE" -ne 0 ]; then
        echo "Error running 'migrate' command. Check the output above for errors."
        echo "Database migrations may not have been applied successfully."
        exit 1
    else
        echo "'migrate' command completed. Database migrations applied."
    fi
fi

exit 0