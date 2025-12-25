# Fire HD 8 (DOUGLAS) Recovery State - December 16, 2025

## Current Status: BRICKED PRELOADER - NEEDS TP28 SHORT

### Device Info
- **Model:** Fire HD 8 2017 (7th Gen)
- **Codename:** DOUGLAS
- **Chip:** MediaTek MT8163
- **Current USB ID:** 0e8d:2000 (Preloader mode - STUCK HERE)
- **Target USB ID:** 0e8d:0003 (BROM mode - NEED THIS)

### Security Status (ALL DISABLED - Good)
- SBC: False
- SLA: False  
- DAA: False
- Mem read/write auth: False

### What's Wrong
The preloader is **zombie** - responds to initial USB handshake but won't execute commands. All mtkclient commands fail with empty responses or struct.error.

### What's Been Tried (DON'T REPEAT)
| Command | Result |
|---------|--------|
| mtkclient crash | Crashes DA, device stays in preloader |
| mtkclient payload | Same - hangs |
| mtkclient plstage | DA_IMAGE_SIG_VERIFY_FAIL |
| mtkclient stage | Hangs after device info |
| mtkclient meta FASTBOOT | Timeout |
| mtkclient peek | struct.error - empty response |
| mtkclient w preloader | "Please disconnect" message |

### Fix Applied to mtkclient
**File:** `~/mtkclient/mtkclient/Library/mtk_preloader.py`  
**Line 205:** Commented out watchdog disable that was hanging
```python
#            self.setreg_disablewatchdogtimer(self.config.hwcode, self.config.hwver)  # D4
```

### Files Ready on Pi
- `~/amonet/bin/preloader.bin` (138924 bytes)
- `~/amonet/bin/lk.bin`
- `~/amonet/bin/twrp.img`
- `~/amonet/bin/tz.img`
- `~/mtkclient/` (modified)

---

## RECOVERY PROCEDURE (WHEN READY)

### Step 1: TP28 Short to Get BROM Mode
1. Unplug USB from tablet
2. Get tweezers/paperclip
3. Short **TP28** test point to ground
4. **While holding short** → plug USB into tablet
5. Run: `lsusb | grep 0e8d`
6. Should show: **0e8d:0003** (BROM)
7. Release short

### Step 2: If BROM Mode (0e8d:0003) Achieved
```bash
sudo python3 ~/mtkclient/mtk.py stage
```
This uploads payload and enables flash access.

### Step 3: Flash Preloader
```bash
sudo python3 ~/mtkclient/mtk.py w preloader ~/amonet/bin/preloader.bin
```

### Step 4: Flash Everything Else (if needed)
```bash
sudo python3 ~/mtkclient/mtk.py w lk ~/amonet/bin/lk.bin
```

---

## TP28 Location
- On the **back** of the tablet mainboard
- Near the battery connector area
- Small test point - needs precision short to ground

## Notes
- TP28 short WAS successful before (got 0e8d:0003)
- The watchdog fix in mtkclient is NEW - haven't tried TP28 + mtkclient stage combo yet
- Device repeatedly boots to 0e8d:2000 without TP28 short
