#!/bin/bash
# Test script to verify network services accessibility in WSL

echo "🔍 A2 WSL Network Access Test"
echo "============================="
echo ""

# Get network info
echo "📡 Network Information:"
echo "WSL IP: $(hostname -I | awk '{print $1}')"
echo "Hostname: $(hostname)"
echo ""

# Function to check if service is listening
check_service() {
    local port=$1
    local service=$2
    
    if sudo ss -tlnp | grep -q ":$port"; then
        echo "✅ $service (Port $port): Listening"
        # Show what's listening
        sudo ss -tlnp | grep ":$port" | awk '{print "   Process: " $6}'
    else
        echo "❌ $service (Port $port): Not listening"
    fi
}

echo "🔌 Service Status:"
echo "-----------------"

# Check SSH
check_service 22 "SSH"

# Check Redis
check_service 6379 "Redis"

# Check common web ports
check_service 3000 "Frontend"
check_service 5000 "STT API"
check_service 8080 "API Gateway"
check_service 8888 "Jupyter"

echo ""
echo "🚀 Starting Missing Services:"
echo "----------------------------"

# Start SSH if not running
if ! systemctl is-active --quiet ssh; then
    echo "Starting SSH service..."
    sudo systemctl start ssh
    sudo systemctl enable ssh
    echo "✅ SSH service started"
fi

# Start Redis if not running
if ! systemctl is-active --quiet redis-server; then
    echo "Starting Redis service..."
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    echo "✅ Redis service started"
fi

echo ""
echo "📝 Quick Start Commands:"
echo "----------------------"
echo "1. On Windows (PowerShell as Admin):"
echo "   cd /path/to/A2/scripts/windows"
echo "   ./wsl-port-forward.ps1"
echo ""
echo "2. Test from Windows:"
echo "   ssh waragainstwork@localhost"
echo "   redis-cli -h localhost ping"
echo ""
echo "3. Start A2 STT service:"
echo "   cd ~/A2/a2-stt"
echo "   python api_server.py"
echo ""

# Check if we can bind to 0.0.0.0
echo "🌐 Network Binding Test:"
echo "-----------------------"
python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 9999))
    s.close()
    print('✅ Can bind to 0.0.0.0 (all interfaces)')
except Exception as e:
    print(f'❌ Cannot bind to 0.0.0.0: {e}')
"

echo ""
echo "✨ Test complete!"