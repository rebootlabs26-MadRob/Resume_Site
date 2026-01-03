#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBoot Lab - DiagTool (final single-file)
Layout:
 Row1: System (full width)
 Row2: CPU (full width)
 Row3: GPU (full width)
 Right column (stacked): Voltage, Network, Storage
 Row4: POST / ERROR LOG (full width, larger)
 Bottom: Save/Export/Error/Print small buttons

Polling: 2 seconds (safe for Pi 3)
Dependencies: psutil
Optional: PIL (Pillow) for skull watermark
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import psutil
import platform
import subprocess
import shutil
import re
import os
import time
import datetime
import json
import logging
import socket
import sys

# ---------------- Config ----------------
POLL_INTERVAL = 2.0  # seconds (Pi 3 recommended)
LOG_FILE = "diagtool.log"
REPORTS_DIR = "reports"
SKULL_IMAGE = "skull.png"  # optional watermark
FULLSCREEN_ON_START = True

# Theme (ReBoot Lab)
BG = "#05060a"           # near black background
CARD_BG = "#0b0c10"      # card background
HEADER = "#9c27b0"       # Joker Purple for headers
ACCENT = "#0b3bff"       # Royal Blue accents
NEON = "#39ff14"         # Neon Green text
ALERT = "#ff3b3b"        # Small red highlights
FG = "#e6eef6"           # foreground text

# ensure reports dir
os.makedirs(REPORTS_DIR, exist_ok=True)

# logging
logger = logging.getLogger("DiagTool")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(fh)

# ---------------- Shared state ----------------
shared_lock = threading.Lock()
shared = {
    "system": {},
    "cpu": {},
    "gpu": {},
    "ram": {},
    "storage": {},
    "network": {},
    "sensors": {},
    "post": {"latest": "N/A", "history": []},
    "errors": [],
    "last_update": None
}
stop_event = threading.Event()

# ---------------- Helper functions ----------------
def now_ts():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def safe_cmd(cmd, timeout=4):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, shell=True, timeout=timeout)
        return out.decode(errors="ignore")
    except Exception as e:
        logger.debug(f"safe_cmd fail: {cmd} -> {e}")
        return ""

def which(cmd):
    return shutil.which(cmd) is not None

def human_bytes(n):
    try:
        n = float(n)
    except Exception:
        return "N/A"
    units = ["B","KB","MB","GB","TB"]
    i=0
    while n>=1024 and i<len(units)-1:
        n/=1024.0; i+=1
    return f"{n:.1f} {units[i]}"

# ---------------- System / Hardware readers (best-effort) ----------------
def get_system_info():
    try:
        s = {}
        s['platform'] = platform.system()
        s['platform_release'] = platform.release()
        s['hostname'] = socket.gethostname()
        s['ip'] = next((x for x in socket.gethostbyname_ex(socket.gethostname())[2] if not x.startswith("127.")), "N/A")
        s['processor'] = platform.processor() or "N/A"
        s['python_version'] = platform.python_version()
        # distro / model / serial
        if s['platform'] == "Linux":
            s['os_release'] = (safe_cmd("cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'=' -f2").strip().strip('"') or "N/A")
            s['model'] = safe_cmd("cat /sys/class/dmi/id/product_name 2>/dev/null").strip() or "N/A"
            s['serial'] = safe_cmd("cat /sys/class/dmi/id/product_serial 2>/dev/null").strip() or "N/A"
            # uptime
            s['uptime'] = safe_cmd("awk '{print int($1/3600)\"h \"int(($1%3600)/60)\"m\"}' /proc/uptime").strip() or "N/A"
        elif s['platform'] == "Windows":
            s['os_release'] = platform.platform()
            s['model'] = safe_cmd("wmic computersystem get model 2>nul").strip().splitlines()[-1] if which("wmic") else "N/A"
            s['serial'] = safe_cmd("wmic bios get serialnumber 2>nul").strip().splitlines()[-1] if which("wmic") else "N/A"
            s['uptime'] = "N/A"
        else:
            s['os_release'] = platform.platform()
            s['model'] = "N/A"
            s['serial'] = "N/A"
            s['uptime'] = "N/A"
        return s
    except Exception:
        logger.exception("get_system_info")
        return {}

