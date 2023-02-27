"""
This module contains a generic Checkers-like board game class as well as a
Checkers specific subclass.
"""

from typing import Dict, List, Tuple, Union

from utils.logic.aux_utils import Move, Piece, PieceColor, Position


# ===============
# Board Class
# ===============


class Board:
    """
    This class represents a generic game board with support for two players.

    Positions on the board are represented from (0, 0) in the top left corner
    increasing down and to the right.
    """

    def __init__(self, height: int,
                 width: Union[int, None] = None,
                 colors: Tuple[PieceColor, ...] = (PieceColor.BLACK,
                                                   PieceColor.RED)) -> None:
        """
        Creates a new game board.

        Args:
            height (int): the height of the board or other size metric. The 
                implementing subclass will ultimately determine the meaning and
                usage of this argument.
            width (int or None): the width of the board. The implementing
                subclass will ultimately determine the meaning and usage of this
                argument.
            colors (Tuple of PieceColor): the colors of the pieces on the board
        """
        # Dictionary of all uncaptured pieces and their positions
        self._pieces: Dict[Position, Piece] = self._gen_pieces(height, width)

        # Each player's pieces that have been captured by the other player
        self._captured: Dict[PieceColor, List[Piece]] = {
            color: [] for color in colors
        }

        # Implementing classes MUST set these attributes to integers
        self._height = height
        self._width = width if (width is not None) else height

    def get_board_pieces(self) -> List[Piece]:
        """
        Getter method that returns a list of all pieces on the board.

        Args:
            None

        Returns:
            List[Piece]: list of pieces on the board
        """
        return list(self._pieces.values())

    def get_captured_pieces(self) -> List[Piece]:
        """
        Getter method that returns a list of all captured pieces.

        Args:
            None

        Returns:
            List[Piece]: list of all captured pieces
        """
        all_pieces = []

        for pieces in self._captured.items():
            all_pieces.extend(pieces)

        return all_pieces

    def get_color_captured_pieces(self, color: PieceColor) -> List[Piece]:
        """
        Getter method that returns a list of captured pieces for a given player
        color.

        This method returns for a color, the pieces of that color that were
        captured by the other player. It returns a list of pieces of the same
        color that was provided.

        Args:
            color (PieceColor): the player being queried

        Returns:
            List[Piece]: list of captured pieces for a color"""
        return self._captured[color]

    def get_color_avail_pieces(self, color: PieceColor) -> List[Piece]:
        """
        Getter that returns a list of pieces still on the board for a given
        player color.

        Args:
            color (PieceColor): the player being queried

        Returns:
            List[Piece]: list of pieces still on the board for that color
        """
        filtered_pieces: List[Piece] = []

        # Sort each piece
        for piece in self._pieces.values():
            if piece.get_color() == color:
                filtered_pieces.append(piece)

        return filtered_pieces

    def get_board_height(self) -> int:
        """
        Getter method for the height of the board

        Args:
            None

        Returns:
            int: the height of the board
        """
        return self._height

    def get_board_width(self) -> int:
        """
        Getter method for the width of the board

        Args:
            None

        Returns:
            int: the width of the board
        """
        return self._width

    def complete_move(self, move: Move) -> List[Move]:
        """
        Method for completing a move. First validates the move using
        self.validate_move() which validates whether the move is even feasible,
        or, if overloaded by a subclass, custom validation.

        Args:
            move (Move): the move to make

        Returns:
            List[Move]: An empty list of follow-up moves. Implementing 
                subclasses ultimately determine meaning and usage of this 
                return. 

        Raises:
            ValueError: If the move is not valid.
        """
        # Make sure this is a valid move
        if not self.validate_move(move):
            raise ValueError(f"Move {repr(move)} is not a valid move.")

        # Process Move - "moving" the piece
        curr_pos = move.get_current_position()
        new_pos = move.get_new_position()

        self._pieces[curr_pos].set_position(new_pos)  # "Move" the piece

        # In self._pieces, replace old position with new position
        self._pieces[new_pos] = self._pieces.pop(curr_pos)

        return []  # Return nothing

    def undo_move(self, move: Move) -> None:
        """
        Abstract method for undoing a given move.

        Args:
            move (Move): the move that is to be undone

        Returns:
            None
        """
        raise NotImplementedError

    def validate_move(self, move: Move) -> bool:
        """
        Validates a potential move. Only checks if the piece exists, is on the
        board, and if the new position is valid and not taken by another piece.

        Args:
            move (Move): the move to validate

        Returns:
            bool: True if the move is valid otherwise False
        """
        # Validate type
        if not isinstance(move, Move):
            return False

        # Make sure move contains a valid piece and starting position
        if move.get_piece() not in self.get_board_pieces():
            return False

        # Make sure that new position is valid and not taken
        new_pos = move.get_new_position()
        if (not self._validate_position(new_pos)) or (new_pos in self._pieces):
            return False

        return True

    def _validate_position(self, pos: Position) -> bool:
        """
        Helper method for checking if a provided position is on the board.

        Args:
            pos (Position): the position to validate

        Returns:
            bool: True if valid otherwise false
        """
        pos_col, pos_row = pos

        # Check if on the board
        if (0 <= pos_col < self._width) and (0 <= pos_row < self._height):
            return True

        return False

    def _gen_pieces(self, height: Union[int, None] = None,
                    width: Union[int, None] = None) -> Dict[Position, Piece]:
        """
        Abstract method for the generation of the pieces. Children of this class
        must implement this method according to the rules of their game.

        Args:
            height (int or None): the height of the board. The implementing
                subclass will ultimately determine the meaning and usage of this
                argument.
            width (int or None): the width of the board. The implementing
                subclass will ultimately determine the meaning and usage of this
                argument.

        Returns:
            Dict[Position, Piece]: Dictionary containing piece locations and
                                   pieces for both players
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """
        Returns a string representation of the board only. Assumes that the
        board space coloring is checkers-like.

        Args:
            None

        Returns:
            str: String representation of the board
        """
        board = '_' * ((self._width + 1) * 2) + '\n'

        for row in range(self._height):
            board += '|'

            # Black spaces alternate between starting in column 0 if odd or in
            # column 1 if even
            black_space_offset = 1 if (row % 2 == 0) else 0

            # Loop thru columns
            for col in range(self._width):
                position = (col, row)

                # Check for a piece in this position
                if position in self._pieces:
                    board += str(self._pieces[position]) + ' '
                    continue

                # No piece, fill with correct "color"

                # Should this be a black square?
                if (col % 2) == black_space_offset:
                    board += 'x '
                else:
                    board += '  '

            board += '|\n'

        board += '‾' * ((self._width + 1) * 2)

        return board

    def __repr__(self) -> str:
        """
        Returns the representation of the board. Intended for debugging.
        Includes captured pieces.

        Assumes board space coloring is checkers-like.

        Args:
            None

        Returns:
            str: representation of the board
        """
        uncaptured_reprs = '\n\nUncaptured pieces:\n'
        for piece in self.get_board_pieces():
            uncaptured_reprs += repr(piece) + '\n'

        captured_reprs = '\nCaptured pieces:\n'
        for piece in self.get_captured_pieces():
            captured_reprs += repr(piece) + '\n'

        return self.__str__() + uncaptured_reprs + captured_reprs
