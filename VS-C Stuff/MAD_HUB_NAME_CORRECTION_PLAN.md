# Mad_Hub System Name Correction Plan
**Date:** January 2, 2026  
**Goal:** Fix ALL name inconsistencies across entire system - NO visual changes

---

## 🔴 CRITICAL RULES
- ✅ **KEEP:** All 25 Grafana panels, layouts, visuals, dashboard structure
- ✅ **KEEP:** Docker setup, InfluxDB data, Telegraf pipeline
- ❌ **CHANGE ONLY:** MQTT topic names and query labels - INFORMATION ONLY

---

## 📦 BACKUP STATUS
**Location:** Mad_Hub at `/home/mastersurface/BACKUP_JAN2_2026_PRE_NAME_FIX.tar.gz`  
**Size:** 3.9KB  
**Contains:**
- docker-compose.yml
- telegraf.conf (current working version)
- pihole_stats.sh
- speedtest_wrapper.sh
- CREDENTIALS.txt (all passwords/tokens)

**Action Needed:** Copy to Windows Quarantine folder

---

## 🔍 CURRENT SYSTEM INVENTORY

### Mad_Hub (192.168.1.188)
**Docker Containers:**
- mosquitto (MQTT broker)
- telegraf (data collector)
- influxdb (database)
- grafana (visualization)
- portainer, loki, suricata

**InfluxDB:**
- Organization: `Mad_Hub`
- Bucket: `Mad_Team`
- Token: `owI3GftJwbKC45FgqHa5fiAn2DxTuivt_jMHGiH3PWfUfnaac59bhrXY4x9_fOGT0q7y4BQ-9yTTeL4NE13Ihg==`

**Grafana:**
- URL: http://192.168.1.188:3000
- Email: rebootlabs26@gmail.com
- Password: Madvi3ws
- Panels: 25 visuals (temp, cpu, mem, disk, throttle, voltage, ping, speedtest, pihole, docker)

---

## ❌ CURRENT PROBLEMS (Name Inconsistencies)

### MQTT Topics - WRONG NAMES:
| Pi | IP | Current Topic | Problem |
|---|---|---|---|
| MadTOOL | 192.168.1.222 | `rbl/sensors/diag` | Says "diag" not "tool" |
| MadHelper | 192.168.1.115 | `rbl/sensors/helper` | ✅ Correct |
| MadGuard | 192.168.1.247 | `rbl/sensors/masterguard` | Says "masterguard" not "guard" |

