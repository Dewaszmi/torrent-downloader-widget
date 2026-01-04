from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer

from .trans_view import TransmissionManager
from .jackett_view import JackettSearch

class CarJacker(App):
    CSS = """
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
    """
    
    BINDINGS = [
        ("tab", "focus_next", "Toggle Focus"),
        ("space", "toggle_status", "Action"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
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
        focused_widget = self.focused
        
        # If the user is focusing the Transmission Table
        if self.query_one(TransmissionManager).query("DataTable:focus"):
            self.query_one(TransmissionManager).toggle_selected()
        
        # If the user is focusing the Search Table
        elif self.query_one(JackettSearch).query("DataTable:focus"):
            # Since JackettSearch.toggle_selected is async, we call it via 'run_worker'
            self.run_worker(self.query_one(JackettSearch).toggle_selected())

if __name__ == "__main__":
    app = CarJacker()
    app.run()