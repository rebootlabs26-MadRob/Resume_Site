# 🎯 Surface 1657 Ultimate Home Lab Master Plan

**Created:** December 16, 2025  
**Device:** Microsoft Surface 1657  
**Purpose:** Command Center for Pi-based Home Lab

---

## 📋 Project List (Selected)

### DIY Security System (Pi-Paired)
| # | Project | Description |
|---|---------|-------------|
| 1 | Security Camera Dashboard | Use Frigate on Pi, Surface as 24/7 wall-mounted monitor |
| 2 | NVR Control Station | Pi handles storage, Surface displays web UI |
| 5 | AI Object Detection NVR | Frigate with Coral TPU on Pi, Surface shows detected objects (person, car, animal) with bounding boxes |

### Network Security & Monitoring
| # | Project | Description |
|---|---------|-------------|
| 1 | Honeypot Command Center | T-Pot on Pi, Surface displays real-time attack map + logs |
| 2 | Packet Sniffer Station | Surface runs Wireshark/NetworkMiner, mirrors traffic from managed switch |
| 3 | Vulnerability Scanner Dashboard | Pi runs OpenVAS or Nessus Essentials, Surface displays scan results |
| 4 | SIEM Home Lab | Wazuh or Security Onion - enterprise-grade security monitoring |
| 11 | Pi-hole Stats Display | Always-on dashboard showing blocked ads/queries |
| 12 | Network Traffic Monitor | ntopng or Wireshark dashboard |
| 13 | Intrusion Detection Display | Pi runs Snort/Suricata, Surface shows alerts |
| 14 | Uptime Kuma Board | Monitor all your services/devices with visual status |
| 15 | Speed Test Logger | Automated tests, Surface shows historical graphs |

### Network Infrastructure
| # | Project | Description |
|---|---------|-------------|
| - | Network-Wide Ad-Block + VPN Gateway | Pi runs Pi-hole + WireGuard, Surface shows blocked domains + VPN status. **YOUR OWN PRIVATE VPN!** |

### Creative / Fun Projects
| # | Project | Description |
|---|---------|-------------|
| 17 | Spotify/Music Visualizer | Always-on album art + visualizations |
| 18 | Weather Station Display | Pi sensors → Surface shows temps, humidity, forecasts |

### Utility / Practical
| # | Project | Description |
|---|---------|-------------|
| 24 | Twitch/YouTube Chat Monitor | Stream chat on second screen |
| 25 | AI Chat Station | AI Team multi-chat as dedicated terminal |

---

## ⚠️ Conflicts & Resolutions

| Conflict | Issue | Resolution |
|----------|-------|------------|
| MotionEye vs Frigate vs ZoneMinder vs Shinobi | All are NVR solutions - pick ONE | **Use Frigate** (best AI detection with Coral) |
| Snort/Suricata vs Wazuh vs Security Onion | Overlapping IDS/SIEM tools | **Use Wazuh + Suricata** (Wazuh integrates Suricata) |
| T-Pot Honeypot | Must be ISOLATED from main network | **Separate Pi on DMZ/VLAN** |
| ntopng vs Grafana ports | Both want port 3000 | Use 3030 for Grafana |

---

## 🏗️ Master Architecture

