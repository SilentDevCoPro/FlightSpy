#!/bin/bash

SCRIPT_DIR="./scripts" # Define script directory for easy changes

echo "Starting Flightspy Setup Script..."

if [ -f "${SCRIPT_DIR}/00-install-docker.sh" ]; then
    bash "${SCRIPT_DIR}/00-install-docker.sh" || exit 1
fi

export DUMP1090_DEVICE="" # Initialize DUMP1090_DEVICE, it will be set by detect-device.sh
bash "${SCRIPT_DIR}/01-detect-device.sh" || exit 1
bash "${SCRIPT_DIR}/02-create-env.sh" || exit 1
bash "${SCRIPT_DIR}/03-set-permissions.sh" || exit 1
bash "${SCRIPT_DIR}/04-create-migrations-dir.sh" || exit 1
bash "${SCRIPT_DIR}/05-docker-up-initial.sh" || exit 1
bash "${SCRIPT_DIR}/06-wait-for-healthy.sh" || exit 1
bash "${SCRIPT_DIR}/07-run-migrations.sh" || exit 1
bash "${SCRIPT_DIR}/08-docker-restart.sh" || exit 1

echo "Setup script completed."
echo "Flightspy should be running. Access it through your configured ports."