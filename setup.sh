#!/bin/bash

SCRIPT_DIR="./scripts" # Define script directory for easy changes

echo "Starting Flightspy Setup Script..."

export DUMP1090_DEVICE=""
bash "${SCRIPT_DIR}/00-install-docker.sh || exit 1
bash "${SCRIPT_DIR}/01-detect-device.sh" || exit 1
bash "${SCRIPT_DIR}/02-create-env.sh" || exit 1
bash "${SCRIPT_DIR}/03-set-permissions.sh" || exit 1
bash "${SCRIPT_DIR}/04-create-migrations-dir.sh" || exit 1
bash "${SCRIPT_DIR}/05-docker-up-initial.sh" || exit 1
bash "${SCRIPT_DIR}/06-wait-for-healthy.sh" || exit 1
bash "${SCRIPT_DIR}/07-run-migrations.sh" || exit 1
bash "${SCRIPT_DIR}/08-docker-restart.sh" || exit 1

echo "Setup script completed."
echo "Flightspy should be running. The jraviles/dump1090 image comes with a frontend"
echo "Access it on your Pi localhost:8080 or if inside the same network $(hostname -I | awk '{print $1}'):8080"
echo For information about backup/restore/wipe database checkout "Database Actions" section in the README
