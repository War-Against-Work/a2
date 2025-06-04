#!/bin/bash
# Configure A2 services for network access

echo "🔧 Configuring A2 Services for Network Access"
echo "==========================================="
echo ""

# Ensure script is run with sudo when needed
if [ "$EUID" -ne 0 ]; then 
    SUDO='sudo'
else
    SUDO=''
fi

# Configure SSH for network access
echo "1️⃣ Configuring SSH..."
if [ -f /etc/ssh/sshd_config ]; then
    # Backup original
    $SUDO cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Ensure SSH listens on all interfaces
    $SUDO sed -i 's/^#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/' /etc/ssh/sshd_config
    $SUDO sed -i 's/^#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    
    # Restart SSH
    $SUDO systemctl restart ssh
    echo "✅ SSH configured and restarted"
else
    echo "⚠️  SSH config not found"
fi

# Configure Redis for network access (if installed)
echo ""
echo "2️⃣ Configuring Redis..."
if [ -f /etc/redis/redis.conf ]; then
    # Backup original
    $SUDO cp /etc/redis/redis.conf /etc/redis/redis.conf.backup
    
    # Allow network connections
    $SUDO sed -i 's/^bind 127.0.0.1.*/bind 0.0.0.0/' /etc/redis/redis.conf
    $SUDO sed -i 's/^protected-mode yes/protected-mode no/' /etc/redis/redis.conf
    
    # Restart Redis
    $SUDO systemctl restart redis-server
    echo "✅ Redis configured for network access"
else
    echo "⚠️  Redis not installed"
fi

# Create systemd service for A2 STT API (optional)
echo ""
echo "3️⃣ Creating A2 STT service..."
cat > /tmp/a2-stt.service << EOF
[Unit]
Description=A2 Robot STT API Service
After=network.target

[Service]
Type=simple
User=waragainstwork
WorkingDirectory=/home/waragainstwork/A2/a2-stt
Environment="PATH=/home/waragainstwork/miniconda3/envs/a2_stt/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/waragainstwork/miniconda3/envs/a2_stt/bin/python api_server.py --host 0.0.0.0 --port 5000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

$SUDO cp /tmp/a2-stt.service /etc/systemd/system/
$SUDO systemctl daemon-reload
echo "✅ A2 STT service created (not started)"
echo "   To start: sudo systemctl start a2-stt"
echo "   To enable on boot: sudo systemctl enable a2-stt"

# Create startup script
echo ""
echo "4️⃣ Creating startup script..."
cat > ~/A2/scripts/start-network-services.sh << 'EOF'
#!/bin/bash
# Start all A2 network services

echo "Starting A2 network services..."

# Start SSH
sudo systemctl start ssh

# Start Redis
sudo systemctl start redis-server

# Start A2 STT (if environment exists)
if [ -d ~/miniconda3/envs/a2_stt ]; then
    cd ~/A2/a2-stt
    source ~/miniconda3/bin/activate a2_stt
    python api_server.py --host 0.0.0.0 --port 5000 &
    echo "STT API started on port 5000"
fi

echo "All services started!"
EOF

chmod +x ~/A2/scripts/start-network-services.sh
echo "✅ Startup script created: ~/A2/scripts/start-network-services.sh"

# Display current status
echo ""
echo "📊 Current Service Status:"
echo "-------------------------"
systemctl is-active ssh && echo "✅ SSH: Active" || echo "❌ SSH: Inactive"
systemctl is-active redis-server && echo "✅ Redis: Active" || echo "❌ Redis: Inactive"

echo ""
echo "🌐 Network Configuration:"
echo "------------------------"
echo "WSL IP: $(hostname -I | awk '{print $1}')"
echo "Gateway: $(ip route | grep default | awk '{print $3}')"

echo ""
echo "📝 Next Steps:"
echo "-------------"
echo "1. Run the Windows PowerShell script (as Admin):"
echo "   ./wsl-port-forward.ps1"
echo ""
echo "2. Test connectivity from Windows:"
echo "   ssh waragainstwork@localhost"
echo ""
echo "3. For persistent setup, add to /etc/wsl.conf:"
echo "   [boot]"
echo "   command = /home/waragainstwork/A2/scripts/start-network-services.sh"
echo ""
echo "✨ Configuration complete!"