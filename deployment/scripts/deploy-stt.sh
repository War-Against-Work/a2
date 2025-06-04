#!/bin/bash
# Deploy A2 STT service to RTX 4080 local system
set -e

echo "=== A2 Robot - STT Service Deployment ==="

# Configuration
STT_SERVICE=${STT_SERVICE:-"stt-service"}
CONTROL_INTERFACE=${CONTROL_INTERFACE:-"control-interface"}

echo "Deploying STT service and control interface..."

# Check if submodules are initialized
if [ ! -d "$STT_SERVICE/.git" ] || [ ! -d "$CONTROL_INTERFACE/.git" ]; then
    echo "Error: Required submodules not initialized"
    echo "Run: git submodule update --init --recursive"
    exit 1
fi

# Update submodules to latest
echo "Updating submodules..."
git submodule update --remote $STT_SERVICE $CONTROL_INTERFACE

# Deploy STT service
echo "Starting STT service..."
cd $STT_SERVICE
if [ -f "docker-compose.yml" ]; then
    docker-compose down
    docker-compose up -d
else
    echo "Building and starting STT service..."
    ./start_backend.sh
fi

# Deploy control interface
echo "Starting control interface..."
cd ../$CONTROL_INTERFACE
if [ -f "docker-compose.yml" ]; then
    docker-compose down
    docker-compose up -d
elif [ -f "start_interface.sh" ]; then
    ./start_interface.sh
else
    echo "Control interface startup script not found"
fi

echo "=== STT Service deployment complete! ==="
echo "STT Service available at: http://localhost:8000"
echo "Control Interface available at: http://localhost:3000"