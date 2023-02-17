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
        raise NotImplementedError

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
        raise NotImplementedError

    def set_captured(self) -> None:
        """
        Sets the piece's to captured. This cannot be undone, please make sure
        you know what you're doing.

        Args:
            None

        Returns:
            None
        """
        raise NotImplementedError

    def is_captured(self) -> bool:
        """
        Returns whether the piece is captured.

        Args:
            None

        Returns:
            True if captured otherwise False
        """
        raise NotImplementedError

    def get_color(self) -> PieceColor:
        """
        Getter function that returns the piece's color.

        Args:
            None

        Returns:
            The color of the piece
        """
        raise NotImplementedError

    def is_king(self) -> bool:
        """
        Getter function that returns whether this piece is a king.

        Args:
            None

        Returns:
            True if this is a king otherwise False
        """
        raise NotImplementedError

    def to_king(self) -> None:
        """
        Update the piece to a king (aka 'kinging'). This can't be undone,
        please make sure you know what you're doing.

        Args:
            None

        Returns:
            None
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def __repr__(self) -> str:
        """
        Returns the representation of this piece. Meant for debugging.

        Args:
            None

        Returns:
            str: Debug representation of the piece
        """
        raise NotImplementedError


class Move:
    """
    Represents a move that can be done by a piece or a resignation/draw offer.
    """

    def __init__(self, piece: Union[Piece, None], new_pos: Position) -> None:
        """
        Creates a new move object.

        Args:
            piece (Piece or None): the piece this move belongs to
            new_pos (Position): the new position after the move
        """
        self._piece = piece  # the piece to be moved

        # The new position. If it is (-1, -1) then it is not a "move" per se
        self._new_x, self._new_y = new_pos

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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

    def __repr__(self) -> str:
        """
        Returns the representation of the move. Intended for debugging.

        Args:
            None

        Returns:
            str: representation of the move
        """
        raise NotImplementedError


class Jump(Move):
    """
    Represents a jump that can done by a piece. Includes the opponent's piece
    that will be captured if the jump is completed.
    """

    def __init__(self,
                 piece: Piece,
                 new_pos: Position,
                 opponent_piece: Piece) -> None:
        """
        Creates a new jump object.

        Args:
            piece (Piece): the piece this move belongs to
            new_pos (Position): the new position after the jump
            opponent_piece (Piece): the piece that will be captured
        """
        super().__init__(piece, new_pos)

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
        raise NotImplementedError

    def __str__(self) -> str:
        """
        Returns a string representation of the move

        Args:
            None

        Returns:
            str: String representation of the move
        """
        raise NotImplementedError


class Resignation(Move):
    """
    Represents a resignation by one player. Upon resignation, an instance of
    this class should be created by the GUI/TUI and be "played".
    """

    def __init__(self) -> None:
        """
        Create a new resignation object.

        Args:
            None
        """
        super().__init__(None, (-1, -1))

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

    def __str__(self) -> str:
        """
        Returns a string representation of the resignation

        Args:
            None

        Returns:
            str: String representation of the move
        """
        raise NotImplementedError


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

    def get_offering_color(self) -> PieceColor:
        """
        Getter to return the color that is offering the draw

        Args:
            None

        Returns:
            PieceColor of the player offering the draw
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """
        Returns a string representation of the draw offer

        Args:
            None

        Returns:
            str: String representation of the move
        """
        raise NotImplementedError


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
        # Dictionary of each player's uncaptured pieces and their positions
        self._pieces: Dict[PieceColor,
                           Dict[Position, Piece]] = self._generate_pieces(n)

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
        raise NotImplementedError

    def get_captured_pieces(self) -> List[Piece]:
        """
        Getter method that reutrns a list of all captured pieces.

        Args:
            None

        Returns:
            List[Piece]: list of all captured pieces
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def get_color_avail_pieces(self, color: PieceColor) -> List[Piece]:
        """
        Getter that returns a list of pieces still on the board for a given
        player color.

        Args:
            color (PieceColor): the player being queried

        Returns:
            List[Piece]: list of pieces still on the board for that color
        """
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

    def validate_move(self, move: Move) -> bool:
        """
        Validates a potential move. If only moves provided by this class are
        attempted, then this function should never return False.

        Args:
            move (Move): the move to be validated

        Returns:
            bool: True if the move is valid, otherwise False
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def _generate_pieces(self,
                         n: int) -> Dict[PieceColor, Dict[Position, Piece]]:
        """
        Private method for setting up the pieces before the game begins.

        Args:
            n (int): number of rows of pieces per player

        Returns:
            Dict[PieceColor, Dict[Position, Piece]]: Dictionary containing
                a dictionary of piece locations and pieces for each player
        """
        raise NotImplementedError

    def _handle_draw_offer(self, offer: DrawOffer) -> List:
        """
        Private method to handle draw offers. Intended to be called by
        complete_move().

        Args:
            offer (DrawOffer): the draw offer

        Returns:
            An empty list
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """
        Returns a string representation of the board

        Args:
            None

        Returns:
            str: String representation of the board
        """
        raise NotImplementedError
