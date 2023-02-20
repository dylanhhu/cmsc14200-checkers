"""
This file includes classes that will aid in implementing the board game
checkers with arbitrary board size. There is one main class that handles the
game logic with supporting classes for storing representations of moves and
pieces.


Examples:

1) Creating a board:

    board = CheckersBoard(8)


2) Checking if a given move is feasible:

    board = CheckersBoard(2)

    # For example only, this should be a proper move, ideally one that is
    # generated by CheckersBoard
    move = Move(...)

    validity = board.validate_move(move)


3) Getting valid moves for a piece on the board:

    board = CheckersBoard(2)
    piece = Piece(...)  # For example only, this should be a proper piece

    piece_moves = board.get_piece_moves(piece)


4) Getting all valid moves for a player:

    current_player = PieceColor.BLACK  # for example, could be either
    player_moves = board.get_player_moves(current_player)


5) Checking for a winner:

    game_status = board.get_game_state()

    if game_status == GameStatus.IN_PROGRESS:
        print("Game in progress")
    elif winner == GameStatus.RED_WINS:
        print("Red wins!")
    elif winner == GameStatus.BLACK_WINS:
        print("Black wins!")
    else:
        print("Draw!")
"""

from enum import Enum
from typing import Tuple, List, Dict, Union


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

    RED = 0
    BLACK = 1


class GameStatus(Enum):
    """
    An enumeration for the current game state.
    """
    # Same as PieceColor values
    RED_WINS = 0
    BLACK_WINS = 1

    # Other statuses
    IN_PROGRESS = 100
    DRAW = 101


# ===============
# DATA CLASSES
# ===============


class Piece:
    """
    Represents a piece on the board.
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

        self.set_position(pos)  # initialize piece position
        self._color = color  # the piece's color
        self._king = king  # is this piece a king?

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
        Update the piece to a king (aka 'kinging'). This can't be undone,
        please make sure you know what you're doing.

        Args:
            None

        Returns:
            None
        """
        self._king = True

    def __str__(self) -> str:
        """
        Returns a string representation of the piece. Returns one character
        which is uppercase if king otherwise lowercase. Raises RuntimeError if
        the Piece's color is invalid.

        Red: 'r' or 'R'
        Black: 'b' or 'B'

        Args:
            None

        Returns:
            str: String representation of the piece

        Raises:
            RuntimeError: if piece's color is invalid (not in PieceColor)
        """
        if self._king:
            if self._color == PieceColor.BLACK:
                return "B"
            elif self._color == PieceColor.RED:
                return "R"

            raise RuntimeError(f"Piece's color ({repr(self._color)}) was \
invalid")

        if self._color == PieceColor.BLACK:
            return "b"
        elif self._color == PieceColor.RED:
            return "r"

        raise RuntimeError(f"Piece's color ({repr(self._color)}) was invalid")

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
            args.append(f'checkers.{self._color}')
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
        if not isinstance(other, Piece):
            return False

        return (self._color == other._color
                and self._king == other._king
                and self._x == other._x
                and self._y == other._y)


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

    def get_new_position(self) -> Position:
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

    def get_current_position(self) -> None:
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

    When a draw is offered, the player will recieve it when getting all valid
    moves for that player.

    To accept a draw, the GUI/TUI must "play" the draw request. To reject,
    play any other move.
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

    def get_new_position(self) -> Position:
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

    def get_current_position(self) -> None:
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


# ===============
# GAME BOARD CLASS
# ===============