def get_cpu_info():
    try:
        c = {}
        c['logical'] = psutil.cpu_count(logical=True)
        c['physical'] = psutil.cpu_count(logical=False)
        c['load'] = psutil.cpu_percent(interval=None)
        freq = psutil.cpu_freq()
        if freq:
            c['min_mhz'] = round(freq.min,1)
            c['current_mhz'] = round(freq.current,1)
            c['max_mhz'] = round(freq.max,1)
        else:
            c['min_mhz']=c['current_mhz']=c['max_mhz']="N/A"
        # model name
        c['model'] = platform.processor() or safe_cmd("lscpu | grep 'Model name' | cut -d: -f2").strip() or "N/A"
        # caches
        lscpu = safe_cmd("lscpu")
        m = re.search(r"L1d cache:\s*(.+)", lscpu); c['l1'] = m.group(1).strip() if m else "N/A"
        m = re.search(r"L2 cache:\s*(.+)", lscpu); c['l2'] = m.group(1).strip() if m else "N/A"
        m = re.search(r"L3 cache:\s*(.+)", lscpu); c['l3'] = m.group(1).strip() if m else "N/A"
        # temps
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # pick a likely CPU sensor name
                for k,arr in temps.items():
                    if arr:
                        c['temp'] = round(arr[0].current,1)
                        break
                else:
                    c['temp'] = "N/A"
            else:
                c['temp'] = "N/A"
        except Exception:
            c['temp'] = "N/A"
        # voltage placeholder
        c['voltage'] = "N/A"
        return c
    except Exception:
        logger.exception("get_cpu_info")
        return {}

def get_gpu_info():
    g = {}
    try:
        # NVIDIA via nvidia-smi
        if which("nvidia-smi"):
            out = safe_cmd("nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,clocks.gr,clocks.mem,temperature.gpu,power.draw --format=csv,noheader,nounits")
            if out:
                first = out.splitlines()[0]
                cols = [c.strip() for c in first.split(",")]
                g['model'] = cols[0] if len(cols)>0 else "NVIDIA"
                g['driver'] = cols[1] if len(cols)>1 else "N/A"
                g['vram_total'] = (cols[2] + " MB") if len(cols)>2 else "N/A"
                g['vram_used'] = (cols[3] + " MB") if len(cols)>3 else "N/A"
                g['clock_core'] = cols[4] if len(cols)>4 else "N/A"
                g['clock_mem'] = cols[5] if len(cols)>5 else "N/A"
                g['temp'] = cols[6] if len(cols)>6 else "N/A"
                g['power'] = cols[7] if len(cols)>7 else "N/A"
            else:
                g['model'] = "NVIDIA (no output)"
        else:
            # Linux lspci or Windows wmic
            if platform.system()=="Linux" and which("lspci"):
                out = safe_cmd("lspci -nn | grep -E 'VGA|3D' -m1")
                g['model'] = out.strip() or "N/A"
            elif platform.system()=="Windows" and which("wmic"):
                out = safe_cmd("wmic path win32_videocontroller get name")
                g['model'] = out.strip().splitlines()[-1] if out else "N/A"
            else:
                g['model'] = "N/A"
            # defaults
            g.setdefault('driver',"N/A"); g.setdefault('vram_total',"N/A")
            g.setdefault('vram_used',"N/A"); g.setdefault('clock_core',"N/A")
            g.setdefault('clock_mem',"N/A"); g.setdefault('temp',"N/A")
            g.setdefault('power',"N/A")
        return g
    except Exception:
        logger.exception("get_gpu_info")
        return {"model":"N/A"}