```
                            ┌─────────────────────────────────────────────────────────┐
                            │              SURFACE 1657 - COMMAND CENTER              │
                            │  ┌─────────────────────────────────────────────────────┐│
                            │  │  Browser Tabs / Kiosk Dashboard                     ││
                            │  │  • Frigate NVR        • Pi-hole Stats               ││
                            │  │  • Wazuh SIEM         • Uptime Kuma                 ││
                            │  │  • ntopng Traffic     • Grafana Metrics             ││
                            │  │  • WireGuard Status   • Weather Station             ││
                            │  │  • Honeypot Map       • AI Team Chat                ││
                            │  └─────────────────────────────────────────────────────┘│
                            └─────────────────────────────────────────────────────────┘
                                                        │
                                                        │ Gigabit Ethernet
                                                        ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    MANAGED SWITCH (PoE)                                        │
│                              Port Mirroring Enabled for Monitoring                             │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
         │              │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   PI #1     │ │   PI #2     │ │   PI #3     │ │   PI #4     │ │  CAMERAS    │ │  HONEYPOT   │
│  MAIN HUB  │ │  SECURITY   │ │  FRIGATE    │ │  SENSORS    │ │   (PoE)     │ │  ISOLATED   │
├─────────────┤ ├─────────────┤ ├─────────────┤ ├─────────────┤ ├─────────────┤ ├─────────────┤
│ • Pi-hole   │ │ • Wazuh     │ │ • Frigate   │ │ • Weather   │ │ • 4-8 cams  │ │ • T-Pot     │
│ • WireGuard │ │ • Suricata  │ │ • Coral TPU │ │   sensors   │ │ • RTSP      │ │ • Own VLAN  │
│ • Uptime    │ │ • ntopng    │ │ • 2TB NVMe  │ │ • Temp/     │ │   streams   │ │ • Internet  │
│   Kuma      │ │ • Speedtest │ │             │ │   Humidity  │ │             │ │   facing    │
│ • Grafana   │ │   Tracker   │ │             │ │             │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
     Pi 4          Pi 4 8GB        Pi 5 8GB        Pi Zero 2W       Reolink        Pi 4 (DMZ)
```

---

## 📦 Hardware Shopping List

### Required Raspberry Pis
| Device | Purpose | Why This One | Est. Cost |
|--------|---------|--------------|-----------|
| **Pi 4 4GB** | Main Hub (Pi-hole, WireGuard, Uptime Kuma) | Low resource needs | $55 |
| **Pi 4 8GB** | Security Stack (Wazuh, Suricata, ntopng) | Memory hungry apps | $75 |
| **Pi 5 8GB** | Frigate NVR + Coral TPU | Needs processing power | $80 |
| **Pi Zero 2W** | Weather sensors | Cheap, low power | $15 |
| **Pi 4 4GB** | Honeypot (ISOLATED) | Separate from main network | $55 |

### Storage & Accessories
| Item | Purpose | Est. Cost |
|------|---------|-----------|
| Google Coral USB TPU | AI object detection | $60 |
| 2TB NVMe + USB 3.0 Enclosure | NVR recordings | $120 |
| 256GB SD Cards (x5) | Pi boot drives | $75 |
| 8-Port Managed PoE Switch | Power cams + port mirror | $80 |
| UPS Battery Backup | Keep running during outages | $50 |

### Cameras
| Item | Qty | Est. Cost |
|------|-----|-----------|
| Reolink RLC-510A (PoE, 5MP) | 4 | $160 |
| OR Amcrest IP5M-T1179EW | 4 | $140 |

### Weather Station Sensors
| Item | Est. Cost |
|------|-----------|
| BME280 (Temp/Humidity/Pressure) | $8 |
| Rain Gauge Sensor | $15 |
| Anemometer (Wind) | $20 |

### **TOTAL ESTIMATE: $800-1000**
*(Can be phased over time!)*

---

## 🗓️ Phased Implementation Plan

### **Phase 1: Foundation (Week 1-2)**
**PI #1 - MAIN HUB**
- [ ] Pi-hole (ad blocking + DNS)
- [ ] WireGuard VPN (your private VPN!)
- [ ] Uptime Kuma (service monitoring)
- [ ] Grafana + Prometheus (metrics dashboard)

**Surface displays:** Pi-hole admin + Uptime Kuma + Grafana

---

### **Phase 2: Security Monitoring (Week 3-4)**
**PI #2 - SECURITY STACK**
- [ ] Wazuh Agent Manager (SIEM)
- [ ] Suricata IDS (intrusion detection)
- [ ] ntopng (network traffic analysis)
- [ ] Speedtest Tracker (bandwidth logging)

**Surface displays:** Wazuh dashboard + ntopng + alerts

---

### **Phase 3: Camera System (Week 5-6)**
**PI #3 - FRIGATE NVR**
- [ ] Frigate with Coral TPU
- [ ] 2TB NVMe storage
- [ ] 4+ PoE cameras
- [ ] AI detection (person, car, animal)
- [ ] Telegram/Pushover alerts

