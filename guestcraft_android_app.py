"""GuestCraft Android App (Kivy).

Features:
- Checks whether Minecraft Bedrock (com.mojang.minecraftpe) is installed.
- Generates a custom player/guest name.
- Launches Bedrock through Android intents.
- Provides an optional "Mouse Mode" with on-screen directional controls that can
  be toggled on/off.

This is a legal helper utility only. It does not bypass login, ownership, or DRM.
"""

from __future__ import annotations

import random
import string
from dataclasses import dataclass
from typing import Optional

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

BEDROCK_PACKAGE = "com.mojang.minecraftpe"


@dataclass
class AndroidLaunchResult:
    ok: bool
    message: str


def _safe_import_android_helpers():
    """Load Android-only dependencies when running on Android."""
    try:
        from android import mActivity  # type: ignore
        from jnius import autoclass, cast  # type: ignore

        return mActivity, autoclass, cast
    except Exception:
        return None, None, None


def is_bedrock_installed() -> bool:
    m_activity, autoclass, _ = _safe_import_android_helpers()
    if not (m_activity and autoclass):
        return False

    try:
        package_manager = m_activity.getPackageManager()
        package_manager.getPackageInfo(BEDROCK_PACKAGE, 0)
        return True
    except Exception:
        return False


def launch_bedrock() -> AndroidLaunchResult:
    m_activity, autoclass, cast = _safe_import_android_helpers()
    if not (m_activity and autoclass and cast):
        return AndroidLaunchResult(False, "Android intent API not available. Run this build on Android.")

    if not is_bedrock_installed():
        return AndroidLaunchResult(False, "Minecraft Bedrock is not installed on this device.")

    try:
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")

        intent = Intent(Intent.ACTION_VIEW)
        intent.setData(Uri.parse("minecraft://"))
        intent.setPackage(BEDROCK_PACKAGE)
        current = cast("android.app.Activity", PythonActivity.mActivity)
        current.startActivity(intent)
        return AndroidLaunchResult(True, "Launched Minecraft Bedrock.")
    except Exception as exc:
        return AndroidLaunchResult(False, f"Failed to launch Bedrock: {exc}")


def random_player_name(prefix: str, length: int = 6) -> str:
    cleaned_prefix = prefix.strip() or "Guest"
    size = max(3, min(16, int(length)))
    alphabet = string.ascii_uppercase + string.digits
    token = "".join(random.choices(alphabet, k=size))
    return f"{cleaned_prefix}_{token}"


class MouseControlPad(BoxLayout):
    """Simple toggleable pad that simulates mouse-control intent in UI."""

    def __init__(self, status_label: Label, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(8), **kwargs)
        self.status_label = status_label

        top = BoxLayout(size_hint_y=None, height=dp(48))
        mid = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        bottom = BoxLayout(size_hint_y=None, height=dp(48))

        up = Button(text="↑")
        left = Button(text="←")
        click = Button(text="Click")
        right = Button(text="→")
        down = Button(text="↓")

        up.bind(on_release=lambda *_: self._announce("Mouse up"))
        left.bind(on_release=lambda *_: self._announce("Mouse left"))
        right.bind(on_release=lambda *_: self._announce("Mouse right"))
        down.bind(on_release=lambda *_: self._announce("Mouse down"))
        click.bind(on_release=lambda *_: self._announce("Mouse click"))

        top.add_widget(Label())
        top.add_widget(up)
        top.add_widget(Label())

        mid.add_widget(left)
        mid.add_widget(click)
        mid.add_widget(right)

        bottom.add_widget(Label())
        bottom.add_widget(down)
        bottom.add_widget(Label())

        self.add_widget(top)
        self.add_widget(mid)
        self.add_widget(bottom)

    def _announce(self, msg: str) -> None:
        self.status_label.text = f"Mouse mode: {msg}"


class GuestCraftAndroidRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(12), spacing=dp(8), **kwargs)

        self.status = Label(text="Checking Bedrock installation...", size_hint_y=None, height=dp(30))
        self.name_input = TextInput(text="Guest", multiline=False, hint_text="Player name prefix")
        self.generated_name = Label(text="Custom player: not generated")

        self.mouse_mode_enabled = False
        self.mouse_pad: Optional[MouseControlPad] = None

        self.add_widget(Label(text="GuestCraft Android Launcher", bold=True, size_hint_y=None, height=dp(34)))
        self.add_widget(self.status)
        self.add_widget(self.name_input)
        self.add_widget(self.generated_name)

        generate_btn = Button(text="Generate Custom Player")
        generate_btn.bind(on_release=self._generate_name)

        launch_btn = Button(text="Launch Bedrock")
        launch_btn.bind(on_release=self._launch)

        self.toggle_mouse_btn = Button(text="Enable Mouse Mode")
        self.toggle_mouse_btn.bind(on_release=self._toggle_mouse_mode)

        self.add_widget(generate_btn)
        self.add_widget(launch_btn)
        self.add_widget(self.toggle_mouse_btn)

        Clock.schedule_once(lambda *_: self._refresh_install_status(), 0.1)

    def _refresh_install_status(self) -> None:
        if is_bedrock_installed():
            self.status.text = "Bedrock detected: installed"
        else:
            self.status.text = "Bedrock not detected. Install Minecraft from Google Play."

    def _generate_name(self, *_args) -> None:
        name = random_player_name(self.name_input.text)
        self.generated_name.text = f"Custom player: {name}"

    def _launch(self, *_args) -> None:
        result = launch_bedrock()
        self.status.text = result.message

    def _toggle_mouse_mode(self, *_args) -> None:
        self.mouse_mode_enabled = not self.mouse_mode_enabled

        if self.mouse_mode_enabled:
            self.toggle_mouse_btn.text = "Disable Mouse Mode"
            if self.mouse_pad is None:
                self.mouse_pad = MouseControlPad(status_label=self.status)
            self.add_widget(self.mouse_pad)
            self.status.text = "Mouse mode enabled"
            return

        self.toggle_mouse_btn.text = "Enable Mouse Mode"
        if self.mouse_pad is not None and self.mouse_pad.parent is self:
            self.remove_widget(self.mouse_pad)
        self.status.text = "Mouse mode disabled"


class GuestCraftAndroidApp(App):
    def build(self):
        return GuestCraftAndroidRoot()


if __name__ == "__main__":
    GuestCraftAndroidApp().run()
