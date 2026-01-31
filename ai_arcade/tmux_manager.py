"""tmux session management for AI Arcade."""

import shlex
import subprocess
from pathlib import Path
from typing import List, Optional


class TmuxManager:
    """Manages tmux session for AI Arcade."""

    def __init__(self, config):
        """
        Initialize tmux manager.

        Args:
            config: Config instance

        Raises:
            RuntimeError: If tmux is not installed
        """
        self.config = config
        self.session_name = config.tmux.session_name
        self.ai_pane_id: Optional[str] = None
        self.game_pane_id: Optional[str] = None

        # Check tmux availability
        if not self._is_tmux_available():
            raise RuntimeError(
                "tmux is not installed.\n"
                "Install with: brew install tmux (macOS) or apt-get install tmux (Linux)"
            )

    def _is_tmux_available(self) -> bool:
        """
        Check if tmux command exists.

        Returns:
            True if tmux is available
        """
        try:
            subprocess.run(
                ["tmux", "-V"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def create_session(self, working_dir: Optional[Path] = None) -> None:
        """
        Create new tmux session with split panes.

        Creates:
        - Top pane (70% height): For AI agent
        - Bottom pane (30% height): For game runner

        Args:
            working_dir: Working directory for session
        """
        # Kill existing session if present
        self._kill_session_if_exists()

        # Build create session command
        cmd = ["tmux", "new-session", "-d", "-s", self.session_name]

        if working_dir:
            cmd.extend(["-c", str(working_dir)])

        # Create new detached session
        subprocess.run(cmd, check=True)

        # Get initial pane ID (this will be AI pane)
        self.ai_pane_id = self._get_pane_id(0)

        # Split horizontally for game pane
        # Top pane gets pane_split_ratio%, bottom gets the rest
        split_percentage = 100 - self.config.tmux.pane_split_ratio
        subprocess.run([
            "tmux", "split-window", "-v",
            "-p", str(split_percentage),
            "-t", f"{self.session_name}:0"
        ], check=True)

        # Get game pane ID
        self.game_pane_id = self._get_pane_id(1)

        # Configure session
        self._configure_session()

    def _configure_session(self) -> None:
        """Set tmux session options."""
        # Enable mouse mode if configured
        if self.config.tmux.mouse_mode:
            self._send_tmux_cmd(["set-option", "-g", "mouse", "on"])

        # Configure status bar
        if self.config.tmux.status_bar:
            self._send_tmux_cmd(["set-option", "-g", "status", "on"])
            self._send_tmux_cmd([
                "set-option", "-g", "status-left",
                "🎮 AI ARCADE | "
            ])
        else:
            self._send_tmux_cmd(["set-option", "-g", "status", "off"])

        # Set keybindings
        prefix = self.config.keybindings.prefix
        self._send_tmux_cmd(["set-option", "-g", "prefix", prefix])

        # Unbind default prefix
        self._send_tmux_cmd(["unbind", "C-b"])

        # Bind prefix key
        self._send_tmux_cmd(["bind-key", prefix.replace("C-", "^"), "send-prefix"])

        # Bind pane switching keys
        switch_up = self.config.keybindings.switch_to_ai
        switch_down = self.config.keybindings.switch_to_game

        self._send_tmux_cmd([
            "bind-key", switch_up,
            "select-pane", "-t", self.ai_pane_id
        ])

        self._send_tmux_cmd([
            "bind-key", switch_down,
            "select-pane", "-t", self.game_pane_id
        ])

    def launch_ai_agent(
        self,
        agent_command: str,
        args: Optional[List[str]] = None,
        working_dir: Optional[Path] = None
    ) -> None:
        """
        Launch AI agent in top pane.

        Args:
            agent_command: Command to launch agent
            args: Optional command arguments
            working_dir: Optional working directory
        """
        if args is None:
            args = []

        # Build full command
        full_command = f"{agent_command} {' '.join(args)}"

        # Change directory if specified
        if working_dir:
            self.send_to_pane(
                self.ai_pane_id,
                f"cd {shlex.quote(str(working_dir))}"
            )

        # Launch agent
        self.send_to_pane(self.ai_pane_id, full_command)

    def launch_game_runner(self) -> None:
        """Launch game runner in bottom pane."""
        # Use Poetry to run the game runner module in the virtual environment
        runner_cmd = "export PATH=\"/Users/anthonygore/.local/bin:$PATH\" && poetry run python -m ai_arcade.game_runner"
        self.send_to_pane(self.game_pane_id, runner_cmd)

    def send_to_pane(
        self,
        pane_id: str,
        command: str,
        literal: bool = False
    ) -> None:
        """
        Send command to specific pane.

        Args:
            pane_id: tmux pane identifier
            command: Command string to send
            literal: If True, send keys literally without Enter
        """
        if literal:
            subprocess.run([
                "tmux", "send-keys", "-t", pane_id, "-l", command
            ], check=True)
        else:
            subprocess.run([
                "tmux", "send-keys", "-t", pane_id, command, "Enter"
            ], check=True)

    def capture_pane_output(self, pane_id: str, lines: int = 50) -> str:
        """
        Capture recent output from pane.

        Args:
            pane_id: Pane to capture
            lines: Number of lines of history to capture

        Returns:
            String containing pane content
        """
        result = subprocess.run([
            "tmux", "capture-pane", "-t", pane_id,
            "-p",  # Print to stdout
            "-S", f"-{lines}",  # Start from N lines back
            "-e"  # Include escape sequences
        ], capture_output=True, text=True, check=True)

        return result.stdout

    def attach(self) -> None:
        """Attach to tmux session (blocking)."""
        # Focus on AI pane first
        subprocess.run([
            "tmux", "select-pane", "-t", self.ai_pane_id
        ], check=True)

        # Attach to session
        subprocess.run([
            "tmux", "attach-session", "-t", self.session_name
        ], check=True)

    def kill_session(self) -> None:
        """Terminate tmux session."""
        subprocess.run([
            "tmux", "kill-session", "-t", self.session_name
        ], check=False)  # Don't fail if session doesn't exist

    def _kill_session_if_exists(self) -> None:
        """Kill session if it already exists."""
        result = subprocess.run([
            "tmux", "has-session", "-t", self.session_name
        ], capture_output=True)

        if result.returncode == 0:
            self.kill_session()

    def _get_pane_id(self, pane_index: int) -> str:
        """
        Get pane ID by index.

        Args:
            pane_index: Index of pane (0-based)

        Returns:
            Pane ID string
        """
        result = subprocess.run([
            "tmux", "list-panes", "-t", self.session_name,
            "-F", "#{pane_id}"
        ], capture_output=True, text=True, check=True)

        pane_ids = result.stdout.strip().split('\n')
        return pane_ids[pane_index]

    def _send_tmux_cmd(self, args: List[str]) -> None:
        """
        Send arbitrary tmux command.

        Args:
            args: Command arguments
        """
        subprocess.run(["tmux"] + args, check=True)
