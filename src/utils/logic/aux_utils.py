"""
This module contains auxiliary classes for representing Pieces on a board and
various moves for Checkers.
"""

from enum import Enum
from typing import Union, Tuple


# ===============
# Type Aliases
# ===============

Position = Tuple[int, int]


# ===============
# ENUMS
# ===============


class PieceColor(Enum):
    """
    An enumeration for the internal representation of a piece's color.
    """

    RED = 'r'
    BLACK = 'b'


# ===============
# DATA CLASSES
# ===============


class GenericPiece:
    """
    Represents a generic piece for a generic board game.
    """

    def __init__(self, pos: Position, color: PieceColor) -> None:
        """
        Constructor for a piece.

        Args:
            pos (Tuple[int, int]): the position of the piece on the board
            color (PieceColor): The color of the piece
        """
        self._x: int
        self._y: int

        self.set_position(pos)  # initialize piece position
        self._color = color  # the piece's color

    def get_position(self) -> Position:
        """
        Getter function that returns the piece's position.

        Args:
            None

        Returns:
            Position of the piece
        """
        return (self._x, self._y)

    def set_position(self, new_pos: Position) -> None:
        """
        Setter for the piece's position. If an invalid position is provided,
        ValueError will be raised.

        Args:
            new_pos (Position): the new position of the piece

        Returns:
            None

        Raises:
            ValueError if invalid position is provided.
        """
        # Check for invalid position
        if new_pos[0] < 0 or new_pos[1] < 0:
            raise ValueError(f"Argument new_pos {str(new_pos)} is invalid.")

        self._x, self._y = new_pos

    def set_captured(self) -> None:
        """
        Sets the piece's to captured. This cannot be undone, please make sure
        you know what you're doing.

        Args:
            None

        Returns:
            None
        """
        self._x = -1
        self._y = -1

    def is_captured(self) -> bool:
        """
        Returns whether the piece is captured.

        Args:
            None

        Returns:
            True if captured otherwise False
        """
        return (self._x == -1) and (self._y == -1)

    def get_color(self) -> PieceColor:
        """
        Getter function that returns the piece's color.

        Args:
            None

        Returns:
            The color of the piece
        """
        return self._color

    def __str__(self) -> str:
        """
        Returns a string representation of the piece. Returns the value of the
        color of the piece (PieceColor.value).

        For example:
        Red: 'r'
        Black: 'b'

        Args:
            None

        Returns:
            str: String representation of the piece
        """
        return self._color.value

    def __repr__(self) -> str:
        """
        Returns the representation of this piece. Meant for debugging.

        Args:
            None

        Returns:
            str: Debug representation of the piece
        """
        args = [
            f'({self._x}, {self._y})'
        ]

        if self._color in PieceColor:
            args.append(f'{__name__}.{self._color}')
        else:
            args.append(repr(self._color))

        return f"{__name__}.GenericPiece({', '.join(args)})"

    def __eq__(self, other: object) -> bool:
        """
        Implements the equality operator for type GenericPiece

        Args:
           other (object): the object to be compared to

        Returns:
            bool: True if equal, False if not
        """
        if not isinstance(other, GenericPiece):
            return False

        return (self._color == other._color
                and self._x == other._x
                and self._y == other._y)


