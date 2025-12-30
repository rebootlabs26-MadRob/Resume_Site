# ReBoot Lab Master Reference

## Last Updated: December 27, 2025

---

## NETWORK INFRASTRUCTURE

### Device Map

| Hostname | IP | MAC | Role |
| ---------- | ----- | ----- | ------ |
| **WastedTime** | 192.168.1.179 | D8:BB:C1:9A:D1:3C | Main PC (Windows 11) |
| **RBL-SurfaceHub** | 192.168.1.188 | 4C:0B:BE:21:74:12 | Monitoring Hub (Ubuntu) |
| **MadTOOL** | 192.168.1.222 | B8:27:EB:3E:61:5C | Pi - Controller/Redis |
| **MadHelper** | 192.168.1.115 | B8:27:EB:D9:7B:89 | Pi - Worker |
| **MadGuard** | 192.168.1.247 | B8:27:EB:B3:5F:E7 | Pi - Security |
| Router | 192.168.1.1 | 4C:43:41:DD:21:0C | Gateway |

### Cameras (LaView)

- 192.168.1.174 (98:A8:29:F4:AE:F5)
- 192.168.1.175 (44:72:AC:06:96:F5)
- 192.168.1.104 (44:72:AC:08:A1:AF)
- 192.168.1.134 (44:72:AC:06:71:43)
- 192.168.1.159 (44:72:AC:07:21:07)

---

## CREDENTIALS

### All Raspberry Pis

- **Username:** rebootlabs
- **Password:** G3t2w0rk

### Surface Hub (RBL-SurfaceHub)

- **Username:** mastersurface
- **Grafana:** Email / T1m32w0rk!
- **InfluxDB Org:** RBL_SPHub
- **InfluxDB Bucket:** Mad_Masters/Helpers
- **InfluxDB Token:** RBL_SuperToken_2024

### MadGuard Security Services

- **Pi-hole admin:** K33p0u5saf3
- **Discord Webhook:** <https://discord.com/api/webhooks/1452960364823318559/i2uPgaYkJ9dFtk2t1BxQ2qMeRStoiif952Nubjxdd13Xcb-4_SWZJVhGTwvHMImXSxB8>

### Router/WiFi

- **Router IP:** 192.168.1.1
- **WiFi SSID:** OkiosAgape13
- **WiFi Password:** K33pth3h3110ut26!

### WastedTime Remote Account

- **Username:** WastedTimeRm
- **Purpose:** Remote SSH access from Surface Hub

### Network DNS

- **Primary:** 192.168.1.247 (Pi-hole on MadGuard)
- **Secondary:** 8.8.8.8
- **Domain:** rebootlabs.local

---

## SERVICES BY DEVICE

### MadTOOL (.222)

- Redis (port 6379)
- RQ load-monitor
- diag_publisher.py → MQTT topic: `rbl/sensors/diag`

### MadHelper (.115)

- RQ worker
- diag_publisher.py → MQTT topic: `rbl/sensors/helper`

### MadGuard (.247)

- **Pi-hole DNS** - Ad/malware blocking (ports 53, 80)
- **WireGuard VPN** - Remote access (port 51820/UDP)
- **Suricata IDS/IPS** - Intrusion detection
- **fail2ban** - Brute force protection
- **security_alerts.py** → Discord + MQTT topic: `rbl/security/alerts`
- diag_publisher.py → MQTT topic: `rbl/sensors/masterguard`

### Surface Hub (.188) - Docker Stack

| Container | Port | Purpose |
| ----------- | ------ | --------- |
| mosquitto | 1883 | MQTT Broker |
| telegraf | - | Data collector |
| influxdb | 8086 | Time-series DB |
| grafana | 3000 | Dashboards |
| portainer | 9000/9443 | Container management |

---

## DATA FLOW

```text
Pi Sensors (diag_publisher.py)
        ↓
    MQTT Messages
        ↓
Mosquitto Broker (Surface Hub)
        ↓
Telegraf (subscribes to rbl/+/+)
        ↓
InfluxDB (stores time-series)
        ↓
Grafana (visualizes dashboards)
```

### MQTT Topics

- `rbl/sensors/diag` - MadTOOL metrics
- `rbl/sensors/helper` - MadHelper metrics
- `rbl/sensors/masterguard` - MadGuard metrics
- `rbl/security/alerts` - Security events

---

## QUICK COMMANDS

### Surface Hub Aliases

```bash
RBLall          # Reboot all 3 Pis simultaneously
RBL-Lab         # Reboot entire lab (asks about WastedTime first)
olla            # Local AI assistant (Ollama with Phi3)
```

### Reboot Scripts Location

- `~/reboot_all_pis.sh` - RBLall script
- `~/reboot_lab.sh` - RBL-Lab script

### Docker Management

