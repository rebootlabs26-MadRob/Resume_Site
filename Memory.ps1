#!/usr/bin/env pwsh
#Requires -Version 7
<#
.SYNOPSIS
    ReBoot Labs Memory System - Auto-capture and organize all work
.DESCRIPTION
    Automatically saves VS Code sessions, Copilot chats, and work context to Obsidian vault
    Prevents data loss and enables easy recall across all AI assistants
    
.NOTES
    FIXED VERSION - Flexible paths, error handling, ChatGPT import
#>

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet("save", "recall", "search", "backup", "status", "auto", "import-chatgpt", "setup")]
    [string]$Action = "save",
    
    [Parameter(Position=1)]
    [string]$Query = "",
    
    [switch]$AutoMode
)

$ErrorActionPreference = "Stop"

# === CONFIGURATION (EDIT THESE FOR YOUR SETUP) ===
$script:Config = @{
    WorkspaceRoot = "c:\Users\Nameless\ReBoot Lab Tools&Scripts"
    ObsidianVault = "ReBoot Lab Notes"
    SessionsFolder = "AI Sessions"
    BackupFolder = ".memory-backup"
    AITeamLogPath = "c:\Users\Nameless\Documents\ReBoot Labs Scripts n Stuff\AIEnv_chatlog.json"
}

# Build full paths
$WorkspaceRoot = $Config.WorkspaceRoot
$ObsidianVault = Join-Path $WorkspaceRoot $Config.ObsidianVault
$SessionsPath = Join-Path $ObsidianVault $Config.SessionsFolder
$BackupPath = Join-Path $WorkspaceRoot $Config.BackupFolder
$AITeamLog = $Config.AITeamLogPath

# === HELPER FUNCTIONS ===
function Get-Timestamp {
    return (Get-Date -Format "yyyy-MM-dd_HH-mm-ss")
}

function Get-DateTag {
    return (Get-Date -Format "yyyy-MM-dd")
}

function Ensure-Directories {
    @($SessionsPath, $BackupPath, (Join-Path $SessionsPath "chatgpt"), (Join-Path $SessionsPath "copilot"), (Join-Path $SessionsPath "claude")) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -Path $_ -ItemType Directory -Force | Out-Null
            Write-Host "  ✓ Created: $_" -ForegroundColor Green
        }
    }
}

