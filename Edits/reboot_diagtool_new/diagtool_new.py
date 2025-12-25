#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBoot Lab - Professional Diagnostic Tool
Clean, modern interface matching reference design
Cross-platform PC/Mac/Linux diagnostics
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading, psutil, platform, subprocess, shutil, re, os, time, datetime, json, logging, socket, sys

# ---------------- Config ----------------
POLL_INTERVAL = 2.0
LOG_FILE = "diagtool.log"
REPORTS_DIR = "reports"

# ReBoot Lab Professional Theme (matching reference image)
BG = "#000000"              # Black background
CARD_BG = "#0a0a0a"         # Dark card background
CARD_BORDER = "#1a1a1a"     # Card border
HEADER_BG = "#1a1a1a"       # Header background
TEXT_PRIMARY = "#00ff00"   # Bright green text
TEXT_SECONDARY = "#cccccc"  # Secondary text
TEXT_WARNING = "#ffaa00"    # Warning text
TEXT_ERROR = "#ff4444"      # Error text
BUTTON_BG = "#0f0f0f"       # Button background
BUTTON_HOVER = "#1f1f1f"    # Button hover

os.makedirs(REPORTS_DIR, exist_ok=True)

# Logging
logger = logging.getLogger("DiagTool")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(fh)

# Shared state
shared_lock = threading.Lock()
shared = {"system": {}, "cpu": {}, "gpu": {}, "ram": {}, "storage": {}, "network": {}, "sensors": {}, "post": {"latest": "N/A", "history": []}, "errors": [], "last_update": None}
stop_event = threading.Event()

# ---------------- Helper Functions ----------------
def now_ts(): return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
def safe_cmd(cmd, timeout=4):
    try: 
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, shell=True, timeout=timeout)
        return out.decode(errors="ignore")
    except Exception: return ""
def which(cmd): return shutil.which(cmd) is not None
def human_bytes(n):
    try: n = float(n)
    except Exception: return "N/A"
    units = ["B","KB","MB","GB","TB"]; i=0
    while n>=1024 and i<len(units)-1: n/=1024.0; i+=1
    return f"{n:.1f} {units[i]}"

# ---------------- System Information Functions ----------------
def get_system_info():
    try:
        s = {}
        s['platform'] = platform.system()
        s['platform_release'] = platform.release()
        s['hostname'] = socket.gethostname()
        s['ip'] = next((x for x in socket.gethostbyname_ex(socket.gethostname())[2] if not x.startswith("127.")), "N/A")
        s['processor'] = platform.processor() or "N/A"
        s['python_version'] = platform.python_version()
        
        # Motherboard/Model information
        if s['platform'] == "Linux":
            s['os_release'] = (safe_cmd("cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'=' -f2").strip().strip('"') or "N/A")
            s['motherboard'] = safe_cmd("cat /sys/class/dmi/id/product_name 2>/dev/null").strip() or "N/A"
            s['motherboard_manufacturer'] = safe_cmd("cat /sys/class/dmi/id/board_vendor 2>/dev/null").strip() or "N/A"
            s['serial'] = safe_cmd("cat /sys/class/dmi/id/product_serial 2>/dev/null").strip() or "N/A"
            s['uptime'] = safe_cmd("awk '{print int($1/3600)\"h \"int(($1%3600)/60)\"m\"}' /proc/uptime").strip() or "N/A"
        elif s['platform'] == "Windows":
            s['os_release'] = platform.platform()
            s['motherboard'] = safe_cmd("wmic computersystem get model 2>nul").strip().splitlines()[-1] if which("wmic") else "N/A"
            s['motherboard_manufacturer'] = safe_cmd("wmic computersystem get manufacturer 2>nul").strip().splitlines()[-1] if which("wmic") else "N/A"
            s['serial'] = safe_cmd("wmic bios get serialnumber 2>nul").strip().splitlines()[-1] if which("wmic") else "N/A"
            s['uptime'] = "N/A"
        else:
            s['os_release'] = platform.platform()
            s['motherboard'] = "N/A"
            s['motherboard_manufacturer'] = "N/A"
            s['serial'] = "N/A"
            s['uptime'] = "N/A"
        return s
    except Exception: return {}

