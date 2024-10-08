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
from typing import Dict, List, Union

from utils.logic.aux_utils import DrawOffer, Jump, Move, Piece, Resignation
from utils.logic.board import Board, PieceColor, Position


# ===============
# ENUMS
# ===============


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


# ====================
# Checkers Game Class
# ====================


class CheckersBoard(Board):
    """
    Represents a checkers game. Provides methods for obtaining valid moves,
    validating moves, and acting upon moves according to the rules of checkers.
    Stores the board state along with all pieces, captured or uncaptured.

    The board square grid begins with (0, 0), a light square, at the "top
    left", where the top rows will contain the black pieces and the bottom rows
    containing the red pieces.
    """

    def __init__(self, rows_per_player: int, caching: bool = True) -> None:
        """
        Creates a new Checkers game.

        Args:
            rows_per_player (int): the number of rows of pieces per player
            caching (bool): whether to cache players' moves or not
        """
        super().__init__(rows_per_player)

        # ==================================
        # CheckersBoard Specific Attributes
        # ==================================

        self._board_size = 2 * (rows_per_player + 1)
        self._rows_per_player = rows_per_player

        # Override parent definition of width and height
        self._width = self._board_size
        self._height = self._board_size

        # Represents an outstanding draw offer and acceptance
        self._draw_offer: Dict[PieceColor, bool] = {
            PieceColor.BLACK: False,
            PieceColor.RED: False
        }

        self._caching = caching  # is caching enabled?
        # Cache of the player's available moves XOR jumps. If the cache is None,
        # then the cache has expired/has not been computed yet. Create this
        # whether or not the caching is enabled or disabled.
        self._move_cache: Dict[PieceColor, Union[List[Move], None]] = {
            PieceColor.BLACK: None,
            PieceColor.RED: None
        }

        self._game_state = GameStatus.IN_PROGRESS  # the game state

        self._moves_since_capture = 0  # number of moves since a capture
        self._max_moves_since_capture = self._calc_draw_timeout(rows_per_player)

    def get_captured_pieces(self) -> List[Piece]:
        """
        Getter method that returns a list of all captured pieces.

        Overrides parent function definition since we know that in checkers
        there are only two defined colors.

        Args:
            None

        Returns:
            List[Piece]: list of all captured pieces
        """
        return (self._captured[PieceColor.RED]
                + self._captured[PieceColor.BLACK])

    def complete_move(self, move: Move,
                      draw_offer: Union[DrawOffer, None] = None) -> List[Move]:
        """
        Complete a move with a piece.

        If the move is not valid, a ValueError is raised. This includes when
        a non-jumping move is attempted when a jump is available. Any provided
        draw offers processed just before the error is raised will be undone.

        Returns a list of possible subsequent jumps, if necessary, that follow
        the provided move. If this list is empty, the player's turn is over.

        If a move results in kinging, the player's turn is over and nothing
        is returned.

        If a resignation is provided, the player's turn is over
        and nothing is returned.

        To offer a draw, a regular move (move/jump) must be provided along with
        a DrawOffer.

        To accept the draw offer, play the draw offer in both `move` and in
        `draw_offer`.

        Args:
            move (Move): move to make
            draw_offer (DrawOffer): optional argument for draw offers

        Returns:
            List[Jump]: list of subsequent jumps for current piece, if any

        Raises:
            ValueError: If the move is not valid
        """
        # Check if this is someone resigning
        if isinstance(move, Resignation):
            resign_color = move.get_resigning_color()

            # Map color to correct GameStatus
            resign_to_status = {
                PieceColor.BLACK: GameStatus.RED_WINS,
                PieceColor.RED: GameStatus.BLACK_WINS
            }

            try:
                # Set appropriate game state
                self._game_state = resign_to_status[resign_color]
                return []
            except KeyError as exc:
                # Shouldn't happen, but what if someone is messing with us?
                raise ValueError(f"Resignation's color {repr(resign_color)} \
was invalid.") from exc

        # Track whether we processed any draw offers. Used if undo is necessary
        draw_offer_changed: Union[PieceColor, None] = None

        # Check if there is a draw_offer attached
        if draw_offer is not None:
            # We're not going to handle any errors that this may raise as we'd
            # just like to pass them on to the frontend
            draw_offer_changed = self._handle_draw_offer(draw_offer)

            # Is this a player accepting a draw?
            if isinstance(move, DrawOffer):
                return []  # Accepted, their turn is over

        else:
            # No draw offer, so check if there were any outstanding draw offers
            # that were not accepted
            if any(self._draw_offer.values()):
                self._reset_draw_offers()  # Offer rejected, clear them

        # Complete the move of the piece
        try:
            super().complete_move(move)
            self._moves_since_capture += 1  # Increment move counter
        except ValueError:
            # Invalid move, check if draw offer undo needed
            if draw_offer_changed:
                self._draw_offer[draw_offer_changed] = False  # undo draw offer

                # If gamestate was changed, reset it to in progress
                if self._game_state == GameStatus.DRAW:
                    self._game_state = GameStatus.IN_PROGRESS

            raise  # Re-raise the exception

        # move.get_piece() not guaranteed to be the same Piece instance as ours
        piece = self._pieces[move.get_new_position()]

        # Process kinging
        was_kinging = False
        if move.is_kinging(self._board_size):
            piece.to_king()
            was_kinging = True

        if self._caching:
            # Pieces pieces were moved/changed, expire the move cache for both
            self._move_cache[PieceColor.RED] = None
            self._move_cache[PieceColor.BLACK] = None

        # Handle the capture, if it's a Jump
        if isinstance(move, Jump):
            # Process the capture
            cap_piece = move.get_captured_piece()

            # Move from board to captured pieces
            cap_color = cap_piece.get_color()
            cap_pos = cap_piece.get_position()
            self._captured[cap_color].append(self._pieces.pop(cap_pos))

            cap_piece.set_captured()
            self._moves_since_capture = 0  # reset counter

            # If move was kinging, the turn is over regardless of further jumps
            if was_kinging:
                return []

            # Return list of following jumps, if any
            return self.get_piece_moves(piece, jumps_only=True)

        # Move completed, turn is over
        return []

    def undo_move(self, move: Move) -> None:
        """
        Undo a provided move (Move or Jump). Implemented for the bot, may not
        work when not used by the bot.

        Args:
            move (Move): the move that is to be undone

        Returns:
            None

        Raises:
            TypeError: if move is a DrawOffer or Resignation
        """
        if isinstance(move, (DrawOffer, Resignation)):
            raise TypeError(f"Move {repr(move)} is not of type Move or Jump.")

        old_pos = move.get_current_position()
        new_pos = move.get_new_position()

        target_piece = self._pieces[new_pos]

        # "Undo" the move
        target_piece.set_position(old_pos)
        self._pieces[old_pos] = target_piece
        del self._pieces[new_pos]

        # Undo any kinging
        if move.is_kinging(self._board_size):
            target_piece.unking()

        if self._caching:
            # Pieces pieces were moved/changed, expire the move cache for both
            self._move_cache[PieceColor.RED] = None
            self._move_cache[PieceColor.BLACK] = None

        # Undo a jump, if necessary
        if isinstance(move, Jump):
            jumped_piece = move.get_captured_piece()

            # Calculate the old position of the jumped piece
            jumped_pos = (int((new_pos[0] + old_pos[0]) / 2),
                          int((new_pos[1] + old_pos[1]) / 2))

            # Undo the capture
            self._pieces[jumped_pos] = jumped_piece
            jumped_piece.set_position(jumped_pos)

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
        color = piece.get_color()
        positions: Dict[Position, Position] = {}

        # Add positions to check based on PieceColor or king status
        # Black pieces can only go to south directions
        if color == PieceColor.BLACK or piece.is_king():
            positions[(curr_col + 1, curr_row + 1)] = (curr_col + 2,
                                                       curr_row + 2)  # se
            positions[(curr_col - 1, curr_row + 1)] = (curr_col - 2,
                                                       curr_row + 2)  # sw

        # Red pieces can only go to north directions
        if color == PieceColor.RED or piece.is_king():
            positions[(curr_col - 1, curr_row - 1)] = (curr_col - 2,
                                                       curr_row - 2)  # nw
            positions[(curr_col + 1, curr_row - 1)] = (curr_col + 2,
                                                       curr_row - 2)  # ne

        # Loop thru immediate positions
        for (position, jump_position) in positions.items():
            # Make sure position is inside the board
            if self._validate_position(position):
                # Check if there's a piece already in the position
                if position not in self._pieces:
                    # Free space in the position
                    if not jumps_only:
                        # We're not looking for only jumps, add the Move
                        possible_moves.append(Move(piece, position))

                    continue  # We're done with this position

                # There's a piece in this position, so we try to jump it by
                # checking if the jump location is valid and whether the
                # jump position is currently taken by another piece

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

        This function sets the player move/jump availability cache.

        Args:
            color (PieceColor): the player being queried

        Returns:
            List[Move]: list of possible moves:
                        ((moves XOR jumps) OR DrawOffer)
        """
        if self._caching:
            # Check cache for previously calculated list of moves
            moves = self._move_cache[color]
            if moves is not None:
                # Add any draw offer, if necessary
                if self._draw_offer[color]:
                    moves.append(DrawOffer(color))

                return moves

        # Not cached, compute the moves

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

        if self._caching:
            # Set cache
            self._move_cache[color] = (possible_jumps
                                       if possible_jumps
                                       else possible_moves)

        # Check for a draw offer
        if self._draw_offer[color]:
            offer = DrawOffer(color)

            # Check if we need to append it to the jumps or to moves
            if possible_jumps:
                possible_jumps.append(offer)
                return possible_jumps

            # There are no jumps available, we can use the normal return below
            possible_moves.append(offer)

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
        # Validate type, piece, starting position, new position
        if not super().validate_move(move):
            return False

        # To be able to check for other jumps, we must get all moves
        player_moves = self.get_player_moves(move.get_piece().get_color())

        # Make sure that this move is a possible move for the player.
        # Since we already have all the moves, we can just test for membership.
        # If this is a Move when the player must Jump, this will catch it.
        if move not in player_moves:
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
        # Check for resignation (set in complete_move()) or draw
        if self._game_state in (GameStatus.BLACK_WINS, GameStatus.RED_WINS,
                                GameStatus.DRAW):
            return self._game_state

        if self._moves_since_capture > self._max_moves_since_capture:
            self._game_state = GameStatus.DRAW  # set anyway, just in case

            return self._game_state

        # Check for winning states (no moves left impl. no pieces left and no
        # DrawOffer). If the player has a DrawOffer, we interpret this as still
        # having a valid move available.

        # Check red's state
        if not self.get_player_moves(PieceColor.RED):
            return GameStatus.BLACK_WINS

        # Check black's state
        if not self.get_player_moves(PieceColor.BLACK):
            return GameStatus.RED_WINS

        # If a player has no pieces but only a DrawOffer, continue so that they
        # have to either take the draw or resign.
        return GameStatus.IN_PROGRESS

    def _handle_draw_offer(self, offer: DrawOffer) -> PieceColor:
        """
        Private method to handle draw offers. Intended to be called by
        complete_move().

        Args:
            offer (DrawOffer): the draw offer

        Returns:
            PieceColor: the color of the player offering/accepting the draw

        Raises:
            ValueError: if the offering color is invalid
            RuntimeError: if the offering color already has a pending offer
        """
        offering_color = offer.get_offering_color()

        # Check for bad offering color
        if offering_color not in self._draw_offer:
            msg = f"DrawOffer's offering color {repr(offering_color)} is not \
in the supported colors."

            # Shouldn't happen, but what if someone's messing with us?
            raise ValueError(msg)

        # Check if the player already has an outstanding draw offer
        if self._draw_offer[offering_color]:
            msg = f"DrawOffer's offering color {repr(offering_color)} already \
has an outstanding draw offer."

            # Shouldn't happen, but what if somewhere else has a bug?
            raise RuntimeError(msg)

        self._draw_offer[offering_color] = True

        # Check for draw condition and set it
        if all(self._draw_offer.values()):
            self._game_state = GameStatus.DRAW

        return offering_color

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

    def _calc_draw_timeout(self, rows_per_player: int,
                           _enabled: bool = True) -> int:
        """
        Private method for calculating the maximum number of moves between
        captures before a stalemate. Roughly set to slightly over the average
        number of moves between captures in a game.

        Datapoints collected by Junfei. Power function values calculated by
        Dylan.

        Args:
            rows_per_player (int): the number of rows per player
            _enabled (bool): Uses calculation if true, otherwise returns 40

        Returns:
            int: number of moves between captures before stalemate
        """
        if not _enabled:
            return 40

        return round(2.2 * (rows_per_player ** 2.2) + 10)

    def _gen_pieces(self, height: Union[int, None] = None,
                    width: Union[int, None] = None) -> Dict[Position, Piece]:
        """
        Private method for generating all pieces before the game begins.

        Overrides the parent `_gen_pieces()` and thus keeps the same method
        signature.

        Args:
            height (int or None): the number of rows per player
            width (int or None): Unused argument for CheckersBoard

        Returns:
            Dict[Position, Piece]: Dictionary containing piece locations and
                                   pieces for both players

        Raises:
            ValueError: if parameter height is None
        """
        if height is None:
            raise ValueError("Parameter height cannot be None.")

        rows_per_player = height  # rename for clarity
        board_len = 2 * rows_per_player + 1  # 0 indexed max value of row, col

        board: Dict[Position, Piece] = {}

        # Generate black's pieces, iterating forwards
        for row in range(0, rows_per_player):
            # Each row of pieces alternates starting in column 0 if odd or in
            # column 1 if even
            offset = 1 if (row % 2 == 0) else 0

            for col in range(offset, board_len + offset, 2):
                position = (col, row)

                board[position] = Piece(position, PieceColor.BLACK)

        # Generate red's pieces, iterating backwards from the end of the board
        for row in range(board_len, board_len - rows_per_player, -1):
            # Each row of pieces alternates starting in column 0 if odd or in
            # column 1 if even
            offset = 1 if (row % 2 == 0) else 0

            for col in range(offset, board_len + offset, 2):
                position = (col, row)

                board[position] = Piece(position, PieceColor.RED)

        return board

    def _can_player_move(self, color: PieceColor) -> bool:
        """
        Private method for getting whether the player has any valid move. Does
        not consider DrawOffer as a possible move.

        This private method is not used, as we currently interpret having a
        DrawOffer as being a valid move.

        Args:
            color (PieceColor): the color of the player being queried

        Returns:
            bool: True if the player has a move available otherwise False
        """
        moves = self.get_player_moves(color)  # get the list of Moves

        # Check if there are any valid moves AND check whether the only move is
        # a DrawOffer (offers are appended to the end, so if the first object
        # is not a DrawOffer, then we're all good)
        if moves and not isinstance(moves[0], DrawOffer):
            return True

        return False
