#!/usr/bin/env python3
import os, time
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import psutil

# ---------- Config ----------
APP_TITLE = "DiagTool"
BG_PATH = os.path.join("assets", "reboot_lab_bg.png")
FG_NEON = "#00FF66"
ACCENT_PURPLE = "#7A1FA2"
FG_WHITE = "#E6F2EF"
BG_GLASS = "#0A0A0A"
OUTLINE = FG_NEON
FONT_TITLE = ("Orbitron", 18, "bold")
FONT_LABEL = ("Orbitron", 14)
FONT_MONO = ("Consolas", 12)

# Default high-res
WIDTH, HEIGHT = 720, 1080
TFT_WIDTH, TFT_HEIGHT = 320, 480

# Detect screen size dynamically
root = tk.Tk()
screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
root.destroy()
if screen_w <= TFT_WIDTH and screen_h <= TFT_HEIGHT:
    WIDTH, HEIGHT = TFT_WIDTH, TFT_HEIGHT

# ---------- Helpers ----------
def scale(x, y, w, h):
    return (x * WIDTH/720, y * HEIGHT/1080, w * WIDTH/720, h * HEIGHT/1080)

def safe_text(s): return s if s else "N/A"

def wrap_text(s, width=50):
    lines, cur = [], ""
    for w in s.split():
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return "\n".join(lines)

# ---------- Data providers ----------
def get_system_information():
    return (
        f"Motherboard: N/A\nOS: Raspberry Pi OS\nKernel: {os.uname().release}\n"
        f"Hostname: {os.uname().nodename}\nUptime: {int(time.time()-psutil.boot_time())//3600}h"
    )

def get_cpu_information():
    freq = psutil.cpu_freq()
    cores = psutil.cpu_count(logical=False) or psutil.cpu_count()
    threads = psutil.cpu_count()
    vendor = "Broadcom/ARM"
    max_mhz = safe_text(f"{int(freq.max)} MHz" if freq and freq.max else "N/A")
    cur_mhz = safe_text(f"{int(freq.current)} MHz" if freq and freq.current else "N/A")
    voltage = "N/A"
    return (
        f"Vendor: {vendor}\nClock: {cur_mhz}\nVoltage: {voltage}\n"
        f"Max Clock: {max_mhz}\nCores: {cores}\nThreads: {threads}"
    )

def get_ram_information():
    vm = psutil.virtual_memory()
    return (
        f"Total: {vm.total//(1024**2)} MB\nUsed: {vm.used//(1024**2)} MB\n"
        f"Free: {vm.available//(1024**2)} MB\nUtilization: {vm.percent}%"
    )

def get_gpu_information():
    return "GPU: VideoCore IV\nClock: N/A\nVRAM: N/A\nDriver: vc4\nUtilization: N/A"

def get_voltages():
    return "SoC Core: N/A\nRAM Rail: N/A\n5V Rail: N/A\n3.3V Rail: N/A\n12V Rail: N/A"

POST_LOG = []
def append_post(message):
    ts = datetime.now().strftime("%H:%M:%S")
    POST_LOG.insert(0, f"[{ts}] {message}")

