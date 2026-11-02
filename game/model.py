"""The Pong game model.

This module contains the central game logic and rules. It owns the game state,
score, paddle positions, CPU behavior, and progression updates.
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
    return SCREEN_HEIGHT / 2 - PADDLE_HEIGHT / 2


def random_launch_direction() -> int:
    return random.choice([-1, 1])


class PongModel:
    """Stores the state and gameplay rules for a single game session."""

    WINNING_SCORE = 7

    def __init__(self, progression_service: ProgressionService | None = None) -> None:
        self.progression_service = progression_service or ProgressionService()
        self.state = GameState.MENU.value
        self.game_mode = None
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

    def get_unlocked_color_names(self) -> list[str]:
        ordered_colors = []
        for color_name in PADDLE_COLORS:
            if color_name in self.unlocked_colors:
                ordered_colors.append(color_name)
        return ordered_colors

    def apply_selected_color_to_player_paddle(self) -> None:
        if self.selected_color_name not in self.unlocked_colors:
            self.selected_color_name = "white"
        self.left_paddle.color = PADDLE_COLORS[self.selected_color_name]

    def cycle_selected_color(self, step: int = 1) -> None:
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
        self.game_mode = mode.value if isinstance(mode, GameMode) else mode
        self.state = GameState.PLAYING.value
        self.player_one_score = 0
        self.player_two_score = 0
        self.winner_name = None
        self.current_survival_time = 0.0

        self.reset_paddles_to_center()
        self.apply_selected_color_to_player_paddle()
        self.ball.reset(random_launch_direction())

    def reset_paddles_to_center(self) -> None:
        self.left_paddle.reset_to_center()
        self.right_paddle.reset_to_center()

    def on_point_conceded(self) -> None:
        if self.game_mode == GameMode.SINGLE_PLAYER.value:
            self.current_survival_time = 0.0

    def handle_score(self) -> None:
        if self.player_one_score >= self.WINNING_SCORE or self.player_two_score >= self.WINNING_SCORE:
            self.state = GameState.GAME_OVER.value
            if self.game_mode == GameMode.SINGLE_PLAYER.value:
                self.winner_name = "Player 1" if self.player_one_score > self.player_two_score else "CPU"
            else:
                self.winner_name = "Player 1" if self.player_one_score > self.player_two_score else "Player 2"
            return

        self.reset_ball_for_next_point()

    def reset_ball_for_next_point(self) -> None:
        if self.player_one_score > self.player_two_score:
            self.ball.reset(1)
        else:
            self.ball.reset(-1)

    def update(self, delta_time: float, key_state: pygame.key.ScancodeWrapper) -> None:
        if self.state != GameState.PLAYING.value:
            return

        self.update_survival_progress(delta_time)
        self.move_left_paddle(key_state, delta_time)

        if self.game_mode == GameMode.SINGLE_PLAYER.value:
            self.update_cpu_paddle(delta_time)
        elif self.game_mode == GameMode.TWO_PLAYER.value:
            self.move_right_paddle(key_state, delta_time)

        self.ball.update(delta_time, self.left_paddle, self.right_paddle, self)

    def update_survival_progress(self, delta_time: float) -> None:
        if self.game_mode != GameMode.SINGLE_PLAYER.value:
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
        move_direction = 0
        if key_state[pygame.K_w]:
            move_direction -= 1
        if key_state[pygame.K_s]:
            move_direction += 1

        self.left_paddle.move(move_direction, delta_time)
        self.left_paddle.clamp()

    def move_right_paddle(self, key_state: pygame.key.ScancodeWrapper, delta_time: float) -> None:
        move_direction = 0
        if key_state[pygame.K_UP]:
            move_direction -= 1
        if key_state[pygame.K_DOWN]:
            move_direction += 1

        self.right_paddle.move(move_direction, delta_time)
        self.right_paddle.clamp()

    def update_cpu_paddle(self, delta_time: float) -> None:
        target_y = self.ball.rect.centery - self.right_paddle.rect.height / 2

        if self.ball.rect.x > SCREEN_WIDTH * 0.35:
            if self.right_paddle.rect.centery < target_y:
                self.right_paddle.move(1, delta_time)
            elif self.right_paddle.rect.centery > target_y:
                self.right_paddle.move(-1, delta_time)

        self.right_paddle.clamp()
