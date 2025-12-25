#Requires -Version 7
<#
.SYNOPSIS
    DEPRECATED - Use Launch-AITeam.ps1 instead
.DESCRIPTION
    This script is kept for reference only.
    The new Launch-AITeam.ps1 provides a better, more secure setup.
#>

Write-Host "⚠️  This script is deprecated!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Please use the new launcher instead:" -ForegroundColor Cyan
Write-Host "  .\Launch-AITeam.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "The new launcher:" -ForegroundColor White
Write-Host "  ✓ Loads API keys from .env file (more secure)" -ForegroundColor Green
Write-Host "  ✓ Auto-creates and activates venv" -ForegroundColor Green
Write-Host "  ✓ Installs/updates dependencies" -ForegroundColor Green
Write-Host "  ✓ Launches the AI Team chat" -ForegroundColor Green
Write-Host ""

$response = Read-Host "Would you like to run the new launcher now? (Y/n)"
if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
    & (Join-Path $PSScriptRoot "Launch-AITeam.ps1")
}