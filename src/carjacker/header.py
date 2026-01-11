import subprocess

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.widgets import Button, Static

LOGO = r"""
 _____   ___  ______   ___  ___  _____  _   __ ___________ 
/  __ \ / _ \ | ___ \ |_  |/ _ \/  __ \| | / /|  ___| ___ \
| /  \// /_\ \| |_/ /   | / /_\ \ /  \/| |/ / | |__ | |_/ /
| |    |  _  ||    /    | |  _  | |    |    \ |  __||    / 
| \__/\| | | || |\ \/\__/ / | | | \__/\| |\  \| |___| |\ \ 
 \____/\_| |_/\_| \_\____/\_| |_/\____/\_| \_/\____/\_| \_|
"""


class CarJackerHeader(Static):
    def compose(self) -> ComposeResult:
        with Horizontal(id="header-container"):
            # Left: Stats
            with Vertical(id="header-stats"):
                yield Static("⬇ 0.0 KB/s", id="down-speed")
                yield Static("⬆ 0.0 KB/s", id="up-speed")
                yield Static()

            # Center: Logo
            with Center(id="header-logo-area"):
                yield Static(LOGO, id="logo-text")

            # Right: Placeholder Button
            # with Vertical(id="header-actions"):
            #     yield Button("SETTINGS", id="toggle-jackett-btn", variant="primary")

    def on_mount(self):
        # Refresh speeds every 2 seconds
        self.set_interval(2, self.update_speeds)

    def update_speeds(self):
        try:
            from transmission_rpc import Client

            client = Client()
            session = client.get_session_stats()

            # Convert bytes to KB/s or MB/s
            down = session.download_speed / 1024
            up = session.upload_speed / 1024

            self.query_one("#down-speed").update(f"⬇ {down:.1f} KB/s")
            self.query_one("#up-speed").update(f"⬆ {up:.1f} KB/s")
        except:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "toggle-jackett-btn":
            jackett_status = (
                subprocess.run(
                    ["systemctl", "is-active", "jackett.service"],
                    stdout=subprocess.PIPE,
                )
                .stdout.decode("utf-8")
                .strip()
            )
            if jackett_status == "active":
                subprocess.run(["systemctl", "stop", "jacket.service"])
            else:
                subprocess.run(["systemctl", "start", "jacket.service"])
