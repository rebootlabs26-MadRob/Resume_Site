# MasterTOOL / MasterHelper Complete Setup Guide

**ReBoot Labs Distributed Compute System**  
**Created:** December 17, 2025  
**Status:** Complete & Tested

---

## Overview

This guide sets up a **two-Pi distributed compute system**:
- **MasterTOOL** — Brain/controller that monitors load and dispatches jobs
- **MasterHelper** — Worker that executes queued jobs
- **RBL-SurfaceHub** — (Optional) Grafana monitoring hub

```
┌─────────────────┐         Redis          ┌─────────────────┐
│   MasterTOOL    │◄──────────────────────►│  MasterHelper   │
│   (Controller)  │      Job Queue         │    (Worker)     │
│                 │                        │                 │
│ • Redis Server  │                        │ • RQ Worker     │
│ • Load Monitor  │                        │ • Task Executor │
│ • Job Dispatch  │                        │                 │
└────────┬────────┘                        └────────┬────────┘
         │                                          │
         │              MQTT Metrics                │
         └──────────────────┬───────────────────────┘
                            ▼
                   ┌─────────────────┐
                   │  RBL-SurfaceHub │
                   │    (Grafana)    │
                   └─────────────────┘
```

---

## Hardware Requirements

- 2× Raspberry Pi 3B (or newer)
- 2× SD cards (16GB+)
- Wi-Fi network (both Pis on same network)
- (Optional) Surface/PC running Grafana + Mosquitto + InfluxDB

---

## Part 1: Initial Pi Setup

### 1.1 Flash Raspberry Pi OS

Use Raspberry Pi Imager:
- OS: Raspberry Pi OS Lite (64-bit recommended)
- Set hostname during imaging:
  - Pi 1: `MasterTOOL-DiagTool0`
  - Pi 2: `MasterHelper`
- Set username: `rebootlabs`
- Set password: (your choice)
- Enable SSH
- Configure Wi-Fi

### 1.2 First Boot & Update

On **BOTH Pis**:
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 Verify Network Connectivity

From MasterTOOL:
```bash
ping MasterHelper
```

From MasterHelper:
```bash
ping MasterTOOL-DiagTool0
```

If hostnames don't resolve, add to `/etc/hosts` on both Pis:
```bash
sudo nano /etc/hosts
```
Add:
```
192.168.1.222    MasterTOOL-DiagTool0
192.168.1.115    MasterHelper
```
(Replace with your actual IPs — find with `hostname -I`)

---

## Part 2: Redis Setup (MasterTOOL Only)

### 2.1 Install Redis

On **MasterTOOL**:
```bash
sudo apt install -y redis-server
```

### 2.2 Configure Redis for Network Access

```bash
sudo nano /etc/redis/redis.conf
```

