"""Save-load service for persistent player progression.

This service centralizes all disk I/O for the player's saved information, including:
- best survival score
- unlocked paddle colors
- selected paddle color

Keeping save logic in a dedicated service reduces responsibility in the model and
makes the code more reusable and testable.
"""

import json
from pathlib import Path

from .config import DEFAULT_PROGRESS_PATH, PADDLE_UNLOCKS


class ProgressionService:
    """Handles loading and saving the player's persistent progression."""

    def __init__(self, save_path: Path | None = None) -> None:
        self.save_path = save_path or DEFAULT_PROGRESS_PATH
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

    def load_progress(self) -> dict:
        """Load the saved progress dictionary from disk."""
        try:
            with self.save_path.open("r", encoding="utf-8") as save_file:
                return json.load(save_file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_progress(self, high_score: float, unlocked_colors: set[str], selected_color: str) -> None:
        """Persist the player's progress to disk."""
        payload = {
            "high_score": round(high_score, 1),
            "unlocked_colors": sorted(unlocked_colors),
            "selected_color": selected_color,
        }

        with self.save_path.open("w", encoding="utf-8") as save_file:
            json.dump(payload, save_file, indent=2)

    def refresh_unlocks(self, high_score: float) -> set[str]:
        """Unlock paddle colors based on the player's best survival score."""
        unlocked_colors = {"white"}
        for color_name, unlock_threshold in PADDLE_UNLOCKS.items():
            if high_score >= unlock_threshold:
                unlocked_colors.add(color_name)
        return unlocked_colors