def get_cpu_info():
    try:
        c = {}
        c['logical'] = psutil.cpu_count(logical=True)
        c['physical'] = psutil.cpu_count(logical=False)
        c['load'] = psutil.cpu_percent(interval=None)
        
        # Clock speeds
        freq = psutil.cpu_freq()
        if freq:
            c['min_mhz'] = round(freq.min,1)
            c['current_mhz'] = round(freq.current,1)
            c['max_mhz'] = round(freq.max,1)
        else: c['min_mhz']=c['current_mhz']=c['max_mhz']="N/A"
        
        # Manufacturer and model
        c['model'] = platform.processor() or safe_cmd("lscpu | grep 'Model name' | cut -d: -f2").strip() or "N/A"
        
        # Cache information
        lscpu = safe_cmd("lscpu")
        m = re.search(r"L1d cache:\s*(.+)", lscpu); c['l1'] = m.group(1).strip() if m else "N/A"
        m = re.search(r"L2 cache:\s*(.+)", lscpu); c['l2'] = m.group(1).strip() if m else "N/A"
        m = re.search(r"L3 cache:\s*(.+)", lscpu); c['l3'] = m.group(1).strip() if m else "N/A"
        
        # Temperature and voltage
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for k,arr in temps.items():
                    if arr: c['temp'] = round(arr[0].current,1); break
                else: c['temp'] = "N/A"
            else: c['temp'] = "N/A"
        except Exception: c['temp'] = "N/A"
        
        # Voltage monitoring
        c['voltage'] = "N/A"
        if which("sensors"):
            out = safe_cmd("sensors")
            m = re.search(r"VCore.*?([\d\.]+)V", out, re.IGNORECASE)
            if m: c['voltage'] = f"{m.group(1)} V"
        
        return c
    except Exception: return {}

def get_gpu_info():
    g = {}
    try:
        # NVIDIA detection
        if which("nvidia-smi"):
            out = safe_cmd("nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used,clocks.gr,clocks.mem,temperature.gpu,power.draw --format=csv,noheader,nounits")
            if out:
                first = out.splitlines()[0]; cols = [c.strip() for c in first.split(",")]
                g['manufacturer'] = "NVIDIA"
                g['model'] = cols[0] if len(cols)>0 else "NVIDIA"
                g['driver'] = cols[1] if len(cols)>1 else "N/A"
                g['vram_total'] = (cols[2] + " MB") if len(cols)>2 else "N/A"
                g['vram_used'] = (cols[3] + " MB") if len(cols)>3 else "N/A"
                g['clock_core'] = cols[4] if len(cols)>4 else "N/A"
                g['clock_mem'] = cols[5] if len(cols)>5 else "N/A"
                g['temp'] = cols[6] if len(cols)>6 else "N/A"
                g['power'] = cols[7] if len(cols)>7 else "N/A"
            else: g['model'] = "NVIDIA (no output)"
        else:
            # AMD/Intel detection
            if platform.system()=="Linux" and which("lspci"):
                out = safe_cmd("lspci -nn | grep -E 'VGA|3D' -m1")
                g['model'] = out.strip() or "N/A"
                if "AMD" in out or "Radeon" in out: g['manufacturer'] = "AMD"
                elif "Intel" in out: g['manufacturer'] = "Intel"
                else: g['manufacturer'] = "Unknown"
            elif platform.system()=="Windows" and which("wmic"):
                out = safe_cmd("wmic path win32_videocontroller get name")
                g['model'] = out.strip().splitlines()[-1] if out else "N/A"
                g['manufacturer'] = "Unknown"
            else: g['model'] = "N/A"; g['manufacturer'] = "Unknown"
            
            # Default values
            g.setdefault('driver',"N/A"); g.setdefault('vram_total',"N/A")
            g.setdefault('vram_used',"N/A"); g.setdefault('clock_core',"N/A")
            g.setdefault('clock_mem',"N/A"); g.setdefault('temp',"N/A"); g.setdefault('power',"N/A")
        return g
    except Exception: return {"manufacturer":"N/A"}

