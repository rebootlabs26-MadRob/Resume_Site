#!/usr/bin/env python3
"""
ReBoot Labs DiagTool - PyQt5 Edition
Cyberpunk-themed diagnostic tool for Raspberry Pi 3B + 3.5" TFT (480x320)
"""

import sys
import os
import json
import subprocess
import socket
import logging
from datetime import datetime
from threading import Lock

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QFrame, QScrollArea,
    QGraphicsDropShadowEffect, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QBrush, QPen

# Optional imports
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

# Screen dimensions (480x320 TFT in landscape)
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320

# Cyberpunk color palette
COLORS = {
    'bg_dark': '#0A0A0A',        # Near-black background
    'bg_tile': '#121218',        # Tile background
    'bg_tile_alt': '#1A1A24',    # Alternate tile bg
    'neon_green': '#00FF66',     # Primary accent
    'neon_cyan': '#00FFFF',      # Secondary accent
    'neon_purple': '#7A1FA2',    # Header purple
    'neon_pink': '#FF00FF',      # Alert color
    'neon_orange': '#FF6600',    # Warning color
    'text_primary': '#FFFFFF',   # Main text
    'text_dim': '#888888',       # Dimmed text
    'text_label': '#AAAAAA',     # Label text
    'border_glow': '#00FF66',    # Glowing border
    'error_red': '#FF3333',      # Error indicator
    'ok_green': '#00FF66',       # OK indicator
}

# Fonts
FONT_HEADER = ('Consolas', 11, 'bold')
FONT_VALUE = ('Consolas', 9)
FONT_LABEL = ('Consolas', 8)
FONT_TITLE = ('Consolas', 14, 'bold')

# Factory defaults for comparison
FACTORY_DEFAULTS = {
    'cpu_temp': 45.0,       # Celsius
    'cpu_freq': 1400,       # MHz (Pi 3B max)
    'gpu_temp': 45.0,       # Celsius
    'ram_total': 1024,      # MB (Pi 3B)
    'voltage_core': 1.20,   # Volts
    'voltage_3v3': 3.30,    # Volts
    'voltage_5v': 5.00,     # Volts
    'voltage_12v': 12.00,   # Volts
}

# Fallback text
NO_INFO = "SrryNoInfo"

