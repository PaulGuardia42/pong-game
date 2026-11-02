"""Controller layer for the Pong game.

This module handles user input and orchestrates the interaction between the model
and view layers. It is responsible for event routing, pause toggling, and the main
frame loop.
"""

import sys

import pygame

from .config import GameMode, GameState
from .model import PongModel
from .view import PongView


class PongController:
    """Coordinates the game loop and input handling."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pong")
        self.screen = pygame.display.set_mode((960, 540))
        self.clock = pygame.time.Clock()
        self.model = PongModel()
        self.view = PongView(self.screen)

    def handle_events(self) -> bool:
        """Process all window and keyboard events for the current frame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type != pygame.KEYDOWN:
                continue

            # Escape should always return to the menu and never leave the game in an
            # inconsistent state while a match is active.
            if event.key == pygame.K_ESCAPE:
                if self.model.state in (GameState.PLAYING.value, GameState.PAUSED.value, GameState.GAME_OVER.value):
                    self.model.return_to_menu()
                elif self.model.state == GameState.MENU.value:
                    return False

            # Pause is toggled with P while the game is running or paused.
            if event.key == pygame.K_p:
                if self.model.state in (GameState.PLAYING.value, GameState.PAUSED.value):
                    self.model.toggle_pause()

            if self.model.state == GameState.MENU.value:
                if event.key == pygame.K_1:
                    self.model.start_game(GameMode.SINGLE_PLAYER)
                elif event.key == pygame.K_2:
                    self.model.start_game(GameMode.TWO_PLAYER)
                elif event.key == pygame.K_c:
                    self.model.cycle_selected_color()
                elif event.key == pygame.K_q:
                    return False

            elif self.model.state == GameState.GAME_OVER.value:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.model.state = GameState.MENU.value
                elif event.key == pygame.K_1:
                    self.model.start_game(GameMode.SINGLE_PLAYER)
                elif event.key == pygame.K_2:
                    self.model.start_game(GameMode.TWO_PLAYER)

        return True

    def update(self, delta_time: float) -> None:
        """Update the model only when the game is actively playing."""
        if self.model.state == GameState.PLAYING.value:
            key_state = pygame.key.get_pressed()
            self.model.update(delta_time, key_state)

    def run(self) -> None:
        """Run the main application loop until the user quits."""
        while True:
            delta_time = self.clock.tick(60) / 1000.0
            should_continue = self.handle_events()
            if not should_continue:
                pygame.quit()
                sys.exit()

            self.update(delta_time)
            self.view.render(self.model)
            pygame.display.flip()
