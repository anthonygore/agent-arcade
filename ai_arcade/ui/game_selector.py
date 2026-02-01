"""Game selection UI for AI Arcade."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import DataTable, Header, Static


class GameSelectorScreen(Screen):
    """Game selection menu screen."""

    BINDINGS = [
        ("q", "quit_to_menu", "Quit"),
        ("enter", "select_game", "Play"),
        ("r", "resume_game", "Resume"),
    ]

    CSS = """
    Screen {
        background: $surface;
    }

    #header-text {
        dock: top;
        height: 1;
        content-align: center middle;
        background: $panel;
        text-style: bold;
    }

    #selector-columns {
        height: 100%;
        margin: 1;
    }

    #games-column {
        width: 2fr;
        height: 100%;
        padding-right: 1;
    }

    #instructions-column {
        width: 1fr;
        height: 100%;
        padding: 1;
        background: $panel;
        content-align: left top;
    }

    #game-table {
        height: 100%;
        width: 100%;
    }

    """

    def __init__(self, library, save_manager):
        """
        Initialize game selector.

        Args:
            library: GameLibrary instance
            save_manager: SaveStateManager instance
        """
        super().__init__()
        self.library = library
        self.save_manager = save_manager
        self.games = library.list_games(sort_by="last_played")
        self.selected_game_id: str = None
        self.resume: bool = False

    def compose(self) -> ComposeResult:
        """Compose UI layout."""
        yield Header()

        yield Static("Select game", id="header-text")

        with Container():
            with Horizontal(id="selector-columns"):
                # Create game table
                table = DataTable(cursor_type="row", id="game-table")
                table.add_columns(
                    "Title",
                    "Description",
                )

                for game_meta in self.games:
                    game_id = game_meta.id

                    table.add_row(
                        game_meta.name,
                        game_meta.description,
                        key=game_id
                    )

                with Container(id="games-column"):
                    yield table

                with Container(id="instructions-column"):
                    yield Static(
                        "Please select a game. Tip: games automatically pause when "
                        "you switch back to your Agent"
                    )

    def on_mount(self) -> None:
        """Focus the table when screen mounts."""
        table = self.query_one(DataTable)
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """
        Handle row selection (Enter key on table).

        Args:
            event: Row selection event
        """
        if event.row_key:
            self.selected_game_id = event.row_key.value
            self.resume = False
            self.dismiss({"game_id": self.selected_game_id, "resume": self.resume})

    def action_select_game(self) -> None:
        """Play selected game (new game)."""
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            cursor_key = table.coordinate_to_cell_key(table.cursor_coordinate)
            if cursor_key.row_key:
                self.selected_game_id = cursor_key.row_key.value
                self.resume = False
                self.dismiss({"game_id": self.selected_game_id, "resume": self.resume})

    def action_resume_game(self) -> None:
        """Resume selected game if save exists."""
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            cursor_key = table.coordinate_to_cell_key(table.cursor_coordinate)
            if cursor_key.row_key:
                game_id = cursor_key.row_key.value

                if self.save_manager.has_save(game_id):
                    self.selected_game_id = game_id
                    self.resume = True
                    self.dismiss({"game_id": self.selected_game_id, "resume": self.resume})
                else:
                    # Show notification that no save exists
                    self.notify("No saved game", severity="warning")

    def action_quit_to_menu(self) -> None:
        """Quit to menu."""
        self.dismiss(None)