### Result:
- Grafana legends all show "host=Mad_Hub" (can't tell Pis apart)
- Confusion in queries and documentation
- Previous mistakes used "MasterTOOL" instead of "MadTOOL"

---

## ✅ THE FIX - Name Corrections Only

### New MQTT Topics (Corrected):
| Pi | IP | NEW Topic | Pi Script Location |
|---|---|---|---|
| MadTOOL | 192.168.1.222 | `rbl/sensors/tool` | `/home/rebootlabs/diag_publisher.py` |
| MadHelper | 192.168.1.115 | `rbl/sensors/helper` | `/home/rebootlabs/diag_publisher.py` |
| MadGuard | 192.168.1.247 | `rbl/sensors/guard` | `/home/rebootlabs/diag_publisher.py` |

### Display Names in Grafana:
- `rbl/sensors/tool` → **MadTOOL**
- `rbl/sensors/helper` → **MadHelper**
- `rbl/sensors/guard` → **MadGuard**

---

## 📝 STEP-BY-STEP EXECUTION PLAN

### Phase 1: Final Backup (5 min)
1. ✅ **DONE:** Created backup on Mad_Hub
2. **TODO:** Copy `BACKUP_JAN2_2026_PRE_NAME_FIX.tar.gz` to Windows Quarantine folder
3. **TODO:** Export Grafana dashboard JSON manually (Settings → JSON Model)

### Phase 2: Update Pi MQTT Topics (10 min)
**SSH to each Pi and update topic name:**

#### MadTOOL (192.168.1.222):
```bash
ssh rebootlabs@192.168.1.222
sudo nano /home/rebootlabs/diag_publisher.py
# Change: TOPIC = "rbl/sensors/diag"
# To:     TOPIC = "rbl/sensors/tool"
sudo systemctl restart diag-publisher
exit
```

#### MadHelper (192.168.1.115):
```bash
ssh rebootlabs@192.168.1.115
# Check current topic - should already be "helper"
grep TOPIC /home/rebootlabs/diag_publisher.py
# If correct, no changes needed
exit
```

#### MadGuard (192.168.1.247):
```bash
ssh rebootlabs@192.168.1.247
sudo nano /home/rebootlabs/diag_publisher.py
# Change: TOPIC = "rbl/sensors/masterguard"
# To:     TOPIC = "rbl/sensors/guard"
sudo systemctl restart diag-publisher
exit
```

### Phase 3: Update Telegraf Config (5 min)
**SSH to Mad_Hub:**
```bash
ssh mastersurface@192.168.1.188
nano ~/telegraf/telegraf.conf
```

**Find this section:**
```toml
[[inputs.mqtt_consumer]]
  servers = ["tcp://mosquitto:1883"]
  topics = ["rbl/+/+"]
```

**Change to:**
```toml
[[inputs.mqtt_consumer]]
  servers = ["tcp://mosquitto:1883"]
  topics = [
    "rbl/sensors/tool",
    "rbl/sensors/helper", 
    "rbl/sensors/guard"
  ]
```

**Restart Telegraf:**
```bash
docker restart telegraf
docker logs telegraf --tail 20
```

### Phase 4: Update Grafana Queries (15 min)
**For EACH panel (temp, cpu, mem, disk, throttle, voltage):**

Open panel → Edit → Replace query with:

**Temperature Query:**
```flux
from(bucket: "Mad_Team")
  |> range(start: -15m)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "temp")
  |> map(fn: (r) => ({
      r with
      device: if r.topic == "rbl/sensors/tool" then "MadTOOL"
              else if r.topic == "rbl/sensors/helper" then "MadHelper"
              else if r.topic == "rbl/sensors/guard" then "MadGuard"
              else "Unknown"
    }))
  |> group(columns: ["device"])
```

**CPU Query:**
```flux
from(bucket: "Mad_Team")
  |> range(start: -15m)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "cpu_pct")
  |> map(fn: (r) => ({
      r with
      device: if r.topic == "rbl/sensors/tool" then "MadTOOL"
              else if r.topic == "rbl/sensors/helper" then "MadHelper"
              else if r.topic == "rbl/sensors/guard" then "MadGuard"
              else "Unknown"
    }))
  |> group(columns: ["device"])
```

**Memory Query:**
```flux
from(bucket: "Mad_Team")
  |> range(start: -15m)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "mem_pct")
  |> map(fn: (r) => ({
      r with
      device: if r.topic == "rbl/sensors/tool" then "MadTOOL"
              else if r.topic == "rbl/sensors/helper" then "MadHelper"
              else if r.topic == "rbl/sensors/guard" then "MadGuard"
              else "Unknown"
    }))
  |> group(columns: ["device"])
```

**Disk Query:**
```flux
from(bucket: "Mad_Team")
  |> range(start: -15m)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "disk_pct")
  |> map(fn: (r) => ({
      r with
      device: if r.topic == "rbl/sensors/tool" then "MadTOOL"
              else if r.topic == "rbl/sensors/helper" then "MadHelper"
              else if r.topic == "rbl/sensors/guard" then "MadGuard"
              else "Unknown"
    }))
  |> group(columns: ["device"])
```

**Throttle Query:**
```flux
from(bucket: "Mad_Team")
  |> range(start: -15m)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "throttle")
  |> map(fn: (r) => ({
      r with
      device: if r.topic == "rbl/sensors/tool" then "MadTOOL"
              else if r.topic == "rbl/sensors/helper" then "MadHelper"
              else if r.topic == "rbl/sensors/guard" then "MadGuard"
              else "Unknown"
    }))
  |> group(columns: ["device"])
```

**Voltage Query:**
```flux
from(bucket: "Mad_Team")
  |> range(start: -15m)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "voltage")
  |> map(fn: (r) => ({
      r with
      device: if r.topic == "rbl/sensors/tool" then "MadTOOL"
              else if r.topic == "rbl/sensors/helper" then "MadHelper"
              else if r.topic == "rbl/sensors/guard" then "MadGuard"
              else "Unknown"
    }))
  |> group(columns: ["device"])
```

### Phase 5: Verify (5 min)
1. Check new MQTT data arriving: `docker logs telegraf --tail 50`
2. Open Grafana dashboard
3. Verify legends show: MadTOOL, MadHelper, MadGuard
4. Confirm all 25 panels still present with correct layout
5. Wait 10 minutes for data to populate

---

## ⚡ WHAT STAYS THE SAME (Do NOT Touch)

- ✅ Docker Compose setup
- ✅ InfluxDB database and token
- ✅ All 25 Grafana panels and layouts
- ✅ Speedtest wrapper script
- ✅ Pi-hole stats script
- ✅ Docker metrics collection
- ✅ Ping monitoring
- ✅ Network configuration (mastersurface_hubnet)
- ✅ All container volumes and persistence

---

## 📊 EXPECTED OUTCOME

**Before Fix:**
- Legends: "host=Mad_Hub, topic=rbl/sensors/diag" (all look the same)
- Confusion about MasterTOOL vs MadTOOL
- Can't distinguish between Pis

**After Fix:**
- Legends: "MadTOOL", "MadHelper", "MadGuard" (clear distinction)
- Consistent naming across entire system
- All 25 visuals intact with correct data flowing

**Data Note:** Historical data will still exist under old topics. New data will be under corrected topics. Dashboard shows last 15 minutes by default, so new data will appear within 15 minutes.

---

## 🚨 ROLLBACK PLAN (If Something Goes Wrong)

```bash
# On Mad_Hub
cd ~
tar -xzf BACKUP_JAN2_2026_PRE_NAME_FIX.tar.gz
cp BACKUP_JAN2_2026_PRE_NAME_FIX/telegraf.conf ~/telegraf/
docker restart telegraf

# On each Pi - revert topic names
ssh rebootlabs@192.168.1.222
sudo nano /home/rebootlabs/diag_publisher.py
# Change back to: TOPIC = "rbl/sensors/diag"
sudo systemctl restart diag-publisher
```

---

## ✅ REVIEW CHECKLIST

Before executing, confirm:
- [ ] Backup completed and copied to Quarantine folder
- [ ] Grafana dashboard JSON exported manually
- [ ] SSH access ready to all 3 Pis
- [ ] Understand ONLY topic names change - NO visual changes
- [ ] Ready to update queries in Grafana (copy/paste provided above)

---

## 📝 YOUR CHANGES/NOTES

(Add any corrections or changes here before we execute)

