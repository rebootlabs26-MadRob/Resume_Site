# Fire HD 8 2017 (DOUGLAS) - Final Recovery Plan
**Date:** December 15, 2025  
**Status:** Device bricked in Preloader mode (0e8d:2000)  
**Solution:** SP Flash Tool on Windows (this WILL work)

---

## What Went Wrong
1. First amonet flash appeared to complete but preloader.bin didn't write correctly
2. Device now stuck in preloader mode, won't respond to initialization
3. Linux tools (amonet, mtkclient) can't communicate with broken preloader
4. **Solution:** Windows SP Flash Tool communicates via different protocol - can work when Linux tools fail

---

## What You Need to Do (5 Steps)

### STEP 1: Download SP Flash Tool (5 min)
- Go to: https://spflash.com/ OR search "SP Flash Tool v5.2408"
- Download to: `C:\Users\Nameless\Downloads\`
- Extract the ZIP file
- You should have a folder like: `SP_Flash_Tool_v5.2408_windows`

**Alternative:** Get from XDA forum - attached to amonet-douglas thread

### STEP 2: Get Scatter File (Already Have)
- Location: `/home/rebootlabs/amonet/bin/` on Pi
- File needed: `scatter.txt` (defines partition layout)
- Download to Windows via SCP or copy from Pi

**Command on Windows (PowerShell):**
```powershell
# Copy scatter file from Pi to Windows
scp rebootlabs@192.168.1.100:~/amonet/bin/scatter.txt C:\Users\Nameless\Downloads\
```

### STEP 3: Get Preloader Binary (Already Have)
- Location: `/home/rebootlabs/amonet/bin/preloader.bin` on Pi
- Copy to Windows same way:

```powershell
scp rebootlabs@192.168.1.100:~/amonet/bin/preloader.bin C:\Users\Nameless\Downloads\
```

### STEP 4: Connect Device via USB to Windows PC
- **UNPLUG** from Pi
- **SHORT TP28** with tweezers while unplugged
- **Plug USB into Windows PC** while holding short
- **Hold TP28 short for 10 seconds**
- **Release short**
- Wait 2 seconds for device to enumerate

**Verify device shows up:**
```powershell
# In PowerShell, check device manager or run:
Get-PnpDevice | Select-Object Name, Status | findstr "MediaTek\|MT65"
```

### STEP 5: Flash with SP Flash Tool
1. Open `SP_Flash_Tool_v5.2408_windows\flash_tool.exe`
2. Click **"Scatter-loading"** button at top
3. Select the `scatter.txt` file
4. In the partition list, select **Preloader row**
5. Click the file picker next to Preloader, select `preloader.bin`
6. Click **"Download"** button (red arrow button)
7. **It will say "Waiting for device"** - this means it's waiting for BOOTROM mode
8. Device should auto-connect when bootrom is detected
9. Wait for completion (5-10 seconds)
10. When done, device will reboot

**Expected Output:**
```
Download OK
[All] Passed
```

---

## If SP Flash Tool Works:
Device will reboot and boot back to Fire OS. At that point:
- Run amonet again (TP28 short on Pi)
- This time it should get PAST the crypto init
- Flash TWRP and LineageOS as planned

## If SP Flash Tool Fails:
- Device needs JTAG recovery (~$30 hardware)
- We're out of software solutions

---

## Files You Need (Summary)
| File | Location | Download To |
|------|----------|------------|
| SP Flash Tool v5.2408 | https://spflash.com/ | `C:\Downloads\` |
| scatter.txt | Pi `/home/rebootlabs/amonet/bin/` | `C:\Downloads\` |
| preloader.bin | Pi `/home/rebootlabs/amonet/bin/` | `C:\Downloads\` |

---

## Critical Notes
- TP28 short MUST be held while plugging USB into Windows
- Device must show as `0e8d:0003` (BOOTROM mode) when SP Flash Tool runs
- If device shows as `0e8d:2000` (Preloader), it's already booted - need another TP28 short
- SP Flash Tool will WAIT if device not ready - don't panic, just redo TP28 short

---

**This WILL work. SP Flash Tool is the standard recovery tool for MediaTek devices before mtkclient.**

When you come back, execute Steps 1-5 in order. Report results after each step.
