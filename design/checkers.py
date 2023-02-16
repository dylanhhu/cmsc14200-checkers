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
    move = Move()  # For example only, this should be a proper move

    validity = board.validate_move(move)


3) Getting valid moves for a piece on the board:

    board = CheckersBoard(2)
    piece = Piece()  # For example only, this should be a proper piece

    piece_moves = board.get_piece_moves(piece)


4) Getting all valid moves for a player:

    current_player = PieceColor.DARK  # for example, could be either
    player_moves = board.get_player_moves(current_player)


5) Checking for a winner:

    game_status = board.get_game_state()

    if game_status == GameStatus.IN_PROGRESS:
        print("Game in progress")
    elif winner == GameStatus.LIGHT_WINS:
        print("Light wins!")
    elif winner == GameStatus.DARK_WINS:
        print("Dark wins!")
    else:
        print("Draw!")
"""

from enum import Enum
from typing import Tuple, List, Dict


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

    LIGHT = 0
    DARK = 1


class GameStatus(Enum):
    """
    An enumeration for the current game state.
    """

    IN_PROGRESS = 0
    LIGHT_WINS = 1
    DARK_WINS = 2
    DRAW = 3


# ===============
# DATA CLASSES
# ===============


class Piece:
    """
    Represents a piece on the board

    TODO: Consider making this a dataclass
    TODO: Add getter functions
    """

    def __init__(self, pos: Position, color: PieceColor) -> None:
        """
        Constructor for a piece

        Args:
            pos (Tuple[int, int]): the position of the piece on the board
            color (PieceColor): The color of the piece
        """

        self.x, self.y = pos
        self.color = color
        self.is_king = False

    def to_king(self) -> None:
        """
        Update the piece to a king (aka 'kinging').

        Args:
            None

        Returns:
            None
        """
        raise NotImplementedError


class Move:
    """
    Represents a move that can be done by a piece.

    TODO: Consider making this a dataclass
    TODO: Add getter methods
    """

    def __init__(self, piece: Piece, new_pos: Position) -> None:
        """
        Creates a new move object.

        Args:
            piece (Piece): the piece this move belongs to
            new_pos (Tuple[int, int]): the new position after the move
        """
        self.piece = piece
        self.new_x, self.new_y = new_pos


class Jump(Move):
    """
    Represents a jump that can done by a piece. Includes the opponent's piece
    that will be captured if the jump is completed.

    TODO: Consider making this a dataclass
    TODO: Add getter methods
    """

    def __init__(self,
                 piece: Piece,
                 new_pos: Position,
                 opponent_piece: Piece) -> None:
        """
        Creates a new jump object.

        Args:
            piece (Piece): the piece this move belongs to
            new_pos (Tuple[int, int]): the new position after the jump
            opponent_piece (Piece): the piece that will be captured
        """
        Move.__init__(self, piece, new_pos)
        self.opponent_piece = opponent_piece


# ===============
# GAME BOARD CLASS
# ===============


class CheckersBoard:
    """
    Represents a checkers game. Provides methods for obtaining valid moves,
    validating moves, and acting upon moves according to the rules of checkers.
    Stores the board state along with all pieces, captured or uncaptured.
    """

    def __init__(self, n: int) -> None:
        """
        Creates a new Checkers game.

        Args:
            n (int): the number of rows of pieces per player
        """
        # Dictionary of each player's pieces and their positions
        self._pieces: Dict[PieceColor,
                           Dict[Position, Piece]] = self._generate_pieces(n)

        # Each player's pieces that have been captured by the other player
        self._captured: Dict[PieceColor, List[Piece]] = {
            PieceColor.LIGHT: [],
            PieceColor.DARK: []
        }

        self._game_state = GameStatus.IN_PROGRESS

    def complete_move(self, move: Move) -> List[Jump]:
        """
        Complete a move with a piece.

        Returns a list of possible subsequent jumps, if necessary, that follow
        the provided move. If this list is empty, the player's turn is over.

        Args:
            move (Move): move to make

        Returns:
            List[Jump]: list of subsequent jumps for current piece
        """

        # This function would call self._get_piece_jumps() for the list of
        # subsequent jumps
        raise NotImplementedError

    def get_piece_moves(self, piece: Piece) -> List[Move]:
        """
        Returns a list of possible moves (moves and jumps) for a piece.

        Args:
            piece (Piece): the piece being queried

        Returns:
            List[Move]: the list of moves for that piece
        """
        raise NotImplementedError

    def get_player_moves(self, color: PieceColor) -> List[Move]:
        """
        Returns a list of possible moves (moves and jumps) for a player's
        pieces. If this list is empty, the player is unable to make a move.

        Args:
            color (PieceColor): the player being queried

        Returns:
            List[Move]: list of possible moves (moves and jumps)
        """
        raise NotImplementedError

    def validate_move(self, move: Move) -> bool:
        """
        Validates a potential move. If used correctly, this method should never
        return False.

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

    def _available_pieces(self, color: PieceColor) -> List[Piece]:
        """
        Private method that returns a list of pieces still on the board for a
        given player.

        Args:
            color (PieceColor): the player being queried

        Returns:
            List[Piece]: list of pieces still on the board
        """
        raise NotImplementedError

    def _get_piece_jumps(self, piece: Piece) -> List[Jump]:
        """
        Private method that returns a list of possible jumps for a piece.

        Args:
            piece (Piece): the piece being queried

        Returns:
            List[Jump]: the list of jumps for that piece
        """

        # This function would just filter the results from
        # self.get_piece_moves()
        raise NotImplementedError
