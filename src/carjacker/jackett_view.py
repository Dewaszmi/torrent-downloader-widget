from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Input, Static

from .api import find_jackett_torrents


class JackettSearch(Static):
    def compose(self) -> ComposeResult:
        with Vertical(id="search-section"):
            yield Static("SEARCH TORRENT API", classes="label")
            yield Input(placeholder="Enter search query...", id="search-input")
            yield DataTable(id="results-table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Seeders", "Category", "Tracker", "Name", "MagnetUrl")
        table.cursor_type = "row"

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
                item.get("MagnetUrl", "N/A")
            )

        self.notify(f"Found {len(results)} results.")

    async def toggle_selected(self) -> None:
        table = self.query_one(DataTable)
        if not table.row_count:
            return

        row_data = table.get_row_at(table.cursor_row)
        magnet_url = row_data[4]
        await self.add_to_transmission(magnet_url)

    # 3. Helper to avoid code duplication
    async def add_to_transmission(self, magnet_url: str):
        if not magnet_url:
            self.notify("No Magnet URL found.", severity="error")
            return
        try:
            self.app.client.add_torrent(magnet_url)
            self.notify("Added to Transmission!", severity="information")
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