Find and change the `bind` line:
```
bind 127.0.0.1 192.168.1.222
```
(Replace `192.168.1.222` with MasterTOOL's actual IP)

Save and restart:
```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### 2.3 Verify Redis

Check it's listening:
```bash
ss -lntp | grep 6379
```

Should show:
```
LISTEN 127.0.0.1:6379
LISTEN 192.168.1.222:6379
```

### 2.4 Test From MasterHelper

On **MasterHelper**:
```bash
sudo apt install -y redis-tools
redis-cli -h MasterTOOL-DiagTool0 ping
```

Should return: `PONG`

---

## Part 3: Python Environment (BOTH Pis)

### 3.1 Create Virtual Environment

On **BOTH Pis**:
```bash
mkdir -p /home/rebootlabs/mastertool/queue
cd /home/rebootlabs/mastertool
python3 -m venv venv
source venv/bin/activate
pip install redis rq psutil
deactivate
```

---

## Part 4: Task Queue Files (BOTH Pis)

### 4.1 Create tasks.py

This file **MUST be identical on both Pis**.

On **BOTH Pis**:
```bash
cat > /home/rebootlabs/mastertool/queue/tasks.py << 'EOF'
# tasks.py - Task functions that workers can import
# This file MUST exist on both MasterTOOL and MasterHelper

def example_task(task_name):
    """Example task that can be queued and processed by workers."""
    import time
    print(f"Running task: {task_name}")
    time.sleep(2)  # Simulate work
    return f"Task {task_name} completed"

def compute_task(n):
    """CPU-intensive example task."""
    result = sum(i * i for i in range(n))
    return f"Computed sum of squares up to {n}: {result}"
EOF
```

### 4.2 Create send_task.py (MasterTOOL Only)

On **MasterTOOL**:
```bash
cat > /home/rebootlabs/mastertool/queue/send_task.py << 'EOF'
# send_task.py - Queue jobs from MasterTOOL
import redis
from rq import Queue
from tasks import example_task, compute_task

# Connect to Redis on MasterTOOL (use your IP)
redis_conn = redis.Redis(host='192.168.1.222', port=6379, db=0)

# Define queues with priorities
high_queue = Queue('high', connection=redis_conn)
default_queue = Queue('default', connection=redis_conn)
low_queue = Queue('low', connection=redis_conn)

# Send tasks to different queues
job1 = high_queue.enqueue(example_task, 'critical_task_1')
job2 = default_queue.enqueue(example_task, 'regular_task_1')
job3 = low_queue.enqueue(compute_task, 100000)

print("Tasks enqueued successfully!")
print(f"  High priority job ID: {job1.id}")
print(f"  Default job ID: {job2.id}")
print(f"  Low priority job ID: {job3.id}")
EOF
```

### 4.3 Create load_monitor.py (MasterTOOL Only)

On **MasterTOOL**:
```bash
cat > /home/rebootlabs/mastertool/queue/load_monitor.py << 'EOF'
# load_monitor.py - Auto-offload when MasterTOOL is stressed
import redis
from rq import Queue
from tasks import compute_task
import psutil
import time

# Thresholds (adjust as needed)
CPU_THRESHOLD = 70    # Offload when CPU > 70%
RAM_THRESHOLD = 75    # Offload when RAM > 75%
CHECK_INTERVAL = 5    # Check every 5 seconds

redis_conn = redis.Redis(host='192.168.1.222', port=6379, db=0)
default_queue = Queue('default', connection=redis_conn)

print("=== MasterTOOL Load Monitor ===")
print(f"CPU threshold: {CPU_THRESHOLD}%")
print(f"RAM threshold: {RAM_THRESHOLD}%")
print(f"Checking every {CHECK_INTERVAL}s")
print("Press Ctrl+C to stop")
print()

jobs_offloaded = 0

while True:
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    
    status = f"CPU: {cpu:5.1f}% | RAM: {ram:5.1f}%"
    
    if cpu > CPU_THRESHOLD or ram > RAM_THRESHOLD:
        # System stressed - offload work!
        job = default_queue.enqueue(compute_task, 500000)
        jobs_offloaded += 1
        print(f"{status} | STRESSED! Offloaded job #{jobs_offloaded} -> MasterHelper")
    else:
        print(f"{status} | OK")
    
    time.sleep(CHECK_INTERVAL)
EOF
```

### 4.4 Create stress_test.py (MasterTOOL Only)

On **MasterTOOL**:
```bash
cat > /home/rebootlabs/mastertool/queue/stress_test.py << 'EOF'
# stress_test.py - Flood the queue and watch MasterHelper work
import redis
from rq import Queue
from tasks import example_task, compute_task

redis_conn = redis.Redis(host='192.168.1.222', port=6379, db=0)

high_queue = Queue('high', connection=redis_conn)
default_queue = Queue('default', connection=redis_conn)
low_queue = Queue('low', connection=redis_conn)

print("Sending 15 jobs to MasterHelper...")

for i in range(3):
    job = high_queue.enqueue(compute_task, 500000)
    print(f"[HIGH] Job {i+1}: {job.id[:8]}...")

for i in range(7):
    job = default_queue.enqueue(example_task, f"batch_job_{i+1}")
    print(f"[DEFAULT] Job {i+1}: {job.id[:8]}...")

for i in range(5):
    job = low_queue.enqueue(compute_task, 1000000)
    print(f"[LOW] Job {i+1}: {job.id[:8]}...")

print("All jobs queued!")
EOF
```

---

## Part 5: Worker Service (MasterHelper Only)

### 5.1 Create systemd Service

On **MasterHelper**:
```bash
sudo nano /etc/systemd/system/rq-worker.service
```

Paste:
```ini
[Unit]
Description=RQ Worker for MasterHelper
After=network.target

[Service]
Type=simple
User=rebootlabs
WorkingDirectory=/home/rebootlabs/mastertool/queue
Environment="PATH=/home/rebootlabs/mastertool/venv/bin"
ExecStart=/home/rebootlabs/mastertool/venv/bin/rq worker --url redis://MasterTOOL-DiagTool0:6379 high default low
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.2 Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable rq-worker
sudo systemctl start rq-worker
sudo systemctl status rq-worker
```

Should show `active (running)` and `Listening on high, default, low...`

---

## Part 6: Load Monitor Service (MasterTOOL Only)

### 6.1 Create systemd Service

On **MasterTOOL**:
```bash
sudo nano /etc/systemd/system/load-monitor.service
```

Paste:
```ini
[Unit]
Description=MasterTOOL Load Monitor
After=network.target redis.service

[Service]
Type=simple
User=rebootlabs
WorkingDirectory=/home/rebootlabs/mastertool/queue
Environment="PATH=/home/rebootlabs/mastertool/venv/bin"
ExecStart=/home/rebootlabs/mastertool/venv/bin/python load_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 6.2 Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable load-monitor
sudo systemctl start load-monitor
sudo systemctl status load-monitor
```

---

## Part 7: Grafana Monitoring (Optional)

### 7.1 Prerequisites

You need a server (Surface/PC) running:
- Mosquitto (MQTT broker) on port 1883
- Telegraf (MQTT → InfluxDB)
- InfluxDB (time-series database)
- Grafana (dashboard)

See `Mad_SPHub_Project_Complete.md` for full setup.

### 7.2 Create diag_publisher.py (BOTH Pis)

On **BOTH Pis**:
```bash
cat > /home/rebootlabs/diag_publisher.py << 'EOF'
#!/usr/bin/env python3
"""
ReBoot Labs Diagnostic Publisher
Publishes system metrics to MQTT broker for Grafana monitoring
"""

import json
import time
import socket
import subprocess
import paho.mqtt.client as mqtt

# Configuration
BROKER = "RBL-SurfaceHub"  # Your Grafana server hostname
PORT = 1883
HOSTNAME = socket.gethostname()

# Set topic based on hostname
if "MasterTOOL" in HOSTNAME:
    TOPIC = "rbl/sensors/diag"
else:
    TOPIC = "rbl/sensors/helper"

INTERVAL = 10  # seconds

def get_cpu_temp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            return round(int(f.read().strip()) / 1000, 1)
    except:
        return 0

def get_cpu_freq():
    try:
        with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq', 'r') as f:
            return round(int(f.read().strip()) / 1000)
    except:
        return 0

def get_cpu_percent():
    try:
        with open('/proc/stat', 'r') as f:
            line = f.readline()
        parts = line.split()
        idle = int(parts[4])
        total = sum(int(p) for p in parts[1:])
        time.sleep(0.1)
        with open('/proc/stat', 'r') as f:
            line = f.readline()
        parts = line.split()
        idle2 = int(parts[4])
        total2 = sum(int(p) for p in parts[1:])
        return round(100 * (1 - (idle2 - idle) / (total2 - total)), 1)
    except:
        return 0

def get_memory():
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        mem = {}
        for line in lines:
            parts = line.split()
            mem[parts[0].rstrip(':')] = int(parts[1])
        total = mem['MemTotal'] / 1024
        available = mem.get('MemAvailable', mem['MemFree']) / 1024
        used = total - available
        return round(used), round(total), round(100 * used / total, 1)
    except:
        return 0, 0, 0

def get_disk():
    try:
        result = subprocess.run(['df', '/'], capture_output=True, text=True)
        line = result.stdout.strip().split('\n')[1]
        parts = line.split()
        total = int(parts[1]) / 1024 / 1024
        used = int(parts[2]) / 1024 / 1024
        return round(used, 1), round(total, 1), round(100 * used / total, 1)
    except:
        return 0, 0, 0

def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            return round(float(f.read().split()[0]) / 3600, 2)
    except:
        return 0

client = mqtt.Client(client_id=HOSTNAME)
client.connect(BROKER, PORT)
client.loop_start()

print(f"Publishing to {BROKER}:{PORT} on topic {TOPIC}")

while True:
    mem_used, mem_total, mem_pct = get_memory()
    disk_used, disk_total, disk_pct = get_disk()
    
    data = {
        "host": HOSTNAME,
        "temp": get_cpu_temp(),
        "freq": get_cpu_freq(),
        "cpu_pct": get_cpu_percent(),
        "mem_used": mem_used,
        "mem_total": mem_total,
        "mem_pct": mem_pct,
        "disk_used": disk_used,
        "disk_total": disk_total,
        "disk_pct": disk_pct,
        "uptime_hrs": get_uptime()
    }
    
    client.publish(TOPIC, json.dumps(data))
    time.sleep(INTERVAL)
EOF
```

### 7.3 Install paho-mqtt

On **BOTH Pis**:
```bash
sudo apt install -y python3-paho-mqtt
```

### 7.4 Add Grafana Server to /etc/hosts

On **BOTH Pis**:
```bash
sudo nano /etc/hosts
```

Add:
```
192.168.1.188    RBL-SurfaceHub
```
(Replace with your Grafana server's actual IP)

### 7.5 Create diag-publisher Service

On **BOTH Pis**:
```bash
sudo nano /etc/systemd/system/diag-publisher.service
```

Paste:
```ini
[Unit]
Description=ReBoot Labs Diagnostic Publisher
After=network.target

[Service]
Type=simple
User=rebootlabs
ExecStart=/usr/bin/python3 /home/rebootlabs/diag_publisher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable diag-publisher
sudo systemctl start diag-publisher
sudo systemctl status diag-publisher
```

---

## Part 8: Testing

### 8.1 Test Basic Job Queue

On **MasterTOOL**:
```bash
cd /home/rebootlabs/mastertool/queue
source ../venv/bin/activate
python send_task.py
```

On **MasterHelper**, verify jobs processed:
```bash
sudo journalctl -u rq-worker -n 20
```

### 8.2 Test Stress Load

On **MasterTOOL**:
```bash
cd /home/rebootlabs/mastertool/queue
source ../venv/bin/activate
python stress_test.py
```

Watch MasterHelper process 15 jobs in priority order.

### 8.3 Test Auto-Offloading

On **MasterTOOL** (spike CPU):
```bash
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
```

Watch load-monitor send jobs:
```bash
sudo journalctl -u load-monitor -f
```

Stop the stress:
```bash
killall yes
```

### 8.4 Verify Grafana

Open browser: `http://RBL-SurfaceHub:3000`

Both MasterTOOL and MasterHelper should show live metrics.

---

## File Structure Reference

### MasterTOOL
```
/home/rebootlabs/
├── diag_publisher.py
└── mastertool/
    ├── venv/
    └── queue/
        ├── tasks.py
        ├── send_task.py
        ├── load_monitor.py
        └── stress_test.py
```

### MasterHelper
```
/home/rebootlabs/
├── diag_publisher.py
└── mastertool/
    ├── venv/
    └── queue/
        └── tasks.py
```

---

## Services Reference

### MasterTOOL
| Service | Purpose | Status Check |
|---------|---------|--------------|
| redis-server | Job broker | `sudo systemctl status redis-server` |
| load-monitor | Auto-offload | `sudo systemctl status load-monitor` |
| diag-publisher | Grafana metrics | `sudo systemctl status diag-publisher` |

### MasterHelper
| Service | Purpose | Status Check |
|---------|---------|--------------|
| rq-worker | Job executor | `sudo systemctl status rq-worker` |
| diag-publisher | Grafana metrics | `sudo systemctl status diag-publisher` |

---

## Network Reference

| Device | Hostname | IP (example) | Role |
|--------|----------|--------------|------|
| Pi 1 | MasterTOOL-DiagTool0 | 192.168.1.222 | Controller |
| Pi 2 | MasterHelper | 192.168.1.115 | Worker |
| Surface | RBL-SurfaceHub | 192.168.1.188 | Monitoring Hub |

---

## Troubleshooting

### Redis Connection Refused
```bash
# Check Redis is running
sudo systemctl status redis-server

# Check Redis is listening on network
ss -lntp | grep 6379

# Test from MasterHelper
redis-cli -h MasterTOOL-DiagTool0 ping
```

### Worker Not Processing Jobs
```bash
# Check worker status
sudo systemctl status rq-worker

# Check worker logs
sudo journalctl -u rq-worker -n 30

# Verify tasks.py exists
ls -la /home/rebootlabs/mastertool/queue/tasks.py
```

### diag-publisher Failing
```bash
# Check logs for error
sudo journalctl -u diag-publisher -n 30

# Test MQTT connection
nc -zv RBL-SurfaceHub 1883

# Verify hostname resolves
ping RBL-SurfaceHub
```

### Hostname Not Resolving
```bash
# Add to /etc/hosts
sudo nano /etc/hosts

# Add entries like:
192.168.1.222    MasterTOOL-DiagTool0
192.168.1.115    MasterHelper
192.168.1.188    RBL-SurfaceHub
```

---

## Quick Reference Commands

```bash
# Restart all services on MasterTOOL
sudo systemctl restart redis-server load-monitor diag-publisher

# Restart all services on MasterHelper
sudo systemctl restart rq-worker diag-publisher

# Watch MasterHelper process jobs
sudo journalctl -u rq-worker -f

# Watch load monitor decisions
sudo journalctl -u load-monitor -f

# Manual job send
cd /home/rebootlabs/mastertool/queue && source ../venv/bin/activate && python send_task.py

# CPU stress test
yes > /dev/null & yes > /dev/null & yes > /dev/null & yes > /dev/null &

# Stop stress test
killall yes
```

---

**Congratulations! You've built a distributed compute system.** 🎉