function Test-GitRepo {
    try {
        git -C $WorkspaceRoot rev-parse --git-dir 2>$null | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Test-VSCodeCLI {
    try {
        code --version 2>$null | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Save-SessionSnapshot {
    param([string]$Title = "Auto-Save")
    
    $timestamp = Get-Timestamp
    $dateTag = Get-DateTag
    $sessionFile = Join-Path $SessionsPath "$dateTag - $Title.md"
    
    # Get git status if available
    $gitStatus = if (Test-GitRepo) {
        git -C $WorkspaceRoot status --short 2>$null
    } else {
        "*Git not initialized in workspace*"
    }
    
    # Get terminal history safely
    $terminalHistory = try {
        Get-History -Count 10 -ErrorAction SilentlyContinue | Format-Table -AutoSize | Out-String
    } catch {
        "*No terminal history available*"
    }
    
    # Get AI Team log if exists
    $aiTeamInfo = if (Test-Path $AITeamLog) {
        try {
            $log = Get-Content $AITeamLog -ErrorAction Stop | ConvertFrom-Json
            "**Total Sessions:** $($log.sessions.Count)`n"
            if ($log.sessions.Count -gt 0) {
                $last = $log.sessions[-1]
                "**Last Prompt:** $($last.user_prompt)`n"
                "**Timestamp:** $($last.timestamp)`n"
            }
        } catch {
            "*AI Team log exists but couldn't be read*"
        }
    } else {
        "*No AI Team log found*"
    }
    
    # Get VS Code open files if CLI available
    $openFiles = if (Test-VSCodeCLI) {
        code --list-files 2>$null | Select-Object -First 20 | ForEach-Object { "- ``$_``" }
    } else {
        "*VS Code CLI not available*"
    }
    
    $content = @"
---
date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
type: session-capture
tags: [ai-session, auto-save]
---

# $Title

**Captured:** $(Get-Date -Format "MMMM dd, yyyy HH:mm:ss")

## Current Context

### Workspace Files Changed
``````
$gitStatus
``````

### Recent Terminal Commands
``````powershell
$terminalHistory
``````

### AI Team Chat Log
$aiTeamInfo

### Open Files in VS Code
$openFiles

---

## Quick Notes
<!-- Add important context here before next session -->


---

## Recovery Info
- **Backup Location:** ``$BackupPath``
- **Session File:** ``$sessionFile``
- **AI Team Log:** ``$AITeamLog``

"@

    # Save to Obsidian
    $content | Set-Content $sessionFile -Encoding UTF8
    
    # Create backup copy
    $backupFile = Join-Path $BackupPath "$timestamp - $Title.md"
    $content | Set-Content $backupFile -Encoding UTF8
    
    return $sessionFile
}

function Backup-AITeamLog {
    if (Test-Path $AITeamLog) {
        $timestamp = Get-Timestamp
        $backupFile = Join-Path $BackupPath "AITeam_$timestamp.json"
        Copy-Item $AITeamLog -Destination $backupFile -Force
        return $backupFile
    }
    return $null
}

function Import-ChatGPTExport {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ExportPath
    )
    
    Write-Host "`n💾 Importing ChatGPT conversations..." -ForegroundColor Cyan
    
    if (-not (Test-Path $ExportPath)) {
        Write-Host "❌ Export file not found: $ExportPath" -ForegroundColor Red
        return
    }
    
    # Handle both .zip and direct JSON
    $tempDir = Join-Path $env:TEMP "chatgpt-import-$(Get-Timestamp)"
    
    if ($ExportPath -like "*.zip") {
        Write-Host "  📦 Extracting ZIP..." -ForegroundColor Yellow
        Expand-Archive -Path $ExportPath -DestinationPath $tempDir -Force
        $jsonFiles = Get-ChildItem -Path $tempDir -Filter "*.json" -Recurse
    } else {
        $jsonFiles = @(Get-Item $ExportPath)
    }
    
    $chatGPTPath = Join-Path $SessionsPath "chatgpt"
    $imported = 0
    
    foreach ($jsonFile in $jsonFiles) {
        try {
            $data = Get-Content $jsonFile.FullName -Raw | ConvertFrom-Json
            
            # ChatGPT export format has conversations array
            if ($data.PSObject.Properties.Name -contains "conversations") {
                foreach ($conv in $data.conversations) {
                    $convId = $conv.id
                    $title = $conv.title -replace '[\\/:*?"<>|]', '_'
                    $createTime = if ($conv.create_time) { 
                        [DateTimeOffset]::FromUnixTimeSeconds($conv.create_time).DateTime.ToString("yyyy-MM-dd") 
                    } else { 
                        Get-DateTag 
                    }
                    
                    $mdFile = Join-Path $chatGPTPath "$createTime - $title.md"
                    
                    $mdContent = @"
---
date: $createTime
type: chatgpt-import
conversation_id: $convId
tags: [chatgpt, imported]
---

# $title

**Created:** $createTime
**Conversation ID:** ``$convId``

## Messages

"@
                    
                    # Extract messages
                    foreach ($msgId in $conv.mapping.PSObject.Properties.Name) {
                        $msg = $conv.mapping.$msgId
                        if ($msg.message -and $msg.message.content -and $msg.message.content.parts) {
                            $role = $msg.message.author.role
                            $text = $msg.message.content.parts -join "`n"
                            
                            if ($role -eq "user") {
                                $mdContent += "`n### 👤 User`n`n$text`n"
                            } elseif ($role -eq "assistant") {
                                $mdContent += "`n### 🤖 ChatGPT`n`n$text`n"
                            }
                        }
                    }
                    
                    $mdContent | Set-Content $mdFile -Encoding UTF8
                    $imported++
                }
            }
        } catch {
            Write-Host "  ⚠️  Skipped $($jsonFile.Name): $_" -ForegroundColor Yellow
        }
    }
    
    # Cleanup temp
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    
    Write-Host "`n✓ Imported $imported ChatGPT conversations to: $chatGPTPath" -ForegroundColor Green
}

function Search-Sessions {
    param([string]$SearchTerm)
    
    if ([string]::IsNullOrWhiteSpace($SearchTerm)) {
        Write-Host "❌ Please provide a search term" -ForegroundColor Red
        return
    }
    
    $results = Get-ChildItem -Path $SessionsPath -Filter "*.md" -Recurse | 
        Select-String -Pattern $SearchTerm -List |
        Select-Object Path, Line
    
    if ($results) {
        Write-Host "`n✓ Found $($results.Count) matches:" -ForegroundColor Green
        $results | ForEach-Object {
            $relativePath = $_.Path.Replace($SessionsPath, "").TrimStart('\')
            Write-Host "  📄 $relativePath" -ForegroundColor Cyan
            Write-Host "     $($_.Line.Trim())" -ForegroundColor White
        }
    } else {
        Write-Host "❌ No matches found for '$SearchTerm'" -ForegroundColor Red
    }
}

function Get-RecentSessions {
    param([int]$Count = 5)
    
    $sessions = Get-ChildItem -Path $SessionsPath -Filter "*.md" -Recurse |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First $Count
    
    if ($sessions.Count -eq 0) {
        Write-Host "`n📋 No sessions saved yet - create your first with: .\Memory.ps1 save" -ForegroundColor Yellow
        return
    }
    
    Write-Host "`n📋 Recent Sessions:" -ForegroundColor Cyan
    $sessions | ForEach-Object {
        $age = (Get-Date) - $_.LastWriteTime
        $ageStr = if ($age.TotalHours -lt 1) { "$([int]$age.TotalMinutes)m ago" }
                  elseif ($age.TotalDays -lt 1) { "$([int]$age.TotalHours)h ago" }
                  else { "$([int]$age.TotalDays)d ago" }
        
        Write-Host "  📄 $($_.Name)" -ForegroundColor White
        Write-Host "     Modified: $ageStr" -ForegroundColor Gray
    }
}

function Show-Status {
    Write-Host "`n═══════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  ReBoot Labs Memory System Status" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
    
    # Session count
    $sessionCount = (Get-ChildItem -Path $SessionsPath -Filter "*.md" -Recurse -ErrorAction SilentlyContinue).Count
    Write-Host "`n📊 Statistics:" -ForegroundColor Green
    Write-Host "  • Total sessions saved: $sessionCount" -ForegroundColor White
    
    # Backup count
    $backupCount = (Get-ChildItem -Path $BackupPath -File -ErrorAction SilentlyContinue).Count
    Write-Host "  • Backup files: $backupCount" -ForegroundColor White
    
    # AI Team log
    if (Test-Path $AITeamLog) {
        try {
            $log = Get-Content $AITeamLog | ConvertFrom-Json
            Write-Host "  • AI Team chats: $($log.sessions.Count)" -ForegroundColor White
        } catch {
            Write-Host "  • AI Team chats: (error reading log)" -ForegroundColor Yellow
        }
    }
    
    # Check components
    Write-Host "`n🔧 System Components:" -ForegroundColor Green
    Write-Host "  • Git: $(if (Test-GitRepo) { '✓ Available' } else { '✗ Not initialized' })" -ForegroundColor $(if (Test-GitRepo) { 'White' } else { 'Yellow' })
    Write-Host "  • VS Code CLI: $(if (Test-VSCodeCLI) { '✓ Available' } else { '✗ Not found' })" -ForegroundColor $(if (Test-VSCodeCLI) { 'White' } else { 'Yellow' })
    
    # Recent activity
    Get-RecentSessions -Count 3
    
    Write-Host "`n📍 Locations:" -ForegroundColor Green
    Write-Host "  • Sessions: $SessionsPath" -ForegroundColor Gray
    Write-Host "  • Backups: $BackupPath" -ForegroundColor Gray
    Write-Host "  • AI Team Log: $AITeamLog" -ForegroundColor Gray
}

function Initialize-Setup {
    Write-Host "`n🔧 INITIAL SETUP - ReBoot Labs Memory System" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
    
    Write-Host "`n📁 Creating directory structure..." -ForegroundColor Yellow
    Ensure-Directories
    
    Write-Host "`n✓ Setup complete!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Save your first session: .\Memory.ps1 save `"Initial Setup`"" -ForegroundColor White
    Write-Host "  2. Import ChatGPT history: .\Memory.ps1 import-chatgpt `"path\to\export.zip`"" -ForegroundColor White
    Write-Host "  3. Check status: .\Memory.ps1 status" -ForegroundColor White
}

# === MAIN LOGIC ===
try {
    switch ($Action) {
        "setup" {
            Initialize-Setup
        }
        
        "save" {
            Ensure-Directories
            $title = if ($Query) { $Query } else { "Session $(Get-Timestamp)" }
            Write-Host "💾 Saving session snapshot..." -ForegroundColor Cyan
            $sessionFile = Save-SessionSnapshot -Title $title
            $backupFile = Backup-AITeamLog
            
            Write-Host "`n✓ Session saved!" -ForegroundColor Green
            Write-Host "  📄 Obsidian: $sessionFile" -ForegroundColor White
            if ($backupFile) {
                Write-Host "  💾 Backup: $backupFile" -ForegroundColor White
            }
        }
        
        "recall" {
            Get-RecentSessions -Count 10
        }
        
        "search" {
            Search-Sessions -SearchTerm $Query
        }
        
        "backup" {
            Write-Host "💾 Creating backup..." -ForegroundColor Cyan
            $backupFile = Backup-AITeamLog
            if ($backupFile) {
                Write-Host "✓ Backup created: $backupFile" -ForegroundColor Green
            } else {
                Write-Host "❌ No AI Team log to backup" -ForegroundColor Red
            }
        }
        
        "status" {
            Show-Status
        }
        
        "auto" {
            # Auto-save mode (run periodically)
            Ensure-Directories
            Write-Host "🔄 Auto-save triggered" -ForegroundColor Cyan
            Save-SessionSnapshot -Title "Auto-Save" | Out-Null
            Backup-AITeamLog | Out-Null
            Write-Host "✓ Auto-save complete" -ForegroundColor Green
        }
        
        "import-chatgpt" {
            Ensure-Directories
            if ([string]::IsNullOrWhiteSpace($Query)) {
                Write-Host "❌ Usage: .\Memory.ps1 import-chatgpt `"C:\path\to\chatgpt-export.zip`"" -ForegroundColor Red
            } else {
                Import-ChatGPTExport -ExportPath $Query
            }
        }
    }
} catch {
    Write-Host "`n❌ ERROR: $_" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Gray
    exit 1
}

Write-Host ""