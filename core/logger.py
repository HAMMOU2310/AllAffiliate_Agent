"""Structured Logger for AllAffiliate_Agent.

Preserves the existing public API:
    Logger.info(message)
    Logger.success(message)
    Logger.warning(message)
    Logger.error(message)

Backend: Python standard-library logging.
Handlers: rich console + rotating file (logs/app.log).
Level: configurable via APP_LOG_LEVEL env var (default: INFO).
"""

from __future__ import annotations

import logging
import logging.handlers
import os
from pathlib import Path

_INITIALIZED = False
_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def _ensure_log_dir() -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)


def _resolve_level() -> int:
    raw = os.getenv("APP_LOG_LEVEL", "").strip().upper()
    if not raw:
        return logging.INFO
    mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    return mapping.get(raw, logging.INFO)


def _init_root(force: bool = False) -> None:
    global _INITIALIZED
    if _INITIALIZED and not force:
        return
    _INITIALIZED = True

    root = logging.getLogger("allaffiliate")
    root.setLevel(_resolve_level())
    root.propagate = False

    if root.handlers and not force:
        return

    root.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _ensure_log_dir()
    fh = logging.handlers.RotatingFileHandler(
        _LOG_DIR / "app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    fh.setLevel(_resolve_level())
    fh.setFormatter(fmt)
    root.addHandler(fh)


def _get_logger() -> logging.Logger:
    _init_root()
    return logging.getLogger("allaffiliate")


class Logger:

    @staticmethod
    def info(message: str) -> None:
        _get_logger().info(message)
        try:
            from rich.console import Console
            Console().print(f"[cyan]{message}[/cyan]")
        except Exception:
            pass

    @staticmethod
    def success(message: str) -> None:
        _get_logger().info(message)
        try:
            from rich.console import Console
            Console().print(f"[green]{message}[/green]")
        except Exception:
            pass

    @staticmethod
    def warning(message: str) -> None:
        _get_logger().warning(message)
        try:
            from rich.console import Console
            Console().print(f"[yellow]{message}[/yellow]")
        except Exception:
            pass

    @staticmethod
    def error(message: str) -> None:
        _get_logger().error(message)
        try:
            from rich.console import Console
            Console().print(f"[red]{message}[/red]")
        except Exception:
            pass
