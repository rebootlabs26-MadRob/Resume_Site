Complete Chat Summary - MasterGuard Security Node Setup
Session Overview
Duration: December 22-23, 2025
Goal: Integrate MasterGuard (3rd Raspberry Pi 3B) as network security/VPN node while maintaining compute worker functionality

Starting Point
Existing Infrastructure:
MasterTOOL (@192.168.1.222) - Redis queue manager, primary compute
MasterHelper (@192.168.1.115) - RQ worker
Mad_SPHub/RBL-SurfaceHub (@192.168.1.188) - Ubuntu Surface Pro 3 with monitoring stack
Network: Wi-Fi "OkiosAgape13", Router @192.168.1.1
Major Phases
Phase 1: Initial Networking Crisis (Hours 1-3)
Problem: MasterGuard became unreachable via SSH after WireGuard installation attempt

Root Cause: WireGuard install script created phantom network interface named "MasterGuard"
Symptoms: Duplicate IP addresses (192.168.1.227 and 192.168.1.247), conflicting routes
Critical Error: ip route show revealed interface "MasterGuard" causing routing chaos
User Frustration: Multiple hours lost in circular troubleshooting when I didn't immediately investigate WireGuard interface creation
Resolution: sudo ip link delete MasterGuard - killed the phantom interface
Key Learning: When user says "something is wrong with X," investigate X immediately, not symptoms.

Phase 2: WireGuard VPN Setup (Corrected)
Problem: Original config used hostname as interface name and conflicting IP subnet

Original Config Issues:
Interface name: "MasterGuard" (created network device with hostname)
VPN subnet: 192.168.1.247/24 (same as LAN - massive conflict!)
Proper Configuration:


Interface: wg0 (standard name)VPN Subnet: 10.8.0.0/24 (separate from LAN)Server: 10.8.0.1/24Client: 10.8.0.2/32
Endpoints:

Local (same network): 192.168.1.227:51820
Remote (public): 38.254.219.148:51820
Client Setup: Windows PC (WastedTime) with WireGuard GUI
Note: VPN breaks PhoneLink device discovery (expected behavior when routing traffic)

Phase 3: Pi-hole DNS Setup
Installed: Network-wide ad/DNS filtering

Admin interface: http://192.168.1.227/admin
Password: K33pou5saf3
Router DNS Configuration: GS7 XGS Fiber Gateway (Wyyred ISP)
DHCP DNS Type: Custom Servers
Primary: 192.168.1.227
Secondary: 8.8.8.8
Domain: rebootlabs.local
Phase 4: Security Stack
Suricata IDS/IPS:

Monitoring interface: wlan0
Log: /var/log/suricata/fast.log
Fail2ban:

SSH protection enabled
Ban time: 1 hour
Max retries: 5
Findtime: 10 minutes
Phase 5: Alert System
Discord Webhook Integration:

URL: https://discord.com/api/webhooks/1452960364823318559/...
Sends Fail2ban bans and Suricata IDS alerts
MQTT Alerts:

Topic: rbl/security/alerts
Broker: 192.168.1.188:1883
Service: security-alerts.service monitoring both systems

Phase 6: Grafana Monitoring Discovery
Critical Discovery: Entire monitoring stack was already running in Docker on Surface!

Containers: grafana, influxdb, mosquitto, telegraf, portainer
Ports: Grafana 3000, InfluxDB 8086, Mosquitto 1883
Telegraf already subscribed to rbl/+/+ topics
Issue: Attempted to install duplicate system services before discovering Docker setup
Resolution: Disabled system services, used existing Docker stack

Telegraf Config (Docker):


servers = ["tcp://172.17.0.1:1883"]topics = ["rbl/+/+"]
InfluxDB Bucket: "Mad_Masters/Helpers"

Phase 7: RQ Worker Integration
MasterGuard integrated into compute cluster:

Service: rq-worker.service
Queues: high, default, low
Redis: MasterTOOL-DiagTool0:6379
Final Configuration
MasterGuard Services (All Running)

✅ diag-publisher.service - MQTT metrics to Grafana✅ rq-worker.service - Compute worker✅ security-alerts.service - Discord/MQTT alerts✅ pihole-FTL.service - DNS filtering✅ wg-quick@wg0.service - VPN server✅ suricata.service - IDS/IPS✅ fail2ban.service - SSH protection
Network Configuration
Static IPs (DHCP reserved):

