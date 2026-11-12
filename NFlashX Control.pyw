# -*- coding: utf-8 -*-
"""NFlashX Control — app quản lý 1-click (không lag: mọi thao tác chạy nền)."""
import os, sys, socket, subprocess, threading, time, webbrowser
import tkinter as tk
from tkinter import ttk

ROOT = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = "127.0.0.1", 8600
LIVE_URL = "https://8600-agq4wbs7wjamf4ucmhvjkbvu4y.instabox.tech"  # bản chạy thật trên cloud
CREATE_NO_WINDOW = 0x08000000
DETACHED = 0x00000008 | 0x00000200

def server_up():
    try:
        with socket.create_connection((HOST, PORT), timeout=0.5):
            return True
    except OSError:
        return False

def find_server_pid():
    try:
        out = subprocess.check_output(["netstat", "-ano"],
            creationflags=CREATE_NO_WINDOW, text=True, errors="ignore")
        for line in out.splitlines():
            if f"{HOST}:{PORT}" in line and "LISTENING" in line:
                return line.split()[-1]
    except Exception:
        pass
    return None

def load_secrets_env():
    """Doc secrets.env (dang batch: set KEY=value) — truyen vao server process."""
    env = dict(os.environ)
    p = os.path.join(ROOT, "secrets.env")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.lower().startswith("set ") and "=" in line:
                    k, _, v = line[4:].partition("=")
                    env[k.strip()] = v.strip()
    return env

def start_server():
    log = open(os.path.join(ROOT, "data", "server_app.log"), "ab")
    subprocess.Popen([sys.executable, "-I", "server.py"], cwd=ROOT,
                     stdout=log, stderr=log, env=load_secrets_env(),
                     creationflags=CREATE_NO_WINDOW)

def stop_server():
    pid = find_server_pid()
    if pid:
        subprocess.Popen(["taskkill", "/PID", pid, "/F"], creationflags=CREATE_NO_WINDOW)

def open_admin(): webbrowser.open(LIVE_URL + "/admin.html")
def open_platform(): webbrowser.open(LIVE_URL + "/platform.html")

STARTUP_DIR = os.path.join(os.environ["APPDATA"],
    "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
AUTOSTART_BAT = os.path.join(STARTUP_DIR, "NFlashX_autostart.bat")

def autostart_on():
    with open(AUTOSTART_BAT, "w", encoding="utf-8") as f:
        f.write(f'@echo off\r\ncd /d "{ROOT}"\r\nstart "" /b "{sys.executable}" -I server.py\r\n')

def autostart_off():
    if os.path.exists(AUTOSTART_BAT):
        os.remove(AUTOSTART_BAT)

def autostart_enabled():
    return os.path.exists(AUTOSTART_BAT)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NFlashX Control")
        self.geometry("380x340")
        self.configure(bg="#04060a")
        self.resizable(False, False)
        self.busy = False
        tk.Label(self, text="NFlashX CONTROL", bg="#04060a", fg="#25e39a",
                 font=("Segoe UI", 16, "bold")).pack(pady=(16, 2))
        tk.Label(self, text="Quản lý server API — 1-click", bg="#04060a", fg="#5c6975",
                 font=("Segoe UI", 9)).pack()
        self.dot = tk.Canvas(self, width=18, height=18, bg="#04060a", highlightthickness=0)
        self.dot.pack(pady=(12, 0))
        self.status = tk.Label(self, text="KIỂM TRA…", bg="#04060a", fg="#96a3b2",
                               font=("Segoe UI", 11, "bold"))
        self.status.pack()
        self.hint = tk.Label(self, text="", bg="#04060a", fg="#5c6975",
                             font=("Segoe UI", 9))
        self.hint.pack()
        style = ttk.Style(self); style.theme_use("clam")
        style.configure("NF.TButton", background="#0c1016", foreground="#f2f6f9",
                        bordercolor="#1f2a36", padding=8)
        style.map("NF.TButton", background=[("active", "#141c26")])
        f = ttk.Frame(self, style="NF.TFrame"); f.pack(pady=10, padx=20, fill="x")
        self.b_start = ttk.Button(f, text="▶  START SERVER", command=self.do_start, style="NF.TButton")
        self.b_stop = ttk.Button(f, text="■  STOP SERVER", command=self.do_stop, style="NF.TButton")
        self.b_admin = ttk.Button(f, text="🛡  MỞ ADMIN CONSOLE (LIVE)", command=open_admin, style="NF.TButton")
        self.b_plat = ttk.Button(f, text="🌐  MỞ PLATFORM (LIVE)", command=open_platform, style="NF.TButton")
        for b in (self.b_start, self.b_stop, self.b_admin, self.b_plat):
            b.pack(fill="x", pady=3, ipady=4)
        self.autovar = tk.BooleanVar(value=autostart_enabled())
        ttk.Checkbutton(self, text="Khởi động server cùng Windows", variable=self.autovar,
                        command=self.toggle_autostart).pack(pady=(2, 0))
        tk.Label(self, text="Đóng app này KHÔNG tắt server.", bg="#04060a", fg="#3d4a56",
                 font=("Segoe UI", 8)).pack(side="bottom", pady=6)
        self.tick()

    # ---------- UI helpers (gọi từ worker thread qua after) ----------
    def set_state(self, up):
        color = "#25e39a" if up else "#ff6b6b"
        self.dot.delete("all")
        self.dot.create_oval(3, 3, 15, 15, fill=color, outline="")
        self.status.config(text="SERVER ĐANG CHẠY" if up else "SERVER ĐÃ DỪNG", fg=color)

    def set_busy(self, msg):
        self.status.config(text=msg, fg="#ffb84d")
        for b in (self.b_start, self.b_stop):
            b.state(["disabled"])

    def set_idle(self, up):
        self.busy = False
        for b in (self.b_start, self.b_stop):
            b.state(["!disabled"])
        self.set_state(up)
        self.hint.config(text="")

    # ---------- workers (chạy nền, UI không treo) ----------
    def do_start(self):
        if self.busy: return
        self.busy = True
        self.set_busy("ĐANG KHỞI ĐỘNG…")
        threading.Thread(target=self._start_worker, daemon=True).start()

    def _start_worker(self):
        if not server_up():
            start_server()
        for _ in range(40):
            time.sleep(0.25)
            if server_up():
                break
        self.after(0, lambda: self.set_idle(server_up()))

    def do_stop(self):
        if self.busy: return
        self.busy = True
        self.set_busy("ĐANG DỪNG…")
        threading.Thread(target=self._stop_worker, daemon=True).start()

    def _stop_worker(self):
        stop_server()
        for _ in range(25):
            time.sleep(0.25)
            if not server_up():
                break
        self.after(0, lambda: self.set_idle(server_up()))

    def toggle_autostart(self):
        autostart_on() if self.autovar.get() else autostart_off()
        self.hint.config(text="Autostart: " + ("BẬT" if autostart_enabled() else "TẮT"))

    def tick(self):
        if not self.busy:
            threading.Thread(target=self._check, daemon=True).start()
        self.after(1500, self.tick)

    def _check(self):
        up = server_up()
        self.after(0, lambda: (self.set_state(up) if not self.busy else None))

if __name__ == "__main__":
    if "--autostart" in sys.argv and server_up():
        sys.exit(0)
    App().mainloop()
