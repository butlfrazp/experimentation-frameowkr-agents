"""Custom logging utilities for the experimentation CLI."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

SUCCESS_LEVEL = logging.INFO + 5
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

DEFAULT_THEME = Theme(
    {
        "log.time": "dim cyan",
        "log.level.info": "bold bright_blue",
        "log.level.success": "bold green",
        "log.level.warning": "bold yellow",
        "log.level.error": "bold red",
        "success": "bold green",
        "info": "bright_cyan",
        "warning": "yellow",
        "error": "bold red",
        "debug": "dim white",
        "banner": "bold cyan",
    }
)


@dataclass
class ExperimentLogger:
    """Wrapper around the standard library logging with Rich formatting."""

    name: str = "exp.cli"
    level: int = logging.INFO
    theme: Theme = DEFAULT_THEME
    console: Optional[Console] = None

    def __post_init__(self) -> None:
        self.console = self.console or Console(theme=self.theme, highlight=False)
        self._logger: logging.Logger = logging.getLogger(self.name)
        self._ensure_handler()
        self._logger.setLevel(self.level)
        self._logger.propagate = False

    def _ensure_handler(self) -> None:
        if any(isinstance(handler, RichHandler) for handler in self._logger.handlers):
            return

        handler = RichHandler(
            console=self.console,
            rich_tracebacks=True,
            show_level=True,
            show_time=True,
            show_path=False,
            markup=True,
            log_time_format="[%X]",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(handler)

    # Delegating helpers -------------------------------------------------
    def banner(self, message: str) -> None:
        """Render a decorative banner line for key events."""
        self.console.rule(f"[banner]{message}[/]")

    def debug(self, message: str, *args, **kwargs) -> None:
        self._logger.debug(f"[debug]{message}[/]", *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        self._logger.info(f"[info]{message}[/]", *args, **kwargs)

    def success(self, message: str, *args, **kwargs) -> None:
        self._logger.log(SUCCESS_LEVEL, f"[success]{message}[/]", *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        self._logger.warning(f"[warning]{message}[/]", *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self._logger.error(f"[error]{message}[/]", *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        self._logger.exception(f"[error]{message}[/]", *args, **kwargs)

    @property
    def logger(self) -> logging.Logger:
        return self._logger


@lru_cache(maxsize=16)
def get_logger(name: str = "exp.cli", level: int = logging.INFO) -> ExperimentLogger:
    """Return a cached `ExperimentLogger` instance."""
    return ExperimentLogger(name=name, level=level)
