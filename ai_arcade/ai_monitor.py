"""AI agent output monitoring."""

import re
import threading
import time
from typing import Callable, Optional

from .agents.base import BaseAgent, AgentStatus
from .tmux_manager import TmuxManager


class AIMonitor:
    """Monitors AI agent output for readiness."""

    # Regex to match ANSI escape sequences
    ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def __init__(self, tmux_manager: TmuxManager, agent: BaseAgent, config):
        """
        Initialize AI monitor.

        Args:
            tmux_manager: TmuxManager instance
            agent: Agent instance
            config: Config instance
        """
        self.tmux = tmux_manager
        self.agent = agent
        self.config = config

        self.check_interval = config.monitoring.check_interval
        self.inactivity_timeout = config.monitoring.inactivity_timeout
        self.buffer_lines = config.monitoring.buffer_lines

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_output = ""
        self._last_change_time = time.time()

        # Agent state: idle or active
        # idle = user is typing or agent is waiting (default state)
        # active = agent is thinking or generating output
        self._is_idle = True  # Default to idle state
        self._last_idle_time = time.time()  # Track when agent last matched idle patterns

        # Callback when state changes
        self.on_state_changed: Optional[Callable[[bool], None]] = None

    @classmethod
    def _strip_ansi_codes(cls, text: str) -> str:
        """
        Remove ANSI escape sequences from text.

        Args:
            text: Text potentially containing ANSI codes

        Returns:
            Text with ANSI codes removed
        """
        return cls.ANSI_ESCAPE.sub('', text)

    def start(self) -> None:
        """Start monitoring in background thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop monitoring thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _monitor_loop(self) -> None:
        """Main monitoring loop (runs in thread)."""
        while self._running:
            try:
                # Capture recent output from AI window
                output = self.tmux.capture_window_output(
                    self.tmux.ai_window_index,
                    lines=self.buffer_lines
                )

                # Check if output has changed
                if output != self._last_output:
                    self._last_output = output
                    self._last_change_time = time.time()

                # Strip ANSI codes before pattern matching for more reliable detection
                clean_output = self._strip_ansi_codes(output)

                # Check agent-specific ready patterns
                status = self.agent.check_ready(clean_output)

                # Determine state: idle or active
                # idle = agent shows ready pattern (user typing or agent waiting)
                # active = agent doesn't show ready pattern (thinking/generating)
                is_idle = status.is_ready

                # Update timestamp when in idle state
                if is_idle:
                    self._last_idle_time = time.time()
                else:
                    # Grace period: if agent was recently idle (< 2s ago),
                    # keep it as idle to prevent flickering when user types
                    time_since_last_idle = time.time() - self._last_idle_time
                    if time_since_last_idle < 2.0:
                        is_idle = True

                # Update state and notify if changed
                if is_idle != self._is_idle:
                    self._is_idle = is_idle

                    # Update status bar
                    self.tmux.set_agent_state(self._is_idle)

                    # Send notification to game pane when becoming idle
                    if self._is_idle and self.config.notifications.enabled:
                        self._send_notification()

                    # Call callback if set
                    if self.on_state_changed:
                        self.on_state_changed(self._is_idle)

                # Monitor game window for current game
                self._monitor_game_status()

                # Sleep until next check
                time.sleep(self.check_interval)

            except Exception as e:
                # Don't crash the monitor thread on errors
                print(f"Monitor error: {e}")
                time.sleep(self.check_interval)

    def _monitor_game_status(self) -> None:
        """Monitor game window to detect current game."""
        try:
            # Capture game window output
            game_output = self.tmux.capture_window_output(
                self.tmux.game_window_index,
                lines=10
            )

            # Check for game indicators in output
            # Look for common game patterns
            current_game = None
            if "Snake" in game_output or "snake" in game_output:
                current_game = "Snake"
            elif "Pong" in game_output or "pong" in game_output:
                current_game = "Pong"
            elif "Tetris" in game_output or "tetris" in game_output:
                current_game = "Tetris"
            elif "Game Selection" in game_output or "Select a game" in game_output:
                current_game = None  # In selector

            # Update status bar if game changed
            if current_game != self.tmux.current_game:
                self.tmux.set_game_status(current_game)

        except Exception:
            # Ignore errors in game monitoring
            pass

    def _send_notification(self) -> None:
        """Send notification to game window that AI is ready."""
        if not self.config.notifications.visual:
            return

        try:
            message = self.config.notifications.message
            duration = int(self.config.notifications.flash_duration * 1000)  # Convert to ms

            target = f"{self.tmux.session_name}:{self.tmux.game_window_index}"
            self.tmux._send_tmux_cmd([
                "display-message", "-t", target,
                "-d", str(duration),
                message
            ])
        except Exception as e:
            print(f"Warning: Could not send notification: {e}")

    @property
    def is_idle(self) -> bool:
        """
        Current agent state.

        Returns:
            True if idle (user typing or agent waiting)
            False if active (agent thinking or generating)
        """
        return self._is_idle
