# ReBoot Lab - Common Commands Reference

**Quick access to frequently used commands for managing your home lab infrastructure**

---

## SSH Access to Lab Devices

```bash
# Surface Hub (Mad_Hub)
ssh mad_hub@192.168.1.188
ssh mad_hub@mad_hub

# MadTOOL (Job Controller)
ssh madtool@192.168.1.222
ssh madtool@madtool

# MadHelper (Task Processor)
ssh madhelper@192.168.1.115
ssh madhelper@madhelper

# MadGuard (Security Pi)
ssh madguard@192.168.1.247
ssh madguard@madguard
```

---

## Docker Container Management

### View Running Containers

```bash
docker ps                    # Running containers only
docker ps -a                 # All containers (including stopped)
docker stats                 # Real-time resource usage
```

### Docker Compose Operations

```bash
docker compose up -d         # Start all services in background
docker compose down          # Stop and remove containers
docker compose restart       # Restart all services
docker compose ps            # Show compose project containers
```

### Container Logs

```bash
docker compose logs -f                    # Follow all logs
docker compose logs -f telegraf           # Follow specific service
docker compose logs -f influxdb
docker compose logs -f grafana
docker compose logs -f mosquitto
docker logs [container_name] -f           # Follow specific container
```

### Container Management

```bash
docker restart [container_name]           # Restart specific container
docker exec -it [container_name] /bin/bash  # Enter container shell
docker stop [container_name]              # Stop container
docker start [container_name]             # Start container
```

### Docker Cleanup

```bash
docker system prune              # Remove unused data
docker system prune -a           # Remove ALL unused images
docker volume prune              # Remove unused volumes
```

---

## System Monitoring

### Quick Status Checks

```bash
htop                    # Interactive process viewer (q to quit)
free -h                 # Memory usage (human readable)
df -h                   # Disk usage (human readable)
uptime                  # System uptime and load
top                     # Process monitor (q to quit)
```

### Detailed System Info

```bash
# Temperature (on Pis)
vcgencmd measure_temp

# CPU Info
lscpu
cat /proc/cpuinfo

# Memory Details
cat /proc/meminfo

# Disk I/O
iostat

# Network interfaces
ip a
ifconfig
```

---

## Service Management

### Systemd Services

```bash
# Status
sudo systemctl status [service]
sudo systemctl status docker
sudo systemctl status telegraf

# Control
sudo systemctl start [service]
sudo systemctl stop [service]
sudo systemctl restart [service]
sudo systemctl enable [service]      # Enable at boot
sudo systemctl disable [service]     # Disable at boot

# Logs
journalctl -u [service] -f          # Follow service logs
journalctl -u docker -f
journalctl -u telegraf -f --since "10 minutes ago"
```

---

## Network Management

### Network Status

```bash
ip a                              # Show all network interfaces
ping 192.168.1.1                  # Test gateway connectivity
ping 8.8.8.8                      # Test internet connectivity
ping madguard                     # Test hostname resolution

# Port listening
sudo netstat -tulpn               # Show listening ports
sudo ss -tulpn                    # Modern alternative to netstat
```

### Network Troubleshooting

```bash
# Trace route
traceroute 8.8.8.8
traceroute google.com

# DNS lookup
nslookup google.com
dig google.com

# Network connections
sudo netstat -anp | grep ESTABLISHED
```

---

## MQTT Monitoring

### Subscribe to MQTT Topics

```bash
# Listen to all topics
mosquitto_sub -h 192.168.1.188 -t '#' -v

# Listen to specific device
mosquitto_sub -h 192.168.1.188 -t 'madtool/#' -v
mosquitto_sub -h 192.168.1.188 -t 'madhelper/#' -v
mosquitto_sub -h 192.168.1.188 -t 'madguard/#' -v

# Listen to specific metric
mosquitto_sub -h 192.168.1.188 -t 'madtool/cpu_temp' -v
mosquitto_sub -h 192.168.1.188 -t 'madguard/memory_percent' -v
```

