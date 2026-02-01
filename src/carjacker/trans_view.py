from rich.text import Text
from textual.widgets import DataTable, Static
from transmission_rpc import Client


class TransmissionManager(Static):
    def compose(self):
        yield Static("LOCAL TORRENT MANAGEMENT", classes="label")
        yield DataTable(id="transmission-table")

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("Status", "Progress", "Name")
        table.cursor_type = "row"
        self.set_interval(2, self.update_stats)

    def get_selected_torrent(self):
        """Helper function to get currently hovered torrent."""
        table = self.query_one(DataTable)
        if not table.row_count:
            return

        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        torrent_id = int(str(row_key.value))
        t = self.app.client.get_torrent(torrent_id)

        return t, torrent_id

    def toggle_selected(self):
        t, torrent_id = self.get_selected_torrent()

        if t.status in ("downloading", "seeding"):
            self.app.client.stop_torrent(torrent_id)
        else:
            self.app.client.start_torrent(torrent_id)

    def remove_selected(self):
        """Remove torrent, leaving the downloaded content."""
        t, torrent_id = self.get_selected_torrent()
        self.app.client.remove_torrent(torrent_id, delete_data=False)

    def purge_selected(self):
        """Remove torrent along the downloaded content."""
        t, torrent_id = self.get_selected_torrent()
        self.app.client.remove_torrent(torrent_id, delete_data=True)

    def update_stats(self):
        table = self.query_one(DataTable)

        # 1. Save all state: Vertical, Horizontal, and Selection
        row_key = None
        if table.row_count > 0 and table.cursor_row is not None:
            try:
                row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
            except Exception:
                pass

        saved_scroll_x = table.scroll_x
        saved_scroll_y = table.scroll_y

        table.clear()
        torrents = self.app.client.get_torrents()

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

            status_display = Text(t.status, style=status_color)
            progress = f"{t.percent_done * 100:.1f}%"

            table.add_row(progress, status_display, t.name, key=str(t.id))

        if row_key:
            try:
                new_pos = table.get_row_index(row_key)
                table.move_cursor(row=new_pos)
            except Exception:
                table.move_cursor(row=0)

        table.scroll_to(x=saved_scroll_x, y=saved_scroll_y, animate=False)
        table.scroll_to(x=saved_scroll_x, y=saved_scroll_y, animate=False)
