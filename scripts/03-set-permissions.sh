#!/bin/bash

if [ -n "${DUMP1090_DEVICE}" ] && [ -e "${DUMP1090_DEVICE}" ]; then
    if command -v sudo &> /dev/null; then
        echo "Setting device permissions (requires sudo)..."
        sudo chmod 666 "${DUMP1090_DEVICE}"
        if [ $? -eq 0 ]; then
            echo "Device permissions set successfully."
        else
            echo "Error setting device permissions. Please run 'sudo chmod 666 ${DUMP1090_DEVICE}' manually."
            exit 1
        fi
    else
        echo "Warning: sudo not found. Device permissions NOT set. You may need to run 'sudo chmod 666 ${DUMP1090_DEVICE}' manually."
        exit 1
    fi
else
    echo "Skipping device permissions: DUMP1090_DEVICE not set or device not present"
    exit 0
fi

exit 0