from types import NoneType

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer
from transmission_rpc import Client

from .header import CarJackerHeader
from .jackett_view import JackettSearch
from .trans_view import TransmissionManager


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
        ("z", "cycle_view", "Cycle View"),
        ("space", "toggle_status", "Action"),
        ("q", "quit", "Quit"),
        ("r", "delete_torrent", "Remove Torrent"),
        ("R", "purge_torrent", "Purge Torrent"),
    ]

    client = None

    def on_mount(self) -> None:
        try:
            self.client = Client()
        except Exception as e:
            self.notify(f"Transmission connection failed: {e}", severity="error")

    def compose(self) -> ComposeResult:
        yield CarJackerHeader()
        with Horizontal():
            # LEFT SIDE: Transmission
            with Vertical(classes="pane", id="transmission-pane"):
                yield TransmissionManager()

            # RIGHT SIDE: Jackett
            with Vertical(classes="pane", id="jackett-pane"):
                yield JackettSearch()
        yield Footer()

    # Tracks the current view state: 0=Both, 1=Transmission Only, 2=Jackett Only
    view_mode = 0

    def on_resize(self, event) -> None:
        """Hide the header if the terminal height is too small."""
        header = self.query_one(CarJackerHeader)

        # If terminal height is less than 20 rows, hide the header
        # You can adjust '20' to whatever threshold looks best for your ASCII art
        if event.size.height < 30:
            header.display = False
        else:
            header.display = True

    def action_cycle_view(self) -> None:
        """Cycles through the three layout modes."""
        self.view_mode = (self.view_mode + 1) % 3

        trans_pane = self.query_one("#transmission-pane")
        jackett_pane = self.query_one("#jackett-pane")

        if self.view_mode == 0:
            trans_pane.display = True
            jackett_pane.display = True
        elif self.view_mode == 1:
            trans_pane.display = True
            jackett_pane.display = False
            trans_pane.focus()
        else:
            trans_pane.display = False
            jackett_pane.display = True
            jackett_pane.focus()

    def action_toggle_status(self):
        """Logic based on which widget currently has the focus."""
        # Transmission interface
        if self.query_one(TransmissionManager).query("DataTable:focus"):
            self.query_one(TransmissionManager).toggle_selected()

        # Jackett interface
        elif self.query_one(JackettSearch).query("DataTable:focus"):
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
