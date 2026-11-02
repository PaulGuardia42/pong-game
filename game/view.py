"""View layer for the Pong game.

This module is responsible for drawing the current game state onto the screen.
It intentionally contains no gameplay logic: it only renders the state provided by
PongModel and the current game objects.
"""

import pygame

from .config import SCREEN_HEIGHT, SCREEN_WIDTH

WHITE = (255, 255, 255)
BLACK = (10, 10, 18)
DARK = (22, 22, 32)
ACCENT = (102, 214, 255)


class PongView:
    """Renders the game board, HUD, menu, pause screen, and game-over overlay."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.title_font = pygame.font.Font(None, 72)
        self.secondary_font = pygame.font.Font(None, 36)
        self.tertiary_font = pygame.font.Font(None, 24)

    def render(self, game_model) -> None:
        """Render the full scene based on the current state of the model."""
        self.screen.fill(BLACK)
        self.draw_center_divider()
        self.draw_paddles(game_model)
        self.draw_ball(game_model.ball)
        self.draw_score(game_model)

        if game_model.state == "menu":
            self.draw_menu(game_model)
        elif game_model.state == "paused":
            self.draw_pause_menu(game_model)
        elif game_model.state == "game_over":
            self.draw_game_over(game_model)

    def draw_center_divider(self) -> None:
        """Draw the dashed center line between the player halves."""
        for y_position in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(self.screen, DARK, (SCREEN_WIDTH // 2 - 2, y_position, 4, 12))

    def draw_paddles(self, game_model) -> None:
        """Render both paddles using their current color values."""
        pygame.draw.rect(self.screen, game_model.left_paddle.color, game_model.left_paddle.rect)
        pygame.draw.rect(self.screen, game_model.right_paddle.color, game_model.right_paddle.rect)

    def draw_ball(self, ball) -> None:
        """Render the ball as an ellipse to emulate the classic Pong look."""
        pygame.draw.ellipse(self.screen, WHITE, ball.rect)

    def draw_score(self, game_model) -> None:
        """Render the score in the center-top HUD area."""
        left_score_text = self.title_font.render(str(game_model.player_one_score), True, WHITE)
        right_score_text = self.title_font.render(str(game_model.player_two_score), True, WHITE)

        self.screen.blit(left_score_text, (SCREEN_WIDTH // 2 - 90, 18))
        self.screen.blit(right_score_text, (SCREEN_WIDTH // 2 + 50, 18))

    def draw_menu(self, game_model) -> None:
        """Draw the start menu including progression and color selection info."""
        title_surface = self.title_font.render("PONG", True, WHITE)
        self.screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 160))

        high_score_text = self.secondary_font.render(f"Best survival: {game_model.high_score:.1f}s", True, ACCENT)
        self.screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 90))

        selected_color_text = self.secondary_font.render(
            f"Selected paddle: {game_model.selected_color_name.title()}",
            True,
            WHITE,
        )
        self.screen.blit(selected_color_text, (SCREEN_WIDTH // 2 - selected_color_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        option_one = self.secondary_font.render("Press 1 for 1 Player (vs CPU)", True, ACCENT)
        option_two = self.secondary_font.render("Press 2 for 2 Players (same keyboard)", True, ACCENT)
        option_three = self.secondary_font.render("Press C to cycle unlocked paddle colors", True, ACCENT)
        quit_prompt = self.secondary_font.render("Esc to quit", True, WHITE)

        self.screen.blit(option_one, (SCREEN_WIDTH // 2 - option_one.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(option_two, (SCREEN_WIDTH // 2 - option_two.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(option_three, (SCREEN_WIDTH // 2 - option_three.get_width() // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(quit_prompt, (SCREEN_WIDTH // 2 - quit_prompt.get_width() // 2, SCREEN_HEIGHT // 2 + 120))

        unlocked_colors = ", ".join(name.title() for name in game_model.get_unlocked_color_names())
        unlocked_text = self.tertiary_font.render(f"Unlocked: {unlocked_colors}", True, WHITE)
        self.screen.blit(unlocked_text, (SCREEN_WIDTH // 2 - unlocked_text.get_width() // 2, SCREEN_HEIGHT // 2 + 160))

    def draw_pause_menu(self, game_model) -> None:
        """Draw the pause overlay and give the player resume or menu choices."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 18, 180))
        self.screen.blit(overlay, (0, 0))

        pause_title = self.title_font.render("PAUSED", True, WHITE)
        self.screen.blit(pause_title, (SCREEN_WIDTH // 2 - pause_title.get_width() // 2, SCREEN_HEIGHT // 2 - 80))

        resume_text = self.secondary_font.render("Press P to resume", True, ACCENT)
        menu_text = self.secondary_font.render("Press Esc to return to menu", True, WHITE)

        self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 + 55))

    def draw_game_over(self, game_model) -> None:
        """Draw the game-over overlay with winner and quick restart instructions."""
        if game_model.game_mode == "single":
            message = "CPU WINS" if game_model.winner_name == "CPU" else "YOU WIN"
            survival_time_text = self.secondary_font.render(
                f"Survival time: {game_model.current_survival_time:.1f}s",
                True,
                ACCENT,
            )
            self.screen.blit(survival_time_text, (SCREEN_WIDTH // 2 - survival_time_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        else:
            message = f"{game_model.winner_name} WINS"

        winner_surface = self.title_font.render(message, True, WHITE)
        self.screen.blit(winner_surface, (SCREEN_WIDTH // 2 - winner_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 60))

        menu_prompt = self.secondary_font.render("Press Enter or Space to return to menu", True, ACCENT)
        self.screen.blit(menu_prompt, (SCREEN_WIDTH // 2 - menu_prompt.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        controls_text = self.tertiary_font.render("1 = 1 Player, 2 = 2 Players", True, WHITE)
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
