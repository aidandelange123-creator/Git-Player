# GuestCraft (Windows Helper Launcher)

GuestCraft is a small **Windows helper launcher** for Minecraft Java Edition.

## Important legal note
This tool **does not bypass Microsoft/Mojang authentication** and **does not provide paid Minecraft access for free**.
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

## About older versions (1.8.x)
GuestCraft does not distribute Minecraft files.  
To play 1.8.x legally, create/select a `release 1.8.9` installation profile in the official Minecraft launcher.
