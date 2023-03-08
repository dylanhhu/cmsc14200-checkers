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

## Design changelog (since Milestone 1)

TODO

## Implementation changelog (since Milestone 2)

### GUI

#### New
- Game menu window (to start new game)
- Click to select a piece and its destination square
- Display king pieces differently from regular pieces
- Check game state (in progress, win or draw)
- Display captured piece statistics
- Command line arguments

#### Improvements
- Generalized dialog opening process
- Maintain previous game setup when starting new game

#### Bug fixes
- Fatal error when bot attempts to execute move before UI rebuild
- King asset size not guaranteed to be correct

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

#### New Changes

* OppoBot is now constructed at most once when evaluatating each MoveSequence, raising efficiency
* Lose_priority now only considered when there are fewer than 4 pieces on bot's side
* OppoBot now only call `_get_mseq_list` once when it's constructed and share this information for both winning
move detection and induced jump detection
* Created `test_bot.py` for testing the bot without using TUI or GUI
* updated the strategy list and the strategies implemented for different SmartLevels
* If a MoveSequence is identified as a winning or losing MoveSequence, it would not be processed by 
other strategies anymore
* The SmartBot now randomly select a MoveSequence with the highest priority (added randomness)

#### Bug Fixes

* Fixed the problem in `_sacrifice_priority` that the difference factor might get negative and encouraging sacrifice
* Fixed the problem in `_stick_priority` that it's possible to count the moved piece itself as a piece in the near 
region of the original position before the piece is moved

## Testing the Game Logic

The game logic does not have a test suite of its own as it was completed before the frontends and bot were completed. Thus, use the [GUI](#running-the-gui) to test the game logic.

## Running the GUI

<img width="1057" alt="Screenshot 2023-03-07 at 6 44 51 PM" src="https://user-images.githubusercontent.com/37193648/223589743-21dae611-c02b-4763-ba77-31e84434f83a.png">


First, make sure that the [environment is activated](#activate-the-environment-using-the-following).

To run the GUI, run the following from the root of the repository:
```shell
python3 src/gui.py
```

### Optional arguments

To change the padding around the window, use `--padding` followed by an option from `{COMFORTABLE,TIGHT,ROOMY}` (default is `COMFORTABLE`):
```shell
python3 src/gui.py --padding TIGHT
```

To open the app in fullscreen mode (not recommended), add the `--fullscreen` flag:
```shell
python3 src/gui.py --fullscreen
```

To see all available command line arguments, run:
```shell
python3 src/gui.py -h
```

### Overview

- 📐 The interface is rendered responsively, so feel free to resize the window by dragging its corners
- 🦾 Random and smart bot included
- 🐌 PyGame doesn't render the board efficiently (recommended: < 15 rows per player)

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

### Divergence from the logic class
- There is no support for offering draws (however, GUI does handle timeout-induced draws)
- Instead of resigning, players simply start a "New game" via the in-game menu

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
with the number of games that we want to run the test with. It should be noted that the test is recommended 
for rows per player within the range of [2, 9]. Otherwise the time to run a game may be more than 15s.

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
