#!/bin/bash

ENV_FILE=".env"
ENV_CONTENT=$(cat <<EOF
POSTGRES_DB=flightspy
POSTGRES_USER=flightspy_user
POSTGRES_PASSWORD=secret_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
DUMP1090_DEVICE=${DUMP1090_DEVICE} # Assuming DUMP1090_DEVICE is exported
EOF
)

echo "Creating .env file..."
echo "${ENV_CONTENT}" > "${ENV_FILE}"
if [ $? -ne 0 ]; then
    echo "Error creating .env file."
    exit 1
fi
echo ".env file created."

exit 0