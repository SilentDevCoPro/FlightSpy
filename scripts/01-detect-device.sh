#!/bin/bash

DEVICE_PATH=$(lsusb | grep "Realtek Semiconductor Corp. RTL2838 DVB-T" | awk '{gsub(/[^0-9]/, "", $2); gsub(/[^0-9]/, "", $4); print "/dev/bus/usb/" $2 "/" $4}')

if [ -z "$DEVICE_PATH" ]; then
    echo "Error: RTL2838 DVB-T device not found. Please ensure it's plugged in."
    exit 1
fi

echo "Detected device path: $DEVICE_PATH"
export DUMP1090_DEVICE="$DEVICE_PATH"

exit 0