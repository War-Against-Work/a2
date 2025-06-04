#!/bin/bash
# Deploy A2 Robot components to Raspberry Pi 5
set -e

echo "=== A2 Robot - Raspberry Pi Deployment ==="

# Configuration
PI_HOST=${PI_HOST:-"a2-pi.local"}
PI_USER=${PI_USER:-"pi"}
ROS_WORKSPACE=${ROS_WORKSPACE:-"ros-workspace"}
PI_SYSTEM=${PI_SYSTEM:-"pi-system"}

echo "Deploying to: $PI_USER@$PI_HOST"

# Check if submodules are initialized
if [ ! -d "$ROS_WORKSPACE/.git" ] || [ ! -d "$PI_SYSTEM/.git" ]; then
    echo "Error: Required submodules not initialized"
    echo "Run: git submodule update --init --recursive"
    exit 1
fi

# Update submodules to latest
echo "Updating submodules..."
git submodule update --remote $ROS_WORKSPACE $PI_SYSTEM

# Sync ROS workspace to Pi
echo "Syncing ROS workspace to Pi..."
rsync -avz --delete $ROS_WORKSPACE/ $PI_USER@$PI_HOST:~/a2-ros-ws/

# Sync Pi system services
echo "Syncing Pi system services..."
rsync -avz --delete $PI_SYSTEM/ $PI_USER@$PI_HOST:~/a2-pi-system/

# Build ROS workspace on Pi
echo "Building ROS workspace on Pi..."
ssh $PI_USER@$PI_HOST << 'EOF'
cd ~/a2-ros-ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
EOF

# Install and start system services
echo "Installing Pi system services..."
ssh $PI_USER@$PI_HOST << 'EOF'
cd ~/a2-pi-system
sudo ./install_services.sh
sudo systemctl enable a2-robot.service
sudo systemctl restart a2-robot.service
EOF

echo "=== Deployment to Raspberry Pi complete! ==="
echo "Check status with: ssh $PI_USER@$PI_HOST 'systemctl status a2-robot.service'"