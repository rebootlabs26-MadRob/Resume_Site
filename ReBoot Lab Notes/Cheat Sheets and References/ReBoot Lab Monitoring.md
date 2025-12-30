## How Your ReBoot Lab Monitoring Works

**The Big Picture:** Your 3 Pis collect data about themselves → send it to the Surface Hub → Hub stores it → Grafana shows it visually.

---

## Each Component Explained:

### **Docker** (The Container Manager)

**What it is:** Think of Docker like a super-efficient apartment building for software.

**How it works:**

- Each "apartment" (container) has its own app running inside
- Containers share the building's resources (CPU, RAM) but stay isolated
- If one container crashes, others keep running
- Easy to start/stop/rebuild without affecting the whole system

**Why you use it:** Runs Mosquitto, Telegraf, InfluxDB, and Grafana all on one Surface Hub without them interfering with each other.

---

### **Mosquitto** (The Message Broker)

**What it is:** A post office for your devices.

**How it works:**

- Pis "mail" their data (temperature, CPU %, etc.) to specific "addresses" called topics
- Topics look like: `rbl/sensors/diag` (MadTOOL's mailbox)
- Other programs "subscribe" to these mailboxes and get copies of everything sent there
- Real-time delivery - messages arrive instantly

**Your topics:**

- `rbl/sensors/diag` - MadTOOL's data
- `rbl/sensors/helper` - MadHelper's data
- `rbl/sensors/masterguard` - MadGuard's data

---

### **Telegraf** (The Data Collector)

**What it is:** A robot mail carrier that picks up messages and delivers them to storage.

**How it works:**

- Subscribes to ALL your MQTT topics (`rbl/#` = "give me everything under rbl/")
- Receives messages from Mosquitto
- Reformats them into InfluxDB's preferred format
- Ships them to InfluxDB for storage

**Why it's needed:** InfluxDB doesn't speak MQTT directly - Telegraf translates.

---

### **InfluxDB** (The Time-Series Database)

**What it is:** A specialized filing cabinet designed for data that changes over time.

**How it works:**

- Stores every measurement with a timestamp
- Organized into "buckets" (your bucket: `Mad_Team`)
- Optimized for questions like "what was CPU temp at 3pm yesterday?"
- Keeps data efficiently - can store millions of data points

**Your data structure:**

```
Bucket: Mad_Team
  └─ Measurement: mqtt_consumer
      ├─ temp: 39.5°C (from MadTOOL, 3:15:22pm)
      ├─ cpu_pct: 12% (from MadTOOL, 3:15:22pm)
      └─ mem_pct: 35% (from MadHelper, 3:15:23pm)
```

---

### **Grafana** (The Dashboard)

**What it is:** Your visual command center.

**How it works:**

- Connects to InfluxDB
- You create "panels" (graphs, gauges, stats)
- Each panel asks InfluxDB a question: "Show me CPU temp from last hour"
- Updates automatically every 10 seconds (your refresh setting)
- Makes thousands of data points understandable at a glance

---

## How They Work Together (Your Flow):

**Step 1:** MadTOOL's Python script reads its CPU temp (39.5°C)

**Step 2:** Script publishes to Mosquitto:

```
Topic: rbl/sensors/diag
Message: {"temp": 39.5, "cpu_pct": 12, "mem_pct": 35}
```

**Step 3:** Telegraf (subscribed to `rbl/#`) receives the message

**Step 4:** Telegraf reformats and sends to InfluxDB:

```
mqtt_consumer,topic=rbl/sensors/diag temp=39.5 1735513200000000000
```

**Step 5:** InfluxDB stores it in the `Mad_Team` bucket with timestamp

**Step 6:** Grafana queries InfluxDB every 10 seconds:

```
"Give me all temps from last 5 minutes"
```

**Step 7:** Grafana draws the graph showing temp changing over time

---

## Pi-hole (Separate But Related)

**What it is:** A DNS filter that blocks ads/malware at the network level.

**How it works:**

1. Your PC asks: "What's the IP for doubleclick.net?"
2. Request goes to Pi-hole (192.168.1.247)
3. Pi-hole checks its blocklist: "That's an ad tracker!"
4. Pi-hole responds: "0.0.0.0" (blocked)
5. Your browser can't load the ad

**Why it's powerful:** Blocks ads for EVERY device on your network (phones, tablets, TVs) without installing anything on them.

---

## Why This Setup Is Good:

**Resilient:** If Grafana crashes, data still flows to InfluxDB **Scalable:** Add more Pis = just publish to new MQTT topics **Historical:** See what happened yesterday, last week, last month **Real-time:** See issues as they happen **Centralized:** One dashboard for everything