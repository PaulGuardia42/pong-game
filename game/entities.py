"""Game entities used by the model layer.

This module holds the object definitions for the ball and paddle, which are game
objects but do not contain full gameplay orchestration.
"""

from dataclasses import dataclass
import math
import random

import pygame

from .config import BALL_SIZE, PADDLE_HEIGHT, PADDLE_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH


@dataclass
class Paddle:
    """Represents a player-controlled or CPU-controlled paddle."""

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
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    def reset_to_center(self) -> None:
        self.rect.y = SCREEN_HEIGHT / 2 - self.height / 2


@dataclass
class Ball:
    """Represents the ball and its physics."""

    x: int
    y: int
    size: int = BALL_SIZE
    speed: float = 430.0
    color: tuple[int, int, int] = (255, 255, 255)

    def __post_init__(self) -> None:
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.velocity = [self.speed, self.speed * 0.4]

    def reset(self, direction: int) -> None:
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        launch_angle = random.uniform(-0.8, 0.8)
        self.velocity = [direction * self.speed, math.sin(launch_angle) * self.speed]

    def update(self, delta_time: float, left_paddle: Paddle, right_paddle: Paddle, game_model: object) -> None:
        self.rect.x += self.velocity[0] * delta_time
        self.rect.y += self.velocity[1] * delta_time

        self._resolve_wall_bounces()
        self._resolve_paddle_collisions(left_paddle, right_paddle)
        self._handle_scoring(game_model)

    def _resolve_wall_bounces(self) -> None:
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity[1] *= -1
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
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

    def _handle_scoring(self, game_model: object) -> None:
        if self.rect.left <= 0:
            game_model.right_score += 1
            game_model.on_point_conceded()
            game_model.handle_score()
        elif self.rect.right >= SCREEN_WIDTH:
            game_model.left_score += 1
            game_model.handle_score()