**Surface displays:** Frigate live view + detection events

---

### **Phase 4: Sensors & Fun (Week 7-8)**
**PI #4 - WEATHER + EXTRAS**
- [ ] Weather station sensors
- [ ] Data to InfluxDB → Grafana
- [ ] Spotify visualizer
- [ ] AI Team Chat terminal

**Surface displays:** Weather dashboard + Spotify Now Playing

---

### **Phase 5: Advanced Security (Week 9-10)**
**PI #5 - HONEYPOT (ISOLATED VLAN)**
- [ ] T-Pot honeypot suite
- [ ] Attack map visualization
- [ ] Completely isolated from main network
- [ ] ⚠️ Internet-facing (use carefully!)

**Surface displays:** Real-time attack map + geo visualization

---

## 🖥️ Surface Dashboard Layout

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        REBOOT LABS COMMAND CENTER                          │
├──────────────────────────────┬─────────────────────────────────────────────┤
│                              │  ┌─────────────────┐ ┌─────────────────┐   │
│    FRIGATE CAMERA GRID       │  │   PI-HOLE       │ │  UPTIME KUMA    │   │
│    ┌─────┐ ┌─────┐          │  │   Blocked: 24k  │ │  ✓ All Systems  │   │
│    │ CAM1│ │ CAM2│          │  │   Queries: 89k  │ │    Online       │   │
│    └─────┘ └─────┘          │  └─────────────────┘ └─────────────────┘   │
│    ┌─────┐ ┌─────┐          │  ┌─────────────────┐ ┌─────────────────┐   │
│    │ CAM3│ │ CAM4│          │  │   WEATHER       │ │  VPN STATUS     │   │
│    └─────┘ └─────┘          │  │   72°F  45%     │ │  ✓ Connected    │   │
│                              │  │   ☀️ Sunny      │ │  3 clients      │   │
├──────────────────────────────┤  └─────────────────┘ └─────────────────┘   │
│     WAZUH SECURITY EVENTS    ├─────────────────────────────────────────────┤
│  ⚠️ SSH login attempt (3)    │         NETWORK TRAFFIC (ntopng)           │
│  ✓ Suricata: No threats     │    ▂▃▅▇█▇▅▃▂▁▂▃▅▇█▇▅▃▂▁▂▃▅▇                │
│  ⚠️ New device detected      │    Current: 45 Mbps ↓  12 Mbps ↑           │
└──────────────────────────────┴─────────────────────────────────────────────┘
```

---

## ✅ Port Reference

| Service | Port | Host Pi |
|---------|------|---------|
| Pi-hole Web | 80 | Pi #1 |
| Pi-hole DNS | 53 | Pi #1 |
| WireGuard | 51820 | Pi #1 |
| Uptime Kuma | 3001 | Pi #1 |
| Grafana | 3030 | Pi #1 |
| Prometheus | 9090 | Pi #1 |
| Wazuh Dashboard | 5601 | Pi #2 |
| Wazuh API | 55000 | Pi #2 |
| ntopng | 3000 | Pi #2 |
| Frigate Web | 5000 | Pi #3 |
| Frigate RTSP | 8554 | Pi #3 |

---

## 🔗 Useful Links

- **Frigate:** https://frigate.video/
- **Pi-hole:** https://pi-hole.net/
- **WireGuard:** https://www.wireguard.com/
- **Wazuh:** https://wazuh.com/
- **Uptime Kuma:** https://github.com/louislam/uptime-kuma
- **T-Pot Honeypot:** https://github.com/telekom-security/tpotce
- **ntopng:** https://www.ntop.org/
- **Google Coral:** https://coral.ai/

---

## 📝 Notes

- T-Pot MUST be on isolated VLAN - never expose main network
- Coral TPU dramatically improves Frigate detection speed
- WireGuard is simpler and faster than OpenVPN
- All dashboards accessible via Surface browser tabs
- Consider Homepage (https://gethomepage.dev/) for unified dashboard

---

*Last Updated: December 16, 2025*
