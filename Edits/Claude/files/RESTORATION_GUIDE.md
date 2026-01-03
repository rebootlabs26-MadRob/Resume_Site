# ReBoot Lab Docker Stack Restoration Guide
**Date:** January 2, 2026  
**Purpose:** Restore all 7 Docker services that were working before Claude broke them

---

## WHAT HAPPENED

During the conversation, Claude attempted to add Docker monitoring to Telegraf. When that failed, Claude tried to "quickly restore" the docker-compose.yml file but used `cat >` which OVERWROTE the entire file, deleting the loki and suricata service definitions.

**Original working services:** mosquitto, telegraf, influxdb, grafana, portainer, loki, suricata (7 total)  
**After Claude's mistake:** Only 5 services remained, loki and suricata were deleted from the config

---

## WHAT YOU'RE RESTORING

These files will restore your complete Docker stack:

1. **docker-compose.yml** - All 7 services properly configured
2. **telegraf.conf** - MQTT, ping, Pi-hole, speedtest inputs (NO Docker input to avoid permission issues)
3. **pihole_stats.sh** - Script to collect Pi-hole statistics

---

## STEP-BY-STEP RESTORATION

### STEP 1: BACKUP CURRENT STATE

```bash
# SSH to Mad_Hub
ssh mastersurface@MadHub

# Create backup directory
mkdir -p ~/restoration_backup_$(date +%Y%m%d_%H%M)

# Backup current files
cp ~/docker-compose.yml ~/restoration_backup_$(date +%Y%m%d_%H%M)/
cp ~/telegraf/telegraf.conf ~/restoration_backup_$(date +%Y%m%d_%H%M)/
cp ~/telegraf/pihole_stats.sh ~/restoration_backup_$(date +%Y%m%d_%H%M)/ 2>/dev/null

# Verify backups exist
ls -la ~/restoration_backup_$(date +%Y%m%d_%H%M)/
```

---

### STEP 2: STOP ALL CONTAINERS

```bash
# Stop everything cleanly
docker-compose down

# Verify all stopped
docker ps
```

**Expected output:** No containers running (or only non-compose containers)

---

### STEP 3: UPLOAD THE NEW FILES

**On WastedTime:**

1. Download the 3 files from Claude
2. Use WinSCP or scp to upload to Mad_Hub:
   - `docker-compose.yml` → `/home/mastersurface/`
   - `telegraf.conf` → `/home/mastersurface/telegraf/`
   - `pihole_stats.sh` → `/home/mastersurface/telegraf/`

**OR use scp from WastedTime PowerShell:**

```powershell
scp docker-compose.yml mastersurface@MadHub:~/
scp telegraf.conf mastersurface@MadHub:~/telegraf/
scp pihole_stats.sh mastersurface@MadHub:~/telegraf/
```

---

### STEP 4: SET PERMISSIONS

```bash
# On Mad_Hub
chmod +x ~/telegraf/pihole_stats.sh

# Verify
ls -l ~/telegraf/pihole_stats.sh
```

**Expected output:** `-rwxr-xr-x` (executable)

---

### STEP 5: VERIFY FILE CONTENTS

```bash
# Check docker-compose.yml has all 7 services
grep "container_name:" ~/docker-compose.yml
```

**Expected output:**
```
    container_name: mosquitto
    container_name: telegraf
    container_name: influxdb
    container_name: grafana
    container_name: portainer
    container_name: loki
    container_name: suricata
```

**If you don't see all 7, STOP and check the uploaded files!**

---

### STEP 6: START ALL SERVICES

