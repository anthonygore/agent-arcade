"""Claude Code agent implementation."""

from typing import List, Tuple

from .base import BaseAgent


class ClaudeCodeAgent(BaseAgent):
    """Claude Code specific configuration."""

    def get_launch_command(self) -> Tuple[str, List[str]]:
        """
        Get command to launch Claude Code.

        Returns:
            (command, args) tuple
        """
        return (self.config.command, self.config.args)
