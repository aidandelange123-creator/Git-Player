"""GuestCraft - a legal Windows helper launcher for Minecraft Java Edition.

This app does NOT bypass login/payment. It opens the official launcher only.
"""

from __future__ import annotations

import os
import random
import string
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import Optional

APP_TITLE = "GuestCraft Launcher"
WINDOW_SIZE = "560x380"
SESSION_LIMIT_SECONDS = 60 * 60


def random_guest_name() -> str:
    token = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"Guest_{token}"


def launch_official_launcher() -> tuple[bool, str, Optional[subprocess.Popen]]:
    """Try known launcher locations, then fallback to minecraft:// URI."""
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    program_files = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
    program_files_x86 = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)"))

    candidates = [
        local / "Programs/Minecraft Launcher/MinecraftLauncher.exe",
        program_files / "Minecraft Launcher/MinecraftLauncher.exe",
        program_files_x86 / "Minecraft Launcher/MinecraftLauncher.exe",
    ]

    for path in candidates:
        if path.exists():
            process = subprocess.Popen([str(path)], shell=False)
            return True, f"Launched: {path}", process

    try:
        # Windows URI scheme fallback
        os.startfile("minecraft://")  # type: ignore[attr-defined]
        return True, "Opened minecraft:// URI", None
    except OSError as exc:
        return False, f"Could not open official launcher: {exc}", None


class GuestCraftApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)

        self.name_var = tk.StringVar(value=random_guest_name())
        self.status_var = tk.StringVar(value="Ready")
        self.timer_var = tk.StringVar(value="Session timer: not running")
        self.remaining_seconds = 0
        self.tracked_process: Optional[subprocess.Popen] = None

        self._build_ui()

    def _build_ui(self) -> None:
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="GuestCraft Launcher",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")

        tk.Label(
            frame,
            text=(
                "Legal helper only: generates a random guest name, starts the official\n"
                "Minecraft Launcher, and optionally enforces a 1-hour play session."
            ),
            fg="#444",
            justify="left",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(6, 16))

        entry_row = tk.Frame(frame)
        entry_row.pack(fill="x")

        tk.Label(entry_row, text="Guest Name:", font=("Segoe UI", 10, "bold")).pack(side="left")

        self.name_entry = tk.Entry(
            entry_row,
            textvariable=self.name_var,
            font=("Consolas", 12),
            width=22,
            justify="center",
        )
        self.name_entry.pack(side="left", padx=(8, 0))

        btn_row = tk.Frame(frame)
        btn_row.pack(fill="x", pady=(14, 8))

        tk.Button(
            btn_row,
            text="Randomize Name",
            command=self.on_randomize,
            width=18,
            font=("Segoe UI", 10),
        ).pack(side="left")

        tk.Button(
            btn_row,
            text="Copy Name",
            command=self.on_copy,
            width=12,
            font=("Segoe UI", 10),
        ).pack(side="left", padx=8)

        tk.Button(
            btn_row,
            text="Launch Minecraft",
            command=self.on_launch,
            width=16,
            font=("Segoe UI", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#449d48",
            relief="raised",
        ).pack(side="left")

        tk.Label(
            frame,
            text="Tip: In the official launcher, create a profile for release 1.8.9.",
            fg="#2d4a8f",
            justify="left",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(8, 6))

        tk.Label(
            frame,
            textvariable=self.timer_var,
            fg="#333",
            justify="left",
            font=("Consolas", 10, "bold"),
        ).pack(anchor="w", pady=(2, 6))

        legal_text = (
            "This app does not crack Minecraft, bypass account checks, or provide paid\n"
            "game access for free. Use a legitimate account."
        )
        tk.Label(frame, text=legal_text, fg="#7a1f1f", justify="left", font=("Segoe UI", 9)).pack(
            anchor="w", pady=(20, 8)
        )

        status = tk.Label(
            frame,
            textvariable=self.status_var,
            bd=1,
            relief="sunken",
            anchor="w",
            padx=8,
            font=("Segoe UI", 9),
        )
        status.pack(fill="x", side="bottom")

    def on_randomize(self) -> None:
        self.name_var.set(random_guest_name())
        self.status_var.set("Generated a new guest name")

    def on_copy(self) -> None:
        name = self.name_var.get().strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(name)
        self.root.update()
        self.status_var.set(f"Copied '{name}' to clipboard")

    def on_launch(self) -> None:
        ok, msg, process = launch_official_launcher()
        self.status_var.set(msg)
        if not ok:
            messagebox.showerror(APP_TITLE, msg)
            return

        self.tracked_process = process
        self.start_session_timer()

    def start_session_timer(self) -> None:
        self.remaining_seconds = SESSION_LIMIT_SECONDS
        self._update_timer()

    def _update_timer(self) -> None:
        if self.remaining_seconds <= 0:
            self.timer_var.set("Session timer: ended")
            if self.tracked_process and self.tracked_process.poll() is None:
                self.tracked_process.terminate()
                self.status_var.set("1-hour limit reached. Closed tracked launcher process.")
                messagebox.showinfo(APP_TITLE, "1-hour limit reached. Closed tracked launcher process.")
            else:
                self.status_var.set("1-hour limit reached.")
            return

        minutes, seconds = divmod(self.remaining_seconds, 60)
        self.timer_var.set(f"Session timer: {minutes:02d}:{seconds:02d}")
        self.remaining_seconds -= 1
        self.root.after(1000, self._update_timer)


def main() -> None:
    root = tk.Tk()
    GuestCraftApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
