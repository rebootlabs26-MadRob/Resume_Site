Raspberry Pi, SSH, Branding, Team Ops, Troubleshooting

🔵 Core Raspberry Pi Commands

Navigation & System

• `ls`, `cd`, `pwd`, `mkdir` , `rm -r`  
• `sudo reboot`  
• `sudo shutdown now`  
• `sudo raspi-config` — Pi settings

Package Management

• `sudo apt update`  
• `sudo apt upgrade -y`  
• `sudo apt install`  
• `sudo apt autoremove`

Networking

• `hostname -I` — show IP  
• `ping`  
• `sudo nano /etc/dhcpcd.conf` — static IP  
• `ip a` — full network info

SSH & Remote Ops

• `ssh pi@`  
• `scp pi@:/path` — copy to Pi  
• `scp pi@:/path` — copy from Pi

🟣 ReBoot Lab / Pi Team Workflow Commands

Branding & Dashboard

• `python3 dashboard.py` — launch GUI  
• `sudo systemctl restart dashboard` — restart service  
• `sudo systemctl status dashboard` — check status

GPIO / POST Code Monitoring

• `gpio readall` — check pin states  
• `python3 post_monitor.py` — run POST reader  
• `sudo systemctl restart post-monitor`

Cluster / Multi-Pi Ops

• `ssh pi@pi1.local`  
• `ssh pi@pi2.local`  
• `ssh pi@hub.local`  
• `tmux new -s cluster` — multi-session control  
• `tmux attach -t cluster`

🟡 Common Errors & Fixes

❗ SSH: “Connection refused”

Fix:  
• Ensure SSH enabled: `sudo raspi-config` → Interface Options → SSH  
• Check IP: `hostname -I`  
• Reboot: `sudo reboot`

❗ Dashboard won’t start

Fix:  
• `sudo systemctl status dashboard`  
• Look for Python errors  
• Missing modules → `pip3 install -r requirements.txt`

❗ GPIO not responding

Fix:  
• Check wiring  
• Run: `gpio readall`  
• Ensure script uses correct BCM pin numbers

❗ Pi won’t boot

Fix:  
• Reflash SD card  
• Check power supply  
• Remove USB devices

🟠 Troubleshooting Section (Fast Mode)

1. Network Issues

• `ping 8.8.8.8` — test internet  
• `ping` — test local  
• `sudo systemctl restart networking`

2. Service Issues

• `sudo systemctl status`  
• `sudo journalctl -u`  
• `sudo systemctl restart`

3. Python Errors

• Missing module → `pip3 install`  
• Wrong Python version → `python3 --version`  
• Permission issue → `sudo python3 script.py`

4. File Permission Problems

• `chmod +x`  
• `sudo chown pi:pi`

5. SD Card Full

• `df -h` — check space  
• `sudo apt autoremove`  
• `sudo journalctl --vacuum-size=100M`