class Piece(GenericPiece):
    """
    Represents a checkers piece.
    """

    def __init__(self, pos: Position, color: PieceColor,
                 king: bool = False) -> None:
        """
        Constructor for a piece.

        Args:
            pos (Tuple[int, int]): the position of the piece on the board
            color (PieceColor): The color of the piece
            king (bool): Is this a king? (Intended for debug scenarios)
        """
        super().__init__(pos, color)

        self._king = king  # is this piece a king?

    def is_king(self) -> bool:
        """
        Getter function that returns whether this piece is a king.

        Args:
            None

        Returns:
            True if this is a king otherwise False
        """
        return self._king

    def to_king(self) -> None:
        """
        Update the piece to a king (aka 'kinging').

        Args:
            None

        Returns:
            None
        """
        self._king = True

    def unking(self) -> None:
        """
        Unset the king state of the piece.

        Args:
            None

        Returns:
            None
        """
        self._king = False

    def __str__(self) -> str:
        """
        Returns a string representation of the piece. Returns one character
        which is uppercase if king otherwise lowercase.

        Red: 'r' or 'R'
        Black: 'b' or 'B'

        Args:
            None

        Returns:
            str: String representation of the piece
        """
        if self._king:
            return super().__str__().upper()

        return super().__str__()

    def __repr__(self) -> str:
        """
        Returns the representation of this piece. Meant for debugging.

        Args:
            None

        Returns:
            str: Debug representation of the piece
        """
        args = [
            f'({self._x}, {self._y})'
        ]

        if self._color in PieceColor:
            args.append(f'{__name__}.{self._color}')
        else:
            args.append(repr(self._color))

        if self._king:
            args.append(repr(self._king))

        return f"{__name__}.Piece({', '.join(args)})"

    def __eq__(self, other: object) -> bool:
        """
        Implements the equality operator for type Piece

        Args:
           other (object): the object to be compared to

        Returns:
            bool: True if equal, False if not
        """
        if not super().__eq__(other):
            return False

        if not isinstance(other, Piece):
            return False

        return self._king == other._king


class Move:
    """
    Represents a move that can be done by a piece or a resignation/draw offer.
    """

    def __init__(self, piece: Union[Piece, None], new_pos: Position,
                 curr_pos: Union[Position, None] = None) -> None:
        """
        Creates a new move object.

        Stores the piece to be moved, the new position after the move, and the
        current position of the piece.

        The current position will be either from:
         1) curr_pos (if provided)
         2) The piece itself (if provided)
         3) (-1, -1), but will raise an error when getting (see method below)

        Args:
            piece (Piece or None): the piece this move belongs to
            new_pos (Position): the new position after the move
            curr_pos (Position or None): optional parameter for the current
                                         position of the piece
        """
        self._piece = piece  # the piece to be moved

        # The new position. If it is (-1, -1) then it is not a "move" per se
        self._new_x, self._new_y = new_pos

        # Handle current piece location as specified in docstring
        if curr_pos:
            self._curr_x, self._curr_y = curr_pos
        elif piece:
            self._curr_x, self._curr_y = piece.get_position()
        else:
            self._curr_x, self._curr_y = (-1, -1)

    def get_new_position(self, _strict: bool = True) -> Position:
        """
        Getter for the new position of the piece after the move. Raises
        RuntimeError if the new position stored is not valid (greater than
        (0, 0)).

        Args:
            _strict (bool): private argument to disable position validity check

        Returns:
            Position of the piece after the move

        Raises:
            RuntimeError: if the new position is not greater than (0, 0)
        """
        if _strict and ((self._new_x < 0) or (self._new_y < 0)):
            pos = (self._new_x, self._new_y)
            raise RuntimeError(f"Move's new position {pos} is invalid.")

        return (self._new_x, self._new_y)

    def get_piece(self) -> Piece:
        """
        Getter for the piece that will move. If there is no piece associated
        with this move then a RuntimeError will be raised.

        Args:
            None

        Returns:
            Piece to be moved

        Raises:
            RuntimeError: if this move has no piece
        """
        if self._piece is None:
            raise RuntimeError("Move has no piece!")

        return self._piece

    def is_kinging(self, board_length: int) -> bool:
        """
        Method that determines whether this move will result in the kinging of
        this piece. Implemented exclusively for the bot, may not work if not
        used by the bot.

        Args:
            board_length (int): the length of the board

        Returns:
            bool: True if this move will result in a kinging else False
        """
        if self.get_piece().is_king():
            return False

        baseline = {PieceColor.RED: 0, PieceColor.BLACK: board_length - 1}
        if baseline[self.get_piece().get_color()] == self.get_new_position()[1]:
            return True

        return False

    def get_current_position(self, _strict: bool = True) -> Position:
        """
        Getter for the current position of the piece that will be moved. If
        there is no position stored or if the position is invalid (captured)
        then this method will raise RuntimeError.

        Does not update the current position if the current position has
        changed in the piece itself.

        Args:
            _strict (bool): private argument to disable position validity check

        Returns:
            Position: current position of the piece

        Raises:
            RuntimeError: if the position is invalid
        """
        # Check for invalid position
        if _strict and (self._curr_x < 0 or self._curr_y < 0):
            raise ValueError("Move's current position is invalid.")

        return (self._curr_x, self._curr_y)

    def __eq__(self, other: object) -> bool:
        """
        Implements the equality operator for type Move

        Args:
           other (object): the object to be compared to

        Returns:
            bool: True if equal, False if not
        """
        if not isinstance(other, Move):
            return False

        return (self._piece == other._piece
                and self._new_x == other._new_x
                and self._new_y == other._new_y)

    def __str__(self) -> str:
        """
        Returns a string representation of the move. Raises RuntimeError if no
        Piece is associated with this move or if the new position is invalid.

        Args:
            None

        Returns:
            str: String representation of the move

        Raises:
            RuntimeError: if this move has no piece
            RuntimeError: if the new position is not greater than (0, 0)
        """
        if self._piece is None:
            raise RuntimeError("Move has no piece!")

        piece = str(self._piece)
        old_loc = self.get_current_position()
        new_loc = self.get_new_position()

        return f'Move: {piece} from {old_loc} to {new_loc}'

    def __repr__(self) -> str:
        """
        Returns the representation of the move. Intended for debugging.

        Args:
            None

        Returns:
            str: representation of the move
        """
        args = [
            repr(self._piece),
            str(self.get_new_position(False)),
            str(self.get_current_position(False))
        ]

        return f'{__name__}.Move({", ".join(args)})'


