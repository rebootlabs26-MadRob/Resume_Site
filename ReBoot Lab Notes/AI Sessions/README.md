---
date: {{date}} {{time}}
type: index
tags: [ai-sessions, memory-system]
---

# AI Sessions Index

This folder contains auto-saved snapshots of all your VS Code and AI Team work.

## Session Types

- **Auto-Save** - Periodic automatic captures (every 30 min)
- **Manual Save** - You triggered save with specific context
- **Recovery** - Backups created before clearing/closing

## How to Use

### Save Current Work

```powershell
.\Memory.ps1 save "Description of what you're working on"
```

### Find Past Work

```powershell
# See recent sessions
.\Memory.ps1 recall

# Search for specific topic
.\Memory.ps1 search "DiagTool"
```

### Restore Lost Work

1. Check this folder for dated files
2. Look in `.memory-backup/` for additional copies
3. Right-click files in VS Code → "Open Timeline"

## Organization

Files are named: `YYYY-MM-DD - Description.md`

- Date prefix for chronological sorting
- Descriptive names for easy identification
- Full context captured in each file

## Integration

This system works with:

- ✅ VS Code Copilot
- ✅ AI Team (Claude/Gemini/OpenAI)
- ✅ ChatGPT (manual copy-paste)
- ✅ Obsidian (you're here!)
- ✅ Any other AI tools

---

**Never lose important work again!** 🎯
