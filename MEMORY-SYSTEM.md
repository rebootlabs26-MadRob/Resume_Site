# ReBoot Labs Memory System

**Status:** ✅ Active  
**Purpose:** Prevent data loss and organize all AI sessions across VS Code, Obsidian, and other tools

## Quick Commands

```powershell
# Save current session
.\Memory.ps1 save "Working on DiagTool GUI"

# Recall recent sessions
.\Memory.ps1 recall

# Search all saved work
.\Memory.ps1 search "DiagTool"

# Backup AI Team log
.\Memory.ps1 backup

# Check system status
.\Memory.ps1 status
```

## What Gets Saved

Every time you run `Memory.ps1 save`:

- ✅ Current workspace file changes
- ✅ Recent terminal commands
- ✅ AI Team chat history
- ✅ Open files in VS Code
- ✅ Timestamp and context tags

## Storage Locations

- **Obsidian Sessions:** `ReBoot Lab Notes/AI Sessions/`
- **Backups:** `.memory-backup/`
- **AI Team Logs:** `ReBoot Labs Scripts n Stuff/AIEnv_chatlog.json`

## Auto-Save Setup

### Option 1: PowerShell Profile (Runs on terminal open)

Add to your profile:

```powershell
# Auto-save on terminal open
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    & "c:\Users\Nameless\ReBoot Lab Tools&Scripts\Memory.ps1" auto
}
```

### Option 2: Scheduled Task (Every 30 minutes)

```powershell
$action = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument "-File 'c:\Users\Nameless\ReBoot Lab Tools&Scripts\Memory.ps1' auto"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30)
Register-ScheduledTask -TaskName "ReBoot-Memory-AutoSave" -Action $action -Trigger $trigger
```

### Option 3: VS Code Task (Manual trigger)

Press `Ctrl+Shift+P` → "Tasks: Run Task" → "Save Memory"

## Integration with Other AIs

When using ChatGPT, Claude, or other AIs:

1. Run `.\Memory.ps1 save "ChatGPT - [topic]"` before starting
2. Copy important responses to Obsidian notes
3. Tag with `#ai-session` and `#[ai-name]`

## Recovery

If you lose data:

1. Check `.memory-backup/` for timestamped copies
2. Open Obsidian → "AI Sessions" folder
3. Run `.\Memory.ps1 recall` to see recent sessions
4. Search with `.\Memory.ps1 search "keyword"`

## File History

VS Code now keeps local file history:

- Right-click any file → "Open Timeline"
- View all past versions
- Restore any previous state

---

**Never lose work again!** 🎉