# Logging setup
LOG_FILE = os.path.expanduser('~/diagtool_pyqt5.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Thread safety
data_lock = Lock()

# ══════════════════════════════════════════════════════════════════════════════
# DATA PROVIDERS
# ══════════════════════════════════════════════════════════════════════════════

def run_cmd(cmd, default=NO_INFO):
    """Run shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.stdout.strip() else default
    except Exception as e:
        logging.error(f"Command failed: {cmd} - {e}")
        return default


def get_system_info():
    """Get basic system information."""
    info = {
        'hostname': socket.gethostname(),
        'platform': NO_INFO,
        'kernel': NO_INFO,
        'uptime': NO_INFO,
        'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    info['platform'] = run_cmd('cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d \\"')
    info['kernel'] = run_cmd('uname -r')
    
    # Uptime
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_sec = float(f.read().split()[0])
            days = int(uptime_sec // 86400)
            hours = int((uptime_sec % 86400) // 3600)
            mins = int((uptime_sec % 3600) // 60)
            info['uptime'] = f"{days}d {hours}h {mins}m"
    except:
        pass
    
    return info


def get_cpu_info():
    """Get CPU information."""
    info = {
        'model': NO_INFO,
        'cores': NO_INFO,
        'freq_current': NO_INFO,
        'freq_max': FACTORY_DEFAULTS['cpu_freq'],
        'temp': NO_INFO,
        'usage': NO_INFO,
        'throttled': False,
    }
    
    # Model
    info['model'] = run_cmd("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2")
    if info['model'] == NO_INFO:
        info['model'] = run_cmd("cat /proc/cpuinfo | grep 'Model' | head -1 | cut -d: -f2")
    
    # Cores
    if HAS_PSUTIL:
        info['cores'] = psutil.cpu_count(logical=True)
        info['usage'] = f"{psutil.cpu_percent(interval=0.1):.1f}%"
    
    # Frequency
    freq = run_cmd("vcgencmd measure_clock arm 2>/dev/null | cut -d= -f2")
    if freq != NO_INFO:
        try:
            info['freq_current'] = int(int(freq) / 1000000)  # Hz to MHz
        except:
            pass
    
    # Temperature
    temp = run_cmd("vcgencmd measure_temp 2>/dev/null | cut -d= -f2 | cut -d\\' -f1")
    if temp != NO_INFO:
        try:
            info['temp'] = float(temp)
        except:
            pass
    
    # Throttle check
    throttle = run_cmd("vcgencmd get_throttled 2>/dev/null | cut -d= -f2")
    if throttle != NO_INFO and throttle != "0x0":
        info['throttled'] = True
    
    return info


def get_gpu_info():
    """Get GPU information."""
    info = {
        'model': 'VideoCore IV',
        'memory': NO_INFO,
        'temp': NO_INFO,
        'freq': NO_INFO,
    }
    
    # GPU memory
    mem = run_cmd("vcgencmd get_mem gpu 2>/dev/null | cut -d= -f2")
    info['memory'] = mem
    
    # GPU temp (same as CPU on Pi)
    temp = run_cmd("vcgencmd measure_temp 2>/dev/null | cut -d= -f2 | cut -d\\' -f1")
    if temp != NO_INFO:
        try:
            info['temp'] = float(temp)
        except:
            pass
    
    # GPU freq
    freq = run_cmd("vcgencmd measure_clock core 2>/dev/null | cut -d= -f2")
    if freq != NO_INFO:
        try:
            info['freq'] = int(int(freq) / 1000000)  # Hz to MHz
        except:
            pass
    
    return info


def get_ram_info():
    """Get RAM information."""
    info = {
        'total': NO_INFO,
        'used': NO_INFO,
        'free': NO_INFO,
        'percent': NO_INFO,
    }
    
    if HAS_PSUTIL:
        mem = psutil.virtual_memory()
        info['total'] = f"{mem.total // (1024**2)} MB"
        info['used'] = f"{mem.used // (1024**2)} MB"
        info['free'] = f"{mem.available // (1024**2)} MB"
        info['percent'] = f"{mem.percent}%"
    
    return info


def get_storage_info():
    """Get storage information."""
    info = {
        'devices': [],
        'root_total': NO_INFO,
        'root_used': NO_INFO,
        'root_free': NO_INFO,
        'root_percent': NO_INFO,
    }
    
    if HAS_PSUTIL:
        # Root partition
        try:
            root = psutil.disk_usage('/')
            info['root_total'] = f"{root.total // (1024**3):.1f} GB"
            info['root_used'] = f"{root.used // (1024**3):.1f} GB"
            info['root_free'] = f"{root.free // (1024**3):.1f} GB"
            info['root_percent'] = f"{root.percent}%"
        except:
            pass
        
        # All partitions
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                info['devices'].append({
                    'device': part.device,
                    'mount': part.mountpoint,
                    'fstype': part.fstype,
                    'total': f"{usage.total // (1024**3):.1f}GB",
                    'percent': f"{usage.percent}%"
                })
            except:
                pass
    
    return info


def get_network_info():
    """Get network information."""
    info = {
        'hostname': socket.gethostname(),
        'ip_local': NO_INFO,
        'ip_external': NO_INFO,
        'mac': NO_INFO,
        'interfaces': [],
    }
    
    # Local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info['ip_local'] = s.getsockname()[0]
        s.close()
    except:
        pass
    
    # External IP
    info['ip_external'] = run_cmd("curl -s ifconfig.me 2>/dev/null", NO_INFO)
    
    # Interfaces
    if HAS_PSUTIL:
        addrs = psutil.net_if_addrs()
        for iface, addr_list in addrs.items():
            iface_info = {'name': iface, 'ip': NO_INFO, 'mac': NO_INFO}
            for addr in addr_list:
                if addr.family == socket.AF_INET:
                    iface_info['ip'] = addr.address
                elif addr.family == psutil.AF_LINK:
                    iface_info['mac'] = addr.address
                    if iface in ['eth0', 'wlan0']:
                        info['mac'] = addr.address
            info['interfaces'].append(iface_info)
    
    return info


def get_voltage_info():
    """Get voltage information (vcgencmd + future ADS1115)."""
    info = {
        'core': NO_INFO,
        'sdram_c': NO_INFO,
        'sdram_i': NO_INFO,
        'sdram_p': NO_INFO,
        'rail_3v3': NO_INFO,
        'rail_5v': NO_INFO,
        'rail_12v': NO_INFO,
        'throttle_status': 'OK',
    }
    
    # Pi voltages via vcgencmd
    for key, cmd_key in [('core', 'core'), ('sdram_c', 'sdram_c'), 
                          ('sdram_i', 'sdram_i'), ('sdram_p', 'sdram_p')]:
        volt = run_cmd(f"vcgencmd measure_volts {cmd_key} 2>/dev/null | cut -d= -f2 | tr -d V")
        if volt != NO_INFO:
            try:
                info[key] = f"{float(volt):.2f}V"
            except:
                pass
    
    # TODO: ADS1115 voltage reading for external rails
    # When ADS1115 is connected, uncomment and configure:
    # try:
    #     import board
    #     import busio
    #     import adafruit_ads1x15.ads1115 as ADS
    #     from adafruit_ads1x15.analog_in import AnalogIn
    #     i2c = busio.I2C(board.SCL, board.SDA)
    #     ads = ADS.ADS1115(i2c)
    #     # Channel 0: 12V rail (with voltage divider)
    #     # Channel 1: 5V rail
    #     # Channel 2: 3.3V rail
    #     chan0 = AnalogIn(ads, ADS.P0)
    #     chan1 = AnalogIn(ads, ADS.P1)
    #     chan2 = AnalogIn(ads, ADS.P2)
    #     info['rail_12v'] = f"{chan0.voltage * 4:.2f}V"  # Adjust multiplier for divider
    #     info['rail_5v'] = f"{chan1.voltage:.2f}V"
    #     info['rail_3v3'] = f"{chan2.voltage:.2f}V"
    # except Exception as e:
    #     logging.error(f"ADS1115 read failed: {e}")
    
    # Throttle status
    throttle = run_cmd("vcgencmd get_throttled 2>/dev/null | cut -d= -f2")
    if throttle != NO_INFO and throttle != "0x0":
        info['throttle_status'] = f"WARN: {throttle}"
    
    return info


def get_post_logs():
    """Get POST/boot logs."""
    logs = {
        'dmesg': [],
        'errors': [],
        'boot_time': NO_INFO,
    }
    
    # Recent dmesg
    dmesg = run_cmd("dmesg | tail -20 2>/dev/null")
    if dmesg != NO_INFO:
        logs['dmesg'] = dmesg.split('\n')[-10:]  # Last 10 lines
    
    # Errors from dmesg
    errors = run_cmd("dmesg | grep -iE 'error|fail|warn' | tail -10 2>/dev/null")
    if errors != NO_INFO:
        logs['errors'] = errors.split('\n')[-5:]  # Last 5 errors
    
    # Boot time
    if HAS_PSUTIL:
        boot = datetime.fromtimestamp(psutil.boot_time())
        logs['boot_time'] = boot.strftime('%Y-%m-%d %H:%M:%S')
    
    return logs


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ══════════════════════════════════════════════════════════════════════════════

class NeonTile(QFrame):
    """Cyberpunk-styled tile with glow effect."""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self._glow_intensity = 0.0
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        self.setObjectName("NeonTile")
        self.setStyleSheet(f"""
            QFrame#NeonTile {{
                background-color: {COLORS['bg_tile']};
                border: 1px solid {COLORS['neon_green']};
                border-radius: 4px;
            }}
        """)
        
        # Glow effect
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(8)
        self.glow.setColor(QColor(COLORS['neon_green']))
        self.glow.setOffset(0, 0)
        self.setGraphicsEffect(self.glow)
        
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 2, 4, 4)
        self.layout.setSpacing(1)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(f"""
            color: {COLORS['neon_purple']};
            font-family: Consolas;
            font-size: 10px;
            font-weight: bold;
            padding: 1px;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)
        
        # Content area
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(2, 0, 2, 2)
        self.content_layout.setSpacing(0)
        self.layout.addWidget(self.content)
    
    def setup_animation(self):
        """Setup subtle pulse animation."""
        self.anim = QPropertyAnimation(self, b"glow_intensity")
        self.anim.setDuration(2000)
        self.anim.setStartValue(0.3)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.InOutSine)
        self.anim.setLoopCount(-1)  # Infinite
        # self.anim.start()  # Uncomment for animation
    
    def get_glow_intensity(self):
        return self._glow_intensity
    
    def set_glow_intensity(self, value):
        self._glow_intensity = value
        self.glow.setBlurRadius(5 + value * 10)
    
    glow_intensity = pyqtProperty(float, get_glow_intensity, set_glow_intensity)
    
    def add_row(self, label, value, factory_default=None, is_value_ok=True):
        """Add a data row with label, value, and optional factory default."""
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(2)
        
        # Label
        lbl = QLabel(f"{label}:")
        lbl.setStyleSheet(f"color: {COLORS['text_label']}; font-family: Consolas; font-size: 8px;")
        lbl.setFixedWidth(50)
        row_layout.addWidget(lbl)
        
        # Value
        val_color = COLORS['ok_green'] if is_value_ok else COLORS['error_red']
        val = QLabel(str(value))
        val.setStyleSheet(f"color: {val_color}; font-family: Consolas; font-size: 8px; font-weight: bold;")
        row_layout.addWidget(val)
        
        # Factory default (if provided)
        if factory_default is not None:
            default = QLabel(f"[{factory_default}]")
            default.setStyleSheet(f"color: {COLORS['text_dim']}; font-family: Consolas; font-size: 7px;")
            row_layout.addWidget(default)
        
        row_layout.addStretch()
        self.content_layout.addWidget(row)
        return val  # Return value label for updates
    
    def clear_content(self):
        """Clear all content rows."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class SplitTile(QFrame):
    """Split tile for POST logs (left) and Errors (right)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tile']};
                border: 1px solid {COLORS['neon_green']};
                border-radius: 4px;
            }}
        """)
        
        # Glow
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(8)
        glow.setColor(QColor(COLORS['neon_green']))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        
        # Left side - POST logs
        self.post_frame = QFrame()
        self.post_frame.setStyleSheet(f"border: none; border-right: 1px solid {COLORS['neon_purple']};")
        post_layout = QVBoxLayout(self.post_frame)
        post_layout.setContentsMargins(2, 0, 2, 0)
        post_layout.setSpacing(0)
        
        post_title = QLabel("POST LOG")
        post_title.setStyleSheet(f"color: {COLORS['neon_purple']}; font-family: Consolas; font-size: 8px; font-weight: bold;")
        post_title.setAlignment(Qt.AlignCenter)
        post_layout.addWidget(post_title)
        
        self.post_content = QLabel(NO_INFO)
        self.post_content.setStyleSheet(f"color: {COLORS['text_dim']}; font-family: Consolas; font-size: 6px;")
        self.post_content.setWordWrap(True)
        self.post_content.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        post_layout.addWidget(self.post_content)
        
        main_layout.addWidget(self.post_frame, 1)
        
        # Right side - Errors only
        self.error_frame = QFrame()
        self.error_frame.setStyleSheet("border: none;")
        error_layout = QVBoxLayout(self.error_frame)
        error_layout.setContentsMargins(2, 0, 2, 0)
        error_layout.setSpacing(0)
        
        error_title = QLabel("ERRORS")
        error_title.setStyleSheet(f"color: {COLORS['error_red']}; font-family: Consolas; font-size: 8px; font-weight: bold;")
        error_title.setAlignment(Qt.AlignCenter)
        error_layout.addWidget(error_title)
        
        self.error_content = QLabel("None")
        self.error_content.setStyleSheet(f"color: {COLORS['ok_green']}; font-family: Consolas; font-size: 6px;")
        self.error_content.setWordWrap(True)
        self.error_content.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        error_layout.addWidget(self.error_content)
        
        main_layout.addWidget(self.error_frame, 1)
    
    def update_content(self, post_logs, errors):
        """Update POST logs and errors."""
        if post_logs:
            self.post_content.setText('\n'.join(post_logs[-4:]))  # Last 4 lines
        else:
            self.post_content.setText(NO_INFO)
        
        if errors:
            self.error_content.setText('\n'.join(errors[-3:]))  # Last 3 errors
            self.error_content.setStyleSheet(f"color: {COLORS['error_red']}; font-family: Consolas; font-size: 6px;")
        else:
            self.error_content.setText("None")
            self.error_content.setStyleSheet(f"color: {COLORS['ok_green']}; font-family: Consolas; font-size: 6px;")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class DiagToolWindow(QMainWindow):
    """Main diagnostic tool window."""
    
    def __init__(self):
        super().__init__()
        self.value_labels = {}  # Store labels for updates
        self.setup_ui()
        self.setup_timer()
        self.update_all_data()
    
    def setup_ui(self):
        self.setWindowTitle("ReBoot Labs DiagTool")
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']};")
        
        # Remove window frame for TFT
        # self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # Header
        header = QLabel("⚡ ReBoot Labs DiagTool ⚡")
        header.setStyleSheet(f"""
            color: {COLORS['neon_green']};
            font-family: Consolas;
            font-size: 12px;
            font-weight: bold;
            padding: 2px;
        """)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Tiles grid (2 rows x 3 columns)
        tiles_widget = QWidget()
        tiles_layout = QGridLayout(tiles_widget)
        tiles_layout.setContentsMargins(0, 0, 0, 0)
        tiles_layout.setSpacing(4)
        
        # Row 1: CPU | GPU | RAM
        self.cpu_tile = NeonTile("CPU")
        tiles_layout.addWidget(self.cpu_tile, 0, 0)
        
        self.gpu_tile = NeonTile("GPU")
        tiles_layout.addWidget(self.gpu_tile, 0, 1)
        
        self.ram_tile = NeonTile("RAM")
        tiles_layout.addWidget(self.ram_tile, 0, 2)
        
        # Row 2: STORAGE | NETWORK | VOLTAGE
        self.storage_tile = NeonTile("STORAGE")
        tiles_layout.addWidget(self.storage_tile, 1, 0)
        
        self.network_tile = NeonTile("NETWORK")
        tiles_layout.addWidget(self.network_tile, 1, 1)
        
        self.voltage_tile = NeonTile("VOLTAGE")
        tiles_layout.addWidget(self.voltage_tile, 1, 2)
        
        main_layout.addWidget(tiles_widget)
        
        # POST/Errors split tile
        self.post_tile = SplitTile()
        self.post_tile.setFixedHeight(60)
        main_layout.addWidget(self.post_tile)
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)
        
        self.refresh_btn = QPushButton("⟳ REFRESH")
        self.refresh_btn.setStyleSheet(self.get_button_style())
        self.refresh_btn.clicked.connect(self.update_all_data)
        btn_layout.addWidget(self.refresh_btn)
        
        self.full_info_btn = QPushButton("📋 FULL INFO")
        self.full_info_btn.setStyleSheet(self.get_button_style())
        self.full_info_btn.clicked.connect(self.show_full_info)
        btn_layout.addWidget(self.full_info_btn)
        
        self.export_btn = QPushButton("💾 EXPORT")
        self.export_btn.setStyleSheet(self.get_button_style())
        self.export_btn.clicked.connect(self.export_report)
        btn_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(btn_layout)
    
    def get_button_style(self):
        return f"""
            QPushButton {{
                background-color: {COLORS['bg_tile']};
                color: {COLORS['neon_green']};
                border: 1px solid {COLORS['neon_green']};
                border-radius: 3px;
                padding: 4px 8px;
                font-family: Consolas;
                font-size: 9px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['neon_green']};
                color: {COLORS['bg_dark']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['neon_purple']};
            }}
        """
    
    def setup_timer(self):
        """Setup auto-refresh timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_data)
        self.timer.start(3000)  # Update every 3 seconds
    
    def update_all_data(self):
        """Update all tiles with fresh data."""
        with data_lock:
            self.update_cpu_tile()
            self.update_gpu_tile()
            self.update_ram_tile()
            self.update_storage_tile()
            self.update_network_tile()
            self.update_voltage_tile()
            self.update_post_tile()
    
    def update_cpu_tile(self):
        self.cpu_tile.clear_content()
        data = get_cpu_info()
        
        temp_ok = True
        if isinstance(data['temp'], (int, float)):
            temp_ok = data['temp'] < 70
            temp_str = f"{data['temp']}°C"
        else:
            temp_str = data['temp']
        
        self.cpu_tile.add_row("Temp", temp_str, f"{FACTORY_DEFAULTS['cpu_temp']}°C", temp_ok)
        self.cpu_tile.add_row("Freq", f"{data['freq_current']}MHz", f"{FACTORY_DEFAULTS['cpu_freq']}MHz")
        self.cpu_tile.add_row("Usage", data['usage'])
        self.cpu_tile.add_row("Cores", data['cores'])
        
        if data['throttled']:
            self.cpu_tile.add_row("⚠️", "THROTTLED!", is_value_ok=False)
    
    def update_gpu_tile(self):
        self.gpu_tile.clear_content()
        data = get_gpu_info()
        
        temp_ok = True
        if isinstance(data['temp'], (int, float)):
            temp_ok = data['temp'] < 70
            temp_str = f"{data['temp']}°C"
        else:
            temp_str = data['temp']
        
        self.gpu_tile.add_row("Temp", temp_str, f"{FACTORY_DEFAULTS['gpu_temp']}°C", temp_ok)
        self.gpu_tile.add_row("Freq", f"{data['freq']}MHz" if data['freq'] != NO_INFO else NO_INFO)
        self.gpu_tile.add_row("Mem", data['memory'])
        self.gpu_tile.add_row("Type", data['model'])
    
    def update_ram_tile(self):
        self.ram_tile.clear_content()
        data = get_ram_info()
        
        self.ram_tile.add_row("Total", data['total'], f"{FACTORY_DEFAULTS['ram_total']}MB")
        self.ram_tile.add_row("Used", data['used'])
        self.ram_tile.add_row("Free", data['free'])
        
        # Usage bar representation
        percent_ok = True
        if data['percent'] != NO_INFO:
            try:
                pct = float(data['percent'].replace('%', ''))
                percent_ok = pct < 85
            except:
                pass
        self.ram_tile.add_row("Use", data['percent'], is_value_ok=percent_ok)
    
    def update_storage_tile(self):
        self.storage_tile.clear_content()
        data = get_storage_info()
        
        self.storage_tile.add_row("Total", data['root_total'])
        self.storage_tile.add_row("Used", data['root_used'])
        self.storage_tile.add_row("Free", data['root_free'])
        
        percent_ok = True
        if data['root_percent'] != NO_INFO:
            try:
                pct = float(data['root_percent'].replace('%', ''))
                percent_ok = pct < 90
            except:
                pass
        self.storage_tile.add_row("Use", data['root_percent'], is_value_ok=percent_ok)
    
    def update_network_tile(self):
        self.network_tile.clear_content()
        data = get_network_info()
        
        self.network_tile.add_row("Host", data['hostname'])
        self.network_tile.add_row("Local", data['ip_local'])
        self.network_tile.add_row("Ext", data['ip_external'][:15] if len(data['ip_external']) > 15 else data['ip_external'])
        self.network_tile.add_row("MAC", data['mac'][-8:] if len(data['mac']) > 8 else data['mac'])
    
    def update_voltage_tile(self):
        self.voltage_tile.clear_content()
        data = get_voltage_info()
        
        self.voltage_tile.add_row("Core", data['core'], f"{FACTORY_DEFAULTS['voltage_core']}V")
        self.voltage_tile.add_row("3.3V", data['rail_3v3'], f"{FACTORY_DEFAULTS['voltage_3v3']}V")
        self.voltage_tile.add_row("5V", data['rail_5v'], f"{FACTORY_DEFAULTS['voltage_5v']}V")
        self.voltage_tile.add_row("12V", data['rail_12v'], f"{FACTORY_DEFAULTS['voltage_12v']}V")
        
        status_ok = data['throttle_status'] == 'OK'
        self.voltage_tile.add_row("Stat", data['throttle_status'], is_value_ok=status_ok)
    
    def update_post_tile(self):
        logs = get_post_logs()
        self.post_tile.update_content(logs['dmesg'], logs['errors'])
    
    def show_full_info(self):
        """Show full system information dialog."""
        info = []
        info.append("=" * 50)
        info.append("ReBoot Labs DiagTool - Full System Report")
        info.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        info.append("=" * 50)
        
        # System
        sys_info = get_system_info()
        info.append("\n[SYSTEM]")
        for k, v in sys_info.items():
            info.append(f"  {k}: {v}")
        
        # CPU
        cpu = get_cpu_info()
        info.append("\n[CPU]")
        for k, v in cpu.items():
            info.append(f"  {k}: {v}")
        
        # GPU
        gpu = get_gpu_info()
        info.append("\n[GPU]")
        for k, v in gpu.items():
            info.append(f"  {k}: {v}")
        
        # RAM
        ram = get_ram_info()
        info.append("\n[RAM]")
        for k, v in ram.items():
            info.append(f"  {k}: {v}")
        
        # Storage
        storage = get_storage_info()
        info.append("\n[STORAGE]")
        for k, v in storage.items():
            if k != 'devices':
                info.append(f"  {k}: {v}")
        for dev in storage.get('devices', []):
            info.append(f"  Device: {dev['device']} -> {dev['mount']} ({dev['percent']})")
        
        # Network
        network = get_network_info()
        info.append("\n[NETWORK]")
        for k, v in network.items():
            if k != 'interfaces':
                info.append(f"  {k}: {v}")
        
        # Voltage
        voltage = get_voltage_info()
        info.append("\n[VOLTAGE]")
        for k, v in voltage.items():
            info.append(f"  {k}: {v}")
        
        # POST
        logs = get_post_logs()
        info.append("\n[POST/BOOT]")
        info.append(f"  boot_time: {logs['boot_time']}")
        info.append("  Recent dmesg:")
        for line in logs['dmesg'][-5:]:
            info.append(f"    {line[:60]}")
        
        info.append("\n" + "=" * 50)
        
        full_text = '\n'.join(info)
        
        # Show in message box (scrollable)
        msg = QMessageBox(self)
        msg.setWindowTitle("Full System Information")
        msg.setText("Full diagnostic report generated.")
        msg.setDetailedText(full_text)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
            }}
            QMessageBox QLabel {{
                color: {COLORS['neon_green']};
            }}
            QPushButton {{
                background-color: {COLORS['bg_tile']};
                color: {COLORS['neon_green']};
                border: 1px solid {COLORS['neon_green']};
                padding: 5px 15px;
            }}
        """)
        
        # Add print button
        print_btn = msg.addButton("🖨️ Print", QMessageBox.ActionRole)
        msg.addButton(QMessageBox.Ok)
        
        msg.exec_()
        
        if msg.clickedButton() == print_btn:
            self.print_report(full_text)
    
    def print_report(self, text):
        """Print report to file or printer."""
        # Save to file
        report_dir = os.path.expanduser('~/reports')
        os.makedirs(report_dir, exist_ok=True)
        
        filename = f"diagtool_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(report_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(text)
        
        logging.info(f"Report saved: {filepath}")
        
        # Try to print (if lp command available)
        try:
            subprocess.run(['lp', filepath], check=True, capture_output=True)
            QMessageBox.information(self, "Print", f"Report sent to printer!\nSaved: {filepath}")
        except:
            QMessageBox.information(self, "Print", f"Report saved to:\n{filepath}")
    
    def export_report(self):
        """Export report to JSON."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system': get_system_info(),
            'cpu': get_cpu_info(),
            'gpu': get_gpu_info(),
            'ram': get_ram_info(),
            'storage': get_storage_info(),
            'network': get_network_info(),
            'voltage': get_voltage_info(),
            'post_logs': get_post_logs(),
        }
        
        report_dir = os.path.expanduser('~/reports')
        os.makedirs(report_dir, exist_ok=True)
        
        filename = f"diagtool_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(report_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logging.info(f"Report exported: {filepath}")
        QMessageBox.information(self, "Export", f"Report exported to:\n{filepath}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(COLORS['bg_dark']))
    palette.setColor(QPalette.WindowText, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.Base, QColor(COLORS['bg_tile']))
    palette.setColor(QPalette.Text, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.Button, QColor(COLORS['bg_tile']))
    palette.setColor(QPalette.ButtonText, QColor(COLORS['neon_green']))
    app.setPalette(palette)
    
    window = DiagToolWindow()
    window.show()
    
    logging.info("DiagTool PyQt5 started")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