### Publish Test Message

```bash
mosquitto_pub -h 192.168.1.188 -t 'test/topic' -m 'test message'
```

---

## Pi-hole Management (MadGuard)

### Status & Control

```bash
pihole status                    # Check Pi-hole status
pihole restartdns                # Restart DNS service
pihole -up                       # Update Pi-hole
pihole -g                        # Update gravity (blocklists)
```

### Query & Debugging

```bash
pihole -q example.com            # Query if domain is blocked
pihole -t                        # Tail Pi-hole log
pihole -c                        # Chronometer (live stats)
```

### Administrative

```bash
pihole checkout master           # Switch to master branch
pihole -r                        # Repair/reconfigure
```

---

## Firewall (UFW)

### Status & Rules

```bash
sudo ufw status                  # View firewall status
sudo ufw status numbered         # Show rule numbers
sudo ufw status verbose          # Detailed status
```

### Allow/Deny Rules

```bash
sudo ufw allow 22                # Allow SSH
sudo ufw allow 3000              # Allow Grafana
sudo ufw allow 1883              # Allow MQTT
sudo ufw deny 80                 # Deny HTTP

# Allow from specific IP
sudo ufw allow from 192.168.1.100 to any port 22
```

### Docker Networking

```bash
sudo ufw default allow routed    # CRITICAL: Allow Docker container communication
```

### Control

```bash
sudo ufw enable                  # Enable firewall
sudo ufw disable                 # Disable firewall
sudo ufw reload                  # Reload rules
sudo ufw delete [rule_number]    # Delete rule by number
```

---

## File Operations

### Viewing Files

```bash
cat filename                     # Display entire file
less filename                    # Page through file (q to quit)
head filename                    # First 10 lines
tail filename                    # Last 10 lines
tail -f filename                 # Follow file updates (logs)
tail -n 50 filename              # Last 50 lines
```

### Editing Files

```bash
nano filename                    # Simple text editor
nano /etc/hosts                  # Edit with sudo if needed
```

### Searching

```bash
grep "search_term" filename      # Search in file
grep -r "search_term" /path/     # Recursive search
grep -i "term" filename          # Case-insensitive search
```

### File Management

```bash
ls -lh                          # List with human-readable sizes
ls -lah                         # Include hidden files
du -sh /path/                   # Directory size
find /path/ -name "*.log"       # Find files by name
```

---

## Telegraf Management

### Testing Configuration

```bash
telegraf --test                              # Test config and show output
telegraf --config /path/to/config --test     # Test specific config
telegraf --test --input-filter mqtt          # Test specific input
```

### Service Control

```bash
sudo systemctl restart telegraf              # Restart service
sudo systemctl status telegraf               # Check status
journalctl -u telegraf -f                    # Follow logs
```

---

## InfluxDB Operations

### Access InfluxDB CLI

```bash
influx                           # Enter InfluxDB shell
```

### Common InfluxDB Commands (inside influx shell)

```influx
# List organizations
org list

# List buckets
bucket list

# Show measurements
show measurements

# Query data
from(bucket: "Mad_Team")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
```

---

## Git Operations

### Basic Workflow

```bash
git status                       # Check status
git add .                        # Stage all changes
git add filename                 # Stage specific file
git commit -m "message"          # Commit changes
git push                         # Push to remote
git pull                         # Pull from remote
```

### Branching

```bash
git branch                       # List branches
git branch new-branch            # Create branch
git checkout branch-name         # Switch branch
git checkout -b new-branch       # Create and switch
```

### Undoing Changes

```bash
git reset --hard                 # Discard all local changes
git reset HEAD filename          # Unstage file
git checkout -- filename         # Discard file changes
```

---

## Python & Scripts

### Running Scripts

```bash
python3 script.py                # Run Python script
python3 script.py &              # Run in background
nohup python3 script.py &        # Run and survive logout
```

