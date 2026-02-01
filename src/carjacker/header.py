import subprocess

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.reactive import reactive
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
    download_dir = reactive("Connecting...")

    def compose(self) -> ComposeResult:
        with Horizontal(id="header-container"):
            # Left: Stats
            with Vertical(id="header-stats"):
                yield Static("⬇ 0.0 MB/s", id="down-speed")
                yield Static("⬆ 0.0 MB/s", id="up-speed")
                yield Static()

            # Center: Logo
            with Center(id="header-logo-area"):
                yield Static(LOGO, id="logo-text")

            yield Static("", id="header-path")

            # Right: Placeholder Button
            # with Vertical(id="header-actions"):
            #     yield Button("SETTINGS", id="toggle-jackett-btn", variant="primary")

    def on_mount(self):
        # Refresh speeds every 2 seconds
        self.set_interval(2, self.update_speeds)

        self.set_timer(1.0, self.update_download_dir)

    def update_speeds(self):
        try:
            session_stats = self.app.client.session_stats()

            # convert bytes to KB/s
            down = session_stats.download_speed / 1024**2
            up = session_stats.upload_speed / 1024**2

            self.query_one("#down-speed").update(f"⬇ {down:.1f} MB/s")
            self.query_one("#up-speed").update(f"⬆ {up:.1f} MB/s")
        except:
            pass

    def update_download_dir(self) -> None:
        try:
            # Access the client initialized in main.py
            session = self.app.client.get_session()
            self.download_dir = session.download_dir
        except Exception:
            self.download_dir = "/var/lib/transmission/..."

    def watch_download_dir(self, new_dir: str) -> None:
        """Textual 'watch' method that fires when download_dir changes."""
        self.query_one("#header-path").update(f"Download dir: {new_dir}")
