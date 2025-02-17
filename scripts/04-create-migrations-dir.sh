#!/bin/bash

MIGRATIONS_DIR="backend/dump1090_collector/migrations"
echo "Creating migrations directory: ${MIGRATIONS_DIR}..."
mkdir -p "${MIGRATIONS_DIR}"
if [ $? -eq 0 ]; then
    echo "Migrations directory created."
    echo "Setting permissions on migrations directory (read/write for owner and group, read for others)..."
    chmod 775 "${MIGRATIONS_DIR}"
    if [ $? -eq 0 ]; then
        echo "Migrations directory permissions set."
    else
        echo "Error setting migrations directory permissions. Permissions may be insufficient."
        exit 1
    fi
else
    echo "Error creating migrations directory. Please check permissions and path."
    exit 1
fi

exit 0