### Virtual Environments

```bash
python3 -m venv venv             # Create virtual environment
source venv/bin/activate         # Activate environment
deactivate                       # Deactivate environment
pip install -r requirements.txt  # Install dependencies
```

---

## Quick Diagnostics

### One-Line System Check

```bash
# Comprehensive system snapshot
echo "=== SYSTEM ===" && uptime && echo && echo "=== MEMORY ===" && free -h && echo && echo "=== DISK ===" && df -h && echo && echo "=== DOCKER ===" && docker ps
```

### Network Quick Check

```bash
# Test all lab devices
ping -c 1 192.168.1.222 && echo "MadTOOL: OK" || echo "MadTOOL: FAIL"
ping -c 1 192.168.1.115 && echo "MadHelper: OK" || echo "MadHelper: FAIL"
ping -c 1 192.168.1.247 && echo "MadGuard: OK" || echo "MadGuard: FAIL"
ping -c 1 192.168.1.188 && echo "Mad_Hub: OK" || echo "Mad_Hub: FAIL"
```

### MQTT Quick Test

```bash
# Test MQTT is receiving data (30 second sample)
timeout 30 mosquitto_sub -h 192.168.1.188 -t '#' -v | head -20
```

---

## Emergency Commands

### When Things Go Wrong

```bash
# Docker not responding
sudo systemctl restart docker
docker compose -f /path/to/docker-compose.yml down
docker compose -f /path/to/docker-compose.yml up -d

# Reset stuck containers
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

# Kill hung process
ps aux | grep [process_name]
sudo kill -9 [PID]

# Clear system cache
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches

# Check what's using space
du -sh /var/lib/docker/*
docker system df
```

### System Recovery

```bash
# Reboot system
sudo reboot

# Force reboot (last resort)
sudo reboot -f

# Check system logs for errors
journalctl -p err -b           # Errors from current boot
journalctl -xe                 # Recent errors
dmesg | tail                   # Kernel messages
```

---

## Lab-Specific Workflows

### Full System Restart Sequence

```bash
# 1. Stop Docker services on Mad_Hub
ssh mad_hub@192.168.1.188
cd /path/to/docker-compose/
docker compose down

# 2. Reboot Pis (from Mad_Hub or local)
ssh madguard@192.168.1.247 "sudo reboot"
ssh madtool@192.168.1.222 "sudo reboot"
ssh madhelper@192.168.1.115 "sudo reboot"

# Wait 2-3 minutes for Pis to boot

# 3. Restart Docker services
docker compose up -d

# 4. Verify everything
docker ps
mosquitto_sub -h 192.168.1.188 -t '#' -v
```

### Check Data Flow

```bash
# 1. Verify MQTT receiving data
mosquitto_sub -h 192.168.1.188 -t 'madtool/#' -v

# 2. Check Telegraf processing
journalctl -u telegraf -f

# 3. Verify InfluxDB receiving data
docker logs influxdb -f

# 4. Check Grafana dashboard
# Open browser: http://192.168.1.188:3000
```

---

## Lab Device Quick Reference

|Device|IP|Hostname|Role|Key Services|
|---|---|---|---|---|
|Mad_Hub|192.168.1.188|mad_hub|Central Monitoring|Docker, Grafana, InfluxDB, Telegraf, MQTT|
|MadTOOL|192.168.1.222|madtool|Job Controller|Redis, MQTT Publisher|
|MadHelper|192.168.1.115|madhelper|Task Processor|MQTT Publisher|
|MadGuard|192.168.1.247|madguard|Security|Pi-hole, Suricata, WireGuard, fail2ban|

---

## Quick Access URLs

- **Grafana Dashboard**: http://192.168.1.188:3000
- **Portainer**: http://192.168.1.188:9000
- **Pi-hole Admin**: http://192.168.1.247/admin

---

**Last Updated**: January 2, 2026 **Maintained by**: MadLab Rob @ ReBoot Lab