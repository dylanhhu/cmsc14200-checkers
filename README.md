# CMSC 14200 - Project

Final project for UChicago class CMSC 14200. Project members: Aidan Parker, Dylan Hu, Kevin Gugelmann, and Junfei Sun.

## Project Responsibilities

* Game logic - Dylan Hu
* Bot - Junfei Sun
* GUI - Kevin Gugelmann
* TUI - Aidan Parker

## Setting up and requirements

This project targets Python versions 3.8 and above. This project requires a few libraries such as PyGame.

We encourage the use of a Python virtual environment to install the dependencies required for this project. To get started, run the following from the root of the repository:

```
python3 -m venv env
```

Activate the environment using the following (for POSIX, Windows may differ):
```
source env/bin/activate
```

Install the required libraries:
```
pip3 install -r requirements.txt
```

To deactivate the virtual environment, run:
```
deactivate
```

## Running the GUI

To run the GUI, run the following from the root of the repository:
```shell
python3 src/gui.py
```

### Editorial notes

- 📐 The interface is rendered responsively, so feel free to resize the window by dragging its corners
- 🦾 Smart bots included
- 🐌 GUI uses PyGame, which has less-than-ideal render performance for large board sizes (above 20 rows per player)

### Game setup

- Each player may be either a human (with a name) or a bot (with a difficulty level)
- Input the number of rows per player
- When ready, click on "Start game"

#### Make sure your inputs are valid:

> - No duplicate names (if both players are human)
> - Natural number for rows per player (>= 1)

### Game play
- Black always starts
- To make a (human) move, use the action bar, located at the bottom of the window
  - Using the left dropdown box, select the position of the checkers piece you wish to move
  - Using the right dropdown box, select the destination position you wish to move the selected piece to
- While a bot is making their move, the other player must wait

#### Performance optimization:
> By design, the GUI displays each bot move with a visual delay. This delay occurs on a thread separate from the main thread, so that the window does not become unresponsive while the bot is 'selecting and making' their move.

## Contributing

Follow our [contribution](CONTRIBUTING.md) guide.
