# ReBoot Labs - AI Coding Instructions

## Project Overview

This workspace contains **two main projects**:

1. **DiagTool / SkullGUI** - Cyberpunk-themed Raspberry Pi diagnostic GUI tools (Tkinter + Python)
2. **AI Team Environment** - Multi-AI chat orchestration system (Claude, Gemini, OpenAI)

## Architecture & Key Files

### DiagTool GUI Variants
| File | Purpose |
|------|---------|
| `Final Working Saves/THISONEWORKSSAVE.py` | Production-ready full diagnostic tool |
| `Edits/SkullGUI/SkullGUI_DiagTool.py` | Neon-themed variant with adaptive scaling |
| `Edits/reboot_diagtool_new/diagtool_fixed.py` | Simplified/fixed version |

### AI Team System (`ReBoot Labs Scripts n Stuff/`)
| File | Purpose |
|------|---------|
| `multi_ai_chat.py` | Core multi-model chat with Claude, Gemini, OpenAI |
| `Launch-AITeam.ps1` | PowerShell launcher (handles venv, deps, env loading) |
| `.env` | API keys (never commit) |

## Code Patterns

### Tkinter GUI Pattern (DiagTool)
```python
# All GUIs use canvas-based layouts with neon styling
BG_GLASS = "#0A0A0A"      # Near-black background
FG_NEON = "#00FF66"       # Neon green accent
ACCENT_PURPLE = "#7A1FA2" # Joker purple headers
FONT_MONO = ("Consolas", 12)  # System data display

# Adaptive screen scaling - always scale from 720x1080 base
def scale(x, y, w, h):
    return (x * WIDTH/720, y * HEIGHT/1080, w * WIDTH/720, h * HEIGHT/1080)
```

### Multi-AI Pattern
```python
# Color-coded responses per AI model
C.L_CLAUDE = '\033[38;5;208m'  # Orange label
C.L_GEMINI = '\033[38;5;129m'  # Purple label
C.L_OPENAI = '\033[38;5;21m'   # Blue label
```

## Running Projects

### DiagTool
```bash
pip install pillow psutil
python "Final Working Saves/THISONEWORKSSAVE.py"
```

### AI Team (PowerShell 7+ required)
```powershell
.\Launch-AITeam.ps1  # Handles everything automatically
```

## Dependencies

- **DiagTool**: `tkinter`, `psutil`, `pillow` (optional for watermarks)
- **AI Team**: `anthropic`, `google-generativeai`, `openai`, `python-dotenv`

## Folder Organization

- **`Edits/`** - Work-in-progress variants from different AI tools
  - `GPT/` - ChatGPT iterations
  - `COPT/` - Copilot iterations
  - `SkullGUI/` - Neon-themed variant
  - `reboot_diagtool_new/` - Simplified versions
- **`Final Working Saves/`** - Production-ready code (current location)
- **`ReBoot Lab GUI Scripts. (Final Saves)/`** - Ultimate destination for finished scripts

## Conventions

- **File naming**: Working saves use `THISONEWORKSSAVE` pattern for production code
- **Config at top**: All constants/colors defined at file start before classes
- **Thread safety**: DiagTool uses `shared_lock` for polling thread data
- **Logging**: DiagTool logs to `diagtool.log`, AI Team to `AIEnv_chatlog.json`
- **Reports**: Saved to `reports/` directory with timestamps

## AI Assistant Guidelines

- **Clear communication**: Step-by-step instructions, minimal unnecessary text
- **Stay organized**: Help track file locations and save states
- **Design accuracy**: Preserve exact hex colors, font choices, and layout specs for DiagTool
- **Check-ins**: Daily wellness reminders (food, water, breaks)
- **Context awareness**: Track conversation progress, avoid confusion

## Platform Notes

- DiagTool targets Raspberry Pi but works on Windows/Linux
- TFT display detection: auto-scales for 320x480 screens
- AI Team venv placed in `$env:USERPROFILE\.ai_team_venv` (avoids Python 3.14 path bug)
