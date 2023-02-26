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

    def undo_move(self, move: Move) -> None:
        """
        Abstract method for undoing a given move.

        Args:
            move (Move): the move that is to be undone

        Returns:
            None
        """
        raise NotImplementedError

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
