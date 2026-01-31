"""Aider agent implementation."""

from typing import List, Tuple

from .base import BaseAgent


class AiderAgent(BaseAgent):
    """Aider specific configuration."""

    def get_launch_command(self) -> Tuple[str, List[str]]:
        """
        Get command to launch Aider.

        Returns:
            (command, args) tuple
        """
        return (self.config.command, self.config.args)
