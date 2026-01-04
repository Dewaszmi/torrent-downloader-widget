from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Input, Static

from .api import find_jackett_torrents


class JackettSearch(Static):
    def compose(self) -> ComposeResult:
        with Vertical(id="search-section"):
            yield Static("🔍 Search New Torrents", classes="label")
            yield Input(    placeholder="Enter search query...", id="search-input")
            yield DataTable(id="results-table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Name", "Seeders", "MagnetLink")
        # table.set_column_visible("MagnetLink", False)
        table.cursor_type = "row"
        # self.check_jackett()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Triggered when Enter is pressed in the Input field."""
        query = event.value.strip()
        if not query:
            return

        table = self.query_one(DataTable)
        table.clear()
        self.notify(f"Searching for: {query}...")

        results = await find_jackett_torrents(search_query=query)

        if not results:
            self.notify("No results found or Jackett error.", severity="error")
            return

        for item in results:
            table.add_row(
                item["Title"],
                str(item["Seeders"]),
                item["MagnetUrl"],  # This column will be visible unless we hide it
            )

        self.notify(f"Found {len(results)} results.")

    async def toggle_selected(self) -> None:
        table = self.query_one(DataTable)
        if not table.row_count:
            return
            
        # Get data from the currently highlighted row
        row_data = table.get_row_at(table.cursor_row)
        magnet_url = row_data[2]
        await self.add_to_transmission(magnet_url)
    
    # 3. Helper to avoid code duplication
    async def add_to_transmission(self, magnet_url: str):
        if not magnet_url:
            self.notify("No Magnet URL found.", severity="error")
            return
        try:
            from transmission_rpc import Client
            client = Client()
            client.add_torrent(magnet_url)
            self.notify("Added to Transmission!", severity="information")
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    # def check_jackett(self) -> None:
    #     result = (
    #         subprocess.run(
    #             ["systemctl", "is-active", "jackett.service"], stdout=subprocess.PIPE
    #         )
    #         .stdout.decode("utf-8")
    #         .strip()
    #     )

    #     jackett_active = result == "active"
    #     self.query_one("#setup-area").set_class(jackett_active, "hidden")
    #     self.query_one("#search-section").set_class(not jackett_active, "hidden")

    #     if not jackett_active and not self.query("#setup-btn"):
    #         area = self.query_one("#setup-area")
    #         area.mount(Static("Jackett daemon is NOT running", classes="warning"))