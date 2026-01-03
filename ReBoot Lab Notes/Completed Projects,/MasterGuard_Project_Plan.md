# MasterGuard Project Plan

**ReBoot Labs Security Node**  
**Created:** December 17, 2025  
**Status:** Planned — Ready to Start

---

## Overview

**MasterGuard** is the 3rd Raspberry Pi joining the MasterTOOL/MasterHelper cluster.

**Primary Role:** Network security, VPN, and home security monitoring  
**Secondary Role:** Assist with compute jobs when idle

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MasterGuard                               │
│                    (Security + VPN Node)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  WireGuard   │  │   Suricata   │  │    Pi-hole           │   │
│  │  VPN Server  │  │   IDS/IPS    │  │  (DNS filtering)     │   │
│  │  + Client    │  │              │  │                      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  Fail2ban    │  │  LaView Cam  │  │   Alert System       │   │
│  │  (Intrusion) │  │  Integration │  │  (Telegram/Email)    │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              RQ Worker (helps MasterTOOL)                │   │
│  │         Processes jobs when security load is low         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
      MasterTOOL     MasterHelper    RBL-SurfaceHub
       (Redis)        (Worker)        (Grafana)
```

---

## Hardware

- Raspberry Pi 3B
- SD card (16GB+)
- Same Wi-Fi network as other Pis

---

## Components to Install

| Component | Purpose | Priority |
|-----------|---------|----------|
| **WireGuard Server** | Remote access INTO home network | High |
| **WireGuard Client** | Route outbound through VPN provider (invisibility) | High |
| **Pi-hole** | DNS-level ad/tracker/malware blocking | High |
| **Suricata** | Full IDS/IPS — detects/blocks intrusions | High |
| **Fail2ban** | Auto-ban IPs after failed logins | Medium |
| **LaView Integration** | Camera monitoring, motion alerts | Medium |
| **Alert System** | Telegram/Email notifications | Medium |
| **RQ Worker** | Help process MasterTOOL jobs when idle | High |

---

## User Preferences (Captured)

| Question | Answer |
|----------|--------|
| VPN Purpose | BOTH — remote access in + privacy tunnel out |
| Security Level | Advanced (full IDS/IPS) |
| Home Security | LaView cameras + software monitoring/alerts |
| Hostname | MasterGuard |

---

## To Determine Before Starting

- [ ] VPN provider for outbound privacy (NordVPN, Mullvad, ProtonVPN, etc.)
- [ ] LaView camera connection method (cloud app, local IP, RTSP?)
- [ ] LaView camera IPs (if local)
- [ ] Alert preference (Telegram recommended, Email, or both)
- [ ] Static or dynamic home IP (for WireGuard remote access)

---

## Implementation Phases

### Phase 1: Basic Setup (Session 1)
- [ ] Flash Pi with Raspberry Pi OS Lite
- [ ] Set hostname: `MasterGuard`
- [ ] Set username: `rebootlabs`
- [ ] Connect to Wi-Fi
- [ ] Update system
- [ ] Add to /etc/hosts on all Pis
- [ ] Set up Python venv
- [ ] Install RQ worker (connect to MasterTOOL Redis)
- [ ] Set up diag-publisher (Grafana monitoring)

### Phase 2: DNS Security (Session 2)
- [ ] Install Pi-hole
- [ ] Configure as network DNS
- [ ] Add custom blocklists
- [ ] Test ad/tracker blocking

### Phase 3: VPN Setup (Session 3)
- [ ] Install WireGuard
- [ ] Configure VPN server (remote access in)
- [ ] Configure VPN client (privacy tunnel out)
- [ ] Set up kill switch
- [ ] Test invisibility

### Phase 4: Intrusion Detection (Session 4)
- [ ] Install Suricata IDS/IPS
- [ ] Configure rules
- [ ] Install Fail2ban
- [ ] Set up SSH protection
- [ ] Configure alerts

### Phase 5: Camera Integration (Session 5)
- [ ] Discover LaView camera IPs/streams
- [ ] Set up motion detection
- [ ] Configure recording (if desired)
- [ ] Set up alerts for motion events

### Phase 6: Alert System (Session 6)
- [ ] Set up Telegram bot (recommended)
- [ ] Configure alert triggers
- [ ] Test notifications
- [ ] Integrate with Grafana

---

## Network Reference (Updated)

| Device | Hostname | IP (example) | Role |
|--------|----------|--------------|------|
| Pi 1 | MasterTOOL-DiagTool0 | 192.168.1.222 | Controller/Redis |
| Pi 2 | MasterHelper | 192.168.1.115 | Compute Worker |
| Pi 3 | MasterGuard | TBD | Security + Worker |
| Surface | RBL-SurfaceHub | 192.168.1.188 | Monitoring Hub |

---

## Files Needed on MasterGuard

Same structure as MasterHelper:
```
/home/rebootlabs/
├── diag_publisher.py          # Grafana metrics
└── mastertool/
    ├── venv/                   # Python virtual environment
    └── queue/
        └── tasks.py            # Same as other Pis
```

Plus security-specific configs:
```
/etc/wireguard/
├── wg0.conf                    # VPN server config
└── wg-client.conf              # VPN client (privacy)

/etc/pihole/
└── (Pi-hole configs)

/etc/suricata/
└── suricata.yaml               # IDS/IPS config

/etc/fail2ban/
└── jail.local                  # Ban rules
```

---

## Quick Start Command (When Ready)

Flash the Pi, then SSH in and run:
```bash
# Will be provided when we start
```

---

**Ready to start when you are!**
