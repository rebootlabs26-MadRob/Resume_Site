# Quick Launcher Alias
# Add this to your PowerShell profile for easy access
# To edit profile: notepad $PROFILE

function Start-AITeam {
    <#
    .SYNOPSIS
        Launch the ReBoot Labs AI Team Chat
    .DESCRIPTION
        Quick launcher for the multi-AI chat system
    .EXAMPLE
        Start-AITeam
        ai-team  # if you create an alias
    #>
    & "C:\Users\Nameless\Documents\ReBoot Labs Scripts n Stuff\Launch-AITeam.ps1"
}

# Create a short alias
Set-Alias -Name ai-team -Value Start-AITeam

Write-Host "✓ AI Team launcher loaded!" -ForegroundColor Green
Write-Host "  Type: Start-AITeam  or  ai-team" -ForegroundColor Cyan
