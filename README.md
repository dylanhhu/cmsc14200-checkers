# CMSC 14200 - Project

Final project for UChicago class CMSC 14200. Project members: Aidan Parker, Dylan Hu, Kevin Gugelmann, and Junfei Sun.

This project implements the board game checkers in Python. We have achieved a fully integrated implementation with a backend game logic that functions with a frontend (GUI or TUI) and bot.

## Project Responsibilities

* Game logic - Dylan Hu
* Bot - Junfei Sun
* GUI - Kevin Gugelmann
* TUI - Aidan Parker

## Setting up and requirements

This project targets Python versions 3.8 and above. This project requires a few libraries such as PyGame.

We encourage the use of a Python virtual environment to install the dependencies required for this project. To get started, run the following from the root of the repository:

```shell
python3 -m venv env
```

#### Activate the environment using the following:
```shell
source env/bin/activate
```
Or, for Windows:
```shell
.\env\Scripts\activate
```

Install the required libraries:
```shell
pip3 install -r requirements.txt
```

To deactivate the virtual environment, run:
```shell
deactivate
```

### WSL2 Notes

If, for some reason you are trying to use this under WSL, you'll likely need to install `libsdl2-dev` for PyGame to work properly, otherwise [you'll get segmentation faults](https://github.com/pygame/pygame/issues/3260#issuecomment-1219040389):

```shell
sudo apt install libsdl2-dev
```

## Design changes since Milestone 1

TODO

## Implementation Changes since Milestone 2

### GUI

- [x] Game menu window (to start new game)
- [x] Click to select a piece and its destination square
- [x] Display king pieces differently from regular pieces
- [x] Check game state (in progress or win)
- [x] Display captured pieces
- [x] Maintain previous game setup when starting new game

### TUI

TODO

### Logic

#### New Changes

* Created generic `Board` class without checkers logic
* Number of moves before stalemate scales with the board size
* Implemented caching of players' moves

#### Bug Fixes

* Fixed jumping into kinging not capturing the piece

### Bot

TODO

## Testing the Game Logic

The game logic does not have a test suite of its own as it was completed before the frontends and bot were completed. Thus, use the GUI to test the game logic.

## Running the GUI

First, make sure that the [environment is activated](#activate-the-environment-using-the-following).

To run the GUI, run the following from the root of the repository:
```shell
python3 src/gui.py
```

### Overview

- 📐 The interface is rendered responsively, so feel free to resize the window by dragging its corners
- 🦾 Random and smart bot included
- 🐌 PyGame doesn't handle O(<img src="https://render.githubusercontent.com/render/math?math=n^2">) board rendering efficiently (recommended: < 15 rows per player)

### Game setup

- Each player may be either a human (with a name) or a bot (with a difficulty level)
- Input the number of rows per player
- When ready, click on "Start game"

#### Make sure your inputs are valid:

- No duplicate names (if both players are human)
- Names have maximum length of 25 characters
- Natural number for rows per player (>= 1)

### Gameplay
- Black always starts
- Selecting a move:
  - Use the action bar, located at the bottom of the window:
    1. Using the left dropdown box, select the position of the checkers piece you wish to move
    2. Using the right dropdown box, select the destination position you wish to move the selected piece to
  - Or click:
    1. On the piece you want to move
    2. On one of the highlighted available destination squares
- To execute a move, click on the "Move" button
- (While a bot is making their move, the other player must wait)
- Click on the "Menu" button at any time, to open the menu dialog. This pauses gameplay.

### N.B. logic class methods
- There is no support in the GUI for offering and accepting draws.
- Instead of resignation, players simply start "New game" via game menu

### Performance optimization
By design, the GUI displays each bot move with a visual delay. This delay occurs on a thread separate from the main thread, so that the window does not become unresponsive while the bot is 'selecting and making' their move.

## Testing the bot
To test the Bot without using GUI or TUI, we offer the test file 'test_bot.py' under src directory. 

This file enables running games between a random bot (black side) and a smart bot (red side) for a 
specified number of games on a board with given rows per player. To achieve that, run commands in the
following form from the root directory
```shell
python3 src/test_bot.py {rows per player} {number of games}
```

replace the {rows per player} above with the number of rows per player and the {number of games} above
with the number of games that we want to run the test with. It should be noted that the test only suppor
rows per player within the range of [2, 9]. 

Here is one example command if I want to run the test for 4 rows per player for 50 games:
```shell
python3 src/test_bot.py 4 50
```

And the test will give out a result that shows the winning rate of the SmartBot and the draw rate, an
example output is as the following
```shell
winning rate of the smart bot on a board with 4 rows per player: 0.94, draw_rate = 0.06
```

It's worth noticing that with the board size getting bigger, the time that's going to be taken for
one game will increase. Therefore, the SmartBot implement fewer strategies as the board size gets 
bigger to save time by changing the SmartLevel of the SmartBot. A corresponding relationship between
rows per player and the SmartLevel of the SmartBot is listed below:
```
    2 rows per player: SmartLevel.HARD,
    3 rows per player: SmartLevel.HARD,
    4 rows per player: SmartLevel.HARD,
    5 rows per player: SmartLevel.HARD,
    6 rows per player: SmartLevel.MEDIUM,
    7 rows per player: SmartLevel.MEDIUM,
    8 rows per player: SmartLevel.SIMPLE,
    9 rows per player: SmartLevel.SIMPLE,
```
And the corresponding strategies that are implemented by each SmartLevel is listed below:
```
SmartLevel.SIMPLE: winning strategy, lose strategy, chase strategy, stick strategy
SmartLevel.MEDIUM: winning strategy, lose strategy, chase strategy, stick strategy, 
                   baseline strategy, push strategy, center strategy
SmartLevel.HARD: winning strategy, lose strategy, sacrifice strategy, capture strategy,
                 corner strategy, baseline strategy, push strategy, king strategy,
                 stick strategy, center strategy, force strategy
```

Finally, an estimation of the time that's going to take per game for different rows per player
if the SmartLevel for each rows per player is in it's default is listed as the following for 
reference:
```
rows per player             average time
    2                           0.07s
    3                           0.30s
    4                           1.52s
    5                           3.82s
    6                           1.23s
    7                           3.19s
    8                           6.09s
    9                           11.23s
```

## TUI
To run the Tui, run the following from the root of the repository:
```
python3 src/tui.py
```

## Contributing

Follow our [contribution](CONTRIBUTING.md) guide.