MasterGuard: 192.168.1.227 (also .247 from old config lingering)
VPN interface: 10.8.0.1
DNS Resolution:

Primary: 192.168.1.227 (Pi-hole)
Secondary: 8.8.8.8
Search domain: RBLGuard
IP Forwarding Enabled

net.ipv4.ip_forward=1
Key Files Created/Modified
MasterGuard:

/etc/wireguard/wg0.conf - VPN server config
/etc/wireguard/WastedTime.conf - Client config template
/home/rebootlabs/security_alerts.py - Alert monitor
/home/rebootlabs/diag_publisher.py - Metrics publisher
/etc/fail2ban/jail.local - SSH protection rules
/etc/systemd/system/security-alerts.service
/etc/systemd/system/diag-publisher.service
Windows PC:

WastedTime.conf - VPN client config
Unresolved/Pending Items
LaView Cameras: Located at 192.168.1.174, 192.168.1.175 but not integrated

Port 554 (RTSP) refused
Port 8000 responds with "Happytimesoft" server
Credentials needed for RTSP access
Port Forwarding: WireGuard port 51820/UDP not forwarded on router for remote access

Grafana Dashboard: MasterGuard panels need to be created/cloned with topic filter rbl/sensors/masterguard

Lessons Learned
Listen to user immediately when they identify problem source (WireGuard)
Check for existing infrastructure before installing new services (Docker stack)
Phantom network interfaces can be created by poorly written install scripts
VPN subnet isolation is critical - never overlap with LAN
Router admin password issues - ISP gateways have unique passwords on stickers
Daily Notes - December 22-23, 2025
MasterGuard Setup Commands Reference
Network Diagnostics (The Crisis)

# Identify network issuesip addr showip route showhostname -Iss -tlnp | grep :22# Check SSH statussudo systemctl status sshsudo ss -tlnp | grep :22sudo iptables -L -n | grep 22# Fix duplicate IP issue - DELETE PHANTOM INTERFACEsudo ip link showsudo ip link set MasterGuard downsudo ip link delete MasterGuard# Renew network connectionsudo nmcli con down "OkiosAgape13"sudo nmcli con up "OkiosAgape13"
WireGuard VPN Setup

# Install WireGuardsudo apt updatesudo apt install -y wireguard# Create proper server config (wg0, not hostname!)sudo bash -c 'cat > /etc/wireguard/wg0.conf << EOF[Interface]Address = 10.8.0.1/24ListenPort = 51820PrivateKey = oJJDWyd3czXUp3Xx0IPrv18SDG7t9/J5Pe4+wb7IzUI=PostUp = iptables -I INPUT -p udp --dport 51820 -j ACCEPTPostUp = iptables -I FORWARD -i wlan0 -o wg0 -j ACCEPTPostUp = iptables -I FORWARD -i wg0 -j ACCEPTPostUp = iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADEPostDown = iptables -D INPUT -p udp --dport 51820 -j ACCEPTPostDown = iptables -D FORWARD -i wlan0 -o wg0 -j ACCEPTPostDown = iptables -D FORWARD -i wg0 -j ACCEPTPostDown = iptables -t nat -D POSTROUTING -o wlan0 -j MASQUERADEEOF'sudo chmod 600 /etc/wireguard/wg0.conf# Enable IP forwardingecho "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.confsudo sysctl -p# Start WireGuardsudo systemctl enable wg-quick@wg0sudo systemctl start wg-quick@wg0sudo systemctl status wg-quick@wg0# Verify interfaceip link show wg0sudo wg show wg0
WireGuard Client Config Generation

# Generate client keypairwg genkey | sudo tee /etc/wireguard/WastedTime_private.key | wg pubkey | sudo tee /etc/wireguard/WastedTime_public.key# View keyssudo cat /etc/wireguard/WastedTime_private.keysudo cat /etc/wireguard/WastedTime_public.key# Add peer to serversudo bash -c 'cat >> /etc/wireguard/wg0.conf << EOF[Peer]# WastedTime PCPublicKey = BURjUW7aJgtGTRa5N0gKipnffigkmi73XFP3kTT9LWE=AllowedIPs = 10.8.0.2/32EOF'# Reload WireGuardsudo wg-quick down wg0sudo wg-quick up wg0sudo wg show wg0# Get public IP for remote accesscurl ifconfig.me
Pi-hole Installation