def get_ram_info():
    try:
        r = {}
        vm = psutil.virtual_memory()
        r['total'] = human_bytes(vm.total)
        r['available'] = human_bytes(vm.available)
        r['used'] = human_bytes(vm.used)
        r['percent'] = f"{vm.percent} %"
        
        # Swap memory
        sv = psutil.swap_memory()
        r['swap_total'] = human_bytes(sv.total)
        r['swap_used'] = human_bytes(sv.used)
        
        # Detailed RAM information
        r['manufacturer'] = "N/A"
        r['part_number'] = "N/A"
        r['type'] = "N/A"
        r['speed'] = "N/A"
        r['max_speed'] = "N/A"
        r['slots'] = []
        
        if which("dmidecode"):
            out = safe_cmd("sudo dmidecode -t memory")
            parts = out.split("Memory Device")
            slots = []
            for dev in parts[1:]:
                slot = {}
                m = re.search(r"Manufacturer:\s*(.+)", dev); slot['manufacturer'] = m.group(1).strip() if m else "N/A"
                m = re.search(r"Part Number:\s*(.+)", dev); slot['part_number'] = m.group(1).strip() if m else "N/A"
                m = re.search(r"Speed:\s*(\d+)\s*MHz", dev); slot['speed'] = (m.group(1) + " MHz") if m else "N/A"
                m = re.search(r"Type:\s*(.+)", dev); slot['type'] = m.group(1).strip() if m else "N/A"
                m = re.search(r"Size:\s*(.+)", dev); slot['size'] = m.group(1).strip() if m else "N/A"
                slots.append(slot)
            if slots:
                r['slots'] = slots
                r['manufacturer'] = slots[0].get('manufacturer', "N/A")
                r['type'] = slots[0].get('type', "N/A")
                r['speed'] = slots[0].get('speed', "N/A")
        
        return r
    except Exception: return {}

def get_storage_info():
    try:
        s = {}; parts = psutil.disk_partitions(all=False); drives=[]
        for p in parts:
            try:
                u = psutil.disk_usage(p.mountpoint)
                drives.append({"device":p.device,"mount":p.mountpoint,"fstype":p.fstype,"total":human_bytes(u.total),"used":human_bytes(u.used),"free":human_bytes(u.free),"percent":f"{u.percent} %"})
            except Exception: drives.append({"device":p.device,"mount":p.mountpoint,"fstype":p.fstype,"total":"N/A","used":"N/A","free":"N/A","percent":"N/A"})
        s['drives']=drives; s['smart']=[]; return s
    except Exception: return {}

def get_network_info():
    try:
        n={}; addrs = psutil.net_if_addrs(); stats = psutil.net_if_stats(); nif={}
        for k,v in addrs.items():
            if k.lower().startswith("lo"): continue; ip="N/A"; mac="N/A"
            for e in v:
                if getattr(e,'family',None)==socket.AF_INET: ip=e.address
                try:
                    if e.family == psutil.AF_LINK: mac=e.address
                except Exception:
                    if hasattr(e, "address") and ":" in e.address: mac = e.address
            stat = stats.get(k)
            nif[k]={"ip":ip or "N/A","mac":mac or "N/A","isup":stat.isup if stat else "N/A","speed":f"{stat.speed}MB/s" if stat and stat.speed else "N/A"}
        n['interfaces']=nif; counters = psutil.net_io_counters(pernic=False)
        n['sent']=human_bytes(counters.bytes_sent); n['recv']=human_bytes(counters.bytes_recv); return n
    except Exception: return {}

