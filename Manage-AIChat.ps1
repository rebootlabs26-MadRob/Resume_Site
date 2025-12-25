#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Manage AI Team chat sessions from PowerShell
.DESCRIPTION
    Clear and restore chat history from VS Code terminal
.PARAMETER Action
    clear - Clear current chat (with backup)
    undo - Restore last cleared chat
    backup - Manual backup of current chat
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("clear", "undo", "backup")]
    [string]$Action
)

$ScriptDir = $PSScriptRoot
$LogFile = Join-Path $ScriptDir "AIEnv_chatlog.json"
$BackupFile = Join-Path $ScriptDir "AIEnv_chatlog.backup.json"

function Clear-Chat {
    if (-not (Test-Path $LogFile)) {
        Write-Host "✗ No chat log found" -ForegroundColor Red
        return
    }
    
    # Backup current log
    Copy-Item $LogFile -Destination $BackupFile -Force
    
    # Clear log
    @{sessions = @()} | ConvertTo-Json -Depth 10 | Set-Content $LogFile -Encoding utf8
    
    Write-Host "✓ Chat cleared. Type 'undo' to restore." -ForegroundColor Green
}

function Undo-Clear {
    if (-not (Test-Path $BackupFile)) {
        Write-Host "✗ No backup found to restore" -ForegroundColor Red
        return
    }
    
    Copy-Item $BackupFile -Destination $LogFile -Force
    
    $data = Get-Content $BackupFile | ConvertFrom-Json
    $count = $data.sessions.Count
    
    Write-Host "✓ Restored $count messages from backup" -ForegroundColor Green
}

function Backup-Chat {
    if (-not (Test-Path $LogFile)) {
        Write-Host "✗ No chat log found" -ForegroundColor Red
        return
    }
    
    Copy-Item $LogFile -Destination $BackupFile -Force
    Write-Host "✓ Chat backed up" -ForegroundColor Green
}

switch ($Action) {
    "clear" { Clear-Chat }
    "undo" { Undo-Clear }
    "backup" { Backup-Chat }
}