def get_ram_info():
    try:
        r = {}
        vm = psutil.virtual_memory()
        r['total'] = human_bytes(vm.total)
        r['available'] = human_bytes(vm.available)
        r['used'] = human_bytes(vm.used)
        r['percent'] = f"{vm.percent} %"
        # swap
        sv = psutil.swap_memory()
        r['swap_total'] = human_bytes(sv.total)
        r['swap_used'] = human_bytes(sv.used)
        # dmidecode info if present
        r['manufacturer'] = "N/A"
        r['type'] = "N/A"
        r['slots'] = []
        if which("dmidecode"):
            out = safe_cmd("sudo dmidecode -t memory")
            parts = out.split("Memory Device")
            slots=[]
            for dev in parts[1:]:
                slot={}
                m = re.search(r"Manufacturer:\s*(.+)", dev); slot['manufacturer']=m.group(1).strip() if m else "N/A"
                m = re.search(r"Part Number:\s*(.+)", dev); slot['part']=m.group(1).strip() if m else "N/A"
                m = re.search(r"Speed:\s*(\d+)\s*MHz", dev); slot['speed']=(m.group(1)+" MHz") if m else "N/A"
                m = re.search(r"Type:\s*(.+)", dev); slot['type']=m.group(1).strip() if m else "N/A"
                m = re.search(r"Size:\s*(.+)", dev); slot['size']=m.group(1).strip() if m else "N/A"
                slots.append(slot)
            if slots:
                r['slots']=slots
                r['manufacturer']=slots[0].get('manufacturer',"N/A")
                r['type']=slots[0].get('type',"N/A")
        return r
    except Exception:
        logger.exception("get_ram_info")
        return {}

def get_storage_info():
    try:
        s = {}
        parts = psutil.disk_partitions(all=False)
        drives=[]
        for p in parts:
            try:
                u = psutil.disk_usage(p.mountpoint)
                drives.append({"device":p.device,"mount":p.mountpoint,"fstype":p.fstype,"total":human_bytes(u.total),"used":human_bytes(u.used),"free":human_bytes(u.free),"percent":f"{u.percent} %"})
            except Exception:
                drives.append({"device":p.device,"mount":p.mountpoint,"fstype":p.fstype,"total":"N/A","used":"N/A","free":"N/A","percent":"N/A"})
        s['drives']=drives
        s['smart']=[]
        if which("smartctl"):
            # best-effort list disks
            devs = safe_cmd("lsblk -ndo NAME,TYPE | awk '$2==\"disk\"{print $1}'").splitlines()
            for d in devs:
                dev = d.strip()
                if dev:
                    out = safe_cmd(f"sudo smartctl -H /dev/{dev}")
                    health = "N/A"
                    if "PASSED" in out:
                        health = "PASSED"
                    elif out.strip():
                        health = out.strip().splitlines()[0]
                    s['smart'].append({"device":f"/dev/{dev}","health":health})
        return s
    except Exception:
        logger.exception("get_storage_info")
        return {}

def get_network_info():
    try:
        n={}
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        nif={}
        for k,v in addrs.items():
            if k.lower().startswith("lo"): continue
            ip="N/A"; mac="N/A"
            for e in v:
                if getattr(e,'family',None)==socket.AF_INET:
                    ip=e.address
                try:
                    if e.family == psutil.AF_LINK:
                        mac=e.address
                except Exception:
                    if hasattr(e, "address") and ":" in e.address:
                        mac = e.address
            stat = stats.get(k)
            nif[k]={"ip":ip or "N/A","mac":mac or "N/A","isup":stat.isup if stat else "N/A","speed":f"{stat.speed}MB/s" if stat and stat.speed else "N/A"}
        n['interfaces']=nif
        counters = psutil.net_io_counters(pernic=False)
        n['sent']=human_bytes(counters.bytes_sent)
        n['recv']=human_bytes(counters.bytes_recv)
        return n
    except Exception:
        logger.exception("get_network_info")
        return {}

