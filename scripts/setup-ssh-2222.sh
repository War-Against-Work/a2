#!/bin/bash
# Configure SSH to listen on port 2222

echo "📋 Setting up SSH on port 2222"
echo "==============================="
echo ""

# Check if SSH is installed
if ! command -v sshd &> /dev/null; then
    echo "❌ SSH server not installed"
    echo "Please run: sudo apt install openssh-server"
    exit 1
fi

# Backup original config
if [ -f /etc/ssh/sshd_config ] && [ ! -f /etc/ssh/sshd_config.backup ]; then
    echo "📁 Backing up SSH config..."
    sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
fi

# Configure SSH to listen on port 2222
echo "🔧 Configuring SSH for port 2222..."
sudo sed -i 's/^#Port 22/Port 2222/' /etc/ssh/sshd_config
sudo sed -i 's/^Port 22/Port 2222/' /etc/ssh/sshd_config

# Ensure it listens on all interfaces
sudo sed -i 's/^#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/' /etc/ssh/sshd_config

# Restart SSH service
echo "🔄 Restarting SSH service..."
sudo systemctl restart ssh

# Enable SSH on boot
sudo systemctl enable ssh

# Check status
echo ""
echo "✅ SSH Configuration Complete"
echo ""
echo "📊 Current Status:"
sudo systemctl status ssh --no-pager | head -10

echo ""
echo "🔍 Listening on port:"
sudo ss -tlnp | grep sshd

echo ""
echo "🎯 Test from Windows:"
echo "  ssh -p 2222 waragainstwork@localhost"
echo ""
echo "Or using your SSH config:"
echo "  ssh light.local"