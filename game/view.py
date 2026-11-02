"""Controller layer for the Pong game.

This module handles input events and coordinates updates between the model and the view.
"""

import sys

import pygame

from .model import PongModel
from .view import PongView


class PongController:
    """Coordinates the game loop and user interaction."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pong")
        self.screen = pygame.display.set_mode((960, 540))
        self.clock = pygame.time.Clock()
        self.model = PongModel()
        self.view = PongView(self.screen)

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.model.state == "playing":
                        self.model.state = "menu"
                        self.model.mode = None
                    elif self.model.state == "game_over":
                        self.model.state = "menu"
                        self.model.mode = None
                    elif self.model.state == "menu":
                        return False

                if self.model.state == "menu":
                    if event.key == pygame.K_1:
                        self.model.start_game("single")
                    elif event.key == pygame.K_2:
                        self.model.start_game("two_player")
                    elif event.key == pygame.K_c:
                        self.model.cycle_selected_color()
                    elif event.key == pygame.K_q:
                        return False

                elif self.model.state == "game_over":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.model.state = "menu"
                    elif event.key == pygame.K_1:
                        self.model.start_game("single")
                    elif event.key == pygame.K_2:
                        self.model.start_game("two_player")

        return True

    def update(self, delta_time: float) -> None:
        if self.model.state == "playing":
            key_state = pygame.key.get_pressed()
            self.model.update(delta_time, key_state)

    def run(self) -> None:
        while True:
            delta_time = self.clock.tick(60) / 1000.0
            should_continue = self.handle_events()
            if not should_continue:
                pygame.quit()
                sys.exit()

            self.update(delta_time)
            self.view.render(self.model)
            pygame.display.flip()
