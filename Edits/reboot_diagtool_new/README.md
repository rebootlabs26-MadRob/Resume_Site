# DiagTool - Raspberry Pi Diagnostic Tool

A comprehensive system monitoring and diagnostic tool for Raspberry Pi with a cyberpunk-themed GUI.

## Features

- **System Information**: OS details, kernel version, hostname, uptime
- **CPU Monitoring**: Clock speed, cores, threads, vendor info
- **RAM Statistics**: Total, used, free memory, utilization percentage
- **GPU Information**: VideoCore IV details and driver info
- **Voltage Monitoring**: System rail voltages (placeholder values)
- **Real-time Clock**: Local time display
- **POST Log**: Power-on self-test and error messages
- **Report Generation**: Save full system reports or error-only reports
- **Responsive Design**: Automatically scales for different screen sizes

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create assets directory and add background image (optional):
```bash
mkdir assets
# Add reboot_lab_bg.png to assets/ folder (or app will use solid background)
```

3. Run the application:
```bash
python diagtool_fixed.py
```

## Dependencies

- Python 3.6+
- tkinter (usually included with Python)
- PIL/Pillow for image handling
- psutil for system monitoring

## Usage

- **REFRESH**: Manually refresh all system information
- **SAVE FULL REPORT**: Export complete system diagnostics to reports/
- **SAVE ERROR REPORT**: Export only errors and warnings
- **EXIT**: Close the application
- **DONT PUSH**: Easter egg button

## Notes

- The tool automatically detects screen size and scales accordingly
- Background image is optional - will use solid background if missing
- Reports are saved with timestamps in the `reports/` directory
- Designed for Raspberry Pi but works on any Linux system with psutil
