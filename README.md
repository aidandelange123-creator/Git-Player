# GuestCraft (PC Helper Launcher)

GuestCraft is a **Windows PC helper launcher** for Minecraft Java Edition.

## Important legal note
This tool **does not bypass Microsoft/Mojang authentication** and **does not provide paid Minecraft access for free**.

## PC Features
- Random guest-name generation with prefix + token length controls
- Optional ambiguous-character filter (`0/O/1/I`)
- Auto-copy and name history
- Launcher path detection + optional custom `MinecraftLauncher.exe` path
- Session timer controls with presets (default session: **90 minutes**)
- Launch delay before timer start (helps when launcher/game startup is slow)
- Activity log + export
- Settings persistence (`guestcraft_settings.json`)

## Licensed 1.8.8 JAR upload flow
GuestCraft includes a **licensed JAR verification step** for Minecraft `1.8.8` uploads:
- Use **Upload Licensed 1.8.8 Jar** in the app
- The file must be a `1.8.8` jar
- The app computes SHA-256 and checks `licensed_jar_hashes.json`
- Only hashes listed in `licensed_sha256` are accepted

Example licensing file:
```json
{
  "licensed_sha256": [
    "<approved-sha256-hash>"
  ]
}
```

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
