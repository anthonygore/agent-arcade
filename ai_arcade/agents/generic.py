"""Generic agent implementation."""

from typing import List, Tuple

from .base import BaseAgent


class GenericAgent(BaseAgent):
    """Generic fallback for any CLI tool."""

    def get_launch_command(self) -> Tuple[str, List[str]]:
        """
        Get command to launch agent.

        Returns:
            (command, args) tuple
        """
        return (self.config.command, self.config.args)
