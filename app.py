import os
import subprocess

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Label

# --- CONFIGURATION ---
TORRENT_DIR = os.path.expanduser(
    "~/dev/torrent-downloader-widget/torrent_dir"
)  # Change this to your path
# ---------------------


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

        self.refresh_all()
        self.set_interval(3, self.refresh_active)  # Auto-refresh active transfers

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