```bash
docker ps -a                    # List all containers
docker logs <container> --tail 50   # View logs
docker restart <container>      # Restart container
docker exec mosquitto mosquitto_sub -t "rbl/#" -v  # Watch MQTT
```

### Check Data Flow

```bash
# Watch MQTT messages (15 seconds)
timeout 15 docker exec mosquitto mosquitto_sub -t "rbl/sensors/#" -v

# Check InfluxDB for recent data
docker exec influxdb influx query --org RBL_SPHub --token "RBL_SuperToken_2024" \
  'from(bucket: "Mad_Masters/Helpers") |> range(start: -5m) |> filter(fn: (r) => r._measurement == "mqtt_consumer") |> distinct(column: "topic")'
```

---

## SECURITY CONFIGURATION

### SSH Keys Deployed

- Surface Hub → MadTOOL ✅
- Surface Hub → MadHelper ✅
- Surface Hub → MadGuard ✅
- Surface Hub → WastedTime ✅ (via WastedTimeRm account)

### SSH Hardening (All Linux Devices)

- Password authentication: DISABLED
- Root login: DISABLED
- Key-based auth only

### Firewalls Active

**MadTOOL:**

- SSH (22)
- Redis (6379)

**MadHelper:**

- SSH (22)

**MadGuard:**

- SSH (22)
- DNS (53)
- Web (80)
- WireGuard (51820/UDP)

**Surface Hub (UFW):**

- SSH (22) - Open
- Grafana (3000) - LAN only
- MQTT (1883) - LAN only
- Docker network (172.20.0.0/16) - Allowed
- **CRITICAL:** `sudo ufw default allow routed` required for Docker!

**WastedTime (Windows):**

- Windows Firewall active on all profiles
- SMB restricted to LocalSubnet only
- Windows Defender active

### Brute Force Protection

- fail2ban running on all Pis + Surface Hub

---

## TROUBLESHOOTING

### Docker Containers Not Talking (Telegraf timeout)

**Cause:** UFW blocking Docker internal traffic
**Fix:**

```bash
sudo ufw default allow routed
sudo ufw reload
docker restart telegraf
```

### MQTT Not Publishing from Pis

**Cause:** Missing `client.loop_start()` after MQTT connect
**Check:** Look for "Sent" in logs but no data in Mosquitto
**Fix:** Add `client.loop_start()` after `client = connect_mqtt()` in diag_publisher.py

### Pi Dual IP Issue

**Symptoms:** Pi responds on two different IPs
**Fix:** Check netplan/NetworkManager configs match router DHCP reservations

### Grafana "No Data"

```bash
# Verify data is reaching InfluxDB
docker exec influxdb influx query --org RBL_SPHub --token "RBL_SuperToken_2024" \
  'from(bucket: "Mad_Masters/Helpers") |> range(start: -5m) |> limit(n:5)'
```

---

## WEB INTERFACES

| Service   | URL                          | Credentials        |
| --------- | ---------------------------- | ------------------ |
| Pi-hole   | <http://madguard/admin>      | K33p0u5saf3        |
| Grafana   | <http://rbl-surfacehub:3000> | admin / rebootlabs |
| Portainer | <http://rbl-surfacehub:9000> | (set during setup) |

---

## KEY FILES LOCATIONS

### Surface Hub

- Docker compose: `~/docker-compose.yml`
- Telegraf config: `~/telegraf/telegraf.conf`
- Mosquitto config: `~/mosquitto/config/mosquitto.conf`
- Reboot scripts: `~/reboot_all_pis.sh`, `~/reboot_lab.sh`
- Ollama modelfile: `~/RBL-Phi3-Modelfile`

### All Pis

- Main script: `/home/rebootlabs/diag_publisher.py`
- Systemd service: `diag-publisher.service`

### MadGuard Additional

- Security alerts: `/home/rebootlabs/security_alerts.py`

---

## CRITICAL NOTES

### WastedTime (Main PC)

⚠️ **ALWAYS requires explicit confirmation before ANY reboot**

- Has motherboard power issues
- Does not get power everywhere it should
- Treat with extra care

### UFW + Docker

UFW's default "deny routed" blocks container-to-container traffic.
After enabling UFW, always run:

```bash
sudo ufw default allow routed
sudo ufw route allow from 172.20.0.0/16 to 172.20.0.0/16
sudo ufw reload
```

### Hostname Resolution

- Pi-hole on MadGuard handles DNS
- Surface Hub also has `/etc/hosts` entries as backup
- Always use hostnames (madtool, madhelper, madguard) not IPs

---

## PENDING/FUTURE TASKS

1. **pfSense Setup** - Replace ISP router for better security
2. **Camera Integration** - LaView F1/F1P ONVIF setup
3. **WireGuard Remote** - Port forward 51820/UDP for remote access
4. **Network Segmentation** - Separate Lab VLAN from home network

---

*"I can do all things through Christ who strengthens me." - Philippians 4:13 NKJV*
