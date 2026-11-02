"""Controller layer for the Pong game.

The controller acts as the glue between user inputs and the model/view:
- listens for key presses and quit events
- updates the model every frame
- tells the view to render the current game state

This keeps input logic and the game loop separate from the actual game rules.
"""

import sys

import pygame

from .model import PongModel
from .view import PongView


class PongController:
    """Coordinates the game loop and user interaction."""

    def __init__(self):
        # Set up the Pygame window and the game components.
        pygame.init()
        pygame.display.set_caption("Pong")
        self.screen = pygame.display.set_mode((960, 540))
        self.clock = pygame.time.Clock()
        self.model = PongModel()
        self.view = PongView(self.screen)

    def handle_events(self) -> bool:
        """Process Pygame events and update the model when a menu or game state changes."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESC can quit from the menu or return to the menu from a game.
                    if self.model.state == "playing":
                        self.model.state = "menu"
                        self.model.mode = None
                    elif self.model.state == "game_over":
                        self.model.state = "menu"
                        self.model.mode = None
                    elif self.model.state == "menu":
                        return False

                if self.model.state == "menu":
                    # Menu selection: choose game mode using the number keys.
                    if event.key == pygame.K_1:
                        self.model.start_game("single")
                    elif event.key == pygame.K_2:
                        self.model.start_game("two_player")
                    elif event.key == pygame.K_c:
                        self.model.cycle_selected_color()
                    elif event.key == pygame.K_q:
                        return False

                elif self.model.state == "game_over":
                    # After a round ends, allow quick restart via Enter/Space or mode choice.
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.model.state = "menu"
                    elif event.key == pygame.K_1:
                        self.model.start_game("single")
                    elif event.key == pygame.K_2:
                        self.model.start_game("two_player")

        return True

    def update(self, dt: float) -> None:
        """Update model logic once per frame, based on the current keyboard state."""
        if self.model.state == "playing":
            keys = pygame.key.get_pressed()
            self.model.update(dt, keys)

    def run(self) -> None:
        """Main application loop.

        This loop is responsible for:
        1. timing the frame rate,
        2. handling input,
        3. updating game logic,
        4. drawing the current scene, and
        5. flipping the display buffer.
        """
        while True:
            dt = self.clock.tick(60) / 1000.0
            running = self.handle_events()
            if not running:
                pygame.quit()
                sys.exit()

            self.update(dt)
            self.view.render(self.model)
            pygame.display.flip()
