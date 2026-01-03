# Mad_Hub Name Correction - Progress Report
**Date:** January 2, 2026  
**Status:** Backend Complete - Grafana Queries Pending

---

## ✅ COMPLETED TASKS

### 1. MadTOOL MQTT Topic Updated
- **Location:** 192.168.1.222
- **Changed:** `TOPIC = "rbl/sensors/diag"` → `TOPIC = "rbl/sensors/tool"`
- **File:** `/home/rebootlabs/diag_publisher.py`
- **Service:** Restarted and active

### 2. MadHelper MQTT Topic Verified
- **Location:** 192.168.1.115
- **Status:** Already correct - `TOPIC = "rbl/sensors/helper"`
- **File:** `/home/rebootlabs/diag_publisher.py`
- **Service:** No changes needed

### 3. MadGuard MQTT Topic Updated
- **Location:** 192.168.1.247
- **Changed:** `TOPIC = "rbl/sensors/masterguard"` → `TOPIC = "rbl/sensors/guard"`
- **File:** `/home/rebootlabs/diag_publisher.py`
- **Service:** Restarted successfully

### 4. Telegraf Configuration Updated
- **Location:** Mad_Hub (192.168.1.188)
- **File:** `~/telegraf/telegraf.conf`
- **Changed:**
```toml
# OLD:
topics = ["rbl/+/+"]

# NEW:
topics = [
  "rbl/sensors/tool",
  "rbl/sensors/helper",
  "rbl/sensors/guard"
]
```

### 5. Telegraf Restarted and Verified
- **Command:** `docker restart telegraf`
- **Status:** Running, MQTT connected
- **Log:** `2026-01-03T06:31:42Z I! [inputs.mqtt_consumer] Connected [tcp://mosquitto:1883]`

---

## ⏳ REMAINING TASKS

### 6. Update Grafana Queries (Manual Step Required)
**Action:** Open Grafana → Edit each panel → Update query

**For each panel** (temp, cpu, mem, disk, throttle, voltage), replace query with:

**Temperature:**
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

**CPU:**
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

**Memory:**
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

**Disk:**
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

**Throttle:**
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

**Voltage:**
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

### 7. Verify Dashboard
- [ ] Check all 25 panels still present
- [ ] Verify legends show: MadTOOL, MadHelper, MadGuard
- [ ] Confirm data populating (may take 10-15 min)
- [ ] Ensure layout unchanged

---

## 📦 BACKUP INFORMATION

**Location:** `c:\Users\Nameless\ReBoot Lab Tools&Scripts\Quarentined_Mad_Lab_Mistakes\Quarantine Mess-Grafana\BACKUP_JAN2_2026_PRE_NAME_FIX.tar.gz`

**Contains:**
- docker-compose.yml (original)
- telegraf.conf (pre-change with `topics = ["rbl/+/+"]`)
- pihole_stats.sh
- speedtest_wrapper.sh
- CREDENTIALS.txt (all passwords/tokens)

**Restore Command (if needed):**
```bash
ssh mastersurface@192.168.1.188
cd ~
tar -xzf BACKUP_JAN2_2026_PRE_NAME_FIX.tar.gz
cp BACKUP_JAN2_2026_PRE_NAME_FIX/telegraf.conf ~/telegraf/
docker restart telegraf
```

---

## 🔑 CREDENTIALS

**Grafana:**
- URL: http://192.168.1.188:3000
- Email: rebootlabs26@gmail.com
- Password: Madvi3ws

**InfluxDB:**
- Token: `owI3GftJwbKC45FgqHa5fiAn2DxTuivt_jMHGiH3PWfUfnaac59bhrXY4x9_fOGT0q7y4BQ-9yTTeL4NE13Ihg==`

---

## 📊 NEW MQTT TOPICS (Active)

| Pi | IP | Topic | Status |
|---|---|---|---|
| MadTOOL | 192.168.1.222 | rbl/sensors/tool | ✅ Active |
| MadHelper | 192.168.1.115 | rbl/sensors/helper | ✅ Active |
| MadGuard | 192.168.1.247 | rbl/sensors/guard | ✅ Active |

---

## 📝 NOTES

- Data collection started at ~06:31:42 UTC (Jan 3, 2026)
- Historical data under old topics still exists in InfluxDB
- New data will appear within 10-15 minutes
- All 25 Grafana panels preserved - NO visual changes made
- MQTT parsing errors in logs are pre-existing and unrelated to changes