def get_sensors_and_volts():
    try:
        s={}
        # temps
        try:
            temps = psutil.sensors_temperatures()
            s['temps'] = {}
            if temps:
                for k,arr in temps.items():
                    if arr:
                        s['temps'][k] = round(arr[0].current,1)
        except Exception:
            s['temps'] = {}
        # voltages from sensors (lm-sensors) if present
        if which("sensors"):
            out = safe_cmd("sensors")
            # parse simple rails
            def match(p):
                m = re.search(p, out, re.IGNORECASE)
                return m.group(1).strip() if m else None
            v12 = match(r"12V.*?([\d\.]+)"); v5 = match(r"5V.*?([\d\.]+)"); v33 = match(r"3\.3V.*?([\d\.]+)")
            s['12v'] = (v12+" V") if v12 else "N/A"
            s['5v'] = (v5+" V") if v5 else "N/A"
            s['3v3'] = (v33+" V") if v33 else "N/A"
        else:
            # try vcgencmd on Pi
            if which("vcgencmd"):
                t = safe_cmd("vcgencmd measure_temp")
                vcore = safe_cmd("vcgencmd measure_volts core")
                s['3v3'] = vcore.strip().replace("volt=","") if vcore else "N/A"
                m = re.search(r"temp=([\d\.]+)'C", t)
                if m: s.setdefault('temps', {})['cpu']=float(m.group(1))
                s.setdefault('12v','N/A'); s.setdefault('5v','N/A')
            else:
                s['12v']="N/A"; s['5v']="N/A"; s['3v3']="N/A"
        return s
    except Exception:
        logger.exception("get_sensors_and_volts")
        return {}

# ---------------- POST / OS error scanning ----------------
def get_post_and_logs():
    p={"latest":"N/A","history":[]}
    try:
        if platform.system()=="Linux":
            dmesg = safe_cmd("dmesg --level=err,warn | tail -n 200")
            p['history'] = [l for l in dmesg.splitlines() if l.strip()]
            p['latest'] = p['history'][0] if p['history'] else "N/A"
        elif platform.system()=="Windows":
            out = safe_cmd('wevtutil qe System /rd:true /f:text /c:100')
            p['history'] = [l for l in out.splitlines() if l.strip()]
            p['latest'] = p['history'][0] if p['history'] else "N/A"
        else:
            out = safe_cmd("dmesg | tail -n 200")
            p['history'] = [l for l in out.splitlines() if l.strip()]
            p['latest'] = p['history'][0] if p['history'] else "N/A"
    except Exception:
        logger.exception("get_post_and_logs")
    return p

def scan_os_errors():
    errs=[]
    try:
        if platform.system()=="Linux":
            out = safe_cmd("dmesg --level=err,warn | tail -n 200")
            for l in out.splitlines():
                if l.strip(): errs.append({"source":"dmesg","msg":l.strip()})
            if which("journalctl"):
                out = safe_cmd("journalctl -p 3 -n 200 --no-pager")
                for l in out.splitlines():
                    if l.strip(): errs.append({"source":"journalctl","msg":l.strip()})
        elif platform.system()=="Windows":
            out = safe_cmd('wevtutil qe System /q:"*[System[(Level=2 or Level=3)]]" /f:text /c:200')
            for l in out.splitlines():
                if l.strip(): errs.append({"source":"WindowsEvent","msg":l.strip()})
        elif platform.system()=="Darwin":
            out = safe_cmd("log show --predicate 'eventType == error' --last 1d --info --style syslog 2>/dev/null | tail -n 200")
            for l in out.splitlines():
                if l.strip(): errs.append({"source":"macOS","msg":l.strip()})
    except Exception:
        logger.exception("scan_os_errors")
    return errs

# ---------------- Polling worker ----------------
def poller():
    logger.info("Starting poller thread")
    while not stop_event.is_set():
        try:
            with shared_lock:
                shared['system'] = get_system_info()
                shared['cpu'] = get_cpu_info()
                shared['gpu'] = get_gpu_info()
                shared['ram'] = get_ram_info()
                shared['storage'] = get_storage_info()
                shared['network'] = get_network_info()
                shared['sensors'] = get_sensors_and_volts()
                shared['post'] = get_post_and_logs()
                shared['errors'] = scan_os_errors()
                shared['last_update'] = datetime.datetime.now().isoformat()
        except Exception:
            logger.exception("poller error")
        # wait with early exit checks
        for _ in range(int(POLL_INTERVAL*10)):
            if stop_event.is_set():
                break
            time.sleep(0.1)
    logger.info("Poller stopped")