def get_sensors_and_volts():
    try:
        s={}
        # Temperature sensors
        try:
            temps = psutil.sensors_temperatures(); s['temps'] = {}
            if temps:
                for k,arr in temps.items():
                    if arr: s['temps'][k] = round(arr[0].current,1)
        except Exception: s['temps'] = {}
        
        # Voltage monitoring
        if which("sensors"):
            out = safe_cmd("sensors")
            def match(p):
                m = re.search(p, out, re.IGNORECASE)
                return m.group(1).strip() if m else None
            v12 = match(r"12V.*?([\d\.]+)"); v5 = match(r"5V.*?([\d\.]+)"); v33 = match(r"3\.3V.*?([\d\.]+)")
            s['12v'] = (v12+" V") if v12 else "N/A"
            s['5v'] = (v5+" V") if v5 else "N/A"
            s['3v3'] = (v33+" V") if v33 else "N/A"
        else:
            # Raspberry Pi voltage monitoring
            if which("vcgencmd"):
                t = safe_cmd("vcgencmd measure_temp")
                vcore = safe_cmd("vcgencmd measure_volts core")
                s['3v3'] = vcore.strip().replace("volt=","") if vcore else "N/A"
                m = re.search(r"temp=([\d\.]+)'C", t)
                if m: s.setdefault('temps', {})['cpu']=float(m.group(1))
                s.setdefault('12v','N/A'); s.setdefault('5v','N/A')
            else: s['12v']="N/A"; s['5v']="N/A"; s['3v3']="N/A"
        return s
    except Exception: return {}

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
    except Exception: pass
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
    except Exception: pass
    return errs

# ---------------- Polling Worker ----------------
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
        except Exception: pass
        for _ in range(int(POLL_INTERVAL*10)):
            if stop_event.is_set(): break
            time.sleep(0.1)
    logger.info("Poller stopped")

# ---------------- Report Functions ----------------
def save_full_report():
    ts = now_ts(); fname = os.path.join(REPORTS_DIR, f"full_report_{ts}.json")
    with shared_lock: snapshot = dict(shared)
    try:
        with open(fname, "w", encoding="utf-8") as f: json.dump(snapshot, f, indent=2, default=str)
        messagebox.showinfo("Saved", f"Full report saved to:\n{fname}")
    except Exception: messagebox.showerror("Error", "Failed to save")

def save_error_report():
    ts = now_ts(); fname = os.path.join(REPORTS_DIR, f"error_report_{ts}.txt")
    with shared_lock: p = shared.get('post',{}); errs = shared.get('errors',[])
    try:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"ReBoot Lab Error Report {ts}\n\n")
            f.write("POST / Boot Logs:\n")
            for line in p.get('history',[])[:500]: f.write(line+"\n")
            f.write("\nDetected errors:\n")
            for e in errs[:1000]: f.write(json.dumps(e)+"\n")
        messagebox.showinfo("Saved", f"Error report saved to:\n{fname}")
    except Exception: messagebox.showerror("Error", "Failed to save")

def print_error_report():
    ts = now_ts(); fname = os.path.join(REPORTS_DIR, f"error_report_{ts}.txt")
    with shared_lock: p = shared.get('post',{}); errs = shared.get('errors',[])
    try:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(f"ReBoot Lab Error Report {ts}\n\n")
            f.write("POST / Boot Logs:\n")
            for line in p.get('history',[])[:500]: f.write(line+"\n")
            f.write("\nDetected errors:\n")
            for e in errs[:1000]: f.write(json.dumps(e)+"\n")
        if platform.system()=="Windows": os.startfile(fname, "print")
        else: safe_cmd(f"lp {fname}")
        messagebox.showinfo("Printed", "Error report sent to printer")
    except Exception: messagebox.showerror("Error", "Failed to print")

