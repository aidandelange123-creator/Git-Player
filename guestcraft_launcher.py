"""GuestCraft - a legal Windows helper launcher for Minecraft Java Edition.

This app does NOT bypass login/payment. It opens the official launcher only.
"""

from __future__ import annotations

import json
import os
import random
import string
import subprocess
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

APP_TITLE = "GuestCraft Launcher"
WINDOW_SIZE = "860x560"
DEFAULT_SESSION_MINUTES = 60
SETTINGS_PATH = Path("guestcraft_settings.json")


class GuestCraftApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(820, 520)

        self.tracked_process: Optional[subprocess.Popen] = None
        self.remaining_seconds = 0
        self.timer_job: Optional[str] = None
        self.last_launch_ts = 0.0
        self.logs: list[str] = []
        self.name_history: list[str] = []

        self.prefix_var = tk.StringVar(value="Guest")
        self.length_var = tk.IntVar(value=6)
        self.ambiguous_var = tk.BooleanVar(value=True)
        self.auto_copy_var = tk.BooleanVar(value=False)
        self.beep_var = tk.BooleanVar(value=True)
        self.session_minutes_var = tk.IntVar(value=DEFAULT_SESSION_MINUTES)

        self.name_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready")
        self.timer_var = tk.StringVar(value="Session timer: not running")
        self.launch_mode_var = tk.StringVar(value="Launch mode: unknown")

        self._build_ui()
        self.load_settings()
        self.on_randomize()
        self.refresh_launcher_status()

    # ---------- Helpers ----------
    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}"
        self.logs.append(line)
        self.log_box.config(state="normal")
        self.log_box.insert("end", line + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    @staticmethod
    def _build_charset(exclude_ambiguous: bool) -> str:
        chars = string.ascii_uppercase + string.digits
        if exclude_ambiguous:
            for bad in "0O1I":
                chars = chars.replace(bad, "")
        return chars

    def random_guest_name(self) -> str:
        prefix = self.prefix_var.get().strip() or "Guest"
        length = max(3, min(16, int(self.length_var.get())))
        chars = self._build_charset(self.ambiguous_var.get())
        token = "".join(random.choices(chars, k=length))
        return f"{prefix}_{token}"

    @staticmethod
    def known_launcher_paths() -> list[Path]:
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        program_files = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
        program_files_x86 = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)"))
        return [
            local / "Programs/Minecraft Launcher/MinecraftLauncher.exe",
            program_files / "Minecraft Launcher/MinecraftLauncher.exe",
            program_files_x86 / "Minecraft Launcher/MinecraftLauncher.exe",
        ]

    def detect_launcher_path(self) -> Optional[Path]:
        for path in self.known_launcher_paths():
            if path.exists():
                return path
        return None

    def refresh_launcher_status(self) -> None:
        path = self.detect_launcher_path()
        if path:
            self.launch_mode_var.set(f"Launcher detected: {path}")
            self.log("Detected official launcher executable.")
        else:
            self.launch_mode_var.set("Launcher not found on default paths; URI fallback will be used")
            self.log("No default launcher path found; minecraft:// fallback only.")

    def add_name_to_history(self, name: str) -> None:
        if name in self.name_history:
            self.name_history.remove(name)
        self.name_history.insert(0, name)
        self.name_history = self.name_history[:20]

        self.history_list.delete(0, "end")
        for item in self.name_history:
            self.history_list.insert("end", item)

    # ---------- Actions ----------
    def on_randomize(self) -> None:
        name = self.random_guest_name()
        self.name_var.set(name)
        self.add_name_to_history(name)
        self.status_var.set("Generated a new guest name")
        self.log(f"Generated name: {name}")

        if self.auto_copy_var.get():
            self.on_copy()

    def on_copy(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            self.status_var.set("Nothing to copy")
            self.log("Copy skipped: empty name")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(name)
        self.root.update()
        self.status_var.set(f"Copied '{name}' to clipboard")
        self.log(f"Copied name to clipboard: {name}")

    def on_history_pick(self, _event: object) -> None:
        selected = self.history_list.curselection()
        if not selected:
            return
        name = self.history_list.get(selected[0])
        self.name_var.set(name)
        self.status_var.set(f"Selected '{name}' from history")

    def open_minecraft_folder(self) -> None:
        roaming = Path(os.environ.get("APPDATA", ""))
        mc_dir = roaming / ".minecraft"
        if not mc_dir.exists():
            messagebox.showwarning(APP_TITLE, f".minecraft folder not found at:\n{mc_dir}")
            self.log("Could not open .minecraft folder: path not found")
            return
        os.startfile(str(mc_dir))  # type: ignore[attr-defined]
        self.log(f"Opened .minecraft folder: {mc_dir}")

    def launch_official_launcher(self) -> tuple[bool, str, Optional[subprocess.Popen]]:
        path = self.detect_launcher_path()
        if path:
            process = subprocess.Popen([str(path)], shell=False)
            return True, f"Launched: {path}", process

        try:
            os.startfile("minecraft://")  # type: ignore[attr-defined]
            return True, "Opened minecraft:// URI", None
        except OSError as exc:
            return False, f"Could not open official launcher: {exc}", None

    def on_launch(self) -> None:
        # Prevent accidental double-launch spam.
        now = time.time()
        if now - self.last_launch_ts < 2.0:
            self.status_var.set("Please wait a moment before launching again")
            return
        self.last_launch_ts = now

        ok, msg, process = self.launch_official_launcher()
        self.status_var.set(msg)
        self.log(msg)

        if not ok:
            messagebox.showerror(APP_TITLE, msg)
            return

        self.tracked_process = process
        self.start_session_timer()

    def start_session_timer(self) -> None:
        # Cancel previous timer before starting a new one.
        self.cancel_timer_job()
        self.remaining_seconds = max(1, int(self.session_minutes_var.get()) * 60)
        self._update_timer()
        self.log(f"Session timer started: {self.session_minutes_var.get()} minutes")

    def cancel_timer_job(self) -> None:
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    def pause_timer(self) -> None:
        self.cancel_timer_job()
        self.status_var.set("Timer paused")
        self.log("Timer paused")

    def resume_timer(self) -> None:
        if self.remaining_seconds <= 0:
            self.status_var.set("No paused timer to resume")
            return
        self.cancel_timer_job()
        self._update_timer()
        self.status_var.set("Timer resumed")
        self.log("Timer resumed")

    def stop_timer(self) -> None:
        self.cancel_timer_job()
        self.remaining_seconds = 0
        self.timer_var.set("Session timer: stopped")
        self.status_var.set("Timer stopped")
        self.log("Timer stopped")

    def set_session_minutes(self, minutes: int) -> None:
        self.session_minutes_var.set(minutes)
        self.status_var.set(f"Session length set to {minutes} minutes")
        self.log(f"Session preset selected: {minutes} minutes")

    def _update_timer(self) -> None:
        if self.remaining_seconds <= 0:
            self.timer_job = None
            self.timer_var.set("Session timer: ended")
            if self.beep_var.get():
                self.root.bell()

            if self.tracked_process and self.tracked_process.poll() is None:
                try:
                    self.tracked_process.terminate()
                    self.status_var.set("Time up. Closed tracked launcher process.")
                    messagebox.showinfo(APP_TITLE, "Session limit reached. Closed tracked launcher process.")
                    self.log("Session ended: tracked launcher process terminated")
                except OSError as exc:
                    self.status_var.set("Time up, but process could not be closed")
                    self.log(f"Error terminating process: {exc}")
            else:
                self.status_var.set("Time up.")
                self.log("Session ended (no tracked process available)")
            return

        minutes, seconds = divmod(self.remaining_seconds, 60)
        self.timer_var.set(f"Session timer: {minutes:02d}:{seconds:02d}")
        self.remaining_seconds -= 1
        self.timer_job = self.root.after(1000, self._update_timer)

    def export_logs(self) -> None:
        default_name = f"guestcraft_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = filedialog.asksaveasfilename(
            title="Export GuestCraft logs",
            initialfile=default_name,
            defaultextension=".txt",
            filetypes=[("Text", "*.txt")],
        )
        if not path:
            return
        Path(path).write_text("\n".join(self.logs), encoding="utf-8")
        self.status_var.set(f"Logs exported to {path}")
        self.log(f"Exported logs to {path}")

    def save_settings(self) -> None:
        data = {
            "prefix": self.prefix_var.get(),
            "length": int(self.length_var.get()),
            "exclude_ambiguous": bool(self.ambiguous_var.get()),
            "auto_copy": bool(self.auto_copy_var.get()),
            "beep": bool(self.beep_var.get()),
            "session_minutes": int(self.session_minutes_var.get()),
            "history": self.name_history[:20],
        }
        SETTINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.status_var.set("Settings saved")
        self.log("Saved settings")

    def load_settings(self) -> None:
        if not SETTINGS_PATH.exists():
            self.log("No saved settings found")
            return
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            self.prefix_var.set(data.get("prefix", "Guest"))
            self.length_var.set(int(data.get("length", 6)))
            self.ambiguous_var.set(bool(data.get("exclude_ambiguous", True)))
            self.auto_copy_var.set(bool(data.get("auto_copy", False)))
            self.beep_var.set(bool(data.get("beep", True)))
            self.session_minutes_var.set(max(1, int(data.get("session_minutes", DEFAULT_SESSION_MINUTES))))

            self.name_history = list(data.get("history", []))[:20]
            self.history_list.delete(0, "end")
            for item in self.name_history:
                self.history_list.insert("end", item)
            self.log("Loaded settings")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            self.log(f"Failed to load settings: {exc}")

    def on_close(self) -> None:
        self.cancel_timer_job()
        self.save_settings()
        self.root.destroy()

    # ---------- UI ----------
    def _build_ui(self) -> None:
        container = tk.Frame(self.root, padx=16, pady=12)
        container.pack(fill="both", expand=True)

        title = tk.Label(container, text="GuestCraft Launcher", font=("Segoe UI", 20, "bold"))
        title.pack(anchor="w")

        subtitle = tk.Label(
            container,
            text=(
                "Legal helper only: generates random guest names, opens the official launcher,\n"
                "and supports optional timed sessions."
            ),
            justify="left",
            fg="#444",
        )
        subtitle.pack(anchor="w", pady=(2, 10))

        top = tk.Frame(container)
        top.pack(fill="x")

        left = tk.LabelFrame(top, text="Name Generator", padx=10, pady=10)
        left.pack(side="left", fill="both", expand=True)

        right = tk.LabelFrame(top, text="Quick Tools", padx=10, pady=10)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        tk.Label(left, text="Prefix").grid(row=0, column=0, sticky="w")
        tk.Entry(left, textvariable=self.prefix_var, width=16).grid(row=0, column=1, sticky="w", padx=8)

        tk.Label(left, text="Token length").grid(row=1, column=0, sticky="w", pady=(8, 0))
        tk.Spinbox(left, from_=3, to=16, textvariable=self.length_var, width=6).grid(
            row=1, column=1, sticky="w", padx=8, pady=(8, 0)
        )

        tk.Checkbutton(left, text="Exclude ambiguous chars (0/O/1/I)", variable=self.ambiguous_var).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        tk.Checkbutton(left, text="Auto-copy after generate", variable=self.auto_copy_var).grid(
            row=3, column=0, columnspan=2, sticky="w"
        )

        tk.Label(left, text="Current name").grid(row=4, column=0, sticky="w", pady=(12, 0))
        tk.Entry(left, textvariable=self.name_var, font=("Consolas", 12), width=24, justify="center").grid(
            row=4, column=1, sticky="w", padx=8, pady=(12, 0)
        )

        tk.Button(left, text="Randomize", command=self.on_randomize, width=14).grid(row=5, column=0, pady=(12, 0))
        tk.Button(left, text="Copy", command=self.on_copy, width=12).grid(row=5, column=1, sticky="w", padx=8, pady=(12, 0))

        tk.Button(right, text="Launch Minecraft", command=self.on_launch, width=22, bg="#4CAF50", fg="white").pack(
            anchor="w"
        )
        tk.Button(right, text="Open .minecraft Folder", command=self.open_minecraft_folder, width=22).pack(
            anchor="w", pady=(8, 0)
        )
        tk.Button(right, text="Refresh Launcher Detection", command=self.refresh_launcher_status, width=22).pack(
            anchor="w", pady=(8, 0)
        )

        tk.Label(right, text="Session length (minutes)").pack(anchor="w", pady=(12, 0))
        tk.Spinbox(right, from_=1, to=240, textvariable=self.session_minutes_var, width=8).pack(anchor="w")

        presets = tk.Frame(right)
        presets.pack(anchor="w", pady=(8, 0))
        tk.Button(presets, text="15m", command=lambda: self.set_session_minutes(15), width=5).pack(side="left")
        tk.Button(presets, text="30m", command=lambda: self.set_session_minutes(30), width=5).pack(side="left", padx=4)
        tk.Button(presets, text="60m", command=lambda: self.set_session_minutes(60), width=5).pack(side="left")

        timer_controls = tk.Frame(right)
        timer_controls.pack(anchor="w", pady=(8, 0))
        tk.Button(timer_controls, text="Pause", command=self.pause_timer, width=7).pack(side="left")
        tk.Button(timer_controls, text="Resume", command=self.resume_timer, width=7).pack(side="left", padx=4)
        tk.Button(timer_controls, text="Stop", command=self.stop_timer, width=7).pack(side="left")

        tk.Checkbutton(right, text="Beep when timer ends", variable=self.beep_var).pack(anchor="w", pady=(8, 0))

        middle = tk.Frame(container)
        middle.pack(fill="both", expand=True, pady=(12, 0))

        history_box = tk.LabelFrame(middle, text="Name History", padx=8, pady=8)
        history_box.pack(side="left", fill="both")

        self.history_list = tk.Listbox(history_box, height=10, width=28)
        self.history_list.pack(fill="both", expand=True)
        self.history_list.bind("<<ListboxSelect>>", self.on_history_pick)

        log_box = tk.LabelFrame(middle, text="Activity Log", padx=8, pady=8)
        log_box.pack(side="left", fill="both", expand=True, padx=(12, 0))

        self.log_box = tk.Text(log_box, height=10, wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True)

        bottom = tk.Frame(container)
        bottom.pack(fill="x", pady=(10, 0))

        tk.Button(bottom, text="Save Settings", command=self.save_settings, width=14).pack(side="left")
        tk.Button(bottom, text="Export Logs", command=self.export_logs, width=14).pack(side="left", padx=8)

        tk.Label(bottom, textvariable=self.timer_var, font=("Consolas", 10, "bold")).pack(side="left", padx=(16, 0))

        legal = tk.Label(
            container,
            text=(
                "This app does not crack Minecraft or bypass account checks. Use a legitimate account.\n"
                "For older versions, create a legal release profile (for example 1.8.9) in the official launcher."
            ),
            fg="#7a1f1f",
            justify="left",
        )
        legal.pack(anchor="w", pady=(8, 2))

        launch_mode = tk.Label(container, textvariable=self.launch_mode_var, anchor="w", fg="#2d4a8f")
        launch_mode.pack(fill="x", side="bottom")

        status = tk.Label(container, textvariable=self.status_var, bd=1, relief="sunken", anchor="w", padx=8)
        status.pack(fill="x", side="bottom")


def main() -> None:
    root = tk.Tk()
    app = GuestCraftApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