# ---------------- Reports ----------------
def save_full_report():
    ts = now_ts()
    fname = os.path.join(REPORTS_DIR, f"full_report_{ts}.json")
    with shared_lock:
        snapshot = dict(shared)
    try:
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, default=str)
        messagebox.showinfo("Saved", f"Full report saved to:\n{fname}")
    except Exception as e:
        logger.exception("save_full_report")
        messagebox.showerror("Error", f"Failed to save: {e}")

def export_log():
    dest = filedialog.asksaveasfilename(title="Export Log", defaultextension=".log", initialfile=f"diagtool_{now_ts()}.log")
    if not dest: return
    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as fr:
            data = fr.read()
        with open(dest, "w", encoding="utf-8") as fw:
            fw.write(data)
        messagebox.showinfo("Exported", f"Log exported to:\n{dest}")
    except Exception:
        logger.exception("export_log")
        messagebox.showerror("Error", "Failed to export log")

def save_error_report():
    ts = now_ts()
    fname = os.path.join(REPORTS_DIR, f"error_report_{ts}.txt")
    with shared_lock:
        p = shared.get('post',{}); errs = shared.get('errors',[])
    try:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"Error Report {ts}\n\n")
            f.write("POST / Boot Logs:\n")
            for line in p.get('history',[])[:500]:
                f.write(line+"\n")
            f.write("\nDetected errors:\n")
            for e in errs[:1000]:
                f.write(json.dumps(e)+"\n")
        messagebox.showinfo("Saved", f"Error report saved to:\n{fname}")
    except Exception:
        logger.exception("save_error_report")
        messagebox.showerror("Error", "Failed to save error report")

def print_error_report():
    # Save then try to print
    ts = now_ts()
    fname = os.path.join(REPORTS_DIR, f"error_report_{ts}.txt")
    with shared_lock:
        p = shared.get('post',{}); errs = shared.get('errors',[])
    try:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"Error Report {ts}\n\n")
            f.write("POST / Boot Logs:\n")
            for line in p.get('history',[])[:500]:
                f.write(line+"\n")
            f.write("\nDetected errors:\n")
            for e in errs[:1000]:
                f.write(json.dumps(e)+"\n")
        # attempt print
        if platform.system()=="Windows":
            os.startfile(fname, "print")
        else:
            safe_cmd(f"lp {fname}")
        messagebox.showinfo("Printed", f"Sent error report to printer (if configured).")
    except Exception:
        logger.exception("print_error_report")
        messagebox.showerror("Error", "Failed to print error report")

