"""GuestCraft Android helper launcher.

This script is intended for Android Python environments such as Termux.
It does not bypass account authentication or provide Minecraft access.
"""

from __future__ import annotations

import argparse
import random
import shutil
import string
import subprocess
import sys
import webbrowser
from dataclasses import dataclass

DEFAULT_PREFIX = "Guest"
DEFAULT_LENGTH = 6


@dataclass
class LaunchResult:
    ok: bool
    message: str


def build_charset(exclude_ambiguous: bool) -> str:
    chars = string.ascii_uppercase + string.digits
    if exclude_ambiguous:
        for ch in "0O1I":
            chars = chars.replace(ch, "")
    return chars


def random_guest_name(prefix: str, length: int, exclude_ambiguous: bool) -> str:
    safe_length = max(3, min(16, length))
    token = "".join(random.choices(build_charset(exclude_ambiguous), k=safe_length))
    clean_prefix = prefix.strip() or DEFAULT_PREFIX
    return f"{clean_prefix}_{token}"


def _run_command(command: list[str]) -> bool:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError:
        return False
    return completed.returncode == 0


def launch_minecraft_android() -> LaunchResult:
    """Launch Minecraft on Android using am/termux-open/webbrowser fallbacks."""
    uri = "minecraft://"

    if shutil.which("am") and _run_command(["am", "start", "-a", "android.intent.action.VIEW", "-d", uri]):
        return LaunchResult(True, "Opened minecraft:// with Android activity manager (am).")

    if shutil.which("termux-open") and _run_command(["termux-open", uri]):
        return LaunchResult(True, "Opened minecraft:// using termux-open.")

    try:
        if webbrowser.open(uri):
            return LaunchResult(True, "Requested minecraft:// through the default Android browser handler.")
    except webbrowser.Error:
        pass

    return LaunchResult(False, "Unable to open minecraft://. Install Minecraft and run from Termux or another Android shell.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GuestCraft Android helper launcher")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX, help="Guest name prefix (default: Guest)")
    parser.add_argument("--length", type=int, default=DEFAULT_LENGTH, help="Random token length (3-16)")
    parser.add_argument(
        "--allow-ambiguous",
        action="store_true",
        help="Allow ambiguous characters like 0/O/1/I in generated names",
    )
    parser.add_argument(
        "--no-launch",
        action="store_true",
        help="Only generate a guest name and do not open minecraft://",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    name = random_guest_name(args.prefix, args.length, exclude_ambiguous=not args.allow_ambiguous)

    print("GuestCraft Android (legal helper)")
    print(f"Generated guest name: {name}")

    if args.no_launch:
        print("Launch step skipped (--no-launch).")
        return 0

    result = launch_minecraft_android()
    print(result.message)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