class Jump(Move):
    """
    Represents a jump that can done by a piece. Includes the opponent's piece
    that will be captured if the jump is completed.
    """

    def __init__(self,
                 piece: Piece,
                 new_pos: Position,
                 opponent_piece: Piece,
                 curr_pos: Union[Position, None] = None) -> None:
        """
        Creates a new jump object.

        Args:
            piece (Piece): the piece this move belongs to
            new_pos (Position): the new position after the jump
            opponent_piece (Piece): the piece that will be captured
        """
        super().__init__(piece, new_pos, curr_pos)

        # The Piece that would be captured during the move
        self._opponent_piece = opponent_piece

    def get_captured_piece(self) -> Piece:
        """
        Getter method that returns the piece that would be captured after the
        jump.

        Args:
            None

        Returns:
            The Piece that would be captured during the move
        """
        return self._opponent_piece

    def __eq__(self, other: object) -> bool:
        """
        Implements the equality operator for type Jump

        Args:
            other (object): the object to be compared to

        Returns:
            bool: True if equal, False if not
        """
        if not super().__eq__(other):
            return False

        if not isinstance(other, Jump):
            return False

        return self._opponent_piece == other._opponent_piece

    def __str__(self) -> str:
        """
        Returns a string representation of the move

        Args:
            None

        Returns:
            str: String representation of the move
        """
        cap_loc = ' ' + str(self.get_captured_piece().get_position())
        addl_txt = f', capturing {str(self.get_captured_piece())} at' + cap_loc

        return "Jump" + super().__str__()[4:] + addl_txt

    def __repr__(self) -> str:
        """
        Returns the representation of the jump. Intended for debugging.

        Args:
            None

        Returns:
            str: representation of the jump
        """
        args = [
            repr(self._piece),
            str(self.get_new_position(False)),
            repr(self._opponent_piece),
            str(self.get_current_position(False))
        ]

        return f'{__name__}.Jump({", ".join(args)})'


