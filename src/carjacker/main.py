from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer

from .trans_view import TransmissionManager
from .jackett_view import JackettSearch
from .header import CarJackerHeader

class CarJacker(App):
    CSS = """
    #logo {
        width: 100%;
        height: 25%;
        content-align: center middle;
        color: $accent;
        margin: 0 0;
        text-style: bold;
    }
    Horizontal {
        height: 1fr;
    }
    .pane {
        width: 50%;
        border: solid $accent;
        margin: 1;
        padding: 1;
        height: 100%;
    }
    # This ensures the internal widgets fill their pane
    TransmissionManager, JackettSearch {
        height: 1fr;
    }
    DataTable {
        height: 1fr;
    }
    .label {
        width: 100%;
        text-align: center;
        text-style: bold;
        background: $accent;
        color: $text;
        margin-bottom: 1;
    }
    DataTable:focus {
        border: double $accent;
    }
    #header-container {
    height: 7; /* Adjust height based on your ASCII art size */
    background: $surface;
    border-bottom: tall $accent;
    # align: middle;
    }
    #header-stats {
    width: 20%;
    padding: 1 2;
    color: $success;
    text-style: bold;
}
#header-logo-area {
    width: 60%;
    color: $accent;
}
#logo-text {
    text-align: center;
    width: 100%;
    height: 5;
    # white-space: pre;
    overflow: hidden;
    color: $accent
}
#header-actions {
    width: 20%;
    align: center middle;
}
#header-btn {
    min-width: 12;
    height: 3;
}
    """
    
    BINDINGS = [
        ("tab", "focus_next", "Toggle Focus"),
        ("space", "toggle_status", "Action"),
        ("q", "quit", "Quit"),
        ("r", "delete_torrent", "Remove Torrent"),
        ("R", "purge_torrent", "Purge Torrent"),
    ]

    def compose(self) -> ComposeResult:
        yield CarJackerHeader()
        with Horizontal():
            # LEFT SIDE: Transmission
            with Vertical(classes="pane"):
                yield TransmissionManager()
            
            # RIGHT SIDE: Jackett
            with Vertical(classes="pane"):
                yield JackettSearch()
        yield Footer()

    def action_toggle_status(self):
        """Logic based on which widget currently has the focus."""
        # Transmission interface
        if self.query_one(TransmissionManager).query("DataTable:focus"):
            self.query_one(TransmissionManager).toggle_selected()
        
        # Jackett interface
        elif self.query_one(JackettSearch).query("DataTable:focus"):
            # Since JackettSearch.toggle_selected is async, we call it via 'run_worker'
            self.run_worker(self.query_one(JackettSearch).toggle_selected())

    def action_delete_torrent(self):
        if self.query_one(TransmissionManager).query("DataTable:focus"):
            self.query_one(TransmissionManager).remove_selected()
    
    def action_purge_torrent(self):
        if self.query_one(TransmissionManager).query("DataTable:focus"):
            self.query_one(TransmissionManager).purge_selected()

def main():
    app = CarJacker()
    app.run()

if __name__ == "__main__":
    main()