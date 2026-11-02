"""Entry point for the Pong game.

This file is intentionally small so the application starts cleanly:
- create the controller,
- run the main game loop.
"""

from game.controller import PongController


if __name__ == "__main__":
    # Start the game by creating the controller and running the application loop.
    PongController().run()