# Install Pi-holecurl -sSL https://install.pi-hole.net | bash# Set/reset admin passwordsudo pihole setpassword# Password: K33pou5saf3# Access admin panel# http://192.168.1.227/admin
Router DNS Configuration
Manual Steps - GS7 XGS Gateway:

Navigate to http://192.168.1.1
DHCP Settings
DHCP DNS Type: Custom Servers
Primary DNS: 192.168.1.227
Secondary DNS: 8.8.8.8
Save and reboot router
Renew DNS on PC:


ipconfig /releaseipconfig /renewipconfig /all | Select-String "DNS Servers"
Suricata IDS/IPS Setup

# Install Suricatasudo apt updatesudo apt install -y suricata suricata-update# Update rulessudo suricata-update# Configure for wlan0sudo sed -i 's/interface: eth0/interface: wlan0/' /etc/suricata/suricata.yaml# Enable and startsudo systemctl enable suricatasudo systemctl start suricatasudo systemctl restart suricata# View alertssudo tail -f /var/log/suricata/fast.log
Fail2ban Setup

# Install Fail2bansudo apt install -y fail2ban# Create local configsudo bash -c 'cat > /etc/fail2ban/jail.local << EOF[DEFAULT]bantime = 1hfindtime = 10mmaxretry = 5[sshd]enabled = trueport = 22logpath = /var/log/auth.logEOF'# Enable and startsudo systemctl enable fail2bansudo systemctl restart fail2ban# Check statussudo fail2ban-client statussudo fail2ban-client status sshd
Security Alerts System

# Install dependenciessudo apt install -y python3-pippip3 install requests paho-mqtt --break-system-packages# Create alert monitor scriptcat > /home/rebootlabs/security_alerts.py << 'EOF'#!/usr/bin/env python3import timeimport jsonimport requestsimport subprocessfrom datetime import datetimeimport paho.mqtt.client as mqttDISCORD_WEBHOOK = "https://discord.com/api/webhooks/1452960364823318559/i2uPgaYkJ9dFtk2t1BxQ2qMeRStoiif952Nubjxdd13Xcb-4_SWZJVhGTwvHMImXSxB8"MQTT_BROKER = "192.168.1.188"MQTT_TOPIC = "rbl/security/alerts"mqtt_client = mqtt.Client()mqtt_client.connect(MQTT_BROKER, 1883, 60)def send_discord(title, description, color=0xFF0000):    data = {        "embeds": [{            "title": f"🚨 {title}",            "description": description,            "color": color,            "timestamp": datetime.utcnow().isoformat()        }]    }    requests.post(DISCORD_WEBHOOK, json=data)def send_mqtt(alert_type, message):    payload = {"type": alert_type, "message": message, "timestamp": time.time()}    mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))last_fail2ban_check = ""while True:    try:        # Check Fail2ban        result = subprocess.run(['sudo', 'fail2ban-client', 'status', 'sshd'],                               capture_output=True, text=True)        if "Currently banned:" in result.stdout:            banned = result.stdout.split("Banned IP list:")[-1].strip()            if banned and banned != last_fail2ban_check and banned != "":                send_discord("Fail2ban: IP Banned", f"**Banned IPs:** {banned}", 0xFFA500)                send_mqtt("fail2ban", f"Banned: {banned}")                last_fail2ban_check = banned                # Check Suricata alerts        result = subprocess.run(['sudo', 'tail', '-n', '50', '/var/log/suricata/fast.log'],                               capture_output=True, text=True)        for line in result.stdout.split('\n'):            if line and "[**]" in line:                send_discord("Suricata IDS Alert", f"```{line[:500]}```", 0xFF0000)                send_mqtt("suricata", line)                time.sleep(2)            except Exception as e:        print(f"Error: {e}")        time.sleep(10)EOFchmod +x /home/rebootlabs/security_alerts.py# Create systemd servicesudo bash -c 'cat > /etc/systemd/system/security-alerts.service << EOF[Unit]Description=Security Alerts MonitorAfter=network.target[Service]Type=simpleUser=rebootlabsExecStart=/usr/bin/python3 /home/rebootlabs/security_alerts.pyRestart=always[Install]WantedBy=multi-user.targetEOF'# Enable and startsudo systemctl daemon-reloadsudo systemctl enable security-alertssudo systemctl start security-alertssudo systemctl status security-alerts
Grafana Monitoring Integration

