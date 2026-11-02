"""Model layer for the Pong game.

This module contains the data and rules of the game:
- paddles and ball state
- scoring logic
- gameplay transitions between menu, playing, and game over

The model has no direct dependency on rendering code, which keeps the game logic
separate from the Pygame drawing code.
"""

import math
import random
from dataclasses import dataclass

import pygame

# Screen dimensions match the window size used by the view.
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540

# Paddle and ball sizing constants to keep movement and collisions consistent.
PADDLE_WIDTH = 16
PADDLE_HEIGHT = 110
BALL_SIZE = 14


@dataclass
class Paddle:
    """Represents one player's paddle.

    A paddle has a rectangle position, a color, and a movement speed.
    The rect property is used for collision detection with the ball.
    """

    x: int
    y: int
    width: int = PADDLE_WIDTH
    height: int = PADDLE_HEIGHT
    color: tuple[int, int, int] = (255, 255, 255)
    speed: float = 520.0

    def __post_init__(self):
        # Create the collision rectangle once the paddle is initialized.
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction: int, dt: float) -> None:
        """Move up or down based on the direction and elapsed time."""
        self.rect.y += direction * self.speed * dt

    def clamp(self) -> None:
        """Keep the paddle inside the playable area."""
        self.rect.y = max(0, min(self.rect.y, WINDOW_HEIGHT - self.rect.height))


@dataclass
class Ball:
    """Represents the moving ball.

    The ball stores its rectangle and velocity so it can travel around the screen,
    bounce off walls, and collide with paddles.
    """

    x: int
    y: int
    size: int = BALL_SIZE
    speed: float = 430.0
    color: tuple[int, int, int] = (255, 255, 255)

    def __post_init__(self):
        # Initialize the ball's drawing box and starting movement vector.
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.velocity = [self.speed, self.speed * 0.4]

    def reset(self, direction: int) -> None:
        """Reset the ball to the center and fire it in a chosen direction."""
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        angle = random.uniform(-0.8, 0.8)
        self.velocity = [direction * self.speed, math.sin(angle) * self.speed]

    def update(self, dt: float, left_paddle: Paddle, right_paddle: Paddle, game: "PongModel") -> None:
        """Advance the ball and handle collisions with walls, paddles, and scoring.

        Parameters:
            dt: elapsed time in seconds for frame-rate-independent movement
            left_paddle: paddle controlled by player 1
            right_paddle: paddle controlled by player 2 or CPU
            game: the full game state, used to update score and game flow
        """
        # Move the ball based on its current velocity and time passed.
        self.rect.x += self.velocity[0] * dt
        self.rect.y += self.velocity[1] * dt

        # Bounce off the top and bottom screen edges.
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity[1] *= -1
        elif self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.velocity[1] *= -1

        # Handle collisions with paddles.
        if self.rect.colliderect(left_paddle.rect):
            self.rect.left = left_paddle.rect.right
            self._bounce(left_paddle, 1)
        elif self.rect.colliderect(right_paddle.rect):
            self.rect.right = right_paddle.rect.left
            self._bounce(right_paddle, -1)

        # Update score when the ball crosses the left or right boundary.
        if self.rect.left <= 0:
            game.right_score += 1
            game.handle_score()
        elif self.rect.right >= WINDOW_WIDTH:
            game.left_score += 1
            game.handle_score()

    def _bounce(self, paddle: Paddle, direction: int) -> None:
        """Change the ball's direction based on where it hits the paddle."""
        # Increase speed slightly to make each hit feel lively.
        speed = max(abs(self.velocity[0]), 430.0) + 30.0

        # offset tells us whether the ball hit near the center or edge of the paddle.
        offset = (self.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
        self.velocity[0] = direction * speed
        self.velocity[1] = offset * 360.0

        # Normalize the velocity so it stays at a consistent speed while changing direction.
        length = math.hypot(self.velocity[0], self.velocity[1]) or 1.0
        self.velocity[0] = (self.velocity[0] / length) * speed
        self.velocity[1] = (self.velocity[1] / length) * speed


class PongModel:
    """The game state and rules.

    This class is responsible for the model layer of the MVC pattern. It tracks:
    - which mode is active (single-player or two-player)
    - current score
    - winner
    - paddle and ball positions
    - game state: menu, playing, or game_over
    """

    WINNING_SCORE = 7

    def __init__(self):
        # Initial state starts at the menu before a game mode is selected.
        self.state = "menu"
        self.mode = None
        self.left_score = 0
        self.right_score = 0
        self.winner = None

        # Create the two paddles and the ball in their starting positions.
        self.left_paddle = Paddle(24, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, (255, 255, 255))
        self.right_paddle = Paddle(WINDOW_WIDTH - 24 - PADDLE_WIDTH, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, (255, 255, 255))
        self.ball = Ball(WINDOW_WIDTH // 2 - BALL_SIZE // 2, WINDOW_HEIGHT // 2 - BALL_SIZE // 2)

    def start_game(self, mode: str) -> None:
        """Reset the game for either one-player or two-player mode."""
        self.mode = mode
        self.state = "playing"
        self.left_score = 0
        self.right_score = 0
        self.winner = None

        # Reset paddle positions to center before the round begins.
        self.left_paddle.rect.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle.rect.y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2

        # Launch the ball in a random direction to start play.
        self.ball.reset(random.choice([-1, 1]))

    def handle_score(self) -> None:
        """Determine if the round has ended or if the ball should be served again."""
        if self.left_score >= self.WINNING_SCORE or self.right_score >= self.WINNING_SCORE:
            self.state = "game_over"
            if self.mode == "single":
                self.winner = "Player 1" if self.left_score > self.right_score else "CPU"
            else:
                self.winner = "Player 1" if self.left_score > self.right_score else "Player 2"
            return

        # Serve toward the player who did not score, keeping the round flowing.
        if self.left_score > self.right_score:
            self.ball.reset(1)
        else:
            self.ball.reset(-1)

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Apply all game logic for the current frame.

        The keys parameter is the current keyboard state from Pygame.
        """
        if self.state != "playing":
            return

        # Move the left paddle using W and S.
        left_direction = 0
        if keys[pygame.K_w]:
            left_direction -= 1
        if keys[pygame.K_s]:
            left_direction += 1
        self.left_paddle.move(left_direction, dt)
        self.left_paddle.clamp()

        # If in single-player mode, the right paddle is controlled by the CPU.
        if self.mode == "single":
            self._update_cpu(dt)
        elif self.mode == "two_player":
            # In local multiplayer, the second player uses Up/Down arrows.
            right_direction = 0
            if keys[pygame.K_UP]:
                right_direction -= 1
            if keys[pygame.K_DOWN]:
                right_direction += 1
            self.right_paddle.move(right_direction, dt)
            self.right_paddle.clamp()

        # Update the ball after both paddles have moved.
        self.ball.update(dt, self.left_paddle, self.right_paddle, self)

    def _update_cpu(self, dt: float) -> None:
        """Move the right paddle toward the ball so the CPU can play defensively."""
        target_y = self.ball.rect.centery - self.right_paddle.rect.height / 2

        # Only track the ball once it is in the player's half of the field.
        if self.ball.rect.x > WINDOW_WIDTH * 0.35:
            if self.right_paddle.rect.centery < target_y:
                self.right_paddle.move(1, dt)
            elif self.right_paddle.rect.centery > target_y:
                self.right_paddle.move(-1, dt)
        self.right_paddle.clamp()
