from textual.widgets import DataTable, Static
from transmission_rpc import Client
from rich.text import Text


class TransmissionManager(Static):
    def compose(self):
        yield Static("LOCAL TORRENT MANAGEMENT", classes="label")
        yield DataTable(id="transmission-table")

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("Status", "Name", "Progress")
        table.cursor_type = "row"
        self.set_interval(2, self.update_stats)

    def get_selected_torrent(self):
        """Helper function to get currently hovered torrent."""
        table = self.query_one(DataTable)
        if not table.row_count:
            return

        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        torrent_id = int(str(row_key.value))
        client = Client()
        t = client.get_torrent(torrent_id)

        return client, t, torrent_id

    def toggle_selected(self):
        client, t, torrent_id = self.get_selected_torrent()

        if t.status in ("downloading", "seeding"):
            client.stop_torrent(torrent_id)
        else:
            client.start_torrent(torrent_id)

    def remove_selected(self):
        """Remove torrent, leaving the downloaded content."""
        client, t, torrent_id = self.get_selected_torrent()
        client.remove_torrent(torrent_id, delete_data=False)

    def purge_selected(self):
        """Remove torrent along the downloaded content."""
        client, t, torrent_id = self.get_selected_torrent()
        client.remove_torrent(torrent_id, delete_data=True)

    def update_stats(self):
        try:
            client = Client()
            torrents = client.get_torrents()
            table = self.query_one(DataTable)
            table.clear()
            
            for t in torrents:
                # Determine color based on status
                status_color = "white"
                if t.status == "downloading":
                    status_color = "bold green"
                elif t.status == "seeding":
                    status_color = "bold cyan"
                elif t.status in ("stopped", "paused"):
                    status_color = "yellow"
                elif "check" in t.status:
                    status_color = "magenta"

                # Create a styled Rich Text object
                status_display = Text(t.status, style=status_color)
                progress = f"{t.percent_done * 100:.1f}%"
                
                table.add_row(
                    status_display, 
                    t.name, 
                    progress, 
                    key=str(t.id)
                )
        except:
            pass
