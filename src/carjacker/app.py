import asyncio
import os
import subprocess

from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Label, RichLog, Static

# --- CONFIGURATION ---
TORRENT_DIR = os.path.expanduser(
    "/home/dewaszmi/torrent-dir"
)  # Change this to your path


class ServerSetup(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Center(id="main-container")
        yield Footer()

    def on_mount(self) -> None:
        self.check_api_availability()
        self.set_interval(5, self.check_api_availability())

    def check_api_availability(self) -> None:
        cmd = 'docker compose ps | grep "api-py"'

        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()

        is_running = len(stdout.strip()) > 0
        container = self.query_one("#main-container")

        if not is_running:
            if not self.query("#setup-btn"):
                container.mount(
                    Static("api-py is NOT running", id="status-msg", classes="warning")
                )
                container.mount(
                    Button("Start api-py Container", id="setup-btn", variant="error")
                )
        else:
            self.query("#status-msg").remove()
            self.query("#setup-btn").remove()
            if not self.query("healthy-msg"):
                container.mount(Static("api-py is running", id="healthy-msg"))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "setup-btn":
            container = self.query_one("#main-container")

            self.query("#status-msg").remove()
            event.button.remove()

            log = RichLog(id="setup-log", highlight=True, markup=True)
            await container.mount(log)

            await self.run_api_server(log)

    async def run_api_server(self, log: RichLog):
        process = await asyncio.create_subprocess_shell(
            "sh scripts/start_api_server",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            log.write(line.decode().strip())

        await asyncio.sleep(3)
        log.remove()
        self.check_api_availability()


class TorrentManager(App):
    CSS = """
    Screen {
        layout: horizontal;
    }
    .pane {
        width: 50%;
        border: solid $accent;
        margin: 1;
        padding: 1;
    }
    DataTable {
        height: 1fr;
    }
    Label {
        width: 100%;
        text-align: center;
        text-style: bold;
        background: $accent;
        color: $text;
    }
    """

    BINDINGS = [
        ("p", "pause", "Pause"),
        ("s", "start", "Resume"),
        ("r", "refresh", "Refresh All"),
        ("space", "download", "Download Selected"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(classes="pane"):
                yield Label("ACTIVE TRANSFERS")
                yield DataTable(id="active-table")
            with Vertical(classes="pane"):
                yield Label("LOCAL TORRENT FILES")
                yield DataTable(id="file-table")
        yield Footer()

    def on_mount(self) -> None:
        # Setup Active Table
        active = self.query_one("#active-table", DataTable)
        active.add_columns("ID", "Done %", "Status", "Name")
        active.cursor_type = "row"

        # Setup File Table
        files = self.query_one("#file-table", DataTable)
        files.add_columns("File Name")
        files.cursor_type = "row"

    def refresh_all(self):
        self.refresh_active()
        self.refresh_files()

    def refresh_active(self) -> None:
        table = self.query_one("#active-table", DataTable)
        try:
            out = subprocess.check_output("transmission-remote -l", shell=True).decode()
            lines = out.strip().split("\n")
            table.clear()
            if len(lines) > 2:
                for line in lines[1:-1]:
                    p = line.split()
                    if len(p) < 9:
                        continue
                    table.add_row(p[0], p[1], p[8], " ".join(p[9:]))
        except Exception:
            self.notify("Transmission not reachable", severity="error")

    def refresh_files(self) -> None:
        table = self.query_one("#file-table", DataTable)
        table.clear()
        if os.path.exists(TORRENT_DIR):
            files = [f for f in os.listdir(TORRENT_DIR) if f.endswith(".torrent")]
            for f in files:
                table.add_row(f)
        else:
            self.notify(f"Directory not found: {TORRENT_DIR}", severity="warning")

    def action_download(self) -> None:
        """Pressing Space on the right pane downloads the file."""
        table = self.query_one("#file-table", DataTable)
        if table.has_focus:
            row_index = table.cursor_row
            if row_index is not None:
                filename = table.get_row_at(row_index)[0]
                filepath = os.path.join(TORRENT_DIR, filename)
                try:
                    subprocess.run(["transmission-remote", "-a", filepath], check=True)
                    self.notify(f"Added: {filename}")
                    self.refresh_active()
                except Exception as e:
                    self.notify(f"Failed to add: {e}", severity="error")

    def action_pause(self) -> None:
        self.control_transmission("-p")

    def action_start(self) -> None:
        self.control_transmission("-s")

    def control_transmission(self, flag):
        table = self.query_one("#active-table", DataTable)
        if table.has_focus and table.cursor_row is not None:
            t_id = table.get_row_at(table.cursor_row)[0]
            subprocess.run(["transmission-remote", "-t", t_id, flag])
            self.refresh_active()

    def action_refresh(self) -> None:
        self.refresh_all()


if __name__ == "__main__":
    app = TorrentManager()
    app.run()
