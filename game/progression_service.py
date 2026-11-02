"""Save/load service for the player's persistent progression.

This service isolates disk I/O from the rest of the game logic. That separation
makes the model easier to reason about, and it makes testing much easier because
progression logic can be validated without interacting with real files.
"""

import json
from pathlib import Path

from .config import DEFAULT_PROGRESS_PATH, PADDLE_UNLOCKS


class ProgressionService:
    """Keeps track of the player's unlocked content and best survival time."""

    def __init__(self, save_path: Path | None = None) -> None:
        self.save_path = save_path or DEFAULT_PROGRESS_PATH
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

    def load_progress(self) -> dict:
        """Load the saved JSON payload from disk, returning empty defaults if absent."""
        try:
            with self.save_path.open("r", encoding="utf-8") as save_file:
                return json.load(save_file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_progress(self, high_score: float, unlocked_colors: set[str], selected_color: str) -> None:
        """Persist progression data to disk as a human-readable JSON file."""
        payload = {
            "high_score": round(high_score, 1),
            "unlocked_colors": sorted(unlocked_colors),
            "selected_color": selected_color,
        }

        with self.save_path.open("w", encoding="utf-8") as save_file:
            json.dump(payload, save_file, indent=2)

    def refresh_unlocks(self, high_score: float) -> set[str]:
        """Recompute unlocked colors for the given survival-time score."""
        unlocked_colors = {"white"}
        for color_name, unlock_threshold in PADDLE_UNLOCKS.items():
            if high_score >= unlock_threshold:
                unlocked_colors.add(color_name)
        return unlocked_colors
