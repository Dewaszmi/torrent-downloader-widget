from textual.widgets import Static, DataTable
from transmission_rpc import Client

class TransmissionManager(Static):
    def compose(self):
        yield Static("📥 Active Downloads (Space to Toggle)", classes="label")
        yield DataTable(id="transmission-table")

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("Status", "Name", "Progress")
        table.cursor_type = "row"
        self.set_interval(2, self.update_stats)

    def update_stats(self):
        try:
            client = Client()
            torrents = client.get_torrents()
            table = self.query_one(DataTable)
            table.clear()
            for t in torrents:
                progress = f"{t.percent_done * 100:.1f}%"
                table.add_row(t.status, t.name, progress, key=str(t.id))
        except: pass

    def toggle_selected(self):
        table = self.query_one(DataTable)
        if not table.row_count: return
        
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        tid = int(str(row_key.value))
        client = Client()
        t = client.get_torrent(tid)
        
        if t.status in ("downloading", "seeding"):
            client.stop_torrent(tid)
        else:
            client.start_torrent(tid)