#!/bin/bash

DEVICE_PATH=$(lsusb | grep "Realtek Semiconductor Corp. RTL2838 DVB-T" | awk '{gsub(/[^0-9]/, "", $2); gsub(/[^0-9]/, "", $4); print "/dev/bus/usb/" $2 "/" $4}')

if [ -z "$DEVICE_PATH" ]; then
    echo "WARNING: RTL2838 DVB-T device not found."
    echo "Continuing setup with empty DUMP1090_DEVICE variable."
    echo "After setup:"
    echo "1. Plug in your SDR device"
    echo "2. Run 'lsusb' to find your device"
    echo "3. Update DUMP1090_DEVICE in .env with the path (format: /dev/bus/usb/BUS/DEVICE)"
    export DUMP1090_DEVICE=""
else
    echo "Detected device path: $DEVICE_PATH"
    export DUMP1090_DEVICE="$DEVICE_PATH"
fi

exit 0