class CheckersBoard:
    """
    Represents a checkers game. Provides methods for obtaining valid moves,
    validating moves, and acting upon moves according to the rules of checkers.
    Stores the board state along with all pieces, captured or uncaptured.

    The board square grid begins with (0, 0), a light square, at the "top
    left", where the top rows will contain the black pieces and the bottom rows
    containing the red pieces.
    """

    def __init__(self, n: int) -> None:
        """
        Creates a new Checkers game.

        Args:
            n (int): the number of rows of pieces per player
        """
        self._n = n  # number of rows of pieces per player
        self._board_length = 2 * (n + 1)  # length of board sides

        # Dictionary of all uncaptured pieces and their positions
        self._pieces: Dict[Position, Piece] = self._generate_pieces(n)

        # Each player's pieces that have been captured by the other player
        self._captured: Dict[PieceColor, List[Piece]] = {
            PieceColor.BLACK: [],
            PieceColor.RED: []
        }

        # Represents an outstanding draw offer and acceptance
        self._draw_offer: Dict[PieceColor, bool] = {
            PieceColor.BLACK: False,
            PieceColor.RED: False
        }

        self._game_state = GameStatus.IN_PROGRESS  # the game state

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
        Getter method that reutrns a list of all captured pieces.

        Args:
            None

        Returns:
            List[Piece]: list of all captured pieces
        """
        return (self._captured[PieceColor.RED]
                + self._captured[PieceColor.BLACK])

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

        # Sort each piece into the two colors
        for piece in self._pieces.values():
            if piece.get_color() == color:
                filtered_pieces.append(piece)

        return filtered_pieces

    def get_board_width(self) -> int:
        """
        Getter method for the length of the board sides. 1-indexed.

        Args:
            None

        Returns:
            int: the length of the board sides"""

        return self._board_length

    def complete_move(self, move: Move,
                      draw_offer: Union[DrawOffer, None] = None) -> List[Jump]:
        """
        Complete a move with a piece.

        If the move is not valid, a ValueError is raised. This includes when
        a non-jumping move is attempted when a jump is available.

        Returns a list of possible subsequent jumps, if necessary, that follow
        the provided move. If this list is empty, the player's turn is over.

        If a move results in kinging, the player's turn is over and nothing
        is returned.

        If a resignation is provided, the player's turn is over
        and nothing is returned.

        To offer a draw, a regular move (move/jump) must be provided along with
        a DrawOffer.

        TODO: Clarify moving into a position with subsequent jumps:
              Do we return this list or not?

        Args:
            move (Move): move to make
            draw_offer (DrawOffer): optional argument for draw offers

        Returns:
            List[Jump]: list of subsequent jumps for current piece, if any

        Raises:
            ValueError: If the move is not valid
        """

        # Check if there is a draw_offer attached
        if draw_offer is not None:
            return self._handle_draw_offer(draw_offer)

        # Check if there were any outstanding draw offers not accepted
        if any(self._draw_offer.values()):
            self._reset_draw_offers()

        # This function would call self.get_piece_moves(jumps_only = True)
        # for the list of subsequent jumps
        raise NotImplementedError

    def get_piece_moves(self, piece: Piece,
                        jumps_only: bool = False) -> List[Move]:
        """
        Returns a list of possible moves (moves and jumps) for a piece. If
        jump(s) are possible, then only jumps will be returned.

        Args:
            piece (Piece): the piece being queried
            jumps_only (bool): only jumps or an empty list will be returned

        Returns:
            List[Move]: the list of moves (move(s) XOR jump(s)) for that piece
        """
        possible_moves: List[Move] = []
        possible_jumps: List[Move] = []

        curr_col, curr_row = piece.get_position()
        positions = {
            (curr_col - 1, curr_row - 1): (curr_col - 2, curr_row - 2),  # nw
            (curr_col + 1, curr_row - 1): (curr_col + 2, curr_row - 2),  # ne
            (curr_col + 1, curr_row + 1): (curr_col + 2, curr_row + 2),  # se
            (curr_col - 1, curr_row + 1): (curr_col - 2, curr_row + 2)   # sw
        }

        # Loop thru immediate positions
        for position in positions.keys():
            # Make sure position is inside the board
            if self._validate_position(position):
                # Check if there's a piece already in the position
                if (not jumps_only) and (position not in self._pieces):
                    # Free space and we're not looking for only jumps
                    possible_moves.append(Move(piece, position))
                    continue

                # There's a piece in this position, so we try to jump it by
                # checking if the jump location is valid and whether the jump
                # position is currently taken by another piece

                jump_position = positions[position]
                if (self._validate_position(jump_position)         # valid?
                        and (jump_position not in self._pieces)):  # taken?

                    # Make sure that we're not jumping our own pieces
                    if (self._pieces[position].get_color()
                            == piece.get_color()):
                        continue

                    # All clear to make the jump
                    captured_piece = self._pieces[position]

                    possible_jumps.append(Jump(piece,
                                               jump_position,
                                               captured_piece))

        return possible_jumps if possible_jumps else possible_moves

    def get_player_moves(self, color: PieceColor) -> List[Move]:
        """
        Returns a list of possible moves for a player's pieces. If this list is
        empty, the player is unable to make a move (and has lost the game).

        If there are any jumps possible, only jumps will be returned.

        If there is a draw offer from the other player, a DrawOffer "move"
        will be included.

        Args:
            color (PieceColor): the player being queried

        Returns:
            List[Move]: list of possible moves:
                        ((moves XOR jumps) OR DrawOffer)
        """
        possible_moves: List[Move] = []
        possible_jumps: List[Move] = []

        for piece in self.get_color_avail_pieces(color):
            piece_moves = self.get_piece_moves(piece)

            # Check if the piece is blocked to avoid further processing
            if not piece_moves:
                continue

            # Check if the piece can only jump
            if isinstance(piece_moves[0], Jump):
                possible_jumps.extend(piece_moves)
                continue

            # Otherwise, just add the moves to possible_moves
            possible_moves.extend(piece_moves)

        return possible_jumps if possible_jumps else possible_moves

    def validate_move(self, move: Move) -> bool:
        """
        Validates a potential move. If only moves provided by this class are
        attempted, then this function should never return False.

        Args:
            move (Move): the move to be validated

        Returns:
            bool: True if the move is valid, otherwise False
        """
        # Validate type
        if not isinstance(move, Move):
            return False

        # Make sure move contains a valid piece
        if move.get_piece() not in self.get_board_pieces():
            return False

        # Make sure that new position is valid; comparing by equality and by
        # whether they are the same object, see:
        # https://docs.python.org/3.8/reference/expressions.html#membership-test-details
        if move.get_new_position() not in self._pieces:
            return False

        # To be able to check for other jumps, we must get all moves
        player_moves = self.get_player_moves(move.get_piece().get_color())

        # Make sure that this move is a possible move for the player
        # Since we already have all the moves, we can just test for membership
        if move not in player_moves:
            return False

        # Make sure that there's not a Jump otherwise available
        # We're guaranteed that player_moves isn't empty here from last check
        if isinstance(move, Move) and isinstance(player_moves[0], Jump):
            return False

        # We are certain the move is valid!
        return True

    def get_game_state(self) -> GameStatus:
        """
        Returns the current game state. Checks for winning conditions before
        returning.

        Should be called before every player's turn.

        Args:
            None

        Returns:
            GameStatus: the game state
        """

        # Check if both colors agree to a draw
        if all(self._draw_offer.values()):
            return GameStatus.DRAW

        raise NotImplementedError

    def _generate_pieces(self, n: int) -> Dict[Position, Piece]:
        """
        Private method for setting up the pieces before the game begins.

        Args:
            n (int): number of rows of pieces per player

        Returns:
            Dict[Position, Piece]: Dictionary containing piece locations and
                                   pieces for both players
        """
        board_length = 2 * n + 1  # 0 indexed max value of row, col

        board: Dict[Position, Piece] = {}

        # Generate black's pieces, iterating forwards
        for row in range(0, n):
            # Each row of pieces alternates starting in column 0 if odd or in
            # column 1 if even
            offset = 1 if (row % 2 == 0) else 0

            for col in range(offset, board_length + offset, 2):
                position = (col, row)

                board[position] = Piece(position, PieceColor.BLACK)

        # Generate red's pieces, iterating backwards from the end of the board
        for row in range(board_length, board_length - n, -1):
            # Each row of pieces alternates starting in column 0 if odd or in
            # column 1 if even
            offset = 1 if (row % 2 == 0) else 0

            for col in range(offset, board_length + offset, 2):
                position = (col, row)

                board[position] = Piece(position, PieceColor.RED)

        return board

    def _handle_draw_offer(self, offer: DrawOffer) -> List:
        """
        Private method to handle draw offers. Intended to be called by
        complete_move().

        Args:
            offer (DrawOffer): the draw offer

        Returns:
            An empty list
        """
        offering_color = offer.get_offering_color()

        self._draw_offer[offering_color] = True

        return []

    def _reset_draw_offers(self) -> None:
        """
        Private method for resetting draw offers.

        Args:
            None

        Returns:
            None
        """
        self._draw_offer: Dict[PieceColor, bool] = {
            PieceColor.BLACK: False,
            PieceColor.RED: False
        }

    def _validate_position(self, pos: Position) -> bool:
        """
        Helper method for checking if a provided position is on the board.

        Args:
            pos (Position): the position to validate

        Returns:
            bool: True if valid otherwise false
        """
        pos_col, pos_row = pos

        # Check upper and left bounds
        if (pos_col < 0) or (pos_row < 0):
            return False

        # Check right and lower bounds
        if (pos_col >= self._board_length) or (pos_row >= self._board_length):
            return False

        return True

    def __str__(self) -> str:
        """
        Returns a string representation of the board only.

        Args:
            None

        Returns:
            str: String representation of the board
        """
        board_length = (self._n + 1) * 2  # max index of a board size plus one
        board = '_' * ((board_length + 1) * 2) + '\n'

        for row in range(board_length):
            board += '|'

            # Each row of pieces alternates starting in column 0 if odd or in
            # column 1 if even
            offset = 1 if (row % 2 == 0) else 0

            # If there's an offset, need to add blank space to front of line
            if offset:
                board += '  '

            # Only loop through columns that can have a piece
            for col in range(offset, board_length + offset, 2):
                position = (col, row)

                # Check for a piece in this position
                if position in self._pieces:
                    board += str(self._pieces[position]) + '   '
                    continue

                # Blank black square, so use some other character
                board += 'x   '

            # If offset, need to remove 2 spaces at end from the else above for
            # proper alignment of the trailing pipe character
            if offset:
                board = board[:-2]

            board += '|\n'

        board += '‾' * ((board_length + 1) * 2)

        return board

    def __repr__(self) -> str:
        """
        Returns the representation of the board. Intended for debugging.
        Includes captured pieces.

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