# ---------------- Main UI Class ----------------
class DiagUI:
    def __init__(self, root):
        self.root = root
        root.title("ReBoot Lab - Professional Diagnostic Tool")
        root.configure(bg=BG)
        root.attributes("-fullscreen", True)
        
        # Create main container
        main_frame = tk.Frame(root, bg=BG)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Grid configuration
        main_frame.grid_rowconfigure(0, weight=0)  # System Info
        main_frame.grid_rowconfigure(1, weight=0)  # CPU
        main_frame.grid_rowconfigure(2, weight=0)  # GPU
        main_frame.grid_rowconfigure(3, weight=0)  # RAM
        main_frame.grid_rowconfigure(4, weight=1)  # POST/ERROR Logs (largest)
        main_frame.grid_rowconfigure(5, weight=0)  # Buttons
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Create tiles
        self.create_system_tile(main_frame)
        self.create_cpu_tile(main_frame)
        self.create_gpu_tile(main_frame)
        self.create_ram_tile(main_frame)
        self.create_post_tile(main_frame)
        self.create_buttons(main_frame)
        
        # Start UI updates
        self.update_ui()

    def create_tile(self, parent, title, row, height=100):
        frame = tk.Frame(parent, bg=CARD_BG, relief="solid", bd=1)
        frame.grid(row=row, column=0, sticky="ew", pady=5)
        
        # Header
        header = tk.Frame(frame, bg=HEADER_BG, height=30)
        header.pack(fill="x")
        header.pack_propagate(False)
        label = tk.Label(header, text=title, bg=HEADER_BG, fg=TEXT_PRIMARY, 
                        font=("Courier", 12, "bold"))
        label.pack(side="left", padx=10, pady=5)
        
        # Content
        content = tk.Frame(frame, bg=CARD_BG, height=height)
        content.pack(fill="both", expand=True, padx=5, pady=5)
        
        return content

    def create_system_tile(self, parent):
        self.system_frame = self.create_tile(parent, "SYSTEM INFO", 0, 80)
        self.system_labels = {}
        
        info_items = [
            ("Motherboard", "motherboard"),
            ("Manufacturer", "motherboard_manufacturer"), 
            ("OS", "os_release"),
            ("Hostname", "hostname"),
            ("IP Address", "ip"),
            ("Uptime", "uptime")
        ]
        
        for i, (label_text, key) in enumerate(info_items):
            frame = tk.Frame(self.system_frame, bg=CARD_BG)
            frame.pack(fill="x", pady=2)
            
            label = tk.Label(frame, text=f"{label_text}:", bg=CARD_BG, fg=TEXT_SECONDARY, 
                           font=("Courier", 10), width=15, anchor="w")
            label.pack(side="left")
            
            value_label = tk.Label(frame, text="N/A", bg=CARD_BG, fg=TEXT_PRIMARY,
                                 font=("Courier", 10), anchor="w")
            value_label.pack(side="left", padx=10)
            self.system_labels[key] = value_label

    def create_cpu_tile(self, parent):
        self.cpu_frame = self.create_tile(parent, "CPU INFO", 1, 100)
        self.cpu_labels = {}
        
        cpu_items = [
            ("Model", "model"),
            ("Cores", "logical"),
            ("Current MHz", "current_mhz"),
            ("Max MHz", "max_mhz"),
            ("Load %", "load"),
            ("Temperature", "temp"),
            ("Voltage", "voltage"),
            ("L1 Cache", "l1"),
            ("L2 Cache", "l2"),
            ("L3 Cache", "l3")
        ]
        
        for i, (label_text, key) in enumerate(cpu_items):
            frame = tk.Frame(self.cpu_frame, bg=CARD_BG)
            frame.pack(fill="x", pady=1)
            
            label = tk.Label(frame, text=f"{label_text}:", bg=CARD_BG, fg=TEXT_SECONDARY,
                           font=("Courier", 9), width=12, anchor="w")
            label.pack(side="left")
            
            value_label = tk.Label(frame, text="N/A", bg=CARD_BG, fg=TEXT_PRIMARY,
                                 font=("Courier", 9), anchor="w")
            value_label.pack(side="left", padx=5)
            self.cpu_labels[key] = value_label

    def create_gpu_tile(self, parent):
        self.gpu_frame = self.create_tile(parent, "GPU INFO", 2, 100)
        self.gpu_labels = {}
        
        gpu_items = [
            ("Manufacturer", "manufacturer"),
            ("Model", "model"),
            ("Driver", "driver"),
            ("VRAM Total", "vram_total"),
            ("VRAM Used", "vram_used"),
            ("Core Clock", "clock_core"),
            ("Memory Clock", "clock_mem"),
            ("Temperature", "temp"),
            ("Power", "power")
        ]
        
        for i, (label_text, key) in enumerate(gpu_items):
            frame = tk.Frame(self.gpu_frame, bg=CARD_BG)
            frame.pack(fill="x", pady=1)
            
            label = tk.Label(frame, text=f"{label_text}:", bg=CARD_BG, fg=TEXT_SECONDARY,
                           font=("Courier", 9), width=12, anchor="w")
            label.pack(side="left")
            
            value_label = tk.Label(frame, text="N/A", bg=CARD_BG, fg=TEXT_PRIMARY,
                                 font=("Courier", 9), anchor="w")
            value_label.pack(side="left", padx=5)
            self.gpu_labels[key] = value_label

    def create_ram_tile(self, parent):
        self.ram_frame = self.create_tile(parent, "RAM INFO", 3, 100)
        self.ram_labels = {}
        
        ram_items = [
            ("Total", "total"),
            ("Used", "used"),
            ("Available", "available"),
            ("Usage %", "percent"),
            ("Swap Total", "swap_total"),
            ("Swap Used", "swap_used"),
            ("Type", "type"),
            ("Speed", "speed"),
            ("Manufacturer", "manufacturer")
        ]
        
        for i, (label_text, key) in enumerate(ram_items):
            frame = tk.Frame(self.ram_frame, bg=CARD_BG)
            frame.pack(fill="x", pady=1)
            
            label = tk.Label(frame, text=f"{label_text}:", bg=CARD_BG, fg=TEXT_SECONDARY,
                           font=("Courier", 9), width=12, anchor="w")
            label.pack(side="left")
            
            value_label = tk.Label(frame, text="N/A", bg=CARD_BG, fg=TEXT_PRIMARY,
                                 font=("Courier", 9), anchor="w")
            value_label.pack(side="left", padx=5)
            self.ram_labels[key] = value_label

    def create_post_tile(self, parent):
        self.post_frame = self.create_tile(parent, "POST / ERROR LOGS", 4, 200)
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(self.post_frame, bg=CARD_BG)
        text_frame.pack(fill="both", expand=True)
        
        self.post_text = tk.Text(text_frame, bg="#000000", fg=TEXT_PRIMARY, 
                                font=("Courier", 9), wrap="none", height=15)
        self.post_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.post_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.post_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure text tags for coloring
        self.post_text.tag_configure("error", foreground=TEXT_ERROR)
        self.post_text.tag_configure("warning", foreground=TEXT_WARNING)
        self.post_text.tag_configure("info", foreground=TEXT_PRIMARY)

    def create_buttons(self, parent):
        button_frame = tk.Frame(parent, bg=BG)
        button_frame.grid(row=5, column=0, pady=10)
        
        buttons = [
            ("Save System Report", save_full_report, TEXT_PRIMARY),
            ("Save Error Report", save_error_report, TEXT_WARNING),
            ("Print Error Report", print_error_report, TEXT_WARNING),
            ("Refresh", self.manual_refresh, TEXT_PRIMARY),
            ("Exit", self.on_exit, TEXT_ERROR),
            ("DON'T PRESS", self.dont_press, TEXT_ERROR)
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=command,
                          bg=BUTTON_BG, fg=color, font=("Courier", 10, "bold"),
                          relief="raised", bd=2, padx=10, pady=5)
            btn.pack(side="left", padx=5)
            
            # Hover effect
            def on_enter(e, b=btn): b.config(bg=BUTTON_HOVER)
            def on_leave(e, b=btn): b.config(bg=BUTTON_BG)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def dont_press(self):
        # Easter egg - create black screen
        black_window = tk.Toplevel(self.root)
        black_window.attributes("-fullscreen", True)
        black_window.configure(bg="black")
        
        # Show warning after 5 seconds
        def show_warning():
            warning_label = tk.Label(black_window, text="I TOLD YOU NOT TO PRESS",
                                   fg="red", bg="black", font=("Arial", 48, "bold"))
            warning_label.place(relx=0.5, rely=0.5, anchor="center")
            
            # Reboot after 5 more seconds
            def reboot_tool():
                black_window.destroy()
                messagebox.showinfo("ReBoot Lab", "Diagnostic Tool Rebooted")
            
            black_window.after(5000, reboot_tool)
        
        black_window.after(5000, show_warning)

    def manual_refresh(self):
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

    def on_exit(self):
        if messagebox.askyesno("Exit", "Exit ReBoot Lab Diagnostic Tool?"):
            stop_event.set()
            self.root.quit()

    def update_ui(self):
        try:
            with shared_lock:
                s = dict(shared)
            
            # Update system info
            sysinfo = s.get('system', {})
            for key, label in self.system_labels.items():
                value = sysinfo.get(key, "N/A")
                label.config(text=str(value))
            
            # Update CPU info
            cpu = s.get('cpu', {})
            for key, label in self.cpu_labels.items():
                value = cpu.get(key, "N/A")
                if key in ['min_mhz', 'current_mhz', 'max_mhz'] and value != "N/A":
                    value = f"{value} MHz"
                elif key == 'load' and value != "N/A":
                    value = f"{value}%"
                elif key == 'temp' and value != "N/A":
                    value = f"{value}°C"
                label.config(text=str(value))
            
            # Update GPU info
            gpu = s.get('gpu', {})
            for key, label in self.gpu_labels.items():
                value = gpu.get(key, "N/A")
                label.config(text=str(value))
            
            # Update RAM info
            ram = s.get('ram', {})
            for key, label in self.ram_labels.items():
                value = ram.get(key, "N/A")
                label.config(text=str(value))
            
            # Update POST/ERROR logs (newest at top, auto-scrolling)
            post = s.get('post', {})
            history = post.get('history', [])
            
            if history:
                # Clear and rebuild with newest at top
                self.post_text.delete(1.0, tk.END)
                
                # Reverse to show newest first
                for line in reversed(history[:100]):  # Limit to last 100 entries
                    if re.search(r"err|fail|fault|panic|critical", line, re.I):
                        self.post_text.insert(tk.END, line + "\n", "error")
                    elif re.search(r"warn|deprecated", line, re.I):
                        self.post_text.insert(tk.END, line + "\n", "warning")
                    else:
                        self.post_text.insert(tk.END, line + "\n", "info")
                
                # Auto-scroll to top (newest)
                self.post_text.see(tk.END)
            
        except Exception as e:
            logger.exception("UI update error")
        
        # Schedule next update
        self.root.after(1000, self.update_ui)  # Update every second

# ---------------- Main Function ----------------
def main():
    # Start poller thread
    t = threading.Thread(target=poller, daemon=True)
    t.start()
    
    # Create GUI
    root = tk.Tk()
    app = DiagUI(root)
    
    # Handle window close
    def on_close():
        if messagebox.askokcancel("Quit", "Quit ReBoot Lab Diagnostic Tool?"):
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
        logger.exception("Fatal error")
        raise
