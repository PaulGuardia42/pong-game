"""Unit tests for the Pong model.

These tests focus on the core gameplay rules and state transitions so regressions
are caught early during development.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from game.model import PongModel
from game.progression_service import ProgressionService


class PongModelTests(unittest.TestCase):
    """Validate the model behavior used by gameplay and progression."""

    def setUp(self) -> None:
        self.temp_directory = TemporaryDirectory()
        progress_path = Path(self.temp_directory.name) / "pong_progress.json"
        self.service = ProgressionService(progress_path)
        self.model = PongModel(progression_service=self.service)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_model_starts_in_menu_state(self) -> None:
        self.assertEqual(self.model.state, "menu")

    def test_start_game_resets_scores_and_mode(self) -> None:
        self.model.start_game("single")

        self.assertEqual(self.model.state, "playing")
        self.assertEqual(self.model.game_mode, "single")
        self.assertEqual(self.model.player_one_score, 0)
        self.assertEqual(self.model.player_two_score, 0)

    def test_cycle_selected_color_moves_to_next_unlocked_option(self) -> None:
        self.model.unlocked_colors = {"white", "cyan", "green"}
        self.model.selected_color_name = "white"

        self.model.cycle_selected_color()

        self.assertEqual(self.model.selected_color_name, "cyan")

    def test_toggle_pause_switches_between_playing_and_paused(self) -> None:
        self.model.state = "playing"

        self.model.toggle_pause()
        self.assertEqual(self.model.state, "paused")

        self.model.toggle_pause()
        self.assertEqual(self.model.state, "playing")

    def test_return_to_menu_clears_active_game_mode(self) -> None:
        self.model.state = "playing"
        self.model.game_mode = "single"

        self.model.return_to_menu()

        self.assertEqual(self.model.state, "menu")
        self.assertIsNone(self.model.game_mode)


if __name__ == "__main__":
    unittest.main()
