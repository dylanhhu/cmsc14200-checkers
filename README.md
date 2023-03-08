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
Or, for Windows in `cmd.exe`:
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

### Overview of changes

* Generalized game board and pieces into `Board` and `GenericPiece` classes
  * `Piece` class inherits `GenericPiece`
  * `CheckersBoard` class inherits `Board`
* Added various methods for better bot support
* Added various attributes for caching of players' moves in `CheckersBoard`

### Details of changes

* `Piece` class changes
  * Added `.unking()` to unset king
  * Added `.__eq__()`
* `Move` class changes
  * Added `_curr_x` and `_curr_y` attributes
  * Added `.__init__(curr_pos)` argument
  * Added `.is_kinging()`
  * Added `.get_current_position()`
  * Added `.__eq__()`
* `Jump` class changes
  * Added `.__init__(curr_pos)` argument to reflect `Move` class changes
  * Added `.__eq__()`
* `Resignation` class changes
  * Updated `.get_new_position()` signature to reflect parent's signature
  * Added `.get_current_position()` to reflect `Move` class changes
  * Added `.__eq__()`
* `DrawOffer` class changes
  * Updated class docstring to clarify usage
  * Updated `.get_new_position()` signature to reflect parent's signature
  * Added `.get_current_position()` to reflect `Move` class changes
  * Added `.__eq__()`
* New: `Board` class
  * Supports arbitrary rectangular sizes
  * Handles setting/gettting pieces
  * Handles basic completion of moves
  * Handles basic validation of moves
  * Handles `.__str__()` and `.__repr__()`
  * Added `.get_board_height()`
  * Added `.get_board_width()`
  * Added abstract method `.undo_move()`
* `CheckersBoard` class changes
  * Inherits `Board` class
  * `.__init__()` changes
    * Added argument `caching: bool` to enable or disable player move caching
    * Overrides `Board` class initializer to accept only one argument (`rows_per_player: int`)
    * Stores board size
    * Stores board size as the height and width of the board (overrides parent definition)
    * Creates dictionary of a list of moves to cache the generated list of available moves for each player
    * Creates a private attribute to store the number of moves since a capture
    * Calls `._calc_draw_timeout(rows_per_player)` to determine the number of moves without capture before a stalemate
  * `.get_captured_pieces()` overrides parent method for speed efficiency
  * `.complete_move()` overrides parent method
  * `.undo_move()` implements abstract parent method
  * Added `._handle_draw_offer()` to handle `DrawOffer`s
  * Added `._calc_draw_timeout()` to scale the number of moves between captures to board size, such that larger boards don't end in stalemate unneccessarily
  * `._gen_piece()` implements abstract parent method
  * Removed `.__str__()` and `.__repr__()` to use parent's generic methods instead
  * Added `._can_player_move()`
  
## Implementation changelog (since Milestone 2)

### GUI

#### New
- Game menu window (to start new game) `MenuDialog`
- Click to select a piece and its destination square
- Display king pieces differently from regular pieces
- Check game state (in progress, win or draw) `WinDialog`, `DrawDialog`
- Display captured piece statistics
- Command line arguments `--debug`, `--padding {COMFORTABLE,TIGHT,ROOMY}`, `--fullscreen`

#### Improvements
- Generalized dialog opening process `state.post_dialog(...)`, `_check_open_dialog()`, `state.close_dialog()`
- Maintain previous game setup when starting new game `state.soft_reset()`
- Organized and documented all code files

#### Bug fixes
- Fatal error when bot attempts to execute move before UI rebuild `_wait_for_rebuild()`
- Fix king asset size not guaranteed to be correct `_update_responsive_assets()`

### TUI

#### New
- Added coordinates to board
- Updated visuals by adding colors
- Updated visuals by changing symbols for pieces
- Updated visuals by adding colored squares

#### Improvements
- Left room for implementation to play versus a bot instead of another human

#### Bug fixes
- Fixed error where game would not print the winner's color when game ended

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

## ▶ Running the GUI

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

- UI adapts responsively to window resizing
- Accepts any combination of players (human-human, human-bot, bot-bot)

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

## ▶ Running the TUI

To run the TUI, run the following from the root of the repository:
```shell
python3 src/tui.py
```

Select moves by entering the number corresponding to move in the list of moves provided.

Repeat for each player until game has ended.

## Testing the bot
To test the Bot without using GUI or TUI, the test file `src/test_bot.py` can be used.

This file runs games between a random bot (black side) and a smart bot (red side) for a specified number of games on a board with given rows per player. Run the following from the root directory:
```shell
python3 src/test_bot.py {rows per player} {number of games}
```

Replace the `{rows per player}` above with the number of rows per player and the `{number of games}` above with the number of games that we want to run the test with. It should be noted that the test is recommended for rows per player within the range of [2, 9]. Otherwise the time to run a game may be more than 15s.

For example, testing 4 rows per player over 50 games:
```shell
python3 src/test_bot.py 4 50
```

The test output will show the winning rate of the SmartBot along with the draw rate. An example output is the following:
```shell
winning rate of the smart bot on a board with 4 rows per player: 0.94, draw_rate = 0.06
```

It's worth noticing that with the board size getting bigger, the time that's going to be taken for one game will increase. Therefore, the SmartBot implements fewer strategies as the board size gets bigger to save time by changing the SmartLevel of the SmartBot. A corresponding relationship between rows per player and the SmartLevel of the SmartBot is listed below:

 - 2-5 rows per player: `SmartLevel.HARD`
 - 6-7 rows per player: `SmartLevel.MEDIUM`
 - 8-9 rows per player: `SmartLevel.SIMPLE`

And the corresponding strategies that are implemented by each SmartLevel are listed below:

- SmartLevel.SIMPLE: winning strategy, lose strategy, chase strategy, stick strategy
- SmartLevel.MEDIUM: All strategies in `SmartLevel.SIMPLE` and baseline strategy, push strategy, center strategy
- SmartLevel.HARD: All strategies in `SmartLevel.MEDIUM` and sacrifice strategy, capture strategy, corner strategy, king strategy, force strategy

Finally, an estimation of the time that's going to take per game for different rows per player if the SmartLevel for each rows per player is in its default is listed as the following for reference (on AMD Zen2 mobile or Intel Comet Lake mobile, other uArch may differ):

| Rows per player | Average time (s) |
|-----------------|------------------|
| 2               | 0.07             |
| 3               | 0.30             |
| 4               | 1.52             |
| 5               | 3.82             |
| 6               | 1.23             |
| 7               | 3.19             |
| 8               | 6.09             |
| 9               | 11.23            |

## Contributing

Follow our [contribution](CONTRIBUTING.md) guide.
