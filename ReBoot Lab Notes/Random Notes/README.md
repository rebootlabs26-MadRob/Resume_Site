# ReBoot Labs AI Team Environment

Multi-AI chat system that coordinates Claude, Gemini, and OpenAI models.

## 🚀 Quick Start

**One command to launch everything:**

```powershell
.\Launch-AITeam.ps1
```

That's it! The launcher automatically:
- ✓ Loads your API keys from `.env`
- ✓ Creates/activates Python virtual environment
- ✓ Installs/updates all dependencies
- ✓ Launches the AI Team chat interface

## 📋 Requirements

- **PowerShell 7+** (Windows PowerShell 7.0 or higher)
- **Python 3.8+**
- API keys for Claude, Gemini, and OpenAI (stored in `.env`)

## 🔑 API Keys Setup

Your API keys are stored in the `.env` file (already configured). This file is:
- ✓ Secure (not in git, not in scripts)
- ✓ Easy to update
- ✓ Never exposed in command history

To update keys, edit `.env` file directly.

## 💬 Using the AI Team

Once launched, you can:

### Quick Commands
- `Claude: your question` - Talk only to Claude
- `Gemini: your question` - Talk only to Gemini
- `OpenAI: your question` - Talk only to OpenAI
- `All: your question` - Run all three and get judge's best answer
- `menu` - Show full menu
- `exit` - Quit

### Examples
```
You: Claude: What's the best way to structure a Python project?
You: All: Compare async/await vs threading in Python
You: Gemini: Explain OAuth2 flow
```

## 📂 Files

- `Launch-AITeam.ps1` - **Main launcher** (use this!)
- `multi_ai_chat.py` - Core AI chat application
- `.env` - API keys and configuration (keep secure!)
- `.gitignore` - Protects sensitive files
- `AIEnv_chatlog.json` - Chat history (auto-created)

## 🔧 Advanced Configuration

Edit `.env` to customize models:

```env
CLAUDE_MODEL_ID=claude-sonnet-4-5-20250929
CLAUDE_JUDGE_MODEL_ID=claude-opus-4-5-20251101
GEMINI_MODEL_ID=gemini-1.5-flash
OPENAI_MODEL_ID=gpt-4o
```

## 📖 Features

- **Multi-Model Comparison** - See responses from all three AIs side-by-side
- **Intelligent Judging** - Claude Opus acts as lead judge to select best answer
- **Shared Context** - All AIs can see conversation history
- **Persistent Logging** - All conversations saved to JSON
- **Flexible Routing** - Talk to specific AIs or all at once

## ⚠️ Security Notes

- Never commit `.env` file to git
- Never share your API keys
- The `.gitignore` file protects sensitive data
- Logs may contain conversation data - review before sharing

---

**ReBoot Labs** | AI Team Environment v1.0
