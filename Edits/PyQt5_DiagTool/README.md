# ReBoot Labs DiagTool - PyQt5 Edition

Cyberpunk-themed diagnostic tool for Raspberry Pi 3B + 3.5" TFT (480x320)

## Features

- **Neon cyberpunk styling** with glow effects
- **6 data tiles**: CPU, GPU, RAM, Storage, Network, Voltage
- **Split POST/Errors tile**: POST log on left, errors only on right
- **Active vs Factory Default values** displayed in each tile
- **Auto-refresh** every 3 seconds
- **Full System Info** button with print option
- **JSON export** for reports

## Requirements

```bash
sudo apt install -y python3-pyqt5 python3-psutil
```

## Running

```bash
python3 DiagTool_PyQt5.py
```

## Tile Layout (480x320)

```
┌────────────────────────────────────────────────┐
│         ⚡ ReBoot Labs DiagTool ⚡              │
├──────────────┬──────────────┬──────────────────┤
│     CPU      │     GPU      │       RAM        │
│ Temp: 45°C   │ Temp: 45°C   │ Total: 1024MB    │
│ Freq: 1400MHz│ Freq: 400MHz │ Used: 512MB      │
│ Usage: 15%   │ Mem: 64MB    │ Free: 512MB      │
├──────────────┼──────────────┼──────────────────┤
│   STORAGE    │   NETWORK    │     VOLTAGE      │
│ Total: 32GB  │ Host: DiagTool│ Core: 1.20V     │
│ Used: 8GB    │ IP: 192.168.x│ 3.3V: SrryNoInfo │
│ Free: 24GB   │ MAC: xx:xx:xx│ 5V: SrryNoInfo   │
├──────────────┴──────────────┴──────────────────┤
│  POST LOG          │          ERRORS           │
│  [boot messages]   │  None / [error list]      │
├────────────────────────────────────────────────┤
│  [⟳ REFRESH]  [📋 FULL INFO]  [💾 EXPORT]     │
└────────────────────────────────────────────────┘
```

## ADS1115 Integration (Coming Soon)

When ADS1115 arrives, uncomment the voltage reading code in `get_voltage_info()`:

```python
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan0 = AnalogIn(ads, ADS.P0)  # 12V (with divider)
chan1 = AnalogIn(ads, ADS.P1)  # 5V
chan2 = AnalogIn(ads, ADS.P2)  # 3.3V
```

## Files

- `DiagTool_PyQt5.py` - Main application
- `~/reports/` - Saved reports (JSON and TXT)
- `~/diagtool_pyqt5.log` - Application log
