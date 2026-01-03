# MasterGuard/Mad-Guard Network Security Check
# ReBoot Labs - Security Node Status

Write-Host "`n🔐 === MASTERGUARD SECURITY CHECK ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

# MasterGuard IPs from documentation
$MasterGuardPrimary = "192.168.1.247"
$MasterGuardAlt = "192.168.1.227"

# Check which IP is active
Write-Host "📡 Network Connectivity:" -ForegroundColor Yellow
$ActiveIP = $null

if (Test-Connection -ComputerName $MasterGuardPrimary -Count 1 -Quiet) {
    Write-Host "  ✅ MasterGuard ONLINE at $MasterGuardPrimary" -ForegroundColor Green
    $ActiveIP = $MasterGuardPrimary
} elseif (Test-Connection -ComputerName $MasterGuardAlt -Count 1 -Quiet) {
    Write-Host "  ✅ MasterGuard ONLINE at $MasterGuardAlt" -ForegroundColor Green
    $ActiveIP = $MasterGuardAlt
} else {
    Write-Host "  ❌ MasterGuard OFFLINE (no response from $MasterGuardPrimary or $MasterGuardAlt)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check Pi-hole DNS (port 53)
Write-Host "🛡️  Security Services:" -ForegroundColor Yellow

$Services = @(
    @{Name="Pi-hole DNS"; Port=53; Protocol="DNS filtering"},
    @{Name="Pi-hole Web"; Port=80; Protocol="Admin panel"},
    @{Name="WireGuard VPN"; Port=51820; Protocol="Remote access"}
)

foreach ($Service in $Services) {
    try {
        $Connection = Test-NetConnection -ComputerName $ActiveIP -Port $Service.Port -WarningAction SilentlyContinue -InformationLevel Quiet
        if ($Connection) {
            Write-Host "  ✅ $($Service.Name) (Port $($Service.Port)) - ACTIVE" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $($Service.Name) (Port $($Service.Port)) - NOT RESPONDING" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ⚠️  $($Service.Name) (Port $($Service.Port)) - CHECK FAILED" -ForegroundColor Yellow
    }
}

Write-Host ""

# Check DNS resolution through Pi-hole
Write-Host "🔍 DNS Security Test:" -ForegroundColor Yellow
try {
    $DNSTest = Resolve-DnsName -Name "google.com" -Server $ActiveIP -Type A -ErrorAction Stop
    Write-Host "  ✅ DNS resolution working through Pi-hole" -ForegroundColor Green
    Write-Host "     (Blocking ads/trackers at network level)" -ForegroundColor Gray
} catch {
    Write-Host "  ⚠️  DNS resolution test failed" -ForegroundColor Yellow
}

Write-Host ""

# Check if VPN endpoint is accessible
Write-Host "🔐 VPN Status:" -ForegroundColor Yellow
$VPNEndpoint = "${ActiveIP}:51820"
Write-Host "  Endpoint: $VPNEndpoint (UDP)" -ForegroundColor Gray

# Check if WireGuard is running on Windows (if client is connected)
$WGInterface = Get-NetAdapter | Where-Object { $_.InterfaceDescription -like "*WireGuard*" }
if ($WGInterface) {
    $Status = $WGInterface.Status
    if ($Status -eq "Up") {
        Write-Host "  ✅ VPN Client CONNECTED on this PC" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  VPN Client installed but disconnected" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ℹ️  VPN Client not active on this PC" -ForegroundColor Gray
}

Write-Host ""

# Security Services Summary (can't check without SSH)
Write-Host "📊 Security Stack (requires SSH to verify):" -ForegroundColor Yellow
Write-Host "  • Suricata IDS/IPS - Intrusion detection" -ForegroundColor Gray
Write-Host "  • Fail2ban - Brute force protection" -ForegroundColor Gray  
Write-Host "  • Security Alerts - Discord notifications" -ForegroundColor Gray
Write-Host "  • MQTT Publisher - Grafana monitoring" -ForegroundColor Gray

Write-Host ""

# Quick reference
Write-Host "🔗 Quick Access:" -ForegroundColor Yellow
Write-Host "  Pi-hole Admin: http://$ActiveIP/admin" -ForegroundColor Cyan
Write-Host "  Password: K33pou5saf3" -ForegroundColor DarkGray

Write-Host ""
Write-Host "✅ MasterGuard security check complete!" -ForegroundColor Green
Write-Host ""