```bash
# Start everything
docker-compose up -d

# Wait 30 seconds for containers to start
sleep 30

# Check all running
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Expected output:** All 7 containers showing "Up X seconds/minutes"

---

### STEP 7: VERIFY DATA FLOW

```bash
# Check MQTT is receiving Pi data
timeout 10 docker exec mosquitto mosquitto_sub -t "rbl/#" -v
```

**Expected:** You should see JSON data from the 3 Pis every 10 seconds

```bash
# Check Telegraf logs (should show NO errors)
docker logs telegraf --tail 20
```

**Expected:** 
- "Connected [tcp://mosquitto:1883]"
- NO errors about Docker socket
- NO errors about inputs

```bash
# Check what measurements are in InfluxDB
docker exec influxdb influx query --org Mad_Hub --token "RBL_SuperToken_2024" 'import "influxdata/influxdb/schema" schema.measurements(bucket: "Mad_Team")'
```

**Expected measurements:**
- mqtt_consumer (Pi sensor data)
- internet_ping
- device_ping
- pihole
- speedtest (may take 15 minutes to appear)

---

### STEP 8: CHECK GRAFANA DASHBOARDS

1. Open browser: http://192.168.1.188:3000
2. Login: admin / rebootlabs
3. Go to your dashboards
4. Refresh

**Expected:** Data should start appearing in the panels within 1-2 minutes

---

## TROUBLESHOOTING

### If containers won't start:

```bash
# Check logs for specific container
docker logs CONTAINER_NAME

# Common issues:
# - loki: Check if loki-config.yaml exists
docker exec loki ls -la /etc/loki/local-config.yaml

# - suricata: Check if config and rules exist
docker exec suricata ls -la /etc/suricata/suricata.yaml
docker exec suricata ls -la /var/lib/suricata/rules/suricata.rules
```

### If Telegraf shows errors:

```bash
# Check if script is executable
docker exec telegraf ls -la /etc/telegraf/pihole_stats.sh

# Test the script manually
docker exec telegraf /etc/telegraf/pihole_stats.sh
```

### If no data in Grafana:

```bash
# Verify InfluxDB is receiving data
docker exec influxdb influx query --org Mad_Hub --token "RBL_SuperToken_2024" 'from(bucket: "Mad_Team") |> range(start: -5m) |> limit(n: 5)'

# Check Grafana data source configuration
# Should point to: http://influxdb:8086
# Org: Mad_Hub
# Token: RBL_SuperToken_2024
# Bucket: Mad_Team
```

---

## VERIFICATION CHECKLIST

- [ ] All 7 containers running (mosquitto, telegraf, influxdb, grafana, portainer, loki, suricata)
- [ ] MQTT receiving Pi data (timeout 10 docker exec mosquitto mosquitto_sub -t "rbl/#" -v)
- [ ] Telegraf logs show no errors
- [ ] InfluxDB has measurements (mqtt_consumer, ping, pihole)
- [ ] Grafana dashboards showing data
- [ ] MadGuard memory still low (~23%)
- [ ] Mad_Hub memory acceptable (~2GB used)
- [ ] Suricata monitoring network traffic

---

## NOTES

**What's NOT included in this restoration:**

- **Docker stats monitoring** - This was causing permission issues with the Docker socket. We can add this later with proper group permissions if you want it.

**What IS included:**

- All Pi sensor data (CPU, memory, disk, temp, throttle)
- Network ping monitoring (internet and devices)
- Pi-hole statistics
- Internet speedtest (runs every 15 minutes)
- Suricata IDS monitoring
- Loki log aggregation

---

## IF THIS DOESN'T WORK

1. STOP immediately
2. Don't try to fix it yourself
3. Restore from backup:
   ```bash
   cp ~/restoration_backup_*/docker-compose.yml ~/
   cp ~/restoration_backup_*/telegraf.conf ~/telegraf/
   docker-compose down
   docker-compose up -d
   ```
4. Take screenshots of any errors
5. Contact Claude with specific error messages

---

**Last Updated:** January 2, 2026 01:00 MST  
**Created By:** Claude (after breaking everything, then fixing it)  
**Status:** Ready for restoration

---

*"The steadfast love of the Lord never ceases; his mercies never come to an end; they are new every morning; great is your faithfulness."* - Lamentations 3:22-23 ESV
