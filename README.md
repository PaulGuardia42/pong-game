# Pong Game

A simple 2D Pong game built with Python and Pygame.

## Overview
This project follows the Model-View-Controller (MVC) pattern to separate core
rules, rendering, and user interaction. The app also tracks progression between
runs using a local JSON save file stored in the OS-specific application data directory.

## Architecture summary
The project is organized in layers so each concern has a clear home:

- Model: game rules, scoring, CPU logic, pause behavior, and survival tracking
- View: rendering to the screen and UI overlays
- Controller: keyboard input, event routing, and the game loop
- Config: constants and enums used across the app
- Entities: Paddle and Ball game objects
- Progression service: save and load logic for persistent player progress

## Project structure
```text
pong-game/
├── README.md
├── requirements.txt
├── pong_game.py
├── game/
│   ├── __init__.py
│   ├── config.py
│   ├── controller.py
│   ├── entities.py
│   ├── model.py
│   ├── progression_service.py
│   └── view.py
├── tests/
│   ├── __init__.py
│   ├── test_model.py
│   └── test_progression_service.py
└── .gitignore
```

## What each file does

### pong_game.py
The application entry point. This file creates a PongController instance and
starts the game loop.

### game/config.py
A central configuration module. It defines:
- screen size
- paddle and ball dimensions
- colors and unlock thresholds
- app save path
- game mode and state enums

This is the first place to update if you want to adjust tuning values or add new
rules or color unlocks.

### game/entities.py
Defines the physical game objects used by the model:
- Paddle
- Ball

These classes handle movement, wall collision, ball rebounds, and simple physics.

### game/progression_service.py
Encapsulates disk I/O for saved progress. It keeps the responsibilities of reading
and writing progress separate from the gameplay model so the game logic stays cleaner.

### game/model.py
The core model layer. It is responsible for:
- game state transitions
- score management
- single-player and two-player rules
- CPU movement
- survival tracking
- pause toggling
- selected paddle color and progression updates

This is the primary place for gameplay logic.

### game/controller.py
The controller layer. It receives player input, handles events, and triggers model
updates and view renders. It coordinates the application lifecycle.

### game/view.py
The view layer. It renders the score, paddles, ball, menu, pause overlay, and
end-of-round screen. It contains no game logic.

### game/__init__.py
Package initializer that makes the game modules import cleanly and exposes the main public classes.

### tests/test_model.py
Unit tests for the model layer, including:
- start-game behavior
- pause toggling
- color cycling
- score reset and game state transitions

### tests/test_progression_service.py
Unit tests for the progression service, including:
- reading missing save files safely
- writing and loading JSON progress data
- unlock progression thresholds

## Controls
- W / S: move the left paddle
- Up / Down: move the right paddle in two-player mode
- 1: start single-player mode
- 2: start two-player mode
- C: cycle unlocked paddle colors in the menu
- P: pause or resume a running match
- Esc: quit from the menu or return to the menu from a game
- Enter / Space: continue from the game-over screen

## Paused gameplay
The game now includes a pause overlay that appears while the match is in progress.
When paused, the player can:
- press P again to resume
- press Esc to return to the main menu

## Running the game
Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Then start the game:

```bash
python pong_game.py
```

## Running tests
The project uses Python's built-in unittest framework, so no external test dependency is needed.

Run the test suite with:

```bash
python -m unittest discover tests
```

## Progress persistence
The game stores player progression using a JSON file in the user's OS app-data directory.

- Windows: %APPDATA%\pong-game\pong_progress.json
- macOS: ~/Library/Application Support/pong-game/pong_progress.json
- Linux: ~/.local/share/pong-game/pong_progress.json

The saved file includes:
- best survival time
- unlocked paddle colors
- selected paddle color

## Development notes
This project is intentionally structured so a new developer can work on a single concern without affecting unrelated logic.

- adjust game rules in game/model.py
- adjust rendering in game/view.py
- adjust event handling in game/controller.py
- adjust constants in game/config.py
- adjust save behavior in game/progression_service.py

## Suggested future enhancements
- add sound effects and music
- create a richer pause menu with resume, restart, and quit buttons
- add a difficulty selector for CPU mode
- add more unit tests for gameplay edge cases
- add a start screen with instructions and a settings panel
- support localization for text strings
