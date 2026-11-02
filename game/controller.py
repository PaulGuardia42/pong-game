"""Controller layer for the Pong game.

This module handles user input and orchestrates the interaction between the model
and the view.
"""

import sys

import pygame

from .config import GameMode, GameState
from .model import PongModel
from .view import PongView


class PongController:
    """The main controller for the game loop."""

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

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                if self.model.state == GameState.PLAYING.value:
                    self.model.state = GameState.MENU.value
                    self.model.game_mode = None
                elif self.model.state == GameState.GAME_OVER.value:
                    self.model.state = GameState.MENU.value
                    self.model.game_mode = None
                elif self.model.state == GameState.MENU.value:
                    return False

            if self.model.state == GameState.MENU.value:
                if event.key == pygame.K_1:
                    self.model.start_game(GameMode.SINGLE_PLAYER.value)
                elif event.key == pygame.K_2:
                    self.model.start_game(GameMode.TWO_PLAYER.value)
                elif event.key == pygame.K_c:
                    self.model.cycle_selected_color()
                elif event.key == pygame.K_q:
                    return False

            elif self.model.state == GameState.GAME_OVER.value:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.model.state = GameState.MENU.value
                elif event.key == pygame.K_1:
                    self.model.start_game(GameMode.SINGLE_PLAYER.value)
                elif event.key == pygame.K_2:
                    self.model.start_game(GameMode.TWO_PLAYER.value)

        return True

    def update(self, delta_time: float) -> None:
        if self.model.state == GameState.PLAYING.value:
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
