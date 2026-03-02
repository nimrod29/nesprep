"""Log tools: log_thought for recording reasoning before every action."""

import sys
from datetime import datetime, timezone

from langchain_core.tools import tool


def _log_line(message: str, log_path: str | None) -> None:
    """Write a timestamped log line to stderr and optionally to a file."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[NesPrep] {ts} | {message}\n"
    sys.stderr.write(line)
    sys.stderr.flush()
    if log_path:
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line)
        except OSError:
            pass


class LogTools:
    """Tools for logging thoughts before actions."""

    def __init__(self, log_file_path: str | None = None):
        self.log_file_path = log_file_path

    def get_tools(self) -> list:
        """Return the list of log tools."""
        log_path = self.log_file_path

        @tool
        def log_thought(thought: str) -> str:
            """Log your thought/reasoning before EVERY action you take.

            IMPORTANT: You MUST call this tool before EVERY other tool call.
            Use it to explain your reasoning, what you're about to do, and why.
            This creates a visible chain-of-thought for the user.

            Examples:
            - "Analyzing constraints for employee שקד - checking availability days."
            - "Assigning דניאל to morning shift on Sunday - he prefers morning shifts."
            - "Validating that no employee exceeds max hours per week."

            Args:
                thought: Your reasoning and what you're about to do next.

            Returns:
                Confirmation that the thought was logged.
            """
            _log_line(thought, log_path)
            return "Logged."

        return [log_thought]