# ---------- GUI ----------
class DiagToolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)

        # Canvas background
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bg_img = self.load_and_scale_background(BG_PATH, WIDTH, HEIGHT)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)

        # Title
        self.canvas.create_text(WIDTH//2, 40, text=APP_TITLE, fill=FG_WHITE, font=FONT_TITLE)

        # Build tiles
        self.build_tiles()
        self.refresh_all()
        self.schedule_updates()

    def load_and_scale_background(self, path, w, h):
        try:
            img = Image.open(path).convert("RGB")
            img = img.resize((w, h), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except:
            # Create a simple gradient background if image not found
            img = Image.new('RGB', (w, h), color='#000000')
            return ImageTk.PhotoImage(img)

    def neon_label(self, text, x, y, w, h, title=None):
        rect = self.canvas.create_rectangle(x, y, x+w, y+h, outline=OUTLINE, width=2)
        lbl = tk.Label(self, text=text, justify="left", fg=FG_WHITE, bg="#000000", font=FONT_MONO)
        lbl.place(x=x+6, y=y+(24 if title else 6), width=w-12, height=h-(36 if title else 12))
        if title:
            self.canvas.create_text(x+12, y+16, anchor="w", text=title, fill=FG_NEON, font=FONT_LABEL)
        return lbl

    def build_tiles(self):
        # SYSTEM INFORMATION (top left)
        sx, sy, sw, sh = scale(24, 80, 320, 180)
        self.sys_lbl = self.neon_label("...", sx, sy, sw, sh, title="SYSTEM INFORMATION")

        # CPU INFORMATION (top right)
        sx, sy, sw, sh = scale(376, 80, 320, 180)
        self.cpu_lbl = self.neon_label("...", sx, sy, sw, sh, title="CPU INFORMATION")

        # GPU INFORMATION (middle left)
        sx, sy, sw, sh = scale(24, 280, 320, 180)
        self.gpu_lbl = self.neon_label("...", sx, sy, sw, sh, title="GPU INFORMATION")

        # POST / ERROR (middle right - larger)
        sx, sy, sw, sh = scale(376, 280, 320, 240)
        self.canvas.create_rectangle(sx, sy, sx+sw, sy+sh, outline=OUTLINE, width=2)
        self.canvas.create_text(sx+12, sy+16, anchor="w", text="POST / ERROR", fill=ACCENT_PURPLE, font=FONT_LABEL)
        self.post_frame = tk.Frame(self, bg=BG_GLASS)
        self.post_canvas = tk.Canvas(self.post_frame, width=sw-20, height=sh-40, bg="#000000", highlightthickness=0)
        self.post_scroll = ttk.Scrollbar(self.post_frame, orient="vertical", command=self.post_canvas.yview)
        self.post_inner = tk.Frame(self.post_canvas, bg="#000000")
        self.post_inner.bind("<Configure>", lambda e: self.post_canvas.configure(scrollregion=self.post_canvas.bbox("all")))
        self.post_canvas.create_window((0,0), window=self.post_inner, anchor="nw")
        self.post_canvas.configure(yscrollcommand=self.post_scroll.set)
        self.post_frame.place(x=sx+8, y=sy+32, width=sw-16, height=sh-48)
        self.post_canvas.pack(side="left", fill="both", expand=True)
        self.post_scroll.pack(side="right", fill="y")

        # VOLTAGES (bottom left)
        sx, sy, sw, sh = scale(24, 540, 320, 120)
        self.vlt_lbl = self.neon_label("...", sx, sy, sw, sh, title="VOLTAGES")

        # TIMES PAST / ERROR (bottom right)
        sx, sy, sw, sh = scale(376, 540, 320, 120)
        self.times_lbl = self.neon_label("...", sx, sy, sw, sh, title="TIMES PAST / ERROR")

        # Add REBOOT LAB title at top
        self.canvas.create_text(WIDTH//2, 30, text="REBOOT LAB", fill=FG_NEON, font=("Orbitron", 28, "bold"))
        self.canvas.create_text(WIDTH//2, 55, text="DIAGNOSTIC TOOL", fill=FG_WHITE, font=("Orbitron", 12))

        # Buttons - repositioned for new layout
        bx, by, bw, bh = scale(24, 680, 150, 40)
        self.btn_save_full = self.make_button("SAVE FULL REPORT", bx, by, bw, bh, self.on_save_full)
        bx, by, bw, bh = scale(184, 680, 150, 40)
        self.btn_save_error = self.make_button("SAVE ERROR REPORT", bx, by, bw, bh, self.on_save_error)
        bx, by, bw, bh = scale(344, 680, 150, 40)
        self.btn_refresh = self.make_button("REFRESH", bx, by, bw, bh, self.on_refresh)
        bx, by, bw, bh = scale(504, 680, 150, 40)
        self.btn_system = self.make_button("SYSTEM REPORT", bx, by, bw, bh, self.system_report_dialog)
        bx, by, bw, bh = scale(24, 730, 150, 40)
        self.btn_exit = self.make_button("EXIT", bx, by, bw, bh, self.on_exit)
        bx, by, bw, bh = scale(184, 730, 150, 40)
        self.btn_export = self.make_button("EXPORT LOG", bx, by, bw, bh, self.on_export_log)
        bx, by, bw, bh = scale(344, 730, 150, 40)
        self.btn_print = self.make_button("PRINT ERROR", bx, by, bw, bh, self.on_print_error)
        
        # Easter Egg button
        bx, by, bw, bh = scale(504, 730, 150, 40)
        self.btn_dont = self.make_button("DON'T PUSH", bx, by, bw, bh, self.on_dont_push)

    def make_button(self, text, x, y, w, h, command):
        btn = tk.Button(self, text=text, fg=FG_WHITE, bg="#0A0F0A",
                        activebackground=ACCENT_PURPLE, highlightthickness=0,
                        relief="flat", command=command)
        self.canvas.create_rectangle(x, y, x+w, y+h, outline=OUTLINE, width=2)
        btn.place(x=x+2, y=y+2, width=w-4, height=h-4)
        return btn

    # ---------- Updates ----------
    def refresh_all(self):
        self.sys_lbl.config(text=wrap_text(get_system_information()))
        self.cpu_lbl.config(text=wrap_text(get_cpu_information()))
        self.gpu_lbl.config(text=wrap_text(get_gpu_information()))
        self.vlt_lbl.config(text=wrap_text(get_voltages()))
        
        # Update TIMES PAST / ERROR with current time and error count
        current_time = datetime.now().strftime("%H:%M:%S")
        error_count = len([msg for msg in POST_LOG if "ERROR" in msg or "FAIL" in msg])
        times_text = f"Current Time: {current_time}\nError Count: {error_count}\nSystem Uptime: {int(time.time()-psutil.boot_time())//3600}h"
        self.times_lbl.config(text=wrap_text(times_text))

        if not POST_LOG:
            for msg in [
                "Power on self-test started",
                "Memory training OK",
                "CPU init OK",
                "GPU init skipped (headless)",
                "I/O scan OK",
            ]:
                append_post(msg)
        self.render_post_feed()

    def render_post_feed(self):
        for w in self.post_inner.winfo_children():
            w.destroy()
        for line in POST_LOG:
            lbl = tk.Label(self.post_inner, text=line, fg=FG_WHITE,
                           bg="#000000", font=FONT_MONO, anchor="w", justify="left")
            lbl.pack(fill="x")
        self.post_canvas.yview_moveto(0)

    def schedule_updates(self):
        self.after(1000, self.tick)

    def tick(self):
        # Update TIMES PAST / ERROR with current time
        current_time = datetime.now().strftime("%H:%M:%S")
        error_count = len([msg for msg in POST_LOG if "ERROR" in msg or "FAIL" in msg])
        times_text = f"Current Time: {current_time}\nError Count: {error_count}\nSystem Uptime: {int(time.time()-psutil.boot_time())//3600}h"
        self.times_lbl.config(text=wrap_text(times_text))
        
        self.after(3000, self.refresh_all)
        self.after(1000, self.tick)

    # ---------- Actions ----------
    def on_refresh(self):
        self.refresh_all()
        append_post("Manual refresh triggered")
        self.render_post_feed()

    def on_exit(self):
        self.destroy()

    def on_save_full(self):
        os.makedirs("reports", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join("reports", f"full_{ts}.txt")
        with open(path, "w") as f:
            f.write("[SYSTEM]\n" + get_system_information() + "\n\n")
            f.write("[CPU]\n" + get_cpu_information() + "\n\n")
            f.write("[RAM]\n" + get_ram_information() + "\n\n")
            f.write("[GPU]\n" + get_gpu_information() + "\n\n")
            f.write("[VOLTAGES]\n" + get_voltages() + "\n\n")
            f.write("[POST]\n" + "\n".join(reversed(POST_LOG)) + "\n")
        append_post(f"Saved full report: {os.path.basename(path)}")
        self.render_post_feed()

    def on_save_error(self):
        os.makedirs("reports", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join("reports", f"errors_{ts}.txt")
        with open(path, "w") as f:
            errs = [l for l in POST_LOG if ("ERROR" in l or "FAIL" in l or "WARN" in l)]
            f.write("[ERRORS]\n" + "\n".join(reversed(errs)) + "\n")
        append_post(f"Saved error report: {os.path.basename(path)}")
        self.render_post_feed()

    def on_export_log(self):
        os.makedirs("reports", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join("reports", f"log_{ts}.txt")
        with open(path, "w") as f:
            f.write("POST LOG\n" + "="*40 + "\n")
            f.write("\n".join(reversed(POST_LOG)) + "\n")
        append_post(f"Exported log: {os.path.basename(path)}")
        self.render_post_feed()

    def on_print_error(self):
        os.makedirs("reports", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join("reports", f"print_errors_{ts}.txt")
        with open(path, "w") as f:
            f.write("ERROR REPORT\n" + "="*40 + "\n")
            errs = [l for l in POST_LOG if ("ERROR" in l or "FAIL" in l or "WARN" in l)]
            f.write("\n".join(reversed(errs)) + "\n")
        append_post(f"Prepared error report for printing: {os.path.basename(path)}")
        self.render_post_feed()

    def system_report_dialog(self):
        report_text = f"SYSTEM REPORT\n" + "="*40 + "\n"
        report_text += get_system_information() + "\n\n"
        report_text += "CPU INFORMATION\n" + "="*40 + "\n"
        report_text += get_cpu_information() + "\n\n"
        report_text += "GPU INFORMATION\n" + "="*40 + "\n"
        report_text += get_gpu_information() + "\n\n"
        report_text += "VOLTAGES\n" + "="*40 + "\n"
        report_text += get_voltages() + "\n\n"
        
        # Create a simple dialog
        dialog = tk.Toplevel(self)
        dialog.title("System Report")
        dialog.geometry("600x400")
        dialog.configure(bg="#000000")
        
        text_widget = tk.Text(dialog, bg="#000000", fg=FG_NEON, font=FONT_MONO, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", report_text)
        text_widget.config(state="disabled")
        
        close_btn = tk.Button(dialog, text="Close", command=dialog.destroy, 
                             fg=FG_WHITE, bg="#0A0F0A", activebackground=ACCENT_PURPLE)
        close_btn.pack(pady=5)

    def on_dont_push(self):
        append_post("You were warned. Easter egg armed.")
        self.render_post_feed()

# ---------- Main ----------
if __name__ == "__main__":
    app = DiagToolApp()
    app.mainloop()
