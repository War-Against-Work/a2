# Fix VoiceCraft port forwarding in Windows
# Run as Administrator in PowerShell

Write-Host "🔧 Fixing VoiceCraft Port Forwarding" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Get current WSL IP
$wslIp = (wsl ip addr show eth0 | Select-String -Pattern "inet\s+(\d+\.\d+\.\d+\.\d+)" | ForEach-Object { $_.Matches[0].Groups[1].Value }).Trim()
Write-Host "WSL IP: $wslIp" -ForegroundColor Green
Write-Host ""

# Remove existing rules for 8080 and 8003
Write-Host "🗑️  Removing existing port forwarding rules..." -ForegroundColor Yellow
netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=* 2>$null
netsh interface portproxy delete v4tov4 listenport=8003 listenaddress=* 2>$null
netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=8003 listenaddress=0.0.0.0 2>$null

# Add fresh forwarding rules
Write-Host "➕ Adding new port forwarding rules..." -ForegroundColor Yellow
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=$wslIp
netsh interface portproxy add v4tov4 listenport=8003 listenaddress=0.0.0.0 connectport=8003 connectaddress=$wslIp

# Update firewall rules
Write-Host ""
Write-Host "🔥 Updating Windows Firewall..." -ForegroundColor Yellow

# Remove old rules
Remove-NetFirewallRule -DisplayName "VoiceCraft Frontend" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "VoiceCraft Backend" -ErrorAction SilentlyContinue

# Add new rules with all profiles
New-NetFirewallRule -DisplayName "VoiceCraft Frontend" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8080 `
    -Action Allow `
    -Profile Any | Out-Null

New-NetFirewallRule -DisplayName "VoiceCraft Backend" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8003 `
    -Action Allow `
    -Profile Any | Out-Null

Write-Host "✅ Firewall rules updated" -ForegroundColor Green

# Show current configuration
Write-Host ""
Write-Host "📋 Current Port Forwarding:" -ForegroundColor Cyan
netsh interface portproxy show all | Select-String -Pattern "(8080|8003|Listen)"

# Test local connectivity
Write-Host ""
Write-Host "🧪 Testing Connectivity:" -ForegroundColor Cyan
Write-Host ""

# Test from Windows to WSL
$test8080 = Test-NetConnection -ComputerName localhost -Port 8080 -WarningAction SilentlyContinue
$test8003 = Test-NetConnection -ComputerName localhost -Port 8003 -WarningAction SilentlyContinue

if ($test8080.TcpTestSucceeded) {
    Write-Host "✅ Port 8080: Accessible from Windows" -ForegroundColor Green
} else {
    Write-Host "❌ Port 8080: Not accessible (service may not be running)" -ForegroundColor Red
}

if ($test8003.TcpTestSucceeded) {
    Write-Host "✅ Port 8003: Accessible from Windows" -ForegroundColor Green
} else {
    Write-Host "❌ Port 8003: Not accessible (service may not be running)" -ForegroundColor Red
}

# Get Windows IPs
Write-Host ""
Write-Host "💻 Your Windows IPs:" -ForegroundColor Cyan
$ips = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.InterfaceAlias -notlike "*WSL*" -and 
    $_.InterfaceAlias -notlike "*Loopback*" -and 
    $_.IPAddress -notlike "169.254.*"
}
$ips | ForEach-Object { Write-Host "  $($_.IPAddress) ($($_.InterfaceAlias))" -ForegroundColor White }

Write-Host ""
Write-Host "🎯 From your Mac, test with:" -ForegroundColor Yellow
$ips | ForEach-Object { 
    if ($_.IPAddress -like "192.168.*") {
        Write-Host "  curl http://$($_.IPAddress):8080" -ForegroundColor White
        Write-Host "  curl http://$($_.IPAddress):8003/health" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "💡 If still getting 'Connection reset':" -ForegroundColor Yellow
Write-Host "  1. Ensure services in WSL are running on 0.0.0.0, not 127.0.0.1" -ForegroundColor White
Write-Host "  2. Check Windows Defender is not blocking" -ForegroundColor White
Write-Host "  3. Try disabling Windows Firewall temporarily to test" -ForegroundColor White