#
# © Kevin Gugelmann, 20 February 2023.
# All rights reserved.
#
import itertools
import json
import random
import shutil
import threading
from dataclasses import dataclass
from enum import Enum, IntEnum
from functools import lru_cache
from typing import Union, Callable, List, Set, Tuple

import pygame
import pygame_gui
from pygame.event import Event
from pygame_gui import UIManager, PackageResource
from pygame_gui.core import ObjectID
from pygame_gui.elements import (UIButton, UILabel, UIPanel, UITextEntryLine,
                                 UIDropDownMenu)

from bot import SmartLevel, SmartBot, RandomBot
from checkers import PieceColor, CheckersBoard, Position, Piece, Move
from utils.gui.components import GuiComponentLib, ModifyElemCommand, Element
from utils.gui.relative_rect import (RelPos, ScreenPos, ElemPos, SelfAlign,
                                     Offset, Fraction, IntrinsicSize,
                                     MatchOtherSide, NegFraction)
from utils.gui.window import Dimensions, WindowOptions, DimensionsTuple


# ===============
# ENUMS
# ===============


class _Screens(Enum):
    """
    An enumeration for the internal representation of each screen.
    """

    SETUP = "#setup"
    GAME = "#game"

    @staticmethod
    def from_string(string: str) -> "_Screens":
        """
        Get enum by its string value.

        Args:
            string (str): enum value

        Returns:
            _Screens: enum
        """
        if string == _Screens.SETUP.value:
            return _Screens.SETUP
        return _Screens.GAME

    @staticmethod
    def get_setup_name() -> str:
        """
        Getter method for Setup Screen name.

        Returns:
            str: Setup Screen name
        """
        return str(_Screens.SETUP.value)

    @staticmethod
    def get_game_name() -> str:
        """
        Getter method for Game Screen name.

        Returns:
            str: Game Screen name
        """
        return str(_Screens.GAME.value)


class _PlayerType(Enum):
    """
    An enumeration for the internal representation of player types.
    """

    HUMAN = "Human"
    BOT = "Bot"

    @staticmethod
    def from_string(string: str) -> "_PlayerType":
        """
        Get enum by its string value.

        Args:
            string (str): enum value

        Returns:
            _PlayerType: enum
        """
        if string == _PlayerType.HUMAN.value:
            return _PlayerType.HUMAN
        return _PlayerType.BOT

    @staticmethod
    def get_human_name() -> str:
        """
        Getter method for human string representation.

        Returns:
            str: human string representation
        """
        return str(_PlayerType.HUMAN.value)

    @staticmethod
    def get_bot_name() -> str:
        """
        Getter method for bot string representation.

        Returns:
            str: bot string representation
        """
        return str(_PlayerType.BOT.value)


class _BotLevel(Enum):
    """
    An enumeration of the smart level for smart bots
    """
    RANDOM = "Random"
    SIMPLE = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

    @staticmethod
    def from_string(string: str) -> "_BotLevel":
        """
        Get enum by its string value.
        Args:
            string (str): enum value
        Returns:
            _BotLevel: enum
        """
        if string == _BotLevel.RANDOM.value:
            return _BotLevel.RANDOM
        if string == _BotLevel.SIMPLE.value:
            return _BotLevel.SIMPLE
        if string == _BotLevel.MEDIUM.value:
            return _BotLevel.MEDIUM
        return _BotLevel.HARD

    @staticmethod
    def get_random_name() -> str:
        """
        Getter method for simple level name.
        Returns:
            str: simple level name
        """
        return str(_BotLevel.RANDOM.value)

    @staticmethod
    def get_simple_name() -> str:
        """
        Getter method for simple level name.
        Returns:
            str: simple level name
        """
        return str(_BotLevel.SIMPLE.value)

    @staticmethod
    def get_medium_name() -> str:
        """
        Getter method for medium level name.
        Returns:
            str: medium level name
        """
        return str(_BotLevel.MEDIUM.value)

    @staticmethod
    def get_hard_name() -> str:
        """
        Getter method for hard level name.
        Returns:
            str: medium hard name
        """
        return str(_BotLevel.HARD.value)


class _KingPiecePngSize(IntEnum):
    """
    An enumeration to represent the different available PNG sizes for king
    checkers piece background images.
    """
    S_8px = 8
    S_12px = 12
    S_16px = 16
    S_20px = 20
    S_24px = 24
    S_32px = 32
    S_36px = 36
    S_42px = 42
    S_48px = 48
    S_56px = 56
    S_64px = 64
    S_80px = 80
    S_96px = 96


# ===============
# STATIC CONSTANT 'ENUMS'
# ===============


class _Sizes:
    MICRO = 2
    XXS = 4
    XS = 8
    S = 12
    M = 16
    L = 20
    XL = 24
    XXL = 32
    MEGA = 42


class _GeneralConsts:
    # Sizes
    LABEL_HEIGHT = 20
    TEXTINPUT_HEIGHT = 40
    DROPDOWN_HEIGHT = 40
    BUTTON_HEIGHT = 40


class _GeneralEvents:
    # Event names
    NAME_REBUILD = "rebuild"
    # Parameters
    PARAM_NAME = "name"
    PARAM_DISABLE_MOVE = "disable-move"
    PARAM_ENABLE_MOVE = "enable-move"

    # PyGame event instances
    REBUILD = pygame.event.Event(pygame.USEREVENT,
                                 {PARAM_NAME: NAME_REBUILD})
    REBUILD_DISABLE_MOVE = pygame.event.Event(pygame.USEREVENT,
                                              {PARAM_NAME: NAME_REBUILD,
                                               PARAM_DISABLE_MOVE: True})
    REBUILD_ENABLE_MOVE = pygame.event.Event(pygame.USEREVENT,
                                             {PARAM_NAME: NAME_REBUILD,
                                              PARAM_ENABLE_MOVE: True})


class _SetupElems:
    # ID
    screen_id = _Screens.get_setup_name()

    # ===============
    # ELEMENTS
    # ===============

    WELCOME_TEXT = "#welcome-text"

    RED_PANEL = "#player-1-panel"
    RED_PANEL_TITLE = "#player-1-type-title-label"
    RED_TYPE_DROPDOWN = "#player-1-type-dropdown"
    RED_NAME_TEXTINPUT = "#player-1-name-textinput"
    RED_BOT_DIFFICULTY_DROPDOWN = "#player-1-bot-difficulty-dropdown"

    BLACK_PANEL = "#player-2-panel"
    BLACK_PANEL_TITLE = "#player-2-type-title-label"
    BLACK_TYPE_DROPDOWN = "#player-2-type-dropdown"
    BLACK_NAME_TEXTINPUT = "#player-2-name-textinput"
    BLACK_BOT_DIFFICULTY_DROPDOWN = "#player-2-bot-difficulty-dropdown"

    NUM_PLAYER_ROWS_TEXTINPUT = "#num-player-rows-textinput"
    NUM_PLAYER_ROWS_TITLE = "#num-player-rows-title"

    START_GAME_BUTTON = "#start-game-button"

    # ===============
    # LIST OF ELEMENT IDS
    # ===============

    elem_ids = [WELCOME_TEXT, RED_PANEL, BLACK_PANEL,
                RED_PANEL_TITLE, BLACK_PANEL_TITLE,
                RED_TYPE_DROPDOWN, BLACK_TYPE_DROPDOWN,
                RED_NAME_TEXTINPUT, BLACK_NAME_TEXTINPUT,
                RED_BOT_DIFFICULTY_DROPDOWN,
                BLACK_BOT_DIFFICULTY_DROPDOWN,
                NUM_PLAYER_ROWS_TEXTINPUT, NUM_PLAYER_ROWS_TITLE,
                START_GAME_BUTTON]


class _SetupConsts:
    # Sizes
    BETWEEN_PANELS = _Sizes.XL
    PANEL_WIDTH = Fraction(0.35)
    PANEL_HEIGHT = 220
    ABOVE_PANELS = _Sizes.MEGA
    PANEL_TITLE_WIDTH = Fraction(1)
    ABOVE_PANEL_TITLE = _Sizes.XXL
    BELOW_PANEL_TITLE = _Sizes.XXL
    BELOW_PLAYER_MODE_DROPDOWN = _Sizes.M
    PANEL_CONTENT_WIDTH = Fraction(0.8)
    START_GAME_BUTTON_WIDTH = Fraction(0.7)
    RIGHT_OF_NUM_ROWS = _Sizes.XS
    ABOVE_NUM_ROWS = _Sizes.XS
    NUM_PLAYER_ROWS_WIDTH = (Fraction(1) - START_GAME_BUTTON_WIDTH) - \
                            Fraction(0.02)

    # Dropdown options
    PLAYER_MODE_OPTIONS = [_PlayerType.get_human_name(),
                           _PlayerType.get_bot_name()]
    BOT_DIFFICULTY_OPTIONS = [_BotLevel.get_random_name(),
                              _BotLevel.get_simple_name(),
                              _BotLevel.get_medium_name(),
                              _BotLevel.get_hard_name()]


class _GameElems:
    # ID
    screen_id = _Screens.get_game_name()

    # ===============
    # ELEMENTS
    # ===============

    TITLE_TEXT = "#title-text"
    MENU_BUTTON = "#menu-button"
    ACTION_BAR = "#action-bar"
    CURRENT_PLAYER_LABEL = "#current-player-label"
    SELECTED_PIECE_DROPDOWN = "#selected-piece-dropdown"
    PIECE_TO_DESTINATION_LABEL = "#piece-to-destination-label"
    DESTINATION_DROPDOWN = "#destination-dropdown"
    SUBMIT_MOVE_BUTTON = "#submit-move-button"
    BOARD = "#game-board"

    # ===============
    # LIST OF ELEMENT IDS
    # ===============

    elem_ids = [TITLE_TEXT, MENU_BUTTON, ACTION_BAR, CURRENT_PLAYER_LABEL,
                SELECTED_PIECE_DROPDOWN, PIECE_TO_DESTINATION_LABEL,
                DESTINATION_DROPDOWN, SUBMIT_MOVE_BUTTON, BOARD]


