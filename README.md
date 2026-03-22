# GuestCraft (Windows Helper Launcher)

GuestCraft is a small **Windows helper launcher** for Minecraft Java Edition.

## Important legal note
This tool **does not bypass Microsoft/Mojang authentication** and **does not provide paid Minecraft access for free**.

It only helps you:
- generate a random guest-style nickname,
- start the official Minecraft launcher installed on your machine,
- optionally run a timed session.

## Features
- Custom guest-name prefix and token length (3–16)
- Optional ambiguous-character filter (`0/O/1/I`)
- Optional auto-copy to clipboard after generation
- Name history panel (up to 20 recent names)
- Launcher path detection + URI fallback (`minecraft://`)
- Open `.minecraft` folder shortcut
- Session-length selector with 15m / 30m / 60m presets (default: 90 minutes)
- Launch-delay control so the timer can start after Minecraft has time to load
- Timer pause/resume/stop controls
- Activity log + export logs to file
- Settings persistence in `guestcraft_settings.json`

## Android support
This repository includes Android launcher helpers:
- `guestcraft_android_app.py` (Kivy app for Android)
- `guestcraft_launcher_android.py` (CLI fallback helper)
- `buildozer.spec` (APK build configuration)

### Build APK (Buildozer)
```bash
pip install buildozer cython
buildozer -v android debug
```

### Termux/CLI helper
```bash
python guestcraft_launcher_android.py --no-launch
```

Useful flags:
- `--prefix Guest` custom prefix
- `--length 8` token size (3-16)
- `--allow-ambiguous` allow `0/O/1/I`
- `--check-bedrock` check installation only

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

## Disclaimer
Use this tool only with a legitimate Minecraft account and in compliance with Mojang/Microsoft terms.
