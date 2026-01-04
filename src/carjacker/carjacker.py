import asyncio
import os
import subprocess
from pathlib import Path

import httpx
from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, RichLog, Static

from .find_jackett_torrents import find_jackett_torrents


class CarJacker(App):
    CSS = """
    #main-container { align: center middle; height: 1fr; }
    .hidden { display: none; }
    
    #search-section {
        height: 1fr;
        border: tall $primary;
        margin: 1;
        padding: 1;
    }
    
    Input { margin-bottom: 1; border: tall $accent; }
    DataTable { height: 1fr; border: round $secondary; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        # Area for Docker Setup (if needed)
        yield Vertical(id="setup-area", classes="hidden")
        # Area for Search and Results
        with Vertical(id="search-section"):
            yield Static("🔍 Search New Torrents")
            yield Input(placeholder="Enter search query...", id="search-input")
            yield DataTable(id="results-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Name", "URL")  # URL column can be hidden if desired
        table.cursor_type = "row"
        self.check_jackett()

    def check_jackett(self) -> None:
        result = subprocess.run(
            ["systemctl", "is-active", "jackett.service"], stdout=subprocess.PIPE
        ).stdout.decode("utf-8")

        jackett_active = result == "active"
        self.query_one("#setup-area").set_class(jackett_active, "hidden")
        self.query_one("#search-section").set_class(not jackett_active, "hidden")

        if not jackett_active and not self.query("#setup-btn"):
            area = self.query_one("#setup-area")
            area.mount(Static("Jackett daemon is NOT running", classes="warning"))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Triggered when Enter is pressed in the Input field."""
        query = event.value.strip()
        if not query:
            return

        table = self.query_one("#results-table", DataTable)
        table.clear()
        self.notify(f"Searching for: {query}...")

        results

    # async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    #     """Triggered when a search result is clicked or Enter is pressed on it."""
    #     row_data = event.data_table.get_row_at(event.cursor_row)
    #     name, torrent_url = row_data[0], row_data[1]
    #
    #     # 1. Download the file
    #     self.notify(f"Downloading .torrent: {name}")
    #     file_path = DOWNLOAD_CACHE / f"temp_{event.cursor_row}.torrent"
    #
    #     try:
    #         async with httpx.AsyncClient() as client:
    #             r = await client.get(torrent_url)
    #             r.raise_for_status()
    #             file_path.write_bytes(r.content)
    #
    #         # 2. Add to transmission
    #         subprocess.run(["transmission-remote", "-a", str(file_path)], check=True)
    #         self.notify("Successfully added to Transmission!", severity="information")
    #
    #         # 3. Cleanup
    #         if file_path.exists():
    #             file_path.unlink()
    #
    #     except Exception as e:
    #         self.notify(f"Transfer failed: {e}", severity="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "setup-btn":
            container = self.query_one("#main-container")

            # Remove the warning UI
            self.query("#status-msg").remove()
            event.button.remove()

            # Dynamically mount the Log widget
            log = RichLog(id="setup-log", highlight=True, markup=True)
            await container.mount(log)


if __name__ == "__main__":
    app = CarJacker()
    app.run()
