"""Shared configuration and constants for the Pong game.

This module centralizes values that are used across the application so they are
not repeated in multiple places. Keeping these values in one file makes the game
much easier to tune and maintain.
"""

from enum import Enum
import os
import sys
from pathlib import Path


class GameMode(str, Enum):
    """Defines the supported match types."""

    SINGLE_PLAYER = "single"
    TWO_PLAYER = "two_player"


class GameState(str, Enum):
    """Defines the lifecycle states of the game."""

    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"


SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
PADDLE_WIDTH = 16
PADDLE_HEIGHT = 110
BALL_SIZE = 14

PADDLE_COLORS = {
    "white": (255, 255, 255),
    "cyan": (102, 214, 255),
    "green": (102, 255, 140),
    "orange": (255, 170, 80),
    "purple": (192, 128, 255),
}

PADDLE_UNLOCKS = {
    "white": 0.0,
    "cyan": 15.0,
    "green": 30.0,
    "orange": 60.0,
    "purple": 90.0,
}


def get_save_directory() -> Path:
    """Return the OS-specific directory where user progress is stored."""
    if os.name == "nt":
        base_directory = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base_directory = Path.home() / "Library" / "Application Support"
    else:
        base_directory = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    app_directory = base_directory / "pong-game"
    app_directory.mkdir(parents=True, exist_ok=True)
    return app_directory


DEFAULT_PROGRESS_PATH = get_save_directory() / "pong_progress.json"
