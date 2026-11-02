"""Game entities used by the model layer.

The entity classes in this module represent the physical objects in the game
world: the paddles and the ball. They know how to move, clamp themselves within
bounds, and react to collisions, but they do not decide high-level game flow.
"""

import math
import random
from dataclasses import dataclass

import pygame

from .config import BALL_SIZE, PADDLE_HEIGHT, PADDLE_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH


@dataclass
class Paddle:
    """Represents a paddle that may be controlled by a human or by the CPU."""

    x: int
    y: int
    width: int = PADDLE_WIDTH
    height: int = PADDLE_HEIGHT
    color: tuple[int, int, int] = (255, 255, 255)
    speed: float = 520.0

    def __post_init__(self) -> None:
        """Instantiate the collision rectangle once the paddle is created."""
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction: int, delta_time: float) -> None:
        """Move the paddle vertically along the Y axis."""
        self.rect.y += direction * self.speed * delta_time

    def clamp(self) -> None:
        """Keep the paddle visible within the play field."""
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    def reset_to_center(self) -> None:
        """Return the paddle to the center of the playfield."""
        self.rect.y = SCREEN_HEIGHT / 2 - self.height / 2


@dataclass
class Ball:
    """Represents the moving ball and its movement physics."""

    x: int
    y: int
    size: int = BALL_SIZE
    speed: float = 430.0
    color: tuple[int, int, int] = (255, 255, 255)

    def __post_init__(self) -> None:
        """Create the ball rectangle and initialize its default velocity."""
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.velocity = [self.speed, self.speed * 0.4]

    def reset(self, direction: int) -> None:
        """Center the ball and launch it toward a chosen side."""
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        launch_angle = random.uniform(-0.8, 0.8)
        self.velocity = [direction * self.speed, math.sin(launch_angle) * self.speed]

    def update(self, delta_time: float, left_paddle: Paddle, right_paddle: Paddle, game_model: object) -> None:
        """Advance the ball by one frame and resolve gameplay interactions."""
        self.rect.x += self.velocity[0] * delta_time
        self.rect.y += self.velocity[1] * delta_time

        self._resolve_wall_bounces()
        self._resolve_paddle_collisions(left_paddle, right_paddle)
        self._handle_scoring(game_model)

    def _resolve_wall_bounces(self) -> None:
        """Bounce the ball off the top and bottom walls."""
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity[1] *= -1
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity[1] *= -1

    def _resolve_paddle_collisions(self, left_paddle: Paddle, right_paddle: Paddle) -> None:
        """Handle collisions with either paddle, updating ball direction."""
        if self.rect.colliderect(left_paddle.rect):
            self.rect.left = left_paddle.rect.right
            self._bounce_off_paddle(left_paddle, direction=1)
        elif self.rect.colliderect(right_paddle.rect):
            self.rect.right = right_paddle.rect.left
            self._bounce_off_paddle(right_paddle, direction=-1)

    def _bounce_off_paddle(self, paddle: Paddle, direction: int) -> None:
        """Change the ball's angle based on the point of impact on the paddle."""
        bounce_speed = max(abs(self.velocity[0]), 430.0) + 30.0
        paddle_offset = (self.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)

        self.velocity[0] = direction * bounce_speed
        self.velocity[1] = paddle_offset * 360.0

        vector_length = math.hypot(self.velocity[0], self.velocity[1]) or 1.0
        self.velocity[0] = (self.velocity[0] / vector_length) * bounce_speed
        self.velocity[1] = (self.velocity[1] / vector_length) * bounce_speed

    def _handle_scoring(self, game_model: object) -> None:
        """Award points when the ball exits the left or right boundary."""
        if self.rect.left <= 0:
            game_model.right_score += 1
            game_model.on_point_conceded()
            game_model.handle_score()
        elif self.rect.right >= SCREEN_WIDTH:
            game_model.left_score += 1
            game_model.handle_score()
