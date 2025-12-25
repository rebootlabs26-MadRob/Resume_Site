# SkullGUI DiagTool - Raspberry Pi System Monitor

A cyberpunk-themed Tkinter diagnostic GUI that displays real-time system metrics in neon-styled tiles.

## Features

- **Adaptive Scaling**: Automatically scales for different screen sizes (320x480 TFT to high-res displays)
- **Real-time Metrics**: CPU, RAM, GPU, voltages, and system uptime
- **Neon UI**: Cyberpunk-themed interface with green borders and monospace fonts
- **POST Log Feed**: Scrollable timestamped log with boot messages
- **Report Generation**: Save full system reports or error-only reports
- **Periodic Updates**: Clock updates every second, system data every 3 seconds

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Add a background image at `assets/reboot_lab_bg.png` for the full cyberpunk experience

## Usage

Run the application:
```bash
python SkullGUI_DiagTool.py
```

## Controls

- **SAVE FULL REPORT**: Generate a complete system diagnostic report
- **SAVE ERROR REPORT**: Save only error/warning entries from the POST log
- **REFRESH**: Manually refresh all system metrics
- **EXIT**: Close the application
- **DONT PUSH**: Easter egg button (you've been warned!)

## Reports

Reports are saved in the `reports/` directory with timestamps:
- `full_YYYYMMDD_HHMMSS.txt` - Complete system snapshot
- `errors_YYYYMMDD_HHMMSS.txt` - Filtered error log entries

## System Requirements

- Python 3.7+
- tkinter (usually included with Python)
- psutil (for system metrics)
- Pillow (for image handling)

## Screen Support

- **TFT Displays**: 320x480 (automatically detected)
- **Standard Monitors**: 720x1080 and higher
- **Responsive Design**: Scales UI elements proportionally
