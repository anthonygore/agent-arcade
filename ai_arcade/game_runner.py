"""Game runner for AI Arcade."""

import time

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from .config import Config
from .game_library import GameLibrary, SaveStateManager
from .games.base_game import GameState
from .ui.game_selector import GameSelectorScreen


class GameRunnerApp(App):
    """Main game runner application."""

    def __init__(self, config: Config):
        """
        Initialize game runner.

        Args:
            config: Config instance
        """
        super().__init__()
        self.config = config
        self.library = GameLibrary()
        self.save_manager = SaveStateManager()

        self.current_game = None
        self.game_start_time = None

    def compose(self) -> ComposeResult:
        """Compose UI layout."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        # Show game selector immediately
        self.show_game_selector()

    def show_game_selector(self) -> None:
        """Show the game selection screen."""
        selector = GameSelectorScreen(self.library, self.save_manager)

        def handle_selection(result):
            """Handle game selection."""
            if result is None:
                # User quit
                self.exit()
            else:
                self.launch_game(result["game_id"], result["resume"])

        self.push_screen(selector, handle_selection)

    def launch_game(self, game_id: str, resume: bool = False) -> None:
        """
        Launch a game.

        Args:
            game_id: Game identifier
            resume: Whether to resume from save
        """
        # Get game instance
        self.current_game = self.library.get_game(game_id)

        if not self.current_game:
            self.notify(f"Error: Could not load game {game_id}", severity="error")
            self.show_game_selector()
            return

        # Load save state if resuming
        if resume and self.save_manager.has_save(game_id):
            save_state = self.save_manager.load_game(game_id)
            if save_state:
                try:
                    self.current_game.load_save_state(save_state)
                except Exception as e:
                    self.notify(f"Warning: Could not load save: {e}", severity="warning")

        # Exit the runner app
        self.exit()

        # Track start time
        self.game_start_time = time.time()

        # Run the game (blocking)
        try:
            self.current_game.run()

            # Game finished, update stats
            play_time = int(time.time() - self.game_start_time)
            score = self.current_game.score

            self.library.update_play_stats(
                self.current_game.metadata.id,
                play_time,
                score
            )

            # Save state if paused
            if self.current_game.state == GameState.PAUSED:
                save_state = self.current_game.get_save_state()
                self.save_manager.save_game(
                    self.current_game.metadata.id,
                    save_state
                )
            elif self.current_game.state == GameState.GAME_OVER:
                # Clear save on game over
                self.save_manager.delete_save(self.current_game.metadata.id)

        except Exception as e:
            print(f"Error running game: {e}")

        finally:
            # Reset state
            self.current_game = None
            self.game_start_time = None

            # Re-run the runner to show selector again
            main()


def main():
    """Entry point for game runner."""
    config = Config.load()
    app = GameRunnerApp(config)
    app.run()


if __name__ == "__main__":
    main()
