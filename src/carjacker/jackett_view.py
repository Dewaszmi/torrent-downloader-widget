import subprocess

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Input, Static

from .api import find_jackett_torrents


class JackettSearch(Static):
    def compose(self) -> ComposeResult:
        with Vertical(id="jackett-ui"):
            yield Static("SEARCH TORRENT API", classes="label")
            yield Input(placeholder="Enter search query...", id="search-input")
            yield DataTable(id="results-table")
        # Displayed if Jackett not running
        yield Static("Jackett service not running.", id="jackett-error", classes="label")

    def on_mount(self) -> None:
        running = self.is_running()
        self.query_one("#jackett-ui").display = running
        self.query_one("#jackett-error").display = not running

        table = self.query_one(DataTable)
        table.add_columns("Seeders", "Category", "Tracker", "Name", "MagnetUrl")
        table.cursor_type = "row"
        if running:
            self.focus_input()

    def is_running(self) -> bool:
        """Boolean check if Jackett service is running."""
        return subprocess.call(["systemctl", "is-active", "--quiet", "jackett"]) == 0

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Triggered when Enter is pressed in the Input field."""
        query = event.value.strip()
        if not query:
            return

        table = self.query_one(DataTable)
        table.clear()

        results = await find_jackett_torrents(search_query=query)

        if not results:
            self.notify("No results found or Jackett error.", severity="error")
            return

        for item in results:
            table.add_row(
                str(item.get("Seeders", 0)),
                item.get("Category", "N/A"),
                item.get("Tracker", "N/A"),
                item.get("Title", "Unknown"),
                item.get("MagnetUrl", "N/A"),
            )

        self.notify(f"Found {len(results)} results.")

    async def toggle_selected(self) -> None:
        table = self.query_one(DataTable)
        if not table.row_count:
            return

        row_data = table.get_row_at(table.cursor_row)
        magnet_url = row_data[4]
        await self.add_to_transmission(magnet_url)

    def focus_input(self):
        self.query_one("#search-input").focus()

    async def add_to_transmission(self, magnet_url: str):
        if not magnet_url:
            self.notify("No Magnet URL found.", severity="error")
            return
        try:
            self.app.client.add_torrent(magnet_url)
            self.notify("Added to Transmission!", severity="information")
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")
