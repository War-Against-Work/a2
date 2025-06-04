#!/bin/bash
# Flash A2 firmware to Teensy 4.1
set -e

echo "=== A2 Robot - Teensy Firmware Deployment ==="

# Configuration
TEENSY_FIRMWARE=${TEENSY_FIRMWARE:-"teensy-firmware"}
TEENSY_PORT=${TEENSY_PORT:-"/dev/ttyACM0"}

echo "Flashing firmware to Teensy 4.1..."

# Check if submodule is initialized
if [ ! -d "$TEENSY_FIRMWARE/.git" ]; then
    echo "Error: Teensy firmware submodule not initialized"
    echo "Run: git submodule update --init --recursive"
    exit 1
fi

# Update submodule to latest
echo "Updating Teensy firmware submodule..."
git submodule update --remote $TEENSY_FIRMWARE

# Build and flash firmware
cd $TEENSY_FIRMWARE

# Check if PlatformIO is available
if ! command -v pio &> /dev/null; then
    echo "Error: PlatformIO CLI not found"
    echo "Install with: pip install platformio"
    exit 1
fi

# Check if Teensy is connected
if [ ! -e "$TEENSY_PORT" ]; then
    echo "Warning: Teensy not found at $TEENSY_PORT"
    echo "Available serial devices:"
    ls -la /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || echo "No serial devices found"
    echo ""
    echo "Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Building firmware..."
pio run

echo "Flashing to Teensy..."
pio run --target upload

echo "=== Teensy firmware deployment complete! ==="
echo "Monitor serial output with: pio device monitor"