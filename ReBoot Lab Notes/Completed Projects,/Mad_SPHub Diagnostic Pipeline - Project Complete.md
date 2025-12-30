**Date:** December 17, 2025
**Status:** ✅ COMPLETE

---

## System Architecture

```
┌─────────────────┐     MQTT      ┌─────────────────────────────────────┐
│ MasterTOOL      │──────────────▶│          Mad_SPHub (Surface)        │
│ DiagTool0       │               │                                     │
│ (Raspberry Pi)  │               │  ┌───────────┐    ┌──────────────┐  │
└─────────────────┘               │  │ Mosquitto │───▶│   Telegraf   │  │
                                  │  │  (MQTT)   │    │              │  │
┌─────────────────┐               │  └───────────┘    └──────┬───────┘  │
│ MasterHelper    │──────────────▶│                          │          │
│ (Raspberry Pi)  │               │                          ▼          │
└─────────────────┘               │                   ┌──────────────┐  │
                                  │                   │   InfluxDB   │  │
                                  │                   │   (Database) │  │
                                  │                   └──────┬───────┘  │
                                  │                          │          │
                                  │                          ▼          │
                                  │                   ┌──────────────┐  │
                                  │                   │   Grafana    │  │
                                  │                   │  (Dashboard) │  │
                                  │                   └──────────────┘  │
                                  └─────────────────────────────────────┘
```

---

## Hostnames (Zero IP Policy)

| Device | Hostname | Role |
|--------|----------|------|
| Surface Pro 3 | RBL-SurfaceHub | Hub/Server |
| Raspberry Pi | MasterTOOL-DiagTool0 | Diagnostic Node |
| Raspberry Pi | MasterHelper | Diagnostic Node |

---

## Docker Containers on Mad_SPHub

| Container | Port | Purpose |
|-----------|------|---------|
| influxdb | 8086 | Time-series database |
| grafana | 3000 | Dashboard visualization |
| telegraf | - | MQTT → InfluxDB pipeline |
| mosquitto | 1883 | MQTT broker |
| portainer | 9000/9443 | Container management |

---

## InfluxDB Configuration

- **Organization:** RBL_SPHub
- **Bucket:** Mad_Masters/Helpers
- **Token:** `iMdFFwa1INU555QXnSGtWjay74bpEqHPHA7fB5dDWr6prRlIA9fuA_N5zFAems8lDdPcUkw-d_-7twV31R5d6A==`

---

## Telegraf Config

**Location:** `/home/mastersurface/telegraf/telegraf.conf`

```toml
[agent]
  interval = "10s"
  round_interval = true
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  flush_interval = "10s"

[[outputs.influxdb_v2]]
  urls = ["http://172.17.0.1:8086"]
  token = "iMdFFwa1INU555QXnSGtWjay74bpEqHPHA7fB5dDWr6prRlIA9fuA_N5zFAems8lDdPcUkw-d_-7twV31R5d6A=="
  organization = "RBL_SPHub"
  bucket = "Mad_Masters/Helpers"

[[inputs.mqtt_consumer]]
  servers = ["tcp://172.17.0.1:1883"]
  topics = ["rbl/+/+"]
  qos = 0
  client_id = "telegraf-hub"
  data_format = "json"
  topic_tag = "topic"
  json_string_fields = ["status"]
```

---

## Mosquitto Config

**Location:** `/home/mastersurface/mosquitto/config/mosquitto.conf`

```
listener 1883
allow_anonymous true
```

---

## Pi Diagnostic Script

**Location on each Pi:** `/home/rebootlabs/diag_publisher.py`

**Service:** `diag-publisher.service`

**Metrics Published:**
| Field | Description | Unit |
|-------|-------------|------|
| temp | CPU Temperature | °C |
| freq | CPU Frequency | MHz |
| cpu_pct | CPU Usage | % |
| mem_used | Memory Used | MB |
| mem_total | Memory Total | MB |
| mem_pct | Memory Usage | % |
| swap | Swap Used | MB |
| disk_used | Disk Used | GB |
| disk_total | Disk Total | GB |
| disk_pct | Disk Usage | % |
| uptime_hrs | Uptime | hours |
| throttle | Throttle Status | 0=OK |
| voltage | Core Voltage | V |

**MQTT Topics:**
- MasterTOOL: `rbl/sensors/diag`
- MasterHelper: `rbl/sensors/helper`

---

## Service Management

**On Pis:**
```bash
# Check status
sudo systemctl status diag-publisher

# Restart
sudo systemctl restart diag-publisher

# View logs
sudo journalctl -u diag-publisher -n 20
```

**On Mad_SPHub:**
```bash
# Check all containers
docker ps

# Restart a container
docker restart telegraf

# View container logs
docker logs telegraf --tail 50
```

---

## Grafana Access

**URL:** `http://localhost:3000` (on Surface)

**Kiosk Mode:**
```bash
firefox --kiosk "http://localhost:3000/d/DASHBOARD_ID"
```

**Flux Query Template:**
```flux
from(bucket: "Mad_Masters/Helpers")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "mqtt_consumer")
  |> filter(fn: (r) => r.topic == "rbl/sensors/diag")
  |> last()
```

---

## Hosts File Entries (on Pis)

```
192.168.1.188 RBL-SurfaceHub RBL-SurfaceHub.home.local Mad_SPHub
```

---

## Troubleshooting

**Telegraf crashing:**
```bash
docker logs telegraf --tail 50
```

**No data in Grafana:**
1. Check time range (Last 15 minutes)
2. Verify Pi service: `sudo systemctl status diag-publisher`
3. Test MQTT: `docker exec mosquitto mosquitto_pub -t rbl/test/temp -m '{"temp": 42.5}'`

**Query InfluxDB directly:**
```bash
docker exec influxdb influx query --org RBL_SPHub --token "TOKEN" 'from(bucket: "Mad_Masters/Helpers") |> range(start: -5m) |> limit(n: 10)'
```

---

## Project Identity

- **Project:** ReBoot Labs (RBL)
- **Hub Hostname:** RBL-SurfaceHub
- **Organization:** RBL_SPHub
- **Bucket:** Mad_TOOL/Helper

---

**Completed:** December 17, 2025

*"I can do all things through Christ who strengthens me." - Philippians 4:13 NKJV*