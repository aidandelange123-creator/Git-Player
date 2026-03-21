[app]
title = GuestCraft Android Launcher
package.name = guestcraftandroid
package.domain = org.guestcraft
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.1.0
requirements = python3,kivy,pyjnius
orientation = portrait
fullscreen = 0

# Entry point for APK build
# Build with: buildozer -v android debug
# Output APK appears under ./bin/

[buildozer]
log_level = 2
warn_on_root = 1
