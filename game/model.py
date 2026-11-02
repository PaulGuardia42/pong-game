"""Model layer for the Pong game.

This module contains the game data and rules, including the ball, paddles,
score tracking, and the current game state. The model does not know anything
about rendering or keyboard input; it only stores information and updates it
according to game rules.
"""

import math
import random
from dataclasses import dataclass

import pygame


# Window dimensions used by the game world.
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540

# Visual and collision sizing for the paddles and ball.
PADDLE_WIDTH = 16
PADDLE_HEIGHT = 110
BALL_SIZE = 14


@dataclass
class Paddle:
    """Represents one player's paddle.

    The paddle is stored as a rectangle so collisions with the ball can be checked
    using Pygame's collision API.
    """

    x: int
    y: int
    width: int = PADDLE_WIDTH
    height: int = PADDLE_HEIGHT
    color: tuple[int, int, int] = (255, 255, 255)
    speed: float = 520.0

    def __post_init__(self):
        # Build the rectangle used for drawing and collision detection.
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction: int, dt: float) -> None:
        """Move the paddle up or down based on the direction value."""
        self.rect.y += direction * self.speed * dt

    def clamp(self) -> None:
        """Keep the paddle inside the playable screen area."""
        self.rect.y = max(0, min(self.rect.y, WINDOW_HEIGHT - self.rect.height))


@dataclass
class Ball:
    """Represents the ball that bounces around the arena.

    It has a position, a velocity vector, and methods to update movement and
    collisions with the paddles and walls.
    """

    x: int
    y: int
    size: int = BALL_SIZE
    speed: float = 430.0
    color: tuple[int, int, int] = (255, 255, 255)

    def __post_init__(self):
        # Create the ball's collision rectangle and starting velocity.
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.velocity = [self.speed, self.speed * 0.4]

    def reset(self, direction: int) -> None:
        """Center the ball and launch it toward the chosen side."""
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        angle = random.uniform(-0.8, 0.8)
        self.velocity = [direction * self.speed, math.sin(angle) * self.speed]

    def update(self, dt: float, left_paddle: Paddle, right_paddle: Paddle, game: "PongModel") -> None:
        """Move the ball and handle all collisions and scoring for the current frame."""
        # Advance the ball using its current velocity and the frame delta time.
        self.rect.x += self.velocity[0] * dt
        self.rect.y += self.velocity[1] * dt

        # Bounce when the ball hits the top or bottom wall.
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity[1] *= -1
        elif self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.velocity[1] *= -1

        # Bounce when the ball collides with either paddle.
        if self.rect.colliderect(left_paddle.rect):
            self.rect.left = left_paddle.rect.right
            self._bounce(left_paddle, 1)
        elif self.rect.colliderect(right_paddle.rect):
            self.rect.right = right_paddle.rect.left
            self._bounce(right_paddle, -1)

        # If the ball passes the left or right edge, award a point to the other side.
        if self.rect.left <= 0:
            game.right_score += 1
            game.handle_score()
        elif self.rect.right >= WINDOW_WIDTH:
            game.left_score += 1
            game.handle_score()

    def _bounce(self, paddle: Paddle, direction: int) -> None:
        """Adjust the ball's velocity when it hits a paddle.

        The direction tells us whether the hit came from the left or right paddle,
        and the offset changes the vertical angle based on where the hit occurred.
        """
        speed = max(abs(self.velocity[0]), 430.0) + 30.0

        # offset is calculated to make angled rebounds feel natural.
        offset = (self.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
        self.velocity[0] = direction * speed
        self.velocity[1] = offset * 360.0

        # Normalize the vector so the ball keeps roughly the same speed after each bounce.
        length = math.hypot(self.velocity[0], self.velocity[1]) or 1.0
        self.velocity[0] = (self.velocity[0] / length) * speed
        self.velocity[1] = (self.velocity[1] / length) * speed


class PongModel:
    """Tracks the full game state and enforces the gameplay rules.

    This class is the Model in the MVC pattern. It stores all of the data the game
    needs to know, including paddle positions, the ball, score, and the current
    mode (single-player or two-player).
    """

    WINNING_SCORE = 7

    def __init__(self):
        # Start in the menu until the player selects a mode.
        self.state = "menu"
        self.mode = None
        self.left_score = 0
        self.right_score = 0
        self.winner = None

        # Create the paddles and ball in their starting positions.
        self.left_paddle = Paddle(24, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, (255, 255, 255))
        self.right_paddle = Paddle(WINDOW_WIDTH - 24 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, (255, 255, 255))
        self.ball = Ball(WINDOW_WIDTH // 2 - BALL_SIZE // 2, WINDOW_HEIGHT // 2 - BALL_SIZE // 2)

    def start_game(self, mode: str) -> None:
        """Reset the game for a fresh match in the selected game mode."""
        self.mode = mode
        self.state = "playing"
        self.left_score = 0
        self.right_score = 0
        self.winner = None

        # Ensure both paddles start centered before the next point begins.
        self.left_paddle.rect.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle.rect.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2

        # Start the ball moving in a random direction to create a fair opening.
        self.ball.reset(random.choice([-1, 1]))

    def handle_score(self) -> None:
        """Check for a match winner or reset the ball after a point is scored."""
        if self.left_score >= self.WINNING_SCORE or self.right_score >= self.WINNING_SCORE:
            self.state = "game_over"
            if self.mode == "single":
                self.winner = "Player 1" if self.left_score > self.right_score else "CPU"
            else:
                self.winner = "Player 1" if self.left_score > self.right_score else "Player 2"
            return

        # Serve the ball to the side that lost the point so play continues smoothly.
        if self.left_score > self.right_score:
            self.ball.reset(1)
        else:
            self.ball.reset(-1)

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Advance the game by one frame using the current keyboard state."""
        if self.state != "playing":
            return

        # Move the left paddle with the W and S keys.
        left_direction = 0
        if keys[pygame.K_w]:
            left_direction -= 1
        if keys[pygame.K_s]:
            left_direction += 1
        self.left_paddle.move(left_direction, dt)
        self.left_paddle.clamp()

        # The right paddle is either controlled by the CPU or by Player 2.
        if self.mode == "single":
            self._update_cpu(dt)
        elif self.mode == "two_player":
            right_direction = 0
            if keys[pygame.K_UP]:
                right_direction -= 1
            if keys[pygame.K_DOWN]:
                right_direction += 1
            self.right_paddle.move(right_direction, dt)
            self.right_paddle.clamp()

        # After both paddles have moved, update the ball's position and collisions.
        self.ball.update(dt, self.left_paddle, self.right_paddle, self)

    def _update_cpu(self, dt: float) -> None:
        """Move the right paddle toward the ball to simulate a simple CPU opponent."""
        target_y = self.ball.rect.centery - self.right_paddle.rect.height / 2

        # Only track the ball once it gets far enough into the field.
        if self.ball.rect.x > WINDOW_WIDTH * 0.35:
            if self.right_paddle.rect.centery < target_y:
                self.right_paddle.move(1, dt)
            elif self.right_paddle.rect.centery > target_y:
                self.right_paddle.move(-1, dt)
        self.right_paddle.clamp()