# ---------------- UI (grid/tile layout) ----------------
class DiagUI:
    def __init__(self, root):
        self.root = root
        root.title("ReBoot Lab - DiagTool")
        root.configure(bg=BG)
        self.fullscreen = FULLSCREEN_ON_START
        if self.fullscreen:
            root.attributes("-fullscreen", True)
        # style
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # main container: use grid with 3 columns: main area (wide), right column (fixed)
        root.grid_rowconfigure(0, weight=0)  # top row (system)
        root.grid_rowconfigure(1, weight=0)  # cpu
        root.grid_rowconfigure(2, weight=0)  # gpu
        root.grid_rowconfigure(3, weight=1)  # post (expand)
        root.grid_rowconfigure(4, weight=0)  # buttons

        root.grid_columnconfigure(0, weight=1)  # main column (wide)
        root.grid_columnconfigure(1, weight=0)  # right column (fixed width)

        # Top-right small control buttons (Exit, Refresh, System Report)
        ctrl_frame = tk.Frame(root, bg=BG)
        ctrl_frame.grid(row=0, column=1, sticky="ne", padx=8, pady=6)
        b_report = tk.Button(ctrl_frame, text="System Report", command=self.show_system_report, bg=NEON, fg="#05060a")
        b_refresh = tk.Button(ctrl_frame, text="Refresh", command=self.manual_refresh, bg=ACCENT, fg=FG)
        b_exit = tk.Button(ctrl_frame, text="Exit", command=self.on_exit, bg=HEADER, fg=FG)
        for b in (b_exit, b_refresh, b_report):
            b.pack(side="right", padx=4)

        # Row1: System tile (full width)
        self.system_card = self.make_card(root, "SYSTEM", row=0, col=0, colspan=1, height=100)
        # right column top tile (Voltage)
        self.voltage_card = self.make_card(root, "VOLTAGE", row=0, col=1, width=320, height=120)

        # Row2: CPU tile (full width)
        self.cpu_card = self.make_card(root, "CPU", row=1, col=0, height=120)
        # right column middle tile (Network)
        self.net_card = self.make_card(root, "NETWORK", row=1, col=1, width=320, height=120)

        # Row3: GPU tile (full width)
        self.gpu_card = self.make_card(root, "GPU", row=2, col=0, height=120)
        # right column bottom tile (Storage)
        self.storage_card = self.make_card(root, "STORAGE", row=2, col=1, width=320, height=120)

        # Row4: POST / Error big tile (full width, larger)
        self.post_card = self.make_card(root, "POST / ERROR LOGS", row=3, col=0, height=320)
        # attach a scrollable text inside post_card
        self.post_text = tk.Text(self.post_card['body'], bg="#000000", fg=NEON, wrap="none", height=18)
        self.post_text.pack(fill="both", expand=True, padx=6, pady=6, side="left")
        psb = ttk.Scrollbar(self.post_card['body'], orient="vertical", command=self.post_text.yview)
        psb.pack(side="right", fill="y")
        self.post_text.configure(yscrollcommand=psb.set)

        # Bottom: buttons row
        btn_frame = tk.Frame(root, bg=BG)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=8)
        s1 = tk.Button(btn_frame, text="Save Full Report", command=save_full_report, bg=HEADER, fg=FG)
        s2 = tk.Button(btn_frame, text="Export Log", command=export_log, bg=ACCENT, fg=FG)
        s3 = tk.Button(btn_frame, text="Save Error Report", command=save_error_report, bg=NEON, fg="#05060a")
        s4 = tk.Button(btn_frame, text="Print Error Report", command=print_error_report, bg=ALERT, fg=BG)
        for b in (s1, s2, s3, s4):
            b.pack(side="left", padx=8, ipadx=6, ipady=4)

        # Populate card bodies with widgets for live data
        # System card content
        self.sys_labels = {}
        for i, key in enumerate(["hostname","platform","os_release","model","serial","ip","uptime","processor","python_version"]):
            lbl = tk.Label(self.system_card['body'], text=f"{key.title()}: N/A", anchor="w", bg=CARD_BG, fg=FG)
            lbl.pack(fill="x", padx=6, pady=2)
            self.sys_labels[key] = lbl

        # CPU card content
        self.cpu_labels = {}
        keys = ["model","physical","logical","min_mhz","current_mhz","max_mhz","load","temp","l1","l2","l3","voltage"]
        for key in keys:
            lbl = tk.Label(self.cpu_card['body'], text=f"{key.replace('_',' ').title()}: N/A", anchor="w", bg=CARD_BG, fg=FG)
            lbl.pack(fill="x", padx=6, pady=2)
            self.cpu_labels[key] = lbl

        # GPU card content
        self.gpu_labels = {}
        gkeys = ["model","driver","vram_total","vram_used","clock_core","clock_mem","temp","power"]
        for k in gkeys:
            lbl = tk.Label(self.gpu_card['body'], text=f"{k.replace('_',' ').title()}: N/A", anchor="w", bg=CARD_BG, fg=FG)
            lbl.pack(fill="x", padx=6, pady=2)
            self.gpu_labels[k] = lbl

        # Voltage card content
        self.vol_labels = {}
        for k in ["12v","5v","3v3","cpu_core","ram","gpu"]:
            lbl = tk.Label(self.voltage_card['body'], text=f"{k.upper()}: N/A", anchor="w", bg=CARD_BG, fg=FG)
            lbl.pack(fill="x", padx=6, pady=2)
            self.vol_labels[k] = lbl

        # Network card content
        self.net_text = tk.Text(self.net_card['body'], height=6, bg=CARD_BG, fg=NEON)
        self.net_text.pack(fill="both", expand=True, padx=6, pady=6)

        # Storage card content
        self.storage_text = tk.Text(self.storage_card['body'], height=6, bg=CARD_BG, fg=NEON)
        self.storage_text.pack(fill="both", expand=True, padx=6, pady=6)

        # small watermark skull (optional)
        if os.path.exists(SKULL_IMAGE):
            try:
                from PIL import Image, ImageTk
                img = Image.open(SKULL_IMAGE).convert("RGBA")
                img = img.resize((96,96), Image.ANTIALIAS)
                imgtk = ImageTk.PhotoImage(img)
                wm = tk.Label(root, image=imgtk, bg=BG)
                wm.image = imgtk
                # bottom-left subtle
                wm.place(relx=0.02, rely=0.95, anchor="sw")
                wm.lower()
            except Exception:
                pass

        # key binding
        root.bind("<Escape>", self.exit_fullscreen)

        # schedule UI updater
        self.update_ui()

    def make_card(self, parent, title, row, col, colspan=1, width=None, height=140):
        # frame with header (header uses HEADER color), body uses CARD_BG
        card_outer = tk.Frame(parent, bg=BG)
        card_outer.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=8, pady=6)
        header = tk.Frame(card_outer, bg=HEADER, height=28)
        header.pack(fill="x")
        label = tk.Label(header, text=title, bg=HEADER, fg=BG, font=("Segoe UI", 11, "bold"))
        label.pack(side="left", padx=8)
        body = tk.Frame(card_outer, bg=CARD_BG, height=height)
        body.pack(fill="both", expand=True)
        # make body constrained
        if width:
            card_outer.grid_propagate(False)
            card_outer.config(width=width)
        return {"outer": card_outer, "header": header, "body": body}

    def exit_fullscreen(self, event=None):
        if self.root.attributes("-fullscreen"):
            self.root.attributes("-fullscreen", False)

    def on_exit(self):
        if messagebox.askyesno("Exit", "Exit DiagTool?"):
            stop_event.set()
            self.root.quit()

    def manual_refresh(self):
        # run a quick poll in background
        t = threading.Thread(target=self._manual_poll, daemon=True)
        t.start()

    def _manual_poll(self):
        with shared_lock:
            shared['system'] = get_system_info()
            shared['cpu'] = get_cpu_info()
            shared['gpu'] = get_gpu_info()
            shared['ram'] = get_ram_info()
            shared['storage'] = get_storage_info()
            shared['network'] = get_network_info()
            shared['sensors'] = get_sensors_and_volts()
            shared['post'] = get_post_and_logs()
            shared['errors'] = scan_os_errors()
            shared['last_update'] = datetime.datetime.now().isoformat()

    def show_system_report(self):
        with shared_lock:
            s = shared.get('system',{})
            last = shared.get('last_update',"N/A")
        lines = [f"System Report (last update: {last})\n"]
        for k,v in s.items():
            lines.append(f"{k}: {v}")
        messagebox.showinfo("System Report", "\n".join(lines[:200]))

    def update_ui(self):
        # update UI elements from shared data
        with shared_lock:
            s = dict(shared)
        # System
        sysinfo = s.get('system',{})
        for key, lbl in self.sys_labels.items():
            val = sysinfo.get(key, "N/A")
            lbl.config(text=f"{key.replace('_',' ').title()}: {val}")
        # CPU
        cpu = s.get('cpu',{})
        self.cpu_labels['model'].config(text=f"Model: {cpu.get('model','N/A')}")
        self.cpu_labels['physical'].config(text=f"Cores: {cpu.get('physical','N/A')}")
        self.cpu_labels['logical'].config(text=f"Threads: {cpu.get('logical','N/A')}")
        self.cpu_labels['min_mhz'].config(text=f"Min MHz: {cpu.get('min_mhz','N/A')}")
        self.cpu_labels['current_mhz'].config(text=f"Current MHz: {cpu.get('current_mhz','N/A')}")
        self.cpu_labels['max_mhz'].config(text=f"Max MHz: {cpu.get('max_mhz','N/A')}")
        self.cpu_labels['load'].config(text=f"Load %: {cpu.get('load','N/A')}")
        self.cpu_labels['temp'].config(text=f"Temp C: {cpu.get('temp','N/A')}")
        self.cpu_labels['l1'].config(text=f"L1: {cpu.get('l1','N/A')}")
        self.cpu_labels['l2'].config(text=f"L2: {cpu.get('l2','N/A')}")
        self.cpu_labels['l3'].config(text=f"L3: {cpu.get('l3','N/A')}")
        self.cpu_labels['voltage'].config(text=f"Voltage: {cpu.get('voltage','N/A')}")

        # GPU
        gpu = s.get('gpu',{})
        for k, lbl in self.gpu_labels.items():
            lbl.config(text=f"{k.replace('_',' ').title()}: {gpu.get(k,'N/A')}")

        # Voltage / Sensors
        sensors = s.get('sensors',{})
        self.vol_labels['12v'].config(text=f"12V: {sensors.get('12v','N/A')}")
        self.vol_labels['5v'].config(text=f"5V: {sensors.get('5v','N/A')}")
        self.vol_labels['3v3'].config(text=f"3.3V: {sensors.get('3v3','N/A')}")
        # placeholders
        self.vol_labels['cpu_core'].config(text=f"CPU Core V: {sensors.get('cpu_core','N/A')}")
        self.vol_labels['ram'].config(text=f"RAM V: {sensors.get('ram','N/A')}")
        self.vol_labels['gpu'].config(text=f"GPU V: {sensors.get('gpu','N/A')}")

        # Network
        net = s.get('network',{}).get('interfaces',{})
        self.net_text.delete(1.0, "end")
        if net:
            for k,v in net.items():
                self.net_text.insert("end", f"{k}: IP {v.get('ip')} MAC {v.get('mac')} Up {v.get('isup')} Speed {v.get('speed')}\n")
        else:
            self.net_text.insert("end", "No network interfaces\n")
        self.net_text.insert("end", f"\nTotal Sent: {s.get('network',{}).get('sent','N/A')}  Recv: {s.get('network',{}).get('recv','N/A')}\n")

        # Storage
        self.storage_text.delete(1.0, "end")
        drives = s.get('storage',{}).get('drives',[])
        if drives:
            for d in drives:
                self.storage_text.insert("end", f"{d.get('device')} @ {d.get('mount')} | {d.get('fstype')} | Total {d.get('total')} Used {d.get('used')} Free {d.get('free')} ({d.get('percent')})\n")
        else:
            self.storage_text.insert("end", "No drives found\n")
        if s.get('storage',{}).get('smart'):
            self.storage_text.insert("end", "\nSMART:\n")
            for sm in s['storage']['smart']:
                self.storage_text.insert("end", f"{sm.get('device')}: {sm.get('health')}\n")

        # POST / Errors (populate text area)
        post = s.get('post',{})
        self.post_text.delete(1.0, "end")
        hist = post.get('history',[])[:1000]
        if hist:
            for line in hist:
                # colorize simple: errors with keywords
                if re.search(r"err|fail|fault|panic|critical", line, re.I):
                    self.post_text.insert("end", line+"\n", ("err",))
                elif re.search(r"warn|deprecated", line, re.I):
                    self.post_text.insert("end", line+"\n", ("warn",))
                else:
                    self.post_text.insert("end", line+"\n")
        else:
            self.post_text.insert("end", "No POST / boot log entries found\n")
        # tag styles
        self.post_text.tag_configure("err", foreground=ALERT)
        self.post_text.tag_configure("warn", foreground=ACCENT)

        # schedule next UI update (more often than poll)
        self.root.after(700, self.update_ui)

# ---------------- Main ----------------
def main():
    # start poller thread
    t = threading.Thread(target=poller, daemon=True)
    t.start()

    root = tk.Tk()
    app = DiagUI(root)

    def on_close():
        if messagebox.askokcancel("Quit", "Quit DiagTool?"):
            stop_event.set()
            root.quit()
    root.protocol("WM_DELETE_WINDOW", on_close)
    try:
        root.mainloop()
    finally:
        stop_event.set()
        logger.info("Shutting down")
        t.join(timeout=2)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Fatal")
        raise
