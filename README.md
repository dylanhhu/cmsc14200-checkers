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

## Design changes since Milestone 1

TODO

## Changes since Milestone 2

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

## Running the GUI

First, make sure that the [environment is activated](#activate-the-environment-using-the-following).

To run the GUI, run the following from the root of the repository:
```shell
python3 src/gui.py
```

### Overview

- 📐 The interface is rendered responsively, so feel free to resize the window by dragging its corners
- 🦾 Random and smart bot included
- 🐌 GUI uses PyGame, which has less-than-ideal render performance for large board sizes (keep below 15 rows per player)

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
- Making a move:
  - Use the action bar, located at the bottom of the window
    - Using the left dropdown box, select the position of the checkers piece you wish to move
    - Using the right dropdown box, select the destination position you wish to move the selected piece to
  - Or, click on the piece you want to move and choose from the available moves displayed on the board
- While a bot is making their move, the other player must wait

### Unimplemented Features
There is no support in the GUI for offering and accepting draws, or for resigning.

### Performance optimization
By design, the GUI displays each bot move with a visual delay. This delay occurs on a thread separate from the main thread, so that the window does not become unresponsive while the bot is 'selecting and making' their move.

## Testing the bot
- To test the Bot without using GUI or TUI, run the following code in Ipython
```python
# random vs smart
from bot import *
black_win = 0  # to record how many rounds has the black side win
red_win = 0  # to record how many rounds has the red side win
game_num = 100 # specify the number of games that you want to test for   

for i in range(game_num):
    # initalize a board
    board = CheckersBoard(4)
    # set out flags to check the current stage of the game (whether both are
    # still playing, or one has lost the game)
    black_flag = True
    red_flag = True

    # when bot player are still in the game
    while black_flag and red_flag:  
        # initialize a random bot to take up the black side
        randBot1 = RandomBot(PieceColor.BLACK, board)
        # complete a move chosen by the random bot for this round and update 
        # the game state
        black_flag = randBot1._complete_move(randBot1.choose_move_list())

        # check whether black side has lost
        if black_flag:
            # if not, intialize a SmartBot to take up the red side. Note that 
            # you can change how many strategies to use by changing the 
            # SmartLevel
            smartBot2 = SmartBot(PieceColor.RED, board, SmartLevel.HARD)
            # complete a move chosen by the smart bot for this round and update 
            # the game state.
            red_flag = smartBot2._complete_move(smartBot2.choose_move_list())

    # a game has ended, update the counter accordingly
    if black_flag:
        black_win += 1
    elif red_flag:
        red_win += 1

print(f"smart bot win rate: {red_win/(black_win + red_win)}")
```

This will run games between a random bot (black side) and a smart bot (red side) for the 
specified number of games. It will print out the resultant state of the board when each 
game ends and print out which side has won the game. After all the games are done, it will
calculate the winning rate of the red side (which is the smart bot winning rate)

Note that you can specify how many strategies the SmartBot wants to take on by changing the 
SmartLevel of the smartBot when initializing it, the correponding relationship between the 
strategies that the bot will take on and the SmartLevel of the bot is as the following:

```
SmartLevel.SIMPLE: winning strategy, lose strategy
SmartLevel.MEDIUM: winning strategy, lose strategy, sacrifice strategy, capture strategy
SmartLevel.HARD: winning strategy, lose strategy, sacrifice strategy, capture strategy,
                 corner strategy, baseline strategy, push strategy, king strategy,
                 stick strategy, center strategy, force strategy
```

## TUI
To run the Tui, run the following from the root of the repository:
```
python3 src/tui.py
```

## Contributing

Follow our [contribution](CONTRIBUTING.md) guide.
