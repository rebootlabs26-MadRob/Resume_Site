#Requires -Version 7
<#
.SYNOPSIS
    Launch ReBoot Labs AI Team Environment
.DESCRIPTION
    One-command launcher for the multi-AI chat system.
    Handles venv setup, dependencies, environment variables, and launches the chat.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectPath = $PSScriptRoot
# Use a venv path without spaces (Python 3.14 bug workaround)
$VenvPath = Join-Path $env:USERPROFILE ".ai_team_venv"
$EnvFile = Join-Path $ProjectPath ".env"
$PythonScript = "multi_ai_chat.py"

# Change to project directory to avoid path issues
Push-Location $ProjectPath
try {

Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   ReBoot Labs AI Team Launcher" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check for .env file
if (-not (Test-Path $EnvFile)) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "   Expected location: $EnvFile" -ForegroundColor Yellow
    Write-Host "   Please create a .env file with your API keys." -ForegroundColor Yellow
    exit 1
}

# Step 2: Load environment variables from .env
Write-Host "📋 Loading environment variables from .env..." -ForegroundColor Green
Get-Content $EnvFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#")) {
        if ($line -match '^([^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "   ✓ Loaded: $name" -ForegroundColor DarkGray
        }
    }
}

# Step 3: Create venv if it doesn't exist
if (-not (Test-Path $VenvPath)) {
    Write-Host ""
    Write-Host "🔧 Creating Python virtual environment..." -ForegroundColor Green
    Write-Host "   Location: $VenvPath" -ForegroundColor DarkGray
    Write-Host "   (Using shared location to avoid Python 3.14 path bug)" -ForegroundColor DarkGray
    python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment!" -ForegroundColor Red
        throw "Virtual environment creation failed"
    }
    Write-Host "   ✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "   ✓ Virtual environment found" -ForegroundColor DarkGray
}

# Step 4: Activate venv
Write-Host ""
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Green
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (-not (Test-Path $ActivateScript)) {
    Write-Host "❌ Activate script not found" -ForegroundColor Red
    throw "Activate script missing"
}
& $ActivateScript

# Step 5: Install/upgrade dependencies
Write-Host ""
Write-Host "📦 Checking Python dependencies..." -ForegroundColor Green
$PipPackages = @("anthropic", "google-generativeai", "openai", "python-dotenv")
Write-Host "   Installing packages: $($PipPackages -join ', ')" -ForegroundColor DarkGray
python -m pip install --upgrade pip --quiet
python -m pip install --upgrade $PipPackages --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ All dependencies ready" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Warning: Some packages may have failed to install" -ForegroundColor Yellow
}

# Step 6: Verify API keys are loaded
Write-Host ""
Write-Host "🔑 Verifying API keys..." -ForegroundColor Green
$keysOk = $true
@("CLAUDE_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY") | ForEach-Object {
    if ([string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable($_))) {
        Write-Host "   ❌ Missing: $_" -ForegroundColor Red
        $keysOk = $false
    } else {
        $keyPreview = ([Environment]::GetEnvironmentVariable($_)).Substring(0, [Math]::Min(15, ([Environment]::GetEnvironmentVariable($_)).Length))
        Write-Host "   ✓ $_`: $keyPreview..." -ForegroundColor Green
    }
}

if (-not $keysOk) {
    Write-Host ""
    Write-Host "❌ Please update your .env file with all required API keys!" -ForegroundColor Red
    exit 1
}

# Step 7: Launch the AI Team chat
Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   🚀 Launching AI Team Chat..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Export env vars to the Python process
$env:CLAUDE_API_KEY = [Environment]::GetEnvironmentVariable("CLAUDE_API_KEY")
$env:GEMINI_API_KEY = [Environment]::GetEnvironmentVariable("GEMINI_API_KEY")
$env:OPENAI_API_KEY = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY")
$env:CLAUDE_MODEL_ID = [Environment]::GetEnvironmentVariable("CLAUDE_MODEL_ID")
$env:CLAUDE_JUDGE_MODEL_ID = [Environment]::GetEnvironmentVariable("CLAUDE_JUDGE_MODEL_ID")
$env:GEMINI_MODEL_ID = [Environment]::GetEnvironmentVariable("GEMINI_MODEL_ID")
$env:OPENAI_MODEL_ID = [Environment]::GetEnvironmentVariable("OPENAI_MODEL_ID")

python $PythonScript

} finally {
    Pop-Location
}