# Install MQTT dependenciessudo pip3 install paho-mqtt psutil --break-system-packages# Create diagnostics publishercat > /home/rebootlabs/diag_publisher.py << 'EOF'#!/usr/bin/env python3import paho.mqtt.client as mqttimport psutilimport timeimport jsonMQTT_BROKER = "192.168.1.188"MQTT_TOPIC = "rbl/sensors/masterguard"HOSTNAME = "MasterGuard"client = mqtt.Client()client.connect(MQTT_BROKER, 1883, 60)while True:    try:        data = {            "hostname": HOSTNAME,            "cpu_temp": psutil.sensors_temperatures()['cpu_thermal'][0].current if 'cpu_thermal' in psutil.sensors_temperatures() else 0,            "cpu_freq": psutil.cpu_freq().current,            "cpu_percent": psutil.cpu_percent(interval=1),            "memory_percent": psutil.virtual_memory().percent,            "disk_percent": psutil.disk_usage('/').percent,            "uptime": time.time() - psutil.boot_time()        }        client.publish(MQTT_TOPIC, json.dumps(data))    except Exception as e:        print(f"Error: {e}")    time.sleep(10)EOFchmod +x /home/rebootlabs/diag_publisher.py# Create servicesudo bash -c 'cat > /etc/systemd/system/diag-publisher.service << EOF[Unit]Description=Diagnostics PublisherAfter=network.target[Service]Type=simpleUser=rebootlabsExecStart=/usr/bin/python3 /home/rebootlabs/diag_publisher.pyRestart=always[Install]WantedBy=multi-user.targetEOF'# Enable and startsudo systemctl daemon-reloadsudo systemctl enable diag-publishersudo systemctl start diag-publishersudo systemctl status diag-publisher# Verify publishingsudo journalctl -u diag-publisher -n 20
Surface Monitoring Stack (Docker Discovery)

# Check running containersdocker ps# Verify Telegraf MQTT subscriptiondocker exec telegraf cat /etc/telegraf/telegraf.conf | grep -A 10 mqtt# Output should show:# servers = ["tcp://172.17.0.1:1883"]# topics = ["rbl/+/+"]# Disable duplicate system services if installedsudo systemctl stop mosquitto telegraf grafana-server influxdbsudo systemctl disable mosquitto telegraf grafana-server influxdb
Camera Discovery

# Install nmapsudo apt install -y nmap# Scan for camerasnmap -p 554,8000,8080 192.168.1.0/24# Test camera endpointscurl -I http://192.168.1.174:8000curl -I http://192.168.1.175:8000# Test RTSP (requires credentials)ffprobe -rtsp_transport tcp rtsp://admin:password@192.168.1.174:554/stream1
Service Management Commands

# Check all MasterGuard servicessudo systemctl status diag-publisher rq-worker security-alerts pihole-FTL wg-quick@wg0 suricata fail2ban# Restart a servicesudo systemctl restart [service-name]# View logssudo journalctl -u [service-name] -n 50 --no-pagersudo journalctl -u [service-name] -f  # Follow mode# Check network connectivityping 192.168.1.188  # Surfaceping 192.168.1.222  # MasterTOOLping 192.168.1.115  # MasterHelperping 10.8.0.1       # VPN interface
Grafana Query for MasterGuard
Flux Query Template:


from(bucket: "Mad_Masters/Helpers")  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)  |> filter(fn: (r) => r._measurement == "mqtt_consumer")  |> filter(fn: (r) => r.topic == "rbl/sensors/masterguard")  |> filter(fn: (r) => r._field == "cpu_percent")  // or memory_percent, disk_percent, etc.  |> last()
Quick Reference - IP Addresses
Device	IP Address	Purpose
Router	192.168.1.1	Gateway
WastedTime PC	192.168.1.179	Main workstation
Mad_SPHub/Surface	192.168.1.188	Monitoring stack (Docker)
MasterTOOL	192.168.1.222	Redis queue, compute
MasterHelper	192.168.1.115	RQ worker
MasterGuard	192.168.1.227	Security/VPN/worker
Camera 1	192.168.1.174	LaView camera
Camera 2	192.168.1.175	LaView camera
VPN Network	10.8.0.0/24	WireGuard subnet
Critical Passwords/Keys

Pi-hole Admin: K33pou5saf3User: rebootlabs / G3t2w0rkDiscord Webhook: https://discord.com/api/webhooks/1452960364823318559/i2uPgaYkJ9dFtk2t1BxQ2qMeRStoiif952Nubjxdd13Xcb-4_SWZJVhGTwvHMImXSxB8
Future Automation Note