class _GameConsts:
    # Sizes
    ACTION_BAR_HEIGHT = 60
    DROPDOWN_WIDTH = 100
    ACTION_BAR_X_PADDING = _Sizes.L
    ACTION_BAR_ARROW_X_MARGIN = _Sizes.S


# ===============
# UNSORTED CONSTANTS
# ===============

_COORD_SQUARES = 1  # Number of square-sized spaces for coordinates

_THEME_FILE = "src/data/themes/theme.json"  # PyGame-GUI theme JSON file
_DYNAMIC_THEME_FILE_NAME = "dynamic_theme.json"
_DYNAMIC_THEME_FILE = f"src/data/themes/{_DYNAMIC_THEME_FILE_NAME}"
_THEME_BOARD_KING_PIECES = ["@board-red-piece-king",
                            "@board-red-piece-king-selected",
                            "@board-black-piece-king",
                            "@board-black-piece-king-selected"]


# ===============
# APP STATE CLASS
# ===============


def _color_str(color: PieceColor) -> str:
    """
    Get a string representation of a piece color.

    Args:
        color (PieceColor): piece color

    Returns:
        str: string representation of piece color

    TODO: consider moving this function to `checkers.py`
    """
    if color == PieceColor.RED:
        return "Red"
    return "Black"


@dataclass
class _AppState:
    """
    Data class holding PyGame stateful values and functions that process them.
    """

    # Lifecycle
    is_alive: bool = True

    # Current screen
    screen: _Screens = _Screens.SETUP

    # ===============
    # SETUP
    # ===============

    # Red player
    red_type: _PlayerType = _PlayerType.HUMAN
    red_bot_level: _BotLevel = _BotLevel.SIMPLE
    _red_name: str = ""
    _red_name_raw: str = str(_red_name)

    @property
    def red_name(self) -> str:
        """
        Getter method for the red player's name.

        Returns:
            str: red player's name
        """
        return self._red_name

    @red_name.setter
    def red_name(self, v: str) -> None:
        """
        Setter method for red player's name.

        Removes leading and trailing whitespace. Also stores raw text input in
        memory.

        Args:
            v (str): value

        Returns:
            None
        """
        self._red_name_raw = v
        self._red_name = v.strip()

    @property
    def red_name_raw(self) -> str:
        """
        Getter method for the raw input value of the red player's name.

        Returns:
            str: raw input for red player's name
        """
        return self._red_name_raw

    # Black player
    black_type: _PlayerType = _PlayerType.HUMAN
    black_bot_level: _BotLevel = _BotLevel.SIMPLE
    _black_name: str = ""
    _black_name_raw: str = str(_black_name)

    @property
    def black_name(self) -> str:
        """
        Getter method for the black player's name.

        Returns:
            str: black player's name
        """
        return self._black_name

    @black_name.setter
    def black_name(self, v: str) -> None:
        """
        Setter method for black player's name.

        Removes leading and trailing whitespace. Also stores raw text input in
        memory.

        Args:
            v (str): value

        Returns:
            None
        """
        self._black_name_raw = v
        self._black_name = v.strip()

    @property
    def black_name_raw(self) -> str:
        """
        Getter method for the raw input value of the black player's name.

        Returns:
            str: raw input for black player's name
        """
        return self._black_name_raw

    # Board settings
    _num_rows_per_player: Union[int, None] = 3
    _num_rows_per_player_raw_input: str = str(_num_rows_per_player)

    @property
    def num_rows_per_player(self) -> Union[int, None]:
        """
        Getter method for the number of rows per player.

        Returns:
            Union[int, None]: numerical value for number of rows per player,
                or None if invalid
        """
        return self._num_rows_per_player

    @property
    def num_rows_per_player_raw(self) -> str:
        """
        Getter method for the raw text input for the number of rows per player.
        """
        return self._num_rows_per_player_raw_input

    @num_rows_per_player.setter
    def num_rows_per_player(self, v: str) -> None:
        """
        Setter method for the number of rows per player.

        Args:
            v (str): value

        Returns:
            None
        """

        # Update raw text input
        self._num_rows_per_player_raw_input = v

        # Update numerical value
        try:
            num_rows_int = int(v)
            if num_rows_int < 1:
                raise ValueError("Number of rows per player must be at least "
                                 "1.")

            # By this point, value is valid!
            self._num_rows_per_player = num_rows_int
        except ValueError:
            # Inputted number of rows per player is not a valid integer
            self._num_rows_per_player = None

    # ===============
    # GAME
    # ===============

    board: CheckersBoard = CheckersBoard(1)
    current_color = PieceColor.BLACK

    @property
    def board_side_num(self) -> int:
        """
        Getter method for the number of board squares per side.
        
        Returns:
            int: number of squares
        """
        return 2 * self.num_rows_per_player + 2

    @property
    def square_side(self) -> Fraction:
        """
        Getter method for the fraction of the game board's width and height
        occupied by one square.

        Returns:
            Fraction: fraction of board width/height occupied
        """
        return Fraction(1) / (self.board_side_num + _COORD_SQUARES)

    def current_player_name(self) -> str:
        """
        Get the current player's name. If human, this is their inputted name. If
        a bot, this is the bot's color followed by "bot".

        Returns:
            str: player name
        """

        def current_bot_name() -> str:
            """
            Produce a string representing the current bot's name.

            Returns:
                str: name
            """
            return f"{self.current_bot_level().value} bot"

        if self.current_color == PieceColor.RED:
            if self.red_type == _PlayerType.HUMAN:
                return self.red_name
            else:
                return current_bot_name()
        else:
            # Black player
            if self.black_type == _PlayerType.HUMAN:
                return self.black_name
            else:
                return current_bot_name()

    def toggle_color(self) -> None:
        """
        Toggle current player color.

        Returns:
            None
        """
        if self.current_color == PieceColor.RED:
            self.current_color = PieceColor.BLACK
        else:
            self.current_color = PieceColor.RED

    _start_pos: Union[Position, None] = None
    dest_pos: Union[Position, None] = None

    def get_selected_move(self) -> Move:
        """
        Getter method for the selected move.

        Returns:
            Move: selected move

        Raises:
            RuntimeError if move is not found.
        """
        for move in self.board.get_player_moves(self.current_color):
            if move.get_current_position() == self._start_pos and \
                    move.get_new_position() == self.dest_pos:
                return move

        raise RuntimeError("Move not found.")

    def is_currently_bot(self) -> bool:
        """
        Determines whether the current player is a bot.

        Returns:
            bool: is bot
        """
        if self.current_color == PieceColor.RED:
            return self.red_type == _PlayerType.BOT
        return self.black_type == _PlayerType.BOT

    def current_bot_level(self) -> _BotLevel:
        """
        Determines the level of the currently playing bot.

        Returns:
            _BotLevel: bot level

        Raises:
            RuntimeError: if current player is not a bot.
        """
        if not self.is_currently_bot():
            raise RuntimeError("Current player is not a bot.")

        if self.current_color == PieceColor.RED:
            return self.red_bot_level
        return self.black_bot_level

    def current_bot_smart_level(self) -> SmartLevel:
        """
        Determines the relevant `SmartLevel` of the currently playing bot.

        This can then be passed into `SmartBot` to compute the moves a smart bot
        would make, given the current board state.

        Returns:
            SmartLevel: bot smart level

        Raises:
            RuntimeError: if current player is not a bot.
            RuntimeError: if the bot is not smart (i.e. random).
        """
        bot_level = self.current_bot_level()

        # Ensure bot is smart
        if bot_level == _BotLevel.RANDOM:
            raise RuntimeError("Bot is not smart - it's random.")

        # Find matching SmartLevel enum for the given _BotLevel
        if bot_level == _BotLevel.SIMPLE:
            return SmartLevel.SIMPLE
        if bot_level == _BotLevel.MEDIUM:
            return SmartLevel.MEDIUM
        return SmartLevel.HARD

    @property
    def start_pos(self) -> Position:
        """
        Getter method for the move starting position.
        """
        return self._start_pos

    @start_pos.setter
    def start_pos(self, v: Position) -> None:
        """
        Setter method for the move starting position.

        Updates the destination position if it is no longer valid.

        Args:
            v (Position): new value

        Returns:
            None
        """
        self._start_pos = v

        if self.dest_pos not in self.get_dest_piece_positions_set():
            # Destination position is no longer valid.
            # Update it with the first valid destination position.
            self.dest_pos = self.grid_position_from_string(
                self.get_dropdown_dest_positions()[0])

    def update_move_options(self) -> None:
        """
        Update the move options for the current player.

        Returns:
            None
        """

        # Select first piece position in dropdown options
        self.start_pos = self.grid_position_from_string(
            self.get_dropdown_start_positions()[0])

    def get_start_piece_positions_set(self) -> Set[Position]:
        """
        Generate a set of the positions of all starting piece positions for the
        current player.

        Returns:
            Set[Position]: starting piece positions
        """
        result = set()
        for move in self.board.get_player_moves(self.current_color):
            result.add(move.get_piece().get_position())

        return result

    def get_dest_piece_positions_set(self) -> Set[Position]:
        """
        Generate a set of the positions of all destination piece positions for
        the current player.

        Returns:
            Set[Position]: destination piece positions
        """
        result = set()
        for move in self.board.get_player_moves(self.current_color):
            if move.get_current_position() == self._start_pos:
                result.add(move.get_new_position())

        return result

    def get_piece_at_pos(self, pos: Position) -> Piece:
        """
        Get checkers piece at a position on the board.

        Args:
            pos (Position): position on board

        Returns:
            Piece: checkers piece

        Raises:
            RuntimeError: If no piece is found at the position on the board.
        """
        for piece in self.board.get_board_pieces():
            if piece.get_position() == pos:
                return piece

        raise RuntimeError(f"No piece found at the position {pos}")

    @staticmethod
    def row_position_to_string(row: int) -> str:
        """
        Convert a row position to a number-based representation.

        Args:
            row (int): row position

        Returns:
            str: number-based string representation

        Raises:
            ValueError: If the row is negative.
        """
        if row < 0:
            raise ValueError("Row position is negative.")

        return str(row + 1)

    @staticmethod
    def col_position_to_string(col: int) -> str:
        """
        Convert a column position to a letter-based representation.

        Args:
            col (int): column position

        Returns:
            str: number-based string representation

        Raises:
            ValueError: If the column is negative.
        """
        if col < 0:
            raise ValueError("Column position is negative.")

        col_num = col + 1
        col_str = ""
        while col_num > 0:
            col_num, remainder = divmod(col_num - 1, 26)
            col_str = chr(65 + remainder) + col_str

        return col_str

    @staticmethod
    def grid_position_to_string(position: Position) -> str:
        """
        Convert a tuple representing a position on a grid to a string in the
        format "B4".

        Args:
            position (tuple[int, int]): A tuple (x, y) representing the
                position on the grid, where (0, 0) is the top left square.

        Returns:
            str: A string in the format "B4", representing the human-readable
                board position

        Raises:
            ValueError: If either of the coordinates are negative.

        Examples:
            >>> _AppState.grid_position_to_string((0, 0))
            'A1'
            >>> _AppState.grid_position_to_string((1, 3))
            'B4'
            >>> _AppState.grid_position_to_string((26, 0))
            'AA1'
            >>> _AppState.grid_position_to_string((27, 0))
            'AB1'
        """
        x, y = position

        return f"{_AppState.col_position_to_string(x)}" \
               f"{_AppState.row_position_to_string(y)}"

    @staticmethod
    def _get_row_col_from_pos_string(s: str) -> Tuple[str, str]:
        """
        Get the row and column string parts from a string in the format of a
        grid position (e.g. "A4", "AB3", "A209", "SNS1", etc.).

        Args:
            s (str): string representation of grid position

        Returns:
            Tuple[str, str]: row, column

        Raises:
            ValueError: If the string does not have the correct format.

        Examples:
            >>> _AppState._get_row_col_from_pos_string("A1")
            ("A", "1")
            >>> _AppState._get_row_col_from_pos_string("B42")
            ("B", "42")
            >>> _AppState._get_row_col_from_pos_string("AA1")
            ("AA", "1")
            >>> _AppState._get_row_col_from_pos_string("AB394")
            ("AB", "394")
        """
        # Find the index of the first digit in the string
        for i, c in enumerate(s):
            if c.isdigit():
                # Split the string into two parts:
                # the column string and the row string
                row_str = s[i:]
                col_str = s[:i]
                break
        else:
            # No digit is found
            raise ValueError("Invalid string format")

        return row_str, col_str

    @staticmethod
    def _pos_string_sort_val(s: str) -> Tuple[int, int]:
        """
        Creates a list sort value for a given position string.

        Args:
            s (str): position string

        Returns:
            Tuple[int, int]: sort value

        Raises:
            ValueError: If the string does not have the correct format.
        """
        return _AppState.grid_position_from_string(s)

    @staticmethod
    def grid_position_from_string(s: str) -> Position:
        """
        Convert a string format of a grid position (e.g. "A4", "AB3", "A209",
        "SNS1", etc.) to a Position.

        Args:
            s (str): string representation of grid position

        Returns:
            tuple[int, int]: A tuple (x, y) representing the position on the
                grid, where (0, 0) is the top left square.

        Raises:
            ValueError: If the string does not have the correct format.

        Examples:
            >>> _AppState.grid_position_from_string("A1")
            (0, 0)
            >>> _AppState.grid_position_from_string("B4")
            (1, 3)
            >>> _AppState.grid_position_from_string("AA1")
            (26, 0)
            >>> _AppState.grid_position_from_string("AB1")
            (27, 0)
        """
        row_str, col_str = _AppState._get_row_col_from_pos_string(s)

        # Convert the column string to a column number
        col_num = 0
        for c in col_str:
            col_num = col_num * 26 + ord(c) - ord('A') + 1

        # Convert the row string to a row number
        row_num = int(row_str)

        # Return a tuple representing the position on the grid
        return col_num - 1, row_num - 1

    def get_dropdown_start_positions(self) -> List[str]:
        """
        Generate dropdown options that represent the starting positions of
        each piece that may be moved in the current player's turn.

        Returns:
            List[str]: dropdown menu options
        """
        result = []
        for pos in self.get_start_piece_positions_set():
            result.append(self.grid_position_to_string(pos))

        # Sort descending
        return sorted(result, key=_AppState._pos_string_sort_val)

    def get_dropdown_dest_positions(self) -> List[str]:
        """
        Generate dropdown options that represent the destinations of the
        currently selected piece.

        Returns:
            List[str]: dropdown menu options
        """
        result = []
        for pos in self.get_dest_piece_positions_set():
            result.append(self.grid_position_to_string(pos))

        # Sort descending
        return sorted(result, key=_AppState._pos_string_sort_val)

    def get_dropdown_piece_destinations(self) -> List[str]:
        """
        Generate dropdown options that represent the positions of every
        destination available to the currently selected checkers piece.

        Returns:
            List[str]: dropdown menu options
        """
        result = []
        for pos in self.get_start_piece_positions_set():
            result.append(self.grid_position_to_string(pos))

        # Sort descending
        return sorted(result, key=_AppState._pos_string_sort_val)


# ===============
# GUI APP CLASS
# ===============


class GuiApp:
    """
    The graphical user interface PyGame application for the checkers board game.

    Start the GUI app via the `run()` command.
    """
    DEFAULT_WINDOW_OPTIONS = WindowOptions()

    def __init__(self,
                 window_options: WindowOptions = WindowOptions(),
                 debug: bool = False) -> None:
        """
        Constructor for the GUI app.

        Args:
            window_options (WindowOptions): options for window presentation
            debug (bool): enable debug mode
        """

        # Initialize PyGame & app state
        pygame.init()
        self._state = _AppState()

        if debug:
            # Mock game setup
            self._state.red_type = _PlayerType.BOT
            self._state.red_bot_level = _BotLevel.HARD
            self._state.red_name = "Kevin"
            self._state.black_type = _PlayerType.BOT
            self._state.black_bot_level = _BotLevel.RANDOM
            self._state.num_rows_per_player = 5
            self._state.board = CheckersBoard(self._state.num_rows_per_player)

            # Directly open Game screen
            self._state.update_move_options()
            self._state.screen = _Screens.GAME
            self._attempt_start_bot_turn()

        # Window setup
        self._update_window(window_options)
        self._bg_surface = None  # All elements will be painted on this surface

        # Copy theme source file to new (dynamic) theme file
        shutil.copyfile(_THEME_FILE, _DYNAMIC_THEME_FILE)

        # Set up PyGame-GUI manager, with the dynamic theme file
        self._ui_manager = UIManager(self._get_window_resolution(),
                                     PackageResource(package="data.themes",
                                                     resource=
                                                     _DYNAMIC_THEME_FILE_NAME))

        # Initialize the element library
        self._lib = GuiComponentLib()
        self._lib.init_screen_elems(_Screens.get_setup_name(),
                                    _SetupElems.elem_ids)
        self._lib.init_screen_elems(_Screens.get_game_name(),
                                    _GameElems.elem_ids)

        # Build the UI for the first time
        self._rebuild_ui()

        # Start the render clock
        self._render_clock = pygame.time.Clock()

    def _update_window(self,
                       new_options: Union[WindowOptions, None] = None,
                       should_refresh_title: bool = True,
                       should_refresh_dimensions: bool = True) -> None:
        """
        Setter method for the app's window options.

        Args:
            new_options (WindowOptions | None): new window options
            should_refresh_title (bool): whether to refresh the window title
            should_refresh_dimensions (bool): whether to refresh the window
                dimensions
        """

        # Update window options in memory
        if new_options:
            self._window_options = new_options

        # Window title
        if should_refresh_title:
            pygame.display.set_caption(self._window_options.get_title())

        # Window dimensions
        if should_refresh_dimensions:
            if self._window_options.is_fullscreen():
                self._window_surface = pygame.display.set_mode(
                    self._window_options.get_dimensions_tuple(),
                    pygame.FULLSCREEN)
            else:
                self._window_surface = pygame.display.set_mode(
                    self._window_options.get_dimensions_tuple(),
                    pygame.RESIZABLE)

    def _get_window_options(self) -> WindowOptions:
        """
        Getter method for the app's window options.

        Returns:
            WindowOptions: the app's window options
        """
        return self._window_options

    def _set_window_dimensions(self, new_dimensions: Dimensions) -> None:
        """
        Setter method for the app's window dimensions.

        Raises:
            ValueError if invalid dimensions are passed.
        """
        self._window_options.set_dimensions(new_dimensions)

    def _get_window_dimensions(self) -> Dimensions:
        """
        Getter method for the app's window dimensions.

        Returns:
            Dimensions: the app's window dimensions
        """
        return self._get_window_options().get_dimensions()

    def _get_window_resolution(self) -> DimensionsTuple:
        """
        Getter method for the app's window dimensions, as a tuple of ints.

        Returns:
            DimensionsTuple: the app's window dimensions
        """
        return self._get_window_options().get_dimensions_tuple()

    def _rel_rect(self,
                  width: Union[int, Fraction, IntrinsicSize, MatchOtherSide],
                  height: Union[int, Fraction, IntrinsicSize, MatchOtherSide],
                  max_width: Union[int, Fraction, None] = None,
                  max_height: Union[int, Fraction, None] = None,
                  parent_id: Union[str, None] = None,
                  ref_pos: Union[ScreenPos, ElemPos] = ScreenPos(),
                  self_align: SelfAlign = SelfAlign(),
                  offset: Offset = Offset()) -> pygame.Rect:
        """
        Create a responsive pygame Rect based on relative screen positioning,
        relative alignment, and an offset.

        Intrinsic sizing only works for PyGame-GUI elements.

        Args:
            width (Union[int, Fraction, IntrinsicSize, MatchOtherSide]): element
                width (either in px, or fraction of parent width, or intrinsic
                width, or match height)
            height (Union[int, Fraction, IntrinsicSize, MatchOtherSide]):
                element height (either in px, or fraction of parent height, or
                intrinsic height, or match width)
            max_width (Union[int, Fraction, None]): maximum element width
                (either in px, or fraction of parent width, or None)
            max_height (Union[int, Fraction, None]): maximum element height
                (either in px, or fraction of parent width, or None)
            parent_id (Union[str, None]): parent element ID – defaults to screen
            ref_pos (Union[ScreenPos, ElemPos]): relative positioning,
                according to the screen or another element (make sure the
                other element is drafted first)
            self_align (SelfAlign): self alignment in reference to `ref_pos`
            offset (Offset): offset from relative position

        Raises:
            ValueError if both sides are assigned `MatchOtherSide()`.
            RuntimeError if parent element's ID doesn't exist.
            RuntimeError if relative element's ID doesn't exist.
        """

        # Check for valid width & height
        if isinstance(width, MatchOtherSide) and \
                isinstance(height, MatchOtherSide):
            raise ValueError("Both width & height are defined using "
                             "MatchOtherSide.")

        # Parent element, if chosen
        parent_elem: Union[Element, None] = None
        if parent_id:
            parent_elem = self._lib.get_elem(parent_id)

        def frac_width(v: Fraction) -> float:
            """
            Compute numerical value for a fractional width.

            Args:
                v (Fraction): value

            Returns:
                float: computed width
            """
            if parent_elem:
                # Fractional width based on parent element
                return parent_elem.relative_rect.width * v.value
            else:
                # Fractional width based on screen and its padding
                return (self._get_window_dimensions().width - 2 *
                        self._get_window_options().get_padding()) * v.value

        def frac_height(v: Fraction) -> float:
            """
            Compute numerical value for a fractional height.

            Args:
                v (Fraction): value

            Returns:
                float: computed height
            """
            if parent_elem:
                # Fractional height based on parent element
                return parent_elem.relative_rect.height * v.value
            else:
                # Fractional height based on screen and its padding
                return (self._get_window_dimensions().height - 2 *
                        self._get_window_options().get_padding()) * v.value

        # Calculate maximum width & height
        max_w, max_h = None, None
        if max_width:
            if isinstance(max_width, Fraction):
                max_w = frac_width(max_width)
            else:
                # Integer value
                max_w = max_width

        if max_height:
            if isinstance(max_height, Fraction):
                max_h = frac_height(max_height)
            else:
                # Integer value
                max_h = max_height

        # Calculate pixel-based width, height values
        w, h = None, None
        if isinstance(width, IntrinsicSize):
            w = -1  # PyGame-GUI interprets this as intrinsic width
        elif isinstance(width, Fraction):
            w = frac_width(width)
        elif isinstance(width, int):
            w = width

        if isinstance(height, IntrinsicSize):
            h = -1  # PyGame-GUI interprets this as intrinsic height
        elif isinstance(height, Fraction):
            h = frac_height(height)
        elif isinstance(height, int):
            h = height

        # Bound width & height to their defined maximums,
        # if both size and max size are defined.
        if w and max_w:
            w = min(w, max_w)
        if h and max_h:
            h = min(h, max_h)

        # If one side should match the other
        common_length = None
        if isinstance(width, MatchOtherSide):
            # Set common length to calculated height or max width (if defined),
            # whichever is smaller.
            common_length = min(h, max_w) if max_w else h
        elif isinstance(height, MatchOtherSide):
            # Set common length to calculated width or max height (if defined),
            # whichever is smaller.
            common_length = min(w, max_h) if max_h else w

        if common_length:
            # Set both sides to same length
            w, h = common_length, common_length

        # Calculate pixel-based reference position
        if isinstance(ref_pos, ScreenPos):
            # In reference to the screen

            if ref_pos.x_pos == RelPos.START:
                # `padding` px from left of screen
                x_ref = self._get_window_options().get_padding()
            elif ref_pos.x_pos == RelPos.CENTER:
                # horizontal center of screen
                x_ref = self._get_center_x()
            else:
                # `padding` px from right of screen
                x_ref = self._get_window_dimensions().width - \
                        self._get_window_options().get_padding()

            if ref_pos.y_pos == RelPos.START:
                # `padding` px from top of screen
                y_ref = self._get_window_options().get_padding()
            elif ref_pos.y_pos == RelPos.CENTER:
                # vertical center of screen
                y_ref = self._get_center_y()
            else:
                # `padding` px from bottom of screen
                y_ref = self._get_window_dimensions().height - \
                        self._get_window_options().get_padding()
        else:
            # In reference to another element
            other_elem = self._lib.get_elem(ref_pos.elem_id)

            if ref_pos.x_pos == RelPos.START:
                # Position left of other element
                x_ref = other_elem.relative_rect.left
            elif ref_pos.x_pos == RelPos.CENTER:
                # Position horizontal center of other element
                x_ref = other_elem.relative_rect.centerx
            else:
                # Position right of other element
                x_ref = other_elem.relative_rect.right

            if ref_pos.y_pos == RelPos.START:
                # Position top of other element
                y_ref = other_elem.relative_rect.top
            elif ref_pos.y_pos == RelPos.CENTER:
                # Position vertical center of other element
                y_ref = other_elem.relative_rect.centery
            else:
                # Position bottom of other element
                y_ref = other_elem.relative_rect.bottom

        # Calculate offset-less position, considering alignment
        if self_align.x_pos == RelPos.START:
            x = x_ref - w
        elif self_align.x_pos == RelPos.CENTER:
            x = x_ref - w / 2
        else:
            x = x_ref

        if self_align.y_pos == RelPos.START:
            y = y_ref - h
        elif self_align.y_pos == RelPos.CENTER:
            y = y_ref - h / 2
        else:
            y = y_ref

        # Calculate numerical offset
        if isinstance(offset.x, NegFraction):
            offset_x = - frac_width(offset.x)
        elif isinstance(offset.x, Fraction):
            offset_x = frac_width(offset.x)
        else:
            offset_x = offset.x

        if isinstance(offset.y, NegFraction):
            offset_y = - frac_height(offset.y)
        elif isinstance(offset.y, Fraction):
            offset_y = frac_height(offset.y)
        else:
            offset_y = offset.y

        # Return pygame Rect, now considering offset
        return pygame.Rect((int(x + offset_x), int(y + offset_y)), (w, h))

    def _get_center_x(self) -> int:
        """
        Get the x-coordinate of the screen's horizontal center.

        Returns:
            int: center x-coordinate
        """
        return self._get_window_dimensions().width // 2

    def _get_center_y(self) -> int:
        """
        Get the y-coordinate of the screen's vertical center.

        Returns:
            int: center y-coordinate
        """
        return self._get_window_dimensions().height // 2

    def _update_responsive_assets(self) -> None:
        """
        Updates the PyGame-GUI theme JSON file so that the size of all assets
        are suitable for the current window dimensions.

        This should be called once when initializing the UI, and afterwards only
        when detecting the window has been resized.

        Must be called after updating the window size in memory and
        rebuilding the UI.

        Returns:
            None
        """

        # ===============
        # READ ORIGINAL THEME FILE
        # ===============
        with open(_THEME_FILE) as theme_file:
            theme_json = json.load(theme_file)

        # ===============
        # SCREEN-RELEVANT ASSETS
        # ===============
        if self._state.screen == _Screens.GAME:
            # ===============
            # Responsively size king piece background images,
            # so they fit well within the circular checkers piece UIPanel shape.
            # ===============

            # Calculate the width/height of individual board squares
            square_size = self._lib.get_elem(_GameElems.BOARD) \
                              .relative_rect.width \
                          * self._state.square_side.value

            def get_king_png_size() -> _KingPiecePngSize:
                """
                Choose the optimal PNG size for the king piece background image.

                Returns:
                    _KingPiecePngSize: PNG size
                """

                # Create list of all available king piece PNG sizes (from the enum)
                king_piece_sizes = [e for e in _KingPiecePngSize]

                for king_size_i in range(1, len(king_piece_sizes)):
                    if square_size < float(king_piece_sizes[king_size_i]) * 2:
                        # Did not overcome the size threshold (2x) for the given
                        # PNG size, so return the PNG size just below threshold
                        return king_piece_sizes[king_size_i - 1]

                # By this point, overcame every threshold!
                # Return largest PNG size
                return king_piece_sizes[-1]

            for king_piece_name in _THEME_BOARD_KING_PIECES:
                color = "red" if "red" in king_piece_name else "black"
                theme_json[king_piece_name]["images"]["background_image"][
                    "path"] = \
                    f"src/data/images/{get_king_png_size()}px/{color}-king.png"

        # ===============
        # UPDATE DYNAMIC JSON FILE
        # ===============
        with open(_DYNAMIC_THEME_FILE, "w") as theme_file:
            json.dump(theme_json, theme_file)

    def _rebuild_ui(self) -> None:
        """
        Rebuilds all UI elements. Only run this if absolutely necessary,
        since compute is expensive.
        """

        # Clean slate window
        self._ui_manager.set_window_resolution(
            self._get_window_resolution())
        self._ui_manager.clear_and_reset()

        # Fill background
        self._bg_surface = pygame.Surface(self._get_window_resolution())
        self._bg_surface.fill(
            self._ui_manager.get_theme().get_colour("dark_bg")
        )

        # Create all UI elements for current screen only
        self._lib.clear_all_screens()
        self._lib.set_draft_screen(self._get_current_screen_name())
        if self._state.screen == _Screens.SETUP:
            # ===============
            # RED PANEL
            # ===============
            self._lib.draft(
                _SetupElems.RED_PANEL,
                UIPanel(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_WIDTH,
                        height=_SetupConsts.PANEL_HEIGHT,
                        ref_pos=ScreenPos(
                            RelPos.CENTER,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.START,
                            RelPos.CENTER
                        ),
                        offset=Offset(
                            - _SetupConsts.BETWEEN_PANELS // 2,
                            _SetupConsts.ABOVE_PANELS // 2),
                    ),
                    starting_layer_height=0))
            self._lib.draft(
                _SetupElems.RED_PANEL_TITLE,
                UILabel(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_TITLE_WIDTH,
                        height=_GeneralConsts.LABEL_HEIGHT,
                        parent_id=_SetupElems.RED_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.RED_PANEL,
                            RelPos.CENTER,
                            RelPos.START
                        ),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0, _SetupConsts.ABOVE_PANEL_TITLE)
                    ),
                    "Red"))
            self._lib.draft(
                _SetupElems.RED_TYPE_DROPDOWN,
                UIDropDownMenu(
                    _SetupConsts.PLAYER_MODE_OPTIONS,
                    str(self._state.red_type.value),
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralConsts.DROPDOWN_HEIGHT,
                        parent_id=_SetupElems.RED_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.RED_PANEL_TITLE,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0, _SetupConsts.BELOW_PANEL_TITLE)),
                    object_id=_SetupElems.RED_TYPE_DROPDOWN,
                    manager=self._ui_manager))
            self._lib.draft(
                _SetupElems.RED_NAME_TEXTINPUT,
                UITextEntryLine(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralConsts.TEXTINPUT_HEIGHT,
                        parent_id=_SetupElems.RED_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.RED_TYPE_DROPDOWN,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0,
                                      _SetupConsts.BELOW_PLAYER_MODE_DROPDOWN)),
                    manager=self._ui_manager,
                    object_id=_SetupElems.RED_NAME_TEXTINPUT,
                    placeholder_text="Name...",
                    initial_text=self._state.red_name_raw,
                    visible=self._state.red_type == _PlayerType.HUMAN))
            self._lib.draft(
                _SetupElems.RED_BOT_DIFFICULTY_DROPDOWN,
                UIDropDownMenu(
                    _SetupConsts.BOT_DIFFICULTY_OPTIONS,
                    str(self._state.red_bot_level.value),
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralConsts.DROPDOWN_HEIGHT,
                        parent_id=_SetupElems.RED_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.RED_TYPE_DROPDOWN,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0,
                                      _SetupConsts.BELOW_PLAYER_MODE_DROPDOWN)),
                    manager=self._ui_manager,
                    object_id=_SetupElems.RED_BOT_DIFFICULTY_DROPDOWN,
                    visible=self._state.red_type == _PlayerType.BOT))

            # ===============
            # BLACK PANEL
            # ===============
            self._lib.draft(
                _SetupElems.BLACK_PANEL,
                UIPanel(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_WIDTH,
                        height=_SetupConsts.PANEL_HEIGHT,
                        ref_pos=ScreenPos(
                            RelPos.CENTER,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.END,
                            RelPos.CENTER
                        ),
                        offset=Offset(
                            _SetupConsts.BETWEEN_PANELS // 2,
                            _SetupConsts.ABOVE_PANELS // 2
                        ),
                    ),
                    starting_layer_height=0,
                    manager=self._ui_manager))
            self._lib.draft(
                _SetupElems.BLACK_PANEL_TITLE,
                UILabel(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_TITLE_WIDTH,
                        height=_GeneralConsts.LABEL_HEIGHT,
                        parent_id=_SetupElems.BLACK_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.BLACK_PANEL,
                            RelPos.CENTER,
                            RelPos.START
                        ),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0, _SetupConsts.ABOVE_PANEL_TITLE)
                    ),
                    "Black"))
            self._lib.draft(
                _SetupElems.BLACK_TYPE_DROPDOWN,
                UIDropDownMenu(
                    _SetupConsts.PLAYER_MODE_OPTIONS,
                    str(self._state.black_type.value),
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralConsts.DROPDOWN_HEIGHT,
                        parent_id=_SetupElems.BLACK_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.BLACK_PANEL_TITLE,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0, _SetupConsts.BELOW_PANEL_TITLE)),
                    object_id=_SetupElems.BLACK_TYPE_DROPDOWN,
                    manager=self._ui_manager))
            self._lib.draft(
                _SetupElems.BLACK_NAME_TEXTINPUT,
                UITextEntryLine(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralConsts.TEXTINPUT_HEIGHT,
                        parent_id=_SetupElems.BLACK_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.BLACK_TYPE_DROPDOWN,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0,
                                      _SetupConsts.BELOW_PLAYER_MODE_DROPDOWN)),
                    manager=self._ui_manager,
                    object_id=_SetupElems.BLACK_NAME_TEXTINPUT,
                    placeholder_text="Name...",
                    initial_text=self._state.black_name_raw,
                    visible=self._state.black_type == _PlayerType.HUMAN))
            self._lib.draft(
                _SetupElems.BLACK_BOT_DIFFICULTY_DROPDOWN,
                UIDropDownMenu(
                    _SetupConsts.BOT_DIFFICULTY_OPTIONS,
                    str(self._state.black_bot_level.value),
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralConsts.DROPDOWN_HEIGHT,
                        parent_id=_SetupElems.BLACK_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.BLACK_TYPE_DROPDOWN,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0,
                                      _SetupConsts.BELOW_PLAYER_MODE_DROPDOWN)),
                    manager=self._ui_manager,
                    object_id=_SetupElems.BLACK_BOT_DIFFICULTY_DROPDOWN,
                    visible=self._state.black_type == _PlayerType.BOT))

            # ===============
            # WELCOME TEXT
            # ===============
            self._lib.draft(
                _SetupElems.WELCOME_TEXT,
                UILabel(
                    self._rel_rect(
                        width=Fraction(1),
                        height=_GeneralConsts.LABEL_HEIGHT,
                        ref_pos=ElemPos(
                            _SetupElems.RED_PANEL,
                            RelPos.END,
                            RelPos.START
                        ),
                        offset=Offset(
                            _SetupConsts.BETWEEN_PANELS // 2,
                            - _SetupConsts.ABOVE_PANELS),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.START
                        )),
                    "Welcome to Checkers!",
                    self._ui_manager,
                    object_id=_SetupElems.WELCOME_TEXT))

            # ===============
            # START GAME BUTTON
            # ===============
            self._lib.draft(
                _SetupElems.START_GAME_BUTTON,
                UIButton(
                    self._rel_rect(
                        width=_SetupConsts.START_GAME_BUTTON_WIDTH,
                        height=_GeneralConsts.BUTTON_HEIGHT,
                        ref_pos=ScreenPos(
                            RelPos.END,
                            RelPos.END
                        ),
                        self_align=SelfAlign(
                            RelPos.START,
                            RelPos.START
                        )),
                    "Start game",
                    self._ui_manager,
                    object_id=_SetupElems.START_GAME_BUTTON))
            self._validate_game_setup()

            # ===============
            # NUM PLAYER ROWS
            # ===============
            self._lib.draft(
                _SetupElems.NUM_PLAYER_ROWS_TEXTINPUT,
                UITextEntryLine(
                    self._rel_rect(
                        width=_SetupConsts.NUM_PLAYER_ROWS_WIDTH,
                        height=_GeneralConsts.BUTTON_HEIGHT,  # match button
                        ref_pos=ElemPos(
                            _SetupElems.START_GAME_BUTTON,
                            RelPos.START,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.START,
                            RelPos.CENTER
                        ),
                        offset=Offset(- _SetupConsts.RIGHT_OF_NUM_ROWS, 0)
                    ),
                    manager=self._ui_manager,
                    object_id=_SetupElems.NUM_PLAYER_ROWS_TEXTINPUT,
                    placeholder_text="Number...",
                    initial_text=self._state.num_rows_per_player_raw))
            self._lib.draft(
                _SetupElems.NUM_PLAYER_ROWS_TITLE,
                UILabel(
                    self._rel_rect(
                        width=IntrinsicSize(),
                        height=_GeneralConsts.LABEL_HEIGHT,
                        ref_pos=ElemPos(
                            _SetupElems.NUM_PLAYER_ROWS_TEXTINPUT,
                            RelPos.START,
                            RelPos.START
                        ),
                        self_align=SelfAlign(
                            RelPos.END,
                            RelPos.START
                        ),
                        offset=Offset(0, - _SetupConsts.ABOVE_NUM_ROWS)
                    ),
                    "Rows per player",
                )
            )
        elif self._state.screen == _Screens.GAME:
            # ===============
            # TITLE BAR
            # ===============
            self._lib.draft(
                _GameElems.TITLE_TEXT,
                UILabel(
                    self._rel_rect(
                        width=IntrinsicSize(),
                        height=_GeneralConsts.BUTTON_HEIGHT,  # same as menu btn
                        ref_pos=ScreenPos(
                            RelPos.START,
                            RelPos.START
                        ),
                        self_align=SelfAlign(
                            RelPos.END,
                            RelPos.END
                        ),
                    ),
                    "Checkers"
                )
            )
            self._lib.draft(
                _GameElems.MENU_BUTTON,
                UIButton(
                    self._rel_rect(
                        width=60,
                        height=_GeneralConsts.BUTTON_HEIGHT,
                        ref_pos=ScreenPos(
                            RelPos.END,
                            RelPos.START
                        ),
                        self_align=SelfAlign(
                            RelPos.START,
                            RelPos.END
                        ),
                    ),
                    "Menu",
                    object_id=_GameElems.MENU_BUTTON,
                    manager=self._ui_manager
                )
            )
            # ===============
            # ACTION BAR
            # ===============
            self._lib.draft(
                _GameElems.ACTION_BAR,
                UIPanel(
                    self._rel_rect(
                        width=Fraction(1),
                        height=_GameConsts.ACTION_BAR_HEIGHT,
                        ref_pos=ScreenPos(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.START
                        )
                    ),
                    starting_layer_height=0
                )
            )
            self._lib.draft(
                _GameElems.CURRENT_PLAYER_LABEL,
                UILabel(
                    self._rel_rect(
                        width=IntrinsicSize(),
                        height=_GeneralConsts.LABEL_HEIGHT,
                        ref_pos=ElemPos(
                            _GameElems.ACTION_BAR,
                            RelPos.START,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.END,
                            RelPos.CENTER
                        ),
                        offset=Offset(_GameConsts.ACTION_BAR_X_PADDING, 0)
                    ),
                    f"{self._state.current_player_name()}'s move:",
                )
            )
            self._lib.draft(
                _GameElems.SELECTED_PIECE_DROPDOWN,
                UIDropDownMenu(
                    self._state.get_dropdown_start_positions(),
                    self._state.grid_position_to_string(self._state.start_pos),
                    self._rel_rect(
                        width=_GameConsts.DROPDOWN_WIDTH,
                        height=_GeneralConsts.DROPDOWN_HEIGHT,
                        ref_pos=ElemPos(
                            _GameElems.CURRENT_PLAYER_LABEL,
                            RelPos.END,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.END,
                            RelPos.CENTER
                        ),
                        offset=Offset(_Sizes.M, 0)
                    ),
                    object_id=_GameElems.SELECTED_PIECE_DROPDOWN
                ),
            )
            self._lib.draft(
                _GameElems.PIECE_TO_DESTINATION_LABEL,
                UILabel(
                    self._rel_rect(
                        width=IntrinsicSize(),
                        height=_GeneralConsts.LABEL_HEIGHT,
                        ref_pos=ElemPos(
                            _GameElems.SELECTED_PIECE_DROPDOWN,
                            RelPos.END,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.END,
                            RelPos.CENTER
                        ),
                        offset=Offset(_GameConsts.ACTION_BAR_ARROW_X_MARGIN, 0)
                    ),
                    "→"
                )
            )
            self._lib.draft(
                _GameElems.DESTINATION_DROPDOWN,
                UIDropDownMenu(
                    self._state.get_dropdown_dest_positions(),
                    self._state.grid_position_to_string(self._state.dest_pos),
                    self._rel_rect(
                        width=_GameConsts.DROPDOWN_WIDTH,
                        height=_GeneralConsts.DROPDOWN_HEIGHT,
                        ref_pos=ElemPos(
                            _GameElems.PIECE_TO_DESTINATION_LABEL,
                            RelPos.END,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.END,
                            RelPos.CENTER
                        ),
                        offset=Offset(_GameConsts.ACTION_BAR_ARROW_X_MARGIN, 0)
                    ),
                    object_id=_GameElems.DESTINATION_DROPDOWN
                ),
            )
            self._lib.draft(
                _GameElems.SUBMIT_MOVE_BUTTON,
                UIButton(
                    self._rel_rect(
                        width=80,
                        height=_GeneralConsts.BUTTON_HEIGHT,
                        ref_pos=ElemPos(
                            _GameElems.ACTION_BAR,
                            RelPos.END,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.START,
                            RelPos.CENTER
                        ),
                        offset=Offset(-_GameConsts.ACTION_BAR_X_PADDING, 0)
                    ),
                    "Move",
                    object_id=_GameElems.SUBMIT_MOVE_BUTTON
                ),
            )
            # ===============
            # CHECKERS BOARD
            # ===============
            self._lib.draft(
                _GameElems.BOARD,
                UIPanel(
                    self._rel_rect(
                        width=MatchOtherSide(),
                        max_width=Fraction(0.7),
                        height=Fraction(0.7),
                        ref_pos=ScreenPos(
                            RelPos.START,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.END,
                            RelPos.CENTER
                        )
                    ),
                    object_id=_GameElems.BOARD,
                    starting_layer_height=0
                )
            )

            # Add every square to board
            for row, col in itertools.product(
                    range(self._state.board_side_num),
                    range(self._state.board_side_num)):
                pos = (row, col)  # square position on game board

                # Initialize board square
                elem_id = self._board_square_id(pos)
                self._lib.init_elem(elem_id,
                                    self._get_current_screen_name())
                # Color
                if (row % 2 == 1 and col % 2 == 0) or \
                        (row % 2 == 0 and col % 2 == 1):
                    elem_class = "@board-square-dark"
                else:
                    elem_class = "@board-square-light"

                # Selected?
                if self._state.dest_pos == pos:
                    elem_class += "-selected"
                    if self._state.get_piece_at_pos(
                            self._state.start_pos).get_color() == \
                            PieceColor.RED:
                        elem_class += "-red"
                    else:
                        elem_class += "-black"

                # Draft square
                self._lib.draft(
                    elem_id,
                    UIPanel(
                        self._rel_rect(
                            width=self._state.square_side,
                            height=MatchOtherSide(),
                            parent_id=_GameElems.BOARD,
                            ref_pos=ElemPos(
                                _GameElems.BOARD,
                                RelPos.START,
                                RelPos.START
                            ),
                            self_align=SelfAlign(
                                RelPos.START,
                                RelPos.START
                            ),
                            offset=Offset(
                                self._state.square_side * (row + 1 +
                                                           _COORD_SQUARES),
                                self._state.square_side * (col + 1 +
                                                           _COORD_SQUARES)
                            )
                        ),
                        starting_layer_height=0,
                        object_id=ObjectID(
                            class_id=elem_class,
                            object_id=elem_id)
                    ),
                )

            # Add coordinates (do both horizontally and vertically at once)
            for side_n in range(self._state.board_side_num):
                # Initialize letter and number
                letter_elem_id = f"coord-letter-{side_n + 1}"
                self._lib.init_elem(letter_elem_id,
                                    self._get_current_screen_name())

                num_elem_id = f"coord-num-{side_n + 1}"
                self._lib.init_elem(num_elem_id,
                                    self._get_current_screen_name())

                # Add coordinate letter
                self._lib.draft(
                    letter_elem_id,
                    UILabel(
                        self._rel_rect(
                            width=self._state.square_side,
                            height=MatchOtherSide(),
                            parent_id=_GameElems.BOARD,
                            ref_pos=ElemPos(
                                self._board_square_id((side_n, 0)),
                                RelPos.CENTER,
                                RelPos.CENTER
                            ),
                            self_align=SelfAlign(
                                RelPos.CENTER,
                                RelPos.START
                            ),
                            offset=Offset(
                                0,
                                NegFraction(self._state.square_side.value / 2)
                            )),
                        _AppState.col_position_to_string(side_n)
                    )
                )

                # Add coordinate number
                self._lib.draft(
                    num_elem_id,
                    UILabel(
                        self._rel_rect(
                            width=self._state.square_side,
                            height=MatchOtherSide(),
                            parent_id=_GameElems.BOARD,
                            ref_pos=ElemPos(
                                self._board_square_id((0, side_n)),
                                RelPos.CENTER,
                                RelPos.CENTER
                            ),
                            self_align=SelfAlign(
                                RelPos.START,
                                RelPos.CENTER
                            ),
                            offset=Offset(
                                NegFraction(self._state.square_side.value / 2),
                                0)),
                        _AppState.row_position_to_string(side_n)
                    )
                )

            # Add pieces
            for piece in self._state.board.get_board_pieces():
                # Get position
                pos = piece.get_position()

                # Initialize checkers piece
                elem_id = self._checkers_piece_id(pos)
                self._lib.init_elem(elem_id,
                                    self._get_current_screen_name())

                # Color
                if piece.get_color() == PieceColor.RED:
                    elem_class = "@board-red-piece"
                else:
                    elem_class = "@board-black-piece"

                # King?
                if piece.is_king():
                    elem_class += "-king"

                # Selected?
                if self._state.start_pos == pos:
                    elem_class += "-selected"

                # Draft checkers piece
                parent_id = self._board_square_id(pos)
                self._lib.draft(
                    elem_id,
                    UIPanel(
                        self._rel_rect(
                            width=Fraction(0.7),
                            height=MatchOtherSide(),
                            parent_id=parent_id,
                            ref_pos=ElemPos(
                                parent_id,
                                RelPos.CENTER,
                                RelPos.CENTER
                            ),
                            self_align=SelfAlign(
                                RelPos.CENTER,
                                RelPos.CENTER
                            )
                        ),
                        starting_layer_height=0,
                        object_id=ObjectID(
                            class_id=elem_class,
                            object_id=elem_id)
                    )
                )

    @staticmethod
    def _board_square_id(position: Position) -> str:
        """
        Get the element ID for a board square at a given position.

        Board starts with light square in the top left hand corner.

        Args:
            position (Position): position on board

        Returns:
            str: element ID

        Raises:
            ValueError: if position is invalid.
        """
        x, y = position
        if x < 0 or y < 0:
            raise ValueError(f"Position {position} is invalid.")

        return f"#board-square-({x},{y})"

    @staticmethod
    def _checkers_piece_id(position: Position) -> str:
        """
        Get the element ID for a checkers piece at a given position.

        Board starts with light square in the top left hand corner.

        Args:
            position (Position): position on board

        Returns:
            str: element ID

        Raises:
            ValueError: if position is invalid.
        """
        x, y = position
        if x < 0 or y < 0:
            raise ValueError(f"Position {position} is invalid.")

        return f"#checkers-piece-({x},{y})"

    def _check_window_dimensions_changed(self) -> None:
        """
        Checks whether the window dimensions have changed. If they have,
        the UI is rebuilt accordingly.
        """
        current_dimensions_tuple = pygame.display.get_surface().get_size()
        if current_dimensions_tuple != self._get_window_resolution():
            # Window dimensions have changed since last paint:
            # store the new dimensions in memory
            self._window_options.set_dimensions(
                Dimensions.from_tuple(current_dimensions_tuple))

            # Update the window & rebuild the UI
            self._update_window(should_refresh_title=False)
            self._rebuild_ui()

            # Update responsive assets
            self._update_responsive_assets()

    def _get_current_screen(self) -> _Screens:
        """
        Getter method for the current screen.

        Returns:
            _Screens: current screen
        """
        return self._state.screen

    def _get_current_screen_name(self) -> str:
        """
        Getter method for the string representation of the current screen.

        Returns:
            str: current screen name
        """
        return str(self._get_current_screen().value)

    def _set_current_screen(self, new_screen: _Screens) -> None:
        """
        Setter method for the current screen.

        Args:
            new_screen (_Screens): new screen
        """
        self._state.screen = new_screen

    def _open_screen(self, new_screen: _Screens) -> None:
        """
        Navigate to a different screen. If screen is already open – ignore.

        Args:
            new_screen (_Screens): screen to navigate to
        """
        if new_screen != self._get_current_screen():
            # Screen is not already open
            self._set_current_screen(new_screen)
            # Needs rebuild UI to clear old screen & draw new screen
            self._rebuild_ui()

    def _validate_game_setup(self) -> None:
        """
        Check whether the game is set up correctly, and enable/disable the
        start game button accordingly.
        """
        try:
            if self._state.num_rows_per_player is None:
                raise ValueError()
            if self._state.red_type == _PlayerType.HUMAN:
                if self._state.red_name == "":
                    raise ValueError()
            if self._state.black_type == _PlayerType.HUMAN:
                if self._state.black_name == "":
                    raise ValueError()
            if self._state.red_type == _PlayerType.HUMAN and \
                    self._state.black_type == _PlayerType.HUMAN:
                if self._state.red_name == self._state.black_name:
                    raise ValueError()

            # By this point, the game setup is all valid!
            self._lib.enable_elem(_SetupElems.START_GAME_BUTTON)
        except ValueError:
            self._lib.disable_elem(_SetupElems.START_GAME_BUTTON)

    def _process_setup_events(self, event: "Event") -> None:
        """
        Process user interactions events for the Setup screen.

        Args:
            event (Event): PyGame event
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_object_id == _SetupElems.START_GAME_BUTTON:
                # ===============
                # Clicked: START GAME BUTTON
                # ===============

                # Recreate board in memory
                self._state.board = CheckersBoard(
                    self._state.num_rows_per_player)

                # Black starts the game
                self._state.current_color = PieceColor.BLACK
                self._state.update_move_options()

                # Open Game screen
                self._open_screen(_Screens.GAME)

                # If starting player is bot, autoplay their turn
                self._attempt_start_bot_turn()

                return  # stop processing UI events in Setup screen

        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_object_id == _SetupElems.NUM_PLAYER_ROWS_TEXTINPUT:
                # ===============
                # Updated text: NUM PLAYER ROWS TEXT INPUT
                # ===============
                self._state.num_rows_per_player = self._lib.get_elem_text(
                    _SetupElems.NUM_PLAYER_ROWS_TEXTINPUT)

        def process_panel_events(
                initial_player_type: _PlayerType,
                player_type_dropdown_id: str,
                on_update_player_type: Callable[[_PlayerType], None],
                name_input_id: str,
                on_update_name: Callable[[str], None],
                initial_bot_difficulty: _BotLevel,
                bot_difficulty_dropdown_id: str,
                on_update_bot_difficulty: Callable[[_BotLevel], None]) -> None:
            """
            Process user interaction events for a given panel.

            Args:
                initial_player_type (_PlayerType): initial player type
                player_type_dropdown_id (str): player type dropdown ID
                on_update_player_type (Callable[[_PlayerType], None]): update
                    player type callback
                name_input_id (str): name text input ID
                on_update_name (Callable[[str], None]): update player name
                    callback
                initial_bot_difficulty (_BotLevel): initial bot difficulty
                    level
                bot_difficulty_dropdown_id (str): bot difficulty level
                    dropdown ID
                on_update_bot_difficulty (Callable[[_BotLevel], None]): update
                    bot difficulty level callback

            """
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_object_id == player_type_dropdown_id:
                    # ===============
                    # Selection: PLAYER TYPE DROPDOWN
                    # ===============
                    selection = self._lib.get_elem_selection(
                        player_type_dropdown_id)
                    selected_type = _PlayerType.from_string(selection)
                    if selected_type != initial_player_type:
                        # ===============
                        # Updated selection: PLAYER TYPE
                        # ===============
                        on_update_player_type(selected_type)
                        # Show elements relevant to that player type
                        self._lib.mod_elem(
                            name_input_id,
                            ModifyElemCommand.SHOW \
                                if selected_type == _PlayerType.HUMAN \
                                else ModifyElemCommand.HIDE)
                        self._lib.mod_elem(
                            bot_difficulty_dropdown_id,
                            ModifyElemCommand.SHOW \
                                if selected_type == _PlayerType.BOT \
                                else ModifyElemCommand.HIDE)
                    return
                elif event.ui_object_id == bot_difficulty_dropdown_id:
                    # ===============
                    # Selection: PLAYER BOT DIFFICULTY DROPDOWN
                    # ===============
                    selection = self._lib.get_elem_selection(
                        bot_difficulty_dropdown_id)
                    selected_difficulty = _BotLevel.from_string(selection)
                    if selected_difficulty != initial_bot_difficulty:
                        # ===============
                        # Updated selection: PLAYER BOT DIFFICULTY
                        # ===============
                        on_update_bot_difficulty(selected_difficulty)
                    return

            elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_object_id == name_input_id:
                    # ===============
                    # Updated text: PLAYER NAME
                    # ===============
                    on_update_name(self._lib.get_elem_text(name_input_id))

        # ===============
        # RED PANEL
        # ===============

        def on_update_red_player_type(new_type: _PlayerType) -> None:
            """
            Callback for when red player type is updated.

            Args:
                new_type (_PlayerType): new player type
            """
            self._state.red_type = new_type

        def on_update_red_name(new_name: str) -> None:
            """
            Callback for when red player name is updated.

            Args:
                new_name (str): new name
            """
            self._state.red_name = new_name

        def on_update_red_bot_difficulty(new_difficulty: _BotLevel) -> None:
            """
            Callback for when red bot difficulty level is updated.

            Args:
                new_difficulty (_BotLevel): new difficulty level
            """
            self._state.red_bot_level = new_difficulty

        process_panel_events(
            initial_player_type=self._state.red_type,
            player_type_dropdown_id=_SetupElems.RED_TYPE_DROPDOWN,
            on_update_player_type=on_update_red_player_type,
            name_input_id=_SetupElems.RED_NAME_TEXTINPUT,
            on_update_name=on_update_red_name,
            initial_bot_difficulty=self._state.red_bot_level,
            bot_difficulty_dropdown_id=_SetupElems.RED_BOT_DIFFICULTY_DROPDOWN,
            on_update_bot_difficulty=on_update_red_bot_difficulty
        )

        # ===============
        # BLACK PANEL
        # ===============

        def on_update_black_player_type(new_type: _PlayerType) -> None:
            """
            Callback for when black player type is updated.

            Args:
                new_type (_PlayerType): new player type
            """
            self._state.black_type = new_type

        def on_update_black_name(new_name: str) -> None:
            """
            Callback for when black player name is updated.

            Args:
                new_name (str): new name
            """
            self._state.black_name = new_name

        def on_update_black_bot_difficulty(new_difficulty: _BotLevel) -> None:
            """
            Callback for when black bot difficulty level is updated.

            Args:
                new_difficulty (_BotLevel): new difficulty level
            """
            self._state.black_bot_level = new_difficulty

        process_panel_events(
            initial_player_type=self._state.black_type,
            player_type_dropdown_id=_SetupElems.BLACK_TYPE_DROPDOWN,
            on_update_player_type=on_update_black_player_type,
            name_input_id=_SetupElems.BLACK_NAME_TEXTINPUT,
            on_update_name=on_update_black_name,
            initial_bot_difficulty=self._state.black_bot_level,
            bot_difficulty_dropdown_id=
            _SetupElems.BLACK_BOT_DIFFICULTY_DROPDOWN,
            on_update_bot_difficulty=on_update_black_bot_difficulty
        )

        # Enable/disable 'start game' button, depending on whether game
        # is set up correctly.
        self._validate_game_setup()

    @staticmethod
    def _rebuild_when_ready(can_user_move: Union[bool, None] = None) -> None:
        """
        Rebuild the PyGame UI at the next drawing opportunity.

        Args:
            can_user_move (Union[bool, None]): whether the user is allowed to
                interact with move UI after rebuild

        Returns:
            None
        """
        if can_user_move is None:
            pygame.event.post(_GeneralEvents.REBUILD)
        elif can_user_move:
            pygame.event.post(_GeneralEvents.REBUILD_ENABLE_MOVE)
        else:
            pygame.event.post(_GeneralEvents.REBUILD_DISABLE_MOVE)

    def _disable_move_elems(self) -> None:
        """
        Disable all elements that the user interacts with to move pieces.

        Returns:
            None
        """
        self._lib.disable_elem(
            _GameElems.SELECTED_PIECE_DROPDOWN)
        self._lib.disable_elem(
            _GameElems.DESTINATION_DROPDOWN)
        self._lib.disable_elem(
            _GameElems.SUBMIT_MOVE_BUTTON)

    def _enable_move_elems(self) -> None:
        """
        Enable all elements that the user interacts with to move pieces.

        Returns:
            None
        """
        self._lib.enable_elem(
            _GameElems.SELECTED_PIECE_DROPDOWN)
        self._lib.enable_elem(
            _GameElems.DESTINATION_DROPDOWN)
        self._lib.enable_elem(
            _GameElems.SUBMIT_MOVE_BUTTON)

    def _complete_bot_moves(self, moves: List[Move]) -> None:
        """
        Complete a series of moves for the currently playing bot.

        While the bot's moves are ongoing, the user-facing move elements are
        disabled.

        Returns:
            None
        """
        move, *remaining_moves = moves

        def visual_delay() -> float:
            """
            Generates a random number of seconds for a visual delay,
            between 0.4 and 0.6 (inclusive).

            Returns:
                float: delay in seconds
            """
            return max(random.random() * 0.6, 0.4)

        def bot_execute_move() -> None:
            """
            Bot executes their move.

            Returns:
                None
            """
            self._execute_move()  # toggles player color if end of turn

            if remaining_moves:
                # Rebuild UI
                self._rebuild_when_ready(can_user_move=False)

                # Complete remaining moves for currently playing bot
                self._complete_bot_moves(remaining_moves)
            else:
                # If next player is also a bot, auto-complete their moves, too
                if not self._attempt_start_bot_turn():
                    self._rebuild_when_ready(can_user_move=True)

        def bot_choose_dest() -> None:
            """
            Bot selects their move destination.

            Returns:
                None
            """
            self._state.dest_pos = move.get_new_position()
            self._rebuild_when_ready(can_user_move=False)

            threading.Timer(visual_delay(), bot_execute_move).start()

        def bot_choose_start_pos() -> None:
            """
            Bot selects their move start position.

            Returns:
                None
            """
            self._state.start_pos = move.get_current_position()
            self._rebuild_when_ready(can_user_move=False)

            threading.Timer(visual_delay(), bot_choose_dest).start()

        # Set up bot's turn by disabling move elements for the user.
        self._rebuild_when_ready(can_user_move=False)

        threading.Timer(visual_delay(), bot_choose_start_pos).start()

    def _execute_move(self) -> None:
        """
        Execute the currently selected move.

        Returns:
            None
        """
        move_result = self._state.board.complete_move(
            self._state.get_selected_move()
        )
        if not move_result:
            # End of turn for current player.
            # Switch to other player.
            self._state.toggle_color()

        # Update the move options
        self._state.update_move_options()

    def _attempt_start_bot_turn(self) -> bool:
        """
        If the current player is a bot, autoplay their sequence of moves.

        Only call at the start of the player's turn.

        Returns:
            bool: whether started bot turn
        """
        if self._state.is_currently_bot():
            # Get random or smart bot moves,
            # according to player bot level
            if self._state.current_bot_level() == _BotLevel.RANDOM:
                bot_moves = RandomBot(
                    own_color=self._state.current_color,
                    checkersboard=self._state.board
                ).choose_move_list()
            else:
                bot_moves = SmartBot(
                    own_color=self._state.current_color,
                    checkersboard=self._state.board,
                    level=self._state.current_bot_smart_level()
                ).choose_move_list()

            # Complete all the bot's moves
            self._complete_bot_moves(bot_moves)

            # Did start bot turn
            return True

        # Did not start bot turn
        return False

    def _submit_move_button(self) -> None:
        """
        User submits the currently selected move.

        Returns:
            None
        """
        # Button pressed means HUMAN just played.
        # Execute the move.
        self._execute_move()

        # Rebuild the game interface
        self._rebuild_ui()

        # Current player is bot? -> compute and make moves automatically
        self._attempt_start_bot_turn()

    def _process_game_events(self, event: "Event") -> None:
        """
        Process user interactions events for the Game screen.

        Args:
            event (Event): PyGame event
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_object_id == _GameElems.SUBMIT_MOVE_BUTTON:
                # ===============
                # Clicked: SUBMIT MOVE BUTTON
                # ===============
                self._submit_move_button()
            elif event.ui_object_id == _GameElems.MENU_BUTTON:
                # ===============
                # Clicked: MENU BUTTON
                # ===============
                print("clicked: menu button")
                # TODO: implement menu window

        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_object_id == _GameElems.SELECTED_PIECE_DROPDOWN:
                # ===============
                # Selection: SELECTED PIECE DROPDOWN
                # ===============
                selection = self._lib.get_elem_selection(
                    _GameElems.SELECTED_PIECE_DROPDOWN)
                selected_pos = _AppState.grid_position_from_string(selection)
                if selected_pos != \
                        self._state.start_pos:
                    # ===============
                    # Updated selection: MOVE START POSITION
                    # ===============
                    self._state.start_pos = selected_pos
                    self._rebuild_ui()
            elif event.ui_object_id == _GameElems.DESTINATION_DROPDOWN:
                # ===============
                # Selection: DESTINATION DROPDOWN
                # ===============
                selection = self._lib.get_elem_selection(
                    _GameElems.DESTINATION_DROPDOWN)
                selected_pos = _AppState.grid_position_from_string(selection)
                if selected_pos != \
                        self._state.dest_pos:
                    # ===============
                    # Updated selection: MOVE DESTINATION POSITION
                    # ===============
                    self._state.dest_pos = selected_pos
                    self._rebuild_ui()

        elif event.type == pygame.MOUSEBUTTONUP:
            if not self._state.is_currently_bot() and \
                    self._lib.get_elem(_GameElems.BOARD).relative_rect \
                        .collidepoint(event.pos):
                # ===============
                # Clicked: CHECKERS BOARD
                # Conditions: [is not bot]
                # ===============

                # Check if clicked on either:
                # - a movable checkers piece, or
                # - a valid destination square.
                for click_pos in itertools.product(
                        range(self._state.board_side_num),
                        range(self._state.board_side_num)):
                    # Get board square element ID
                    square_id = self._board_square_id(click_pos)

                    # Check if the cursor clicked on this board square
                    if self._lib.get_elem(square_id) \
                            .relative_rect.collidepoint(event.pos):
                        # ===============
                        # Clicked: BOARD SQUARE
                        # ===============
                        if click_pos in self._state \
                                .get_start_piece_positions_set():
                            # Board square contains a valid move start piece
                            self._state.start_pos = click_pos
                            self._rebuild_ui()

                            break  # stop searching for valid board click
                        elif click_pos in self._state \
                                .get_dest_piece_positions_set():
                            # Board square is a valid move destination
                            self._state.dest_pos = click_pos
                            self._rebuild_ui()

                            break  # stop searching for valid board click

    @lru_cache(maxsize=1)
    def _responsive_assets_setup(self) -> None:
        """
        Set up responsive PyGame-GUI asset sizing. Throwaway method that is
        ignored after being called the first time.

        Returns:
            None
        """
        self._update_responsive_assets()

    def _process_events(self) -> None:
        """
        Process user interaction events. This is the planning stage for
        painting.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Quit the app
                self._state.is_alive = False
                return

            # Inform the PyGame-GUI UIManager of events
            # (e.g. updating button hover state)
            self._ui_manager.process_events(event)

            # Process events for the current screen
            if self._get_current_screen() == _Screens.SETUP:
                self._process_setup_events(event)
            elif self._get_current_screen() == _Screens.GAME:
                self._process_game_events(event)

            # Custom events
            if event.type == pygame.USEREVENT:
                if event.dict.get(_GeneralEvents.PARAM_NAME, None) == \
                        _GeneralEvents.NAME_REBUILD:
                    # ===============
                    # REBUILD USER INTERFACE
                    # ===============
                    self._rebuild_ui()
                    if event.dict.get(_GeneralEvents.PARAM_DISABLE_MOVE, False):
                        # ===============
                        # Rebuild option: DISABLE MOVE ELEMENTS
                        # ===============
                        self._disable_move_elems()
                    elif event.dict.get(
                            _GeneralEvents.PARAM_ENABLE_MOVE, False):
                        # ===============
                        # Rebuild option: ENABLE MOVE ELEMENTS
                        # ===============
                        self._enable_move_elems()

        # If this is the first event loop, set up responsive assets
        self._responsive_assets_setup()

        # In every loop, check whether the window has been resized
        self._check_window_dimensions_changed()

    def run(self) -> None:
        """
        Start the app in a GUI window.
        """
        while self._state.is_alive:
            # Check for user interaction
            self._process_events()

            # Update UI elements in memory
            time_delta = self._render_clock.tick() / 1000.0
            self._ui_manager.update(time_delta)

            # Paint all changes
            self._window_surface.blit(self._bg_surface, (0, 0))
            self._ui_manager.draw_ui(self._window_surface)

            # Update PyGame display
            pygame.display.update()


if __name__ == "__main__":
    app = GuiApp(
        window_options=WindowOptions(
            min_dimensions=Dimensions(800, 600)
        )
    )
    app.run()
