# Pong Game

A simple 2D Pong game built with Python and Pygame.

## Overview
This project is a small Pong game written using the Model-View-Controller (MVC) pattern. The code is organized so the rules of the game live in the model layer, rendering lives in the view layer, and user input and loop orchestration live in the controller layer.

The application also includes a lightweight persistent progression system that stores the player's best survival score and unlocked paddle colors.

## Architecture
The app is intentionally separated into layers so it is easier to maintain and debug.

- Model: game rules, score tracking, CPU logic, save/load behavior coordination
- View: rendering to the screen
- Controller: keyboard input, events, and the main game loop
- Config: shared constants and enums
- Entities: paddle and ball game objects
- Progression service: persistent save/load functionality

## Project Structure
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
└── .gitignore
```

## What each file does

### pong_game.py
Entry point for the game. This is the small script that creates the controller and starts the game loop.

### game/config.py
This file contains all shared constants, enums, and app configuration values, including:
- screen dimensions
- paddle sizes
- ball size
- game modes and states
- available paddle color definitions
- progression unlock thresholds
- default save path

This file is the primary place to adjust gameplay tuning values.

### game/entities.py
Contains the domain objects used by the model:
- Paddle
- Ball

These classes represent the physical entities in the game, including position, movement, collisions, and rebound behavior.

### game/progression_service.py
Handles the persistent player progress. It is responsible for:
- opening and reading the save file
- writing updated progression data
- converting a high score into unlocked paddle colors
- ensuring the save data is valid enough to fall back safely on startup

### game/model.py
This is the main gameplay model. It owns:
- current state of the game
- current mode (single-player or two-player)
- player score and winner logic
- CPU movement logic
- ball reset and serve logic
- survival time tracking
- applying selected paddle colors
- progress updates when a new high score is reached

This file contains the core rules of the Pong game.

### game/controller.py
This file is the application controller. It does the following:
- listens for keyboard input and quit events
- starts new games
- handles menu navigation
- updates the model on each frame
- coordinates the view render pass

### game/view.py
This is the rendering layer. It draws:
- the score panel
- paddles
- ball
- center divider
- start menu
- game-over screen

The view should not contain gameplay rules or state mutation logic.

### game/__init__.py
Package init file for the game package.

## Gameplay features
- Single-player CPU mode
- Local two-player mode using a shared keyboard
- Win condition at 7 points
- Survival high score measured in seconds without conceding a point
- Unlockable paddle colors driven by progression thresholds
- Persistent save data stored in the OS-specific application data directory

## Running the game
Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Then run:

```bash
python pong_game.py
```

## Controls
- W / S: move left paddle
- Up / Down: move right paddle in two-player mode
- 1: start single-player mode
- 2: start two-player mode
- C: cycle unlocked colors from the main menu
- Esc: quit the game or return to menu
- Enter / Space: start a new match from the game-over screen

## Progress persistence
The game stores player progress in a JSON file under the operating system's user data directory so it persists across runs:

- Windows: %APPDATA%\pong-game\pong_progress.json
- macOS: ~/Library/Application Support/pong-game/pong_progress.json
- Linux: ~/.local/share/pong-game/pong_progress.json

This stores:
- best survival time
- unlocked paddle colors
- selected paddle color

## Development notes
This project is deliberately organized so a developer can work on one layer without disturbing unrelated logic:

- adjust game rules in game/model.py
- adjust rendering in game/view.py
- adjust input handling in game/controller.py
- adjust tuning values in game/config.py
- adjust save behavior in game/progression_service.py

Keeping the concerns separated makes debugging and testing much easier.

## Future improvements
Possible next steps for this project include:
- adding automated tests for scoring and progression
- adding sound effects and music
- implementing a pause menu
- adding richer CPU difficulty levels
- introducing unlock notifications and a progression screen
- extracting the app into a more formal package layout if the game grows further
