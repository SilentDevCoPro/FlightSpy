#!/bin/bash

if command -v sudo &> /dev/null; then # Check if sudo is available
    echo "Setting device permissions (requires sudo)..."
    sudo chmod 666 "${DUMP1090_DEVICE}" # Assuming DUMP1090_DEVICE is exported
    if [ $? -eq 0 ]; then
        echo "Device permissions set successfully."
    else
        echo "Error setting device permissions. Please run 'sudo chmod 666 ${DUMP1090_DEVICE}' manually after the script."
        exit 1
    fi
else
    echo "Warning: sudo not found. Device permissions NOT set. You may need to run 'sudo chmod 666 ${DUMP1090_DEVICE}' manually."
    exit 1 # Exit as permissions are likely needed
fi

exit 0