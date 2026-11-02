"""Model layer for the Pong game.

This module contains the game state, gameplay rules, and save/load logic.
The model is responsible for data and behavior only; it does not render the game
or directly read keyboard input.
"""

import json
import math
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path

import pygame


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
PADDLE_WIDTH = 16
PADDLE_HEIGHT = 110
BALL_SIZE = 14

PLAYER_ONE = "player_one"
PLAYER_TWO = "player_two"
MODE_SINGLE_PLAYER = "single"
MODE_TWO_PLAYER = "two_player"
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

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
    """Return the OS-specific directory used to store user progress."""
    if os.name == "nt":
        base_directory = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base_directory = Path.home() / "Library" / "Application Support"
    else:
        base_directory = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    app_directory = base_directory / "pong-game"
    app_directory.mkdir(parents=True, exist_ok=True)
    return app_directory


PROGRESS_FILE = get_save_directory() / "pong_progress.json"


def center_paddle_y() -> float:
    """Return the vertical center position for a paddle."""
    return WINDOW_HEIGHT / 2 - PADDLE_HEIGHT / 2


def launch_direction() -> int:
    """Return a random direction for the opening serve."""
    return random.choice([-1, 1])


@dataclass
class Paddle:
    """Represents a single paddle used by either player or CPU."""

    x: int
    y: int
    width: int = PADDLE_WIDTH
    height: int = PADDLE_HEIGHT
    color: tuple[int, int, int] = (255, 255, 255)
    speed: float = 520.0

    def __post_init__(self) -> None:
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction: int, delta_time: float) -> None:
        self.rect.y += direction * self.speed * delta_time

    def clamp(self) -> None:
        self.rect.y = max(0, min(self.rect.y, WINDOW_HEIGHT - self.rect.height))

    def reset_to_center(self) -> None:
        self.rect.y = center_paddle_y()


@dataclass
class Ball:
    """Represents the moving ball in the arena."""

    x: int
    y: int
    size: int = BALL_SIZE
    speed: float = 430.0
    color: tuple[int, int, int] = (255, 255, 255)

    def __post_init__(self) -> None:
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.velocity = [self.speed, self.speed * 0.4]

    def reset(self, direction: int) -> None:
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        launch_angle = random.uniform(-0.8, 0.8)
        self.velocity = [direction * self.speed, math.sin(launch_angle) * self.speed]

    def update(self, delta_time: float, left_paddle: Paddle, right_paddle: Paddle, game: "PongModel") -> None:
        self.rect.x += self.velocity[0] * delta_time
        self.rect.y += self.velocity[1] * delta_time

        self._resolve_wall_collision()
        self._resolve_paddle_collisions(left_paddle, right_paddle)
        self._award_scoring_points(game)

    def _resolve_wall_collision(self) -> None:
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity[1] *= -1
        elif self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.velocity[1] *= -1

    def _resolve_paddle_collisions(self, left_paddle: Paddle, right_paddle: Paddle) -> None:
        if self.rect.colliderect(left_paddle.rect):
            self.rect.left = left_paddle.rect.right
            self._bounce_off_paddle(left_paddle, direction=1)
        elif self.rect.colliderect(right_paddle.rect):
            self.rect.right = right_paddle.rect.left
            self._bounce_off_paddle(right_paddle, direction=-1)

    def _bounce_off_paddle(self, paddle: Paddle, direction: int) -> None:
        bounce_speed = max(abs(self.velocity[0]), 430.0) + 30.0
        paddle_offset = (self.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)

        self.velocity[0] = direction * bounce_speed
        self.velocity[1] = paddle_offset * 360.0

        vector_length = math.hypot(self.velocity[0], self.velocity[1]) or 1.0
        self.velocity[0] = (self.velocity[0] / vector_length) * bounce_speed
        self.velocity[1] = (self.velocity[1] / vector_length) * bounce_speed

    def _award_scoring_points(self, game: "PongModel") -> None:
        if self.rect.left <= 0:
            game.right_score += 1
            game.on_point_conceded()
            game.handle_score()
        elif self.rect.right >= WINDOW_WIDTH:
            game.left_score += 1
            game.handle_score()


class PongModel:
    """Stores the game state and enforces the rules of the match."""

    WINNING_SCORE = 7

    def __init__(self) -> None:
        self.state = STATE_MENU
        self.mode = None
        self.left_score = 0
        self.right_score = 0
        self.winner = None

        self.high_score = 0.0
        self.current_survival_time = 0.0
        self.unlocked_colors = {"white"}
        self.selected_color_name = "white"
        self._load_progress()

        self.left_paddle = Paddle(24, center_paddle_y(), PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLORS[self.selected_color_name])
        self.right_paddle = Paddle(WINDOW_WIDTH - 24 - PADDLE_WIDTH, center_paddle_y(), PADDLE_WIDTH, PADDLE_HEIGHT, (255, 255, 255))
        self.ball = Ball(WINDOW_WIDTH // 2 - BALL_SIZE // 2, WINDOW_HEIGHT // 2 - BALL_SIZE // 2)
        self._apply_selected_color_to_player_paddle()

    def _load_progress(self) -> None:
        try:
            with PROGRESS_FILE.open("r", encoding="utf-8") as save_file:
                progress_data = json.load(save_file)
        except (FileNotFoundError, json.JSONDecodeError):
            progress_data = {}

        self.high_score = float(progress_data.get("high_score", 0.0))
        self.unlocked_colors = set(progress_data.get("unlocked_colors", ["white"]))
        self.selected_color_name = progress_data.get("selected_color", "white")
        self._refresh_unlocks_from_best_score()

        if self.selected_color_name not in self.unlocked_colors:
            self.selected_color_name = "white"

    def _save_progress(self) -> None:
        progress_data = {
            "high_score": round(self.high_score, 1),
            "unlocked_colors": sorted(self.unlocked_colors),
            "selected_color": self.selected_color_name,
        }

        with PROGRESS_FILE.open("w", encoding="utf-8") as save_file:
            json.dump(progress_data, save_file, indent=2)

    def _refresh_unlocks_from_best_score(self) -> None:
        for color_name, unlock_threshold in PADDLE_UNLOCKS.items():
            if self.high_score >= unlock_threshold:
                self.unlocked_colors.add(color_name)

    def _apply_selected_color_to_player_paddle(self) -> None:
        if self.selected_color_name not in self.unlocked_colors:
            self.selected_color_name = "white"
        self.left_paddle.color = PADDLE_COLORS[self.selected_color_name]

    def get_unlocked_color_names(self) -> list[str]:
        unlocked_names = []
        for color_name in PADDLE_COLORS:
            if color_name in self.unlocked_colors:
                unlocked_names.append(color_name)
        return unlocked_names

    def cycle_selected_color(self, step: int = 1) -> None:
        unlocked_colors = self.get_unlocked_color_names()
        if not unlocked_colors:
            return

        current_index = unlocked_colors.index(self.selected_color_name)
        next_index = (current_index + step) % len(unlocked_colors)
        self.selected_color_name = unlocked_colors[next_index]
        self._apply_selected_color_to_player_paddle()
        self._save_progress()

    def start_game(self, mode: str) -> None:
        self.mode = mode
        self.state = STATE_PLAYING
        self.left_score = 0
        self.right_score = 0
        self.winner = None
        self.current_survival_time = 0.0

        self._reset_paddles_to_center()
        self._apply_selected_color_to_player_paddle()
        self.ball.reset(launch_direction())

    def _reset_paddles_to_center(self) -> None:
        self.left_paddle.reset_to_center()
        self.right_paddle.reset_to_center()

    def on_point_conceded(self) -> None:
        if self.mode == MODE_SINGLE_PLAYER:
            self.current_survival_time = 0.0

    def handle_score(self) -> None:
        if self.left_score >= self.WINNING_SCORE or self.right_score >= self.WINNING_SCORE:
            self.state = STATE_GAME_OVER
            if self.mode == MODE_SINGLE_PLAYER:
                self.winner = "Player 1" if self.left_score > self.right_score else "CPU"
            else:
                self.winner = "Player 1" if self.left_score > self.right_score else "Player 2"
            return

        if self.left_score > self.right_score:
            self.ball.reset(1)
        else:
            self.ball.reset(-1)

    def update(self, delta_time: float, key_state: pygame.key.ScancodeWrapper) -> None:
        if self.state != STATE_PLAYING:
            return

        self._update_survival_progress(delta_time)
        self._move_left_paddle(key_state, delta_time)

        if self.mode == MODE_SINGLE_PLAYER:
            self._update_cpu_paddle(delta_time)
        elif self.mode == MODE_TWO_PLAYER:
            self._move_right_paddle(key_state, delta_time)

        self.ball.update(delta_time, self.left_paddle, self.right_paddle, self)

    def _update_survival_progress(self, delta_time: float) -> None:
        if self.mode != MODE_SINGLE_PLAYER:
            return

        self.current_survival_time += delta_time
        previous_best = self.high_score
        self.high_score = max(self.high_score, self.current_survival_time)

        if self.high_score > previous_best:
            self._refresh_unlocks_from_best_score()
            self._save_progress()

    def _move_left_paddle(self, key_state: pygame.key.ScancodeWrapper, delta_time: float) -> None:
        move_direction = 0
        if key_state[pygame.K_w]:
            move_direction -= 1
        if key_state[pygame.K_s]:
            move_direction += 1

        self.left_paddle.move(move_direction, delta_time)
        self.left_paddle.clamp()

    def _move_right_paddle(self, key_state: pygame.key.ScancodeWrapper, delta_time: float) -> None:
        move_direction = 0
        if key_state[pygame.K_UP]:
            move_direction -= 1
        if key_state[pygame.K_DOWN]:
            move_direction += 1

        self.right_paddle.move(move_direction, delta_time)
        self.right_paddle.clamp()

    def _update_cpu_paddle(self, delta_time: float) -> None:
        target_y = self.ball.rect.centery - self.right_paddle.rect.height / 2

        if self.ball.rect.x > WINDOW_WIDTH * 0.35:
            if self.right_paddle.rect.centery < target_y:
                self.right_paddle.move(1, delta_time)
            elif self.right_paddle.rect.centery > target_y:
                self.right_paddle.move(-1, delta_time)

        self.right_paddle.clamp()
