# GuestCraft (Windows Helper Launcher)

GuestCraft is a small **Windows helper launcher** for Minecraft Java Edition.

## Important legal note
This tool **does not bypass Microsoft/Mojang authentication** and **does not provide paid Minecraft access for free**.
It only helps you open the official launcher and manage quality-of-life utilities around legal usage.

## What was improved (15 features)
1. Custom guest-name prefix input.
2. Adjustable random token length (3–16).
3. Optional ambiguous-character filter (`0/O/1/I`).
4. Optional auto-copy to clipboard after generation.
5. Name history panel (up to 20 recent names).
6. Click-to-reuse names from history.
7. Launcher path detection status line.
8. Manual launcher detection refresh button.
9. Open `.minecraft` folder button.
10. Session-length selector (1–240 minutes).
11. Quick time presets (15m / 30m / 60m).
12. Timer pause/resume controls.
13. Timer stop control.
14. Activity log panel with timestamps.
15. Export logs to a text file.

## Bug fixes and reliability improvements
- Fixed duplicate/overlapping timer jobs by canceling active `after()` callbacks before restarting.
- Added launch spam guard (2-second cooldown) to prevent accidental double-launching.
- Added safer process termination handling with error reporting.
- Added empty-name handling for clipboard copy.
- Added persistent settings load/save (`guestcraft_settings.json`).
It only helps you:
- generate a random guest-style nickname, and
- start the official Minecraft launcher installed on your machine,
- enforce an optional 1-hour session limit.

## Features
- One-click random guest name generation (e.g., `Guest_8F3K2Q`)
- Starts official Minecraft Launcher from:
  - default install paths, or
  - `minecraft://` URI fallback
- 1-hour session timer (closes tracked launcher process when possible)
- Copy generated name to clipboard
- Reminder to use a legal 1.8.9 profile in the official launcher


## Android APK launcher
This repository now includes an Android app entrypoint (`guestcraft_android_app.py`) that:
- checks whether **Minecraft Bedrock** (`com.mojang.minecraftpe`) is installed,
- launches Bedrock using Android intents,
- generates a custom player name,
- includes a **Mouse Mode** toggle with on-screen directional/click buttons.

### Android source files
- `guestcraft_android_app.py` (Kivy app for Android)
- `buildozer.spec` (APK build configuration)
- `guestcraft_launcher_android.py` (CLI fallback helper)

### Build APK
On Linux with Buildozer + Android SDK/NDK installed:

```bash
pip install buildozer cython
buildozer -v android debug
```

Generated APK output:
- `bin/*.apk`

If you only need CLI behavior in Termux:

```bash
python guestcraft_launcher_android.py --no-launch
```
## Android helper (new)
If you want a lightweight Android/Termux-friendly helper, use:

```bash
python guestcraft_launcher_android.py
```

Useful flags:
- `--no-launch` generate a name only
- `--prefix Guest` custom prefix
- `--length 8` token size (3-16)
- `--allow-ambiguous` allow `0/O/1/I`

This Android script tries `am start`, then `termux-open`, then browser fallback with `minecraft://`.

## Requirements
- Windows 10/11
- Python 3.10+
- Official Minecraft Launcher installed

## Run
```powershell
python guestcraft_launcher.py
```

## Build EXE (optional)
```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed guestcraft_launcher.py
```
The executable will be created in `dist/`.

## Older versions (1.8.x)
GuestCraft does not distribute Minecraft files. To play 1.8.x legally, create/select a `release 1.8.9` installation profile in the official Minecraft launcher.
## Disclaimer
Use this tool only with a legitimate Minecraft account and in compliance with Mojang/Microsoft terms.

## About older versions (1.8.x)
GuestCraft does not distribute Minecraft files.  
To play 1.8.x legally, create/select a `release 1.8.9` installation profile in the official Minecraft launcher.
