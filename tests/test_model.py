"""Unit tests for the progression service.

These tests verify that progress can be saved and restored safely and that the
unlock rules behave as expected.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from game.progression_service import ProgressionService


class ProgressionServiceTests(unittest.TestCase):
    """Validate the disk persistence layer used by the game."""

    def setUp(self) -> None:
        self.temp_directory = TemporaryDirectory()
        self.save_path = Path(self.temp_directory.name) / "progress.json"
        self.service = ProgressionService(self.save_path)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_load_progress_returns_empty_dict_when_file_is_missing(self) -> None:
        progress = self.service.load_progress()

        self.assertEqual(progress, {})

    def test_save_and_load_round_trip_keeps_data(self) -> None:
        self.service.save_progress(25.5, {"white", "cyan", "green"}, "green")

        reloaded = self.service.load_progress()

        self.assertEqual(reloaded["high_score"], 25.5)
        self.assertIn("cyan", reloaded["unlocked_colors"])
        self.assertEqual(reloaded["selected_color"], "green")

    def test_refresh_unlocks_creates_expected_colors(self) -> None:
        unlocked_colors = self.service.refresh_unlocks(15.0)

        self.assertIn("white", unlocked_colors)
        self.assertIn("cyan", unlocked_colors)

    def test_refresh_unlocks_does_not_unlock_later_colors_too_early(self) -> None:
        unlocked_colors = self.service.refresh_unlocks(10.0)

        self.assertNotIn("green", unlocked_colors)


if __name__ == "__main__":
    unittest.main()
