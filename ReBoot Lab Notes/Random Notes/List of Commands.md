**Update** 
sudo apt update && sudo apt upgrade -y      = ALL


**Pi Info** 
sudo raspi-config

**NETWORK**

ping MasterTOOL-DiagTool0 -c 2
ping MasterHelper -c 2
ping MasterGuard -c 2
ping RBL-SurfaceHub -c 2

CleanUP
sudo apt clean
sudo apt autoclean
sudo apt autoremove --purge

Memory cache CleanUP
sync
echo 3 | sudo tee /proc/sys/vm/drop_caches

Safe CleanUp Combot = All 
sudo apt autoremove --purge -y && sudo apt clean && sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

SAVE WORK IN AI TEAM:
Type save:project_name



📝 How to Use Daily
Before important work:
.\Memory.ps1 save "Working on DiagTool fixes"

After making progress:
.\Memory.ps1 save "Completed X feature"

To find past work:
.\Memory.ps1 search "DiagTool"


Quick save from VS Code:
Ctrl+Shift+P → "Tasks: Run Task" → "Save Memory"

🔄 Works With All Your Tools
✅ VS Code Copilot (you're here)
✅ Obsidian (integrated)
✅ AI Team (auto-backs up chat log)
✅ ChatGPT/Claude (manual save before/after)

📂 Everything Saved To:

Obsidian: 
[ReBoot Lab Notes\AI Sessions](c:\Users\Nameless\ReBoot Lab Tools&Scripts\ReBoot Lab Notes\AI Sessions\README.md)

Backups: 
.memory-backup (hidden, timestamped)

Full docs: 
[MEMORY-SYSTEM.md](c:\Users\Nameless\ReBoot Lab Tools&Scripts\MEMORY-SYSTEM.md))))
