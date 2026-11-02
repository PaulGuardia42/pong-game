"""View layer for the Pong game.

This module handles all rendering tasks. It is responsible only for drawing the
current game state on the screen and does not contain gameplay rules.
"""

import pygame

from .model import WINDOW_HEIGHT, WINDOW_WIDTH

# Colors used by the UI and game objects.
WHITE = (255, 255, 255)
BLACK = (10, 10, 18)
DARK = (22, 22, 32)
ACCENT = (102, 214, 255)


class PongView:
    """Responsible for drawing the current state of the model to the screen."""

    def __init__(self, screen: pygame.Surface):
        # Keep a reference to the screen so we can draw shapes and text onto it.
        self.screen = screen

        # Font objects are created once for efficiency and reuse.
        self.font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 36)
        self.tiny_font = pygame.font.Font(None, 24)

    def render(self, model) -> None:
        """Render the complete game screen based on the current model state."""
        self.screen.fill(BLACK)

        # Draw the center divider line.
        for y in range(0, WINDOW_HEIGHT, 20):
            pygame.draw.rect(self.screen, DARK, (WINDOW_WIDTH // 2 - 2, y, 4, 12))

        # Draw paddles and ball.
        self._draw_paddle(model.left_paddle)
        self._draw_paddle(model.right_paddle)
        self._draw_ball(model.ball)

        # Display the score at the top of the screen.
        left_text = self.font.render(str(model.left_score), True, WHITE)
        right_text = self.font.render(str(model.right_score), True, WHITE)
        self.screen.blit(left_text, (WINDOW_WIDTH // 2 - 90, 18))
        self.screen.blit(right_text, (WINDOW_WIDTH // 2 + 50, 18))

        # Switch UI based on current game state.
        if model.state == "menu":
            self.draw_menu(model)
        elif model.state == "game_over":
            self.draw_game_over(model)

    def _draw_paddle(self, paddle) -> None:
        """Draw one paddle using its rectangle."""
        pygame.draw.rect(self.screen, paddle.color, paddle.rect)

    def _draw_ball(self, ball) -> None:
        """Draw the ball using its rectangle. A circle is used for the classic Pong feel."""
        pygame.draw.ellipse(self.screen, WHITE, ball.rect)

    def draw_menu(self, model) -> None:
        """Show the start screen with mode selection instructions and paddle customization."""
        title = self.font.render("PONG", True, WHITE)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, WINDOW_HEIGHT // 2 - 160))

        high_score = self.small_font.render(f"Best survival: {model.high_score:.1f}s", True, ACCENT)
        self.screen.blit(high_score, (WINDOW_WIDTH // 2 - high_score.get_width() // 2, HEIGHT // 2 - 90))

        color_name = model.selected_color_name.title()
        color_text = self.small_font.render(f"Selected paddle: {color_name}", True, WHITE)
        self.screen.blit(color_text, (WINDOW_WIDTH // 2 - color_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))

        option1 = self.small_font.render("Press 1 for 1 Player (vs CPU)", True, ACCENT)
        option2 = self.small_font.render("Press 2 for 2 Players (same keyboard)", True, ACCENT)
        option3 = self.small_font.render("Press C to cycle unlocked paddle colors", True, ACCENT)
        prompt = self.small_font.render("Esc to quit", True, WHITE)

        self.screen.blit(option1, (WINDOW_WIDTH // 2 - option1.get_width() // 2, WINDOW_HEIGHT // 2 + 0))
        self.screen.blit(option2, (WINDOW_WIDTH // 2 - option2.get_width() // 2, WINDOW_HEIGHT // 2 + 40))
        self.screen.blit(option3, (WINDOW_WIDTH // 2 - option3.get_width() // 2, WINDOW_HEIGHT // 2 + 80))
        self.screen.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, WINDOW_HEIGHT // 2 + 120))

        unlocked = ", ".join(name.title() for name in model.get_unlocked_color_names())
        unlocked_text = self.tiny_font.render(f"Unlocked: {unlocked}", True, WHITE)
        self.screen.blit(unlocked_text, (WINDOW_WIDTH // 2 - unlocked_text.get_width() // 2, WINDOW_HEIGHT // 2 + 160))

    def draw_game_over(self, model) -> None:
        """Display the winner and offer a quick way to return to the menu."""
        if model.mode == "single":
            message = "CPU WINS" if model.winner == "CPU" else "YOU WIN"
            survival = self.small_font.render(f"Survival time: {model.current_survival_time:.1f}s", True, ACCENT)
            self.screen.blit(survival, (WINDOW_WIDTH // 2 - survival.get_width() // 2, WINDOW_HEIGHT // 2 + 10))
        else:
            message = f"{model.winner} WINS"

        winner_text = self.font.render(message, True, WHITE)
        self.screen.blit(winner_text, (WINDOW_WIDTH // 2 - winner_text.get_width() // 2, WINDOW_HEIGHT // 2 - 60))

        prompt = self.small_font.render("Press Enter or Space to return to menu", True, ACCENT)
        self.screen.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, WINDOW_HEIGHT // 2 + 60))

        controls = self.tiny_font.render("1 = 1 Player, 2 = 2 Players", True, WHITE)
        self.screen.blit(controls, (WINDOW_WIDTH // 2 - controls.get_width() // 2, WINDOW_HEIGHT // 2 + 100))