class Resignation(Move):
    """
    Represents a resignation by one player. Upon resignation, an instance of
    this class should be created by the GUI/TUI and be "played".
    """

    def __init__(self, color: PieceColor) -> None:
        """
        Create a new resignation object. The color of the player that is
        resigning must be provided.

        Args:
            color (PieceColor): the color of the player that is resigning
        """
        super().__init__(None, (-1, -1))

        self._resigning_color = color

    def get_new_position(self, _strict: bool = True) -> Position:
        """
        Overrides the parent Piece getter function. Raises TypeError.

        Args:
            _strict (bool): unused as this method only errors

        Returns:
            None

        Raises:
            TypeError, as this class does not contain valid values to get
        """
        raise TypeError

    def get_piece(self) -> Piece:
        """
        Overrides the parent Piece getter function. Raises TypeError.

        Args:
            None

        Returns:
            None

        Raises:
            TypeError, as this class does not contain valid values to get
        """
        raise TypeError

    def get_current_position(self, _strict: bool = True) -> None:
        """
        Overrides the parent Piece getter function. Raises TypeError.

        Args:
            _strict (bool): unused argument as this only errors

        Returns:
            None

        Raises:
            TypeError, as this class does not contain valid values to get
        """
        raise TypeError

    def get_resigning_color(self) -> PieceColor:
        """
        Getter for the color of the player that is resigning.

        Args:
            None

        Returns:
            PieceColor: the color of the player that is resigning.
        """
        return self._resigning_color

    def __eq__(self, other: object) -> bool:
        """
        Implements the equality operator for type Resignation

        Args:
            other (object): the object to be compared to

        Returns:
            bool: True if equal, False if not
        """
        if not isinstance(other, Resignation):
            return False

        return self._resigning_color == other._resigning_color

    def __str__(self) -> str:
        """
        Returns a string representation of the resignation

        Args:
            None

        Returns:
            str: String representation of the move
        """
        if self._resigning_color == PieceColor.BLACK:
            color = "black"
        elif self._resigning_color == PieceColor.RED:
            color = "red"
        else:
            raise RuntimeError(f"Resignations's color \
({repr(self._resigning_color)}) was invalid")

        return f'Resignation: {color} resigns'

    def __repr__(self) -> str:
        """
        Returns the representation of the resignation. Intended for debugging.

        Args:
            None

        Returns:
            str: representation of the resignation
        """
        return f'{__name__}.Resignation({str(self._resigning_color)})'


class DrawOffer(Move):
    """
    Represents an offer/acceptance of a draw.

    When offering a draw, the GUI/TUI must create an instance of this class and
    "play" it along with another "regular" move (move/jump).

    When a draw is offered, the player will receive it when getting all valid
    moves for that player. The color stored in that DrawOffer will be the
    recipient player's color, NOT the offering player's color.

    To accept a draw, the GUI/TUI must "play" the draw request provided when
    getting the player's move. To reject, play any other move.
    """

    def __init__(self, offering_color: PieceColor) -> None:
        """
        Create a new draw offer. The offering player's color is stored.

        Args:
            offering_color (PieceColor): the color of player that is offering
                                         the draw
        """
        super().__init__(None, (-1, -1))

        # The color of the player offering the draw
        self._offering_color = offering_color

    def get_new_position(self, _strict: bool = True) -> Position:
        """
        Overrides the parent Piece getter function. Raises TypeError.

        Args:
            _strict (bool): unused argument as this only errors

        Returns:
            None

        Raises:
            TypeError, as this class does not contain valid values to get
        """
        raise TypeError

    def get_piece(self) -> Piece:
        """
        Overrides the parent Piece getter function. Raises TypeError.

        Args:
            None

        Returns:
            None

        Raises:
            TypeError, as this class does not contain valid values to get
        """
        raise TypeError

    def get_current_position(self, _strict: bool = True) -> None:
        """
        Overrides the parent Piece getter function. Raises TypeError.

        Args:
            _strict (bool): unused argument as this only errors

        Returns:
            None

        Raises:
            TypeError, as this class does not contain valid values to get
        """
        raise TypeError

    def get_offering_color(self) -> PieceColor:
        """
        Getter to return the color that is offering the draw

        Args:
            None

        Returns:
            PieceColor of the player offering the draw
        """
        return self._offering_color

    def __eq__(self, other: object) -> bool:
        """
        Implements the equality operator for type DrawOffer

        Args:
            other (object): the object to be compared to

        Returns:
            bool: True if equal, False if not
        """
        if not isinstance(other, DrawOffer):
            return False

        return self._offering_color == other._offering_color

    def __str__(self) -> str:
        """
        Returns a string representation of the draw offer

        Args:
            None

        Returns:
            str: String representation of the move
        """
        if self._offering_color == PieceColor.BLACK:
            color = "black"
        elif self._offering_color == PieceColor.RED:
            color = "red"
        else:
            raise RuntimeError(f"DrawOffer's color \
({repr(self._offering_color)}) was invalid")

        return f'Draw offer: {color} offers a draw'

    def __repr__(self) -> str:
        """
        Returns the representation of the offer. Intended for debugging.

        Args:
            None

        Returns:
            str: representation of the offer
        """
        return f'{__name__}.DrawOffer({str(self._offering_color)})'
