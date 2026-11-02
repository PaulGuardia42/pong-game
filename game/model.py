"""The main Pong game model.

This module owns the gameplay rules, score tracking, pause state, CPU behavior,
and progression updates. It is intentionally free of rendering and input concerns
so it can be tested and evolved independently from the screen layer.
"""

import random

import pygame

from .config import (
    BALL_SIZE,
    PADDLE_COLORS,
    PADDLE_HEIGHT,
    PADDLE_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    GameMode,
    GameState,
)
from .entities import Ball, Paddle
from .progression_service import ProgressionService


def center_paddle_y() -> float:
    """Return the Y position that centers a paddle vertically on screen."""
    return SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2


def random_launch_direction() -> int:
    """Return a random sign for the opening serve."""
    return random.choice([-1, 1])


class PongModel:
    """Stores the current game session and enforces game rules."""

    WINNING_SCORE = 7

    def __init__(self, progression_service: ProgressionService | None = None) -> None:
        self.progression_service = progression_service or ProgressionService()
        self.state = GameState.MENU.value
        self.game_mode: str | GameMode | None = None
        self.player_one_score = 0
        self.player_two_score = 0
        self.winner_name = None

        self.high_score = 0.0
        self.current_survival_time = 0.0
        self.selected_color_name = "white"

        progress_data = self.progression_service.load_progress()
        self.high_score = float(progress_data.get("high_score", 0.0))
        self.unlocked_colors = set(progress_data.get("unlocked_colors", ["white"]))
        self.selected_color_name = progress_data.get("selected_color", "white")
        self.unlocked_colors = self.progression_service.refresh_unlocks(self.high_score)

        if self.selected_color_name not in self.unlocked_colors:
            self.selected_color_name = "white"

        self.left_paddle = Paddle(
            24,
            center_paddle_y(),
            PADDLE_WIDTH,
            PADDLE_HEIGHT,
            PADDLE_COLORS[self.selected_color_name],
        )
        self.right_paddle = Paddle(
            SCREEN_WIDTH - 24 - PADDLE_WIDTH,
            center_paddle_y(),
            PADDLE_WIDTH,
            PADDLE_HEIGHT,
            (255, 255, 255),
        )
        self.ball = Ball(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2)
        self.apply_selected_color_to_player_paddle()

    def _mode_value(self, mode: str | GameMode | None) -> str | None:
        """Normalize a mode to a consistent string value for comparisons."""
        if mode is None:
            return None
        if isinstance(mode, GameMode):
            return mode.value
        return mode

    def _is_single_player_mode(self) -> bool:
        """Return True when the active match is in single-player mode."""
        return self._mode_value(self.game_mode) == GameMode.SINGLE_PLAYER.value

    def _is_two_player_mode(self) -> bool:
        """Return True when the active match is in two-player mode."""
        return self._mode_value(self.game_mode) == GameMode.TWO_PLAYER.value

    def get_unlocked_color_names(self) -> list[str]:
        """Return the unlocked colors preserving the order defined in the palette."""
        ordered_colors = []
        for color_name in PADDLE_COLORS:
            if color_name in self.unlocked_colors:
                ordered_colors.append(color_name)
        return ordered_colors

    def apply_selected_color_to_player_paddle(self) -> None:
        """Apply the currently selected color to the player's paddle."""
        if self.selected_color_name not in self.unlocked_colors:
            self.selected_color_name = "white"
        self.left_paddle.color = PADDLE_COLORS[self.selected_color_name]

    def cycle_selected_color(self, step: int = 1) -> None:
        """Move to the next unlocked paddle color and persist it."""
        unlocked_colors = self.get_unlocked_color_names()
        if not unlocked_colors:
            return

        current_index = unlocked_colors.index(self.selected_color_name)
        next_index = (current_index + step) % len(unlocked_colors)
        self.selected_color_name = unlocked_colors[next_index]
        self.apply_selected_color_to_player_paddle()
        self.progression_service.save_progress(
            self.high_score,
            self.unlocked_colors,
            self.selected_color_name,
        )

    def start_game(self, mode: str | GameMode) -> None:
        """Initialize a fresh round in the requested mode."""
        self.game_mode = GameMode(mode) if isinstance(mode, str) else mode
        self.state = GameState.PLAYING.value
        self.player_one_score = 0
        self.player_two_score = 0
        self.winner_name = None
        self.current_survival_time = 0.0

        self.reset_paddles_to_center()
        self.apply_selected_color_to_player_paddle()
        self.ball.reset(random_launch_direction())

    def reset_paddles_to_center(self) -> None:
        """Reset both paddles to the center of the court before play resumes."""
        self.left_paddle.reset_to_center()
        self.right_paddle.reset_to_center()

    def on_point_conceded(self) -> None:
        """Reset the survival timer when a player loses a point in single-player mode."""
        if self._is_single_player_mode():
            self.current_survival_time = 0.0

    def handle_score(self) -> None:
        """Check for a winner and reset the ball for the next serve."""
        if self.player_one_score >= self.WINNING_SCORE or self.player_two_score >= self.WINNING_SCORE:
            self.state = GameState.GAME_OVER.value
            if self._is_single_player_mode():
                self.winner_name = "Player 1" if self.player_one_score > self.player_two_score else "CPU"
            else:
                self.winner_name = "Player 1" if self.player_one_score > self.player_two_score else "Player 2"
            return

        self.reset_ball_for_next_point()

    def reset_ball_for_next_point(self) -> None:
        """Serve the ball toward the player who did not just concede the point."""
        if self.player_one_score > self.player_two_score:
            self.ball.reset(1)
        else:
            self.ball.reset(-1)

    def update(self, delta_time: float, key_state: pygame.key.ScancodeWrapper) -> None:
        """Advance the game by a single frame using the keyboard state."""
        if self.state != GameState.PLAYING.value:
            return

        self.update_survival_progress(delta_time)
        self.move_left_paddle(key_state, delta_time)

        if self._is_single_player_mode():
            self.update_cpu_paddle(delta_time)
        elif self._is_two_player_mode():
            self.move_right_paddle(key_state, delta_time)

        self.ball.update(delta_time, self.left_paddle, self.right_paddle, self)

    def update_survival_progress(self, delta_time: float) -> None:
        """Track survival time for single-player mode and update unlocked content."""
        if not self._is_single_player_mode():
            return

        self.current_survival_time += delta_time
        previous_best_score = self.high_score
        self.high_score = max(self.high_score, self.current_survival_time)

        if self.high_score > previous_best_score:
            self.unlocked_colors = self.progression_service.refresh_unlocks(self.high_score)
            self.progression_service.save_progress(
                self.high_score,
                self.unlocked_colors,
                self.selected_color_name,
            )

    def move_left_paddle(self, key_state: pygame.key.ScancodeWrapper, delta_time: float) -> None:
        """Move the left paddle using the W and S keys."""
        move_direction = 0
        if key_state[pygame.K_w]:
            move_direction -= 1
        if key_state[pygame.K_s]:
            move_direction += 1

        self.left_paddle.move(move_direction, delta_time)
        self.left_paddle.clamp()

    def move_right_paddle(self, key_state: pygame.key.ScancodeWrapper, delta_time: float) -> None:
        """Move the right paddle using the arrow keys for local multiplayer."""
        move_direction = 0
        if key_state[pygame.K_UP]:
            move_direction -= 1
        if key_state[pygame.K_DOWN]:
            move_direction += 1

        self.right_paddle.move(move_direction, delta_time)
        self.right_paddle.clamp()

    def update_cpu_paddle(self, delta_time: float) -> None:
        """Move the CPU paddle toward the ball to give a basic challenge."""
        target_y = self.ball.rect.centery - self.right_paddle.rect.height / 2

        if self.ball.rect.x > SCREEN_WIDTH * 0.35:
            if self.right_paddle.rect.centery < target_y:
                self.right_paddle.move(1, delta_time)
            elif self.right_paddle.rect.centery > target_y:
                self.right_paddle.move(-1, delta_time)

        self.right_paddle.clamp()

    def toggle_pause(self) -> None:
        """Toggle the game between playing and paused states."""
        if self.state == GameState.PLAYING.value:
            self.state = GameState.PAUSED.value
        elif self.state == GameState.PAUSED.value:
            self.state = GameState.PLAYING.value

    def return_to_menu(self) -> None:
        """Return to the menu and clear the active match mode."""
        self.state = GameState.MENU.value
        self.game_mode = None
