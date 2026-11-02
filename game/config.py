"""Shared configuration and constants for the Pong game.

This module defines the values that are reused across the game, such as window
size, paddle parameters, game state names, color selections, and progression
thresholds. Centralizing them here keeps tuning and future refactors easier and
reduces the risk of inconsistent values across the codebase.
"""

from enum import Enum
import os
import sys
from pathlib import Path


class GameMode(str, Enum):
    """Defines the supported game types.

    Using an Enum instead of raw strings prevents typo-prone comparisons and makes
    the game state more self-documenting as the project grows.
    """

    SINGLE_PLAYER = "single"
    TWO_PLAYER = "two_player"


class GameState(str, Enum):
    """Defines the lifecycle states for the game session.

    The application can be in a menu, actively playing, paused, or in a game-over
    screen. Explicit states make transitions clearer than loose string values.
    """

    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
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
    """Return the OS-specific directory used to store user progress.

    Saving user data under the OS app-data directory keeps project files clean and
    follows platform-specific conventions for long-term local storage.
    """
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
