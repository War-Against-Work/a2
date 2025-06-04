# WSL Port Forwarding Script for A2 Robot Development
# Run this script in PowerShell as Administrator on Windows

# Get WSL IP address
$wslIp = (wsl hostname -I).trim()
Write-Host "WSL IP Address: $wslIp" -ForegroundColor Green

# Define ports for A2 robot services
$ports = @{
    22 = "SSH"
    6379 = "Redis (State Cache)"
    8080 = "API Gateway"
    9090 = "ROS2 Web Tools"
    5000 = "STT API Server"
    3000 = "Frontend Services"
    4000 = "Additional Services"
    8888 = "Jupyter Notebook"
}

Write-Host "`nRemoving existing port forwarding rules..." -ForegroundColor Yellow

# Remove existing port proxy rules
foreach ($port in $ports.Keys) {
    netsh interface portproxy delete v4tov4 listenport=$port listenaddress=0.0.0.0 2>$null
}

Write-Host "`nAdding new port forwarding rules..." -ForegroundColor Yellow

# Add new port forwarding rules
foreach ($port in $ports.Keys) {
    $service = $ports[$port]
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIp
    Write-Host "✓ Port $port ($service) -> $wslIp`:$port" -ForegroundColor Green
}

# Configure Windows Firewall
Write-Host "`nConfiguring Windows Firewall..." -ForegroundColor Yellow

foreach ($port in $ports.Keys) {
    $service = $ports[$port]
    $ruleName = "A2 WSL - $service (Port $port)"
    
    # Remove existing rule
    Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    
    # Add new rule
    New-NetFirewallRule -DisplayName $ruleName `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort $port `
        -Action Allow `
        -Profile Private,Domain | Out-Null
        
    Write-Host "✓ Firewall rule added: $ruleName" -ForegroundColor Green
}

# Display current configuration
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Current Port Forwarding Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
netsh interface portproxy show all

# Test connectivity
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing Connectivity" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Test SSH
$sshTest = Test-NetConnection -ComputerName localhost -Port 22 -WarningAction SilentlyContinue
if ($sshTest.TcpTestSucceeded) {
    Write-Host "✓ SSH (Port 22): Connected" -ForegroundColor Green
} else {
    Write-Host "✗ SSH (Port 22): Not available (start SSH in WSL)" -ForegroundColor Red
}

# Get Windows IP for external access
$windowsIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*WSL*" -and $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*"}).IPAddress | Select-Object -First 1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Access Information" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "From Windows:" -ForegroundColor Yellow
Write-Host "  ssh waragainstwork@localhost" -ForegroundColor White
Write-Host "  http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "From other machines on network:" -ForegroundColor Yellow
Write-Host "  ssh waragainstwork@$windowsIp" -ForegroundColor White
Write-Host "  http://${windowsIp}:5000" -ForegroundColor White

Write-Host "`n✅ Port forwarding configuration complete!" -ForegroundColor Green