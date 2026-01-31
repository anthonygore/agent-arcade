"""Main CLI entry point for AI Arcade."""

import atexit
import signal
import sys

from .agents import create_agent
from .ai_monitor import AIMonitor
from .config import Config
from .game_runner import GameRunnerApp
from .tmux_manager import TmuxManager
from .ui.launcher_menu import show_launcher


def main():
    """Main entry point for ai-arcade command."""
    try:
        # Load configuration
        config = Config.load()

        # Show launcher menu
        print("🎮 Starting AI Arcade...")
        selection = show_launcher(config)

        if selection["games_only"]:
            # Launch game runner without AI agent
            run_games_only(config)
        elif selection["agent"]:
            # Launch dual-pane with AI agent
            run_with_agent(config, selection["agent"])
        else:
            # User quit from launcher
            print("Exiting AI Arcade.")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n👋 Exiting AI Arcade.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def run_games_only(config):
    """
    Run game runner without AI agent.

    Args:
        config: Config instance
    """
    app = GameRunnerApp(config)
    app.run()


def run_with_agent(config, agent_id: str):
    """
    Run dual-pane mode with AI agent and games.

    Args:
        config: Config instance
        agent_id: ID of agent to launch (e.g., "claude_code")
    """
    # Get agent configuration
    agent_config = config.get_agent(agent_id)
    if not agent_config:
        print(f"❌ Error: Unknown agent '{agent_id}'")
        sys.exit(1)

    # Create agent instance
    agent = create_agent(agent_id, agent_config)

    # Get working directory
    working_dir = agent.get_working_directory()

    # Create tmux manager
    print(f"⚙️  Setting up tmux session for {agent_config.name}...")

    try:
        tmux = TmuxManager(config)
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # Set up cleanup handlers
    def cleanup():
        """Clean up tmux session on exit."""
        try:
            tmux.kill_session()
        except:
            pass

    atexit.register(cleanup)

    def signal_handler(sig, frame):
        """Handle termination signals."""
        print("\n👋 Exiting AI Arcade...")
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Create split-pane session
        tmux.create_session(working_dir)

        # Launch AI agent in top pane
        cmd, args = agent.get_launch_command()
        print(f"🤖 Launching {agent_config.name}...")
        tmux.launch_ai_agent(cmd, args, working_dir)

        # Launch game runner in bottom pane
        print("🎮 Starting game runner...")
        tmux.launch_game_runner()

        # Start AI monitoring
        print("👁️  Starting AI monitor...")
        monitor = AIMonitor(tmux, agent, config)
        monitor.start()

        # Show usage instructions
        print("\n" + "="*60)
        print("🎮 AI ARCADE is ready!")
        print("="*60)
        print(f"Prefix key: {config.keybindings.prefix}")
        print(f"  {config.keybindings.prefix} + {config.keybindings.switch_to_ai}: Switch to AI pane")
        print(f"  {config.keybindings.prefix} + {config.keybindings.switch_to_game}: Switch to game pane")
        print(f"  {config.keybindings.prefix} + {config.keybindings.quit}: Quit session")
        print("\nPress Ctrl+C to exit AI Arcade")
        print("="*60 + "\n")

        # Attach to tmux session (blocking)
        tmux.attach()

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        cleanup()
        sys.exit(1)

    finally:
        # Cleanup
        if 'monitor' in locals():
            monitor.stop()
        cleanup()


if __name__ == "__main__":
    main()
