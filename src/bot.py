import math
from copy import deepcopy
from enum import Enum
from typing import List, Tuple, Union
from checkers import Piece, Move, CheckersBoard, PieceColor, Jump


class SmartLevel(Enum):
    """
    An enumeration of the smart level for smart bots
    """
    SIMPLE = 0
    MEDIUM = 1
    HARD = 2


class Bot:
    """
    Represents a fundamental structure of the bot with basic abilitieis to
    conduct a move on behave of one player. Provides the method to get all
    available moves at one turn and complete that move

    Note that this class in itself doesn't support any choosing of the move
    from all available moves
    """

    def __init__(self, own_color, oppo_color, checkersboard) -> None:
        """
        construct for a bot

        Parameters:
            own_color(PieceColor): the color of the piece that
                                   the bot is in control of
            oppo_color(PieceColor): the color of the piece that
                                    the opponent is in control of
            checkerboard(CheckersBoard): the checkerboard

        Return: None
        """
        self._own_color = own_color
        self._oppo_color = oppo_color
        self._checkersboard = checkersboard
        # initialize a copy of the checkerboard
        self._experimentboard = deepcopy(self._checkersboard)

    def get_avail_moves(self) -> List[Move]:
        """
        get all the available moves for all pieces according to the color
        that the bot is in control of

        Parameters: None

        Return: List[Move]: a list of all the moves available
        """

        # return a list of all moves available on the experiment board
        return self._experimentboard.get_player_moves(self._own_color)

    def get_oppo_avail_moves(self) -> List[Move]:
        """
        get all the available moves for all pieces of the opponent

        Parameters: None

        Return: List[Move]: a list of all the moves available
        """

        # return a list of all moves available on the experiment board
        return self._experimentboard.get_player_moves(self._oppo_color)

    def complete_move(self, move_list) -> None:
        """
        complete a list of moves that is decided to be taken by the bot, if
        any of the move is invalid, raise an exception

        Parameters:
            move_list(List[Move]): the move list that is decided to be taken

        Return: None
        """
        # initialize a list of the possible next steps to take
        valid_nxt_list = self.get_avail_moves()

        # take the moves consecutively in the move_list
        for nxt_move in move_list:
            # verify whether the nxt_move is a valid move to take
            if nxt_move in valid_nxt_list:
                # valid, take the move, and update the possible next steps to take
                valid_nxt_list = self._checkersboard.complete_move(nxt_move)

            else:
                # invalid, raise error
                raise Exception("The bot is trying to take an invalid move")


class RandomBot(Bot):
    """
    Represents a bot that is capable of selecting moves randomly
    """

    def __init__(self, own_color, oppo_color, checkersboard) -> None:
        """
        construct for a RandomBot

        Parameters:
            own_color(PieceColor): the color of the piece that
                                   the bot is in control of
            oppo_color(PieceColor): the color of the piece that
                                    the opponent is in control of
            checkerboard(CheckersBoard): the checkerboard

        Return: None
        """
        super().__init__(own_color, oppo_color, checkersboard)

    def choose_move(self, avail_moves) -> Move:
        """
        choose a move from avail_moves randomly

        Parameters:
            avail_moves(List[Move]): a list of available moves that
                                     the random bot is going to choose
                                     from

        Return: Move: the move that is chosen
        """
        raise NotImplementedError


class MoveSequence:
    """
    Represents a sequence of moves that valid to be chosen by the robot

    This class is specially for the smartbot to use for choosing and 
    completing moves
    """

    def __init__(self, move_list, result_board, kinged) -> None:
        """
        construct a movesequence

        Parameters:
            move_list(List[Move]): a list of the moves that can be taken 
                                   consecutively
            result_board(CheckersBoard): the result board state if the moves in 
                                         the move list is taken
            kinged(Bool): indicate whether a piece is kinged by this MoveSequence

        Return: None
        """
        self._move_list = move_list
        self._result_board = result_board
        self._kinged = kinged

        # initialize the priority of the move sequence to 0
        self._priority = 0

    def get_original_position(self) -> Tuple[int, int]:
        """
        get the original position from which the MoveSequence is going to start 

        Parameters: None

        Return: Tuple[int,int]: (x, y) on the board
        """
        return self._move_list[0].get_current_position()

    def get_end_position(self) -> Tuple[int, int]:
        """
        get the end position to which the MoveSequence is going to head

        Parameters: None

        Return: Tuple[int,int]: (x, y) on the board
        """
        return self._move_list[-1].get_new_position()

    def get_target_piece(self) -> Piece:
        """
        get the piece that is moved in this move sequence

        Parameters: None

        Return Piece: the piece that is moved
        """
        return self._move_list[0].get_piece()

    def get_move_list(self) -> List[Move]:
        """
        getter function of the move_list of the MoveSequence

        Parameters: None

        Return: List[Move]: the list of moves of the MoveSequence
        """
        return self._move_list

    def get_result_board(self) -> CheckersBoard:
        """
        getter function of the move_list of the MoveSequence

        Parameters: None

        Return: List[Move]: the list of moves of the MoveSequence
        """
        return self._result_board

    def get_priority(self) -> float:
        """
        getter function of the priority of the MoveSequence

        Parameters: None

        Return: Float: the priority of the MoveSequence
        """
        return self._priority

    def set_priority(self, new_pri) -> None:
        """
        change the priority of a move sequence

        Parameters:
            new_pri(float): the new_priority value

        Return: None
        """
        self._priority = new_pri

    def is_kinged(self) -> bool:
        """
        determine whether the target piece will be kinged by this sequence of move

        Parameters: None

        Return: bool: True if it is kinged, False otherwise
        """
        return self._kinged


class SmartBot(Bot):
    """
    Represents a bot that is capable of selecting moves according
    to some strategies in a certain group of strategies, including:
    1) more inclined to attack opponent's double corner
    2) more inclined to hold two anchor checkers in the base line
    3) more inclined to get kings
    4) more inclined to sacrifice pieces when leading
    5) more inclined to pick the move that capture the most opponent pieces
    6) more inclined to push forward
    7) more inclined to occupy the center
    8) able to conduct the wining move if possible
    9) able to avoid a lossing move if possible
    10) more inclined to conduct forcing

    citations for the strategies:
    https://www.ultraboardgames.com/checkers/tips.php
    https://www.youtube.com/watch?v=Lfo3yfrbUs0
    https://www.gamblingsites.com/skill-games/checkers/
    https://medium.com/@theflintquill/checkers-eba4d8862719
    """

    def __init__(self, own_color, oppo_color, checkersboard, level) -> None:
        """
        construct for a smart bot

        Parameters:
            own_color(PieceColor): the color of the piece that
                                   the bot is in control of
            oppo_color(PieceColor): the color of the piece that
                                    the opponent is in control of
            checkerboard(CheckersBoard): the checkerboard
            level(SmartLevel): how smart the bot has to be

        Return: None
        """
        super().__init__(own_color, oppo_color, checkersboard)

        # smart level of the bot, reflecting in how many strategies are adopted
        self._level = level

    def choose_move(self, avail_moves) -> Move:
        """
        choose a move from avail_moves

        The move would be chosen according to the smart level of the
        bot, the higher the smart level, the more strategies that the
        choosing would take into consideration

        Parameters:
            avail_moves(List[List[Move]]): a list of available moves sequences
                                     that the smart bot is going to choose
                                     from according to the strategy

        Return: Move: the move that is chosen
        """
        raise NotImplementedError

    def _get_mseq_list(self, strategy_list) -> List[MoveSequence]:
        """
        initialize a list of MoveSequences that we can take with their priority updated according to different strategies

        Parameters: 
            strategy_list(List[Tuple(Functionsm, float)]): a list of functions that updates the priority of a MoveSequence according to some strategy and their correponding weight

        Return: List[MoveSequence]:
                A list of all possible MoveSequences with their updated priority
        """
        # get all the immediate next moves that are possible
        nxt_move_list = self.get_avail_moves()
        Movesequence_list = []

        def helper(move_list, curr_path, curr_board, kinged) -> None:
            """
            a helper funciton to recursively find out all possible move
            sequences and update the output_list accordingly

            Parameters:
                move_list(List[Move]): a list of the next step that can be taken
                curr_path(List[Move]): a list of that keeps track of the current
                                       path of moves taken
                curr_board(CheckersBoard): represent the current board state
                kinged(Bool): to record whether a piece is kinged during a MoveSequence

            Return: None
            """
            if not move_list:
                # if there's no move in the list, reached the end
                # of one potential move list, create a corresponding
                # MoveSequence and add that to the Movesequence_list with its
                # priority
                mseq = MoveSequence(curr_path[:], curr_board, kinged)
                self._assign_priority(mseq, strategy_list)
                Movesequence_list.append(mseq)

            # traverse through all the possible next moves, take the moves
            # on a cloned board and recursively call helper
            for nxt_move in move_list:
                # update the path and the board state
                curr_path.append(nxt_move)

                # determine whether the piece about to be moved is a king now
                if not nxt_move.get_piece().is_king():
                    not_king = True
                else:
                    not_king = False

                # complete the next move
                valid_nxt_list = curr_board.complete_move(nxt_move)

                # determine whether the piece is kinged by this next move
                if not_king and nxt_move.get_piece().is_king():
                    # kinged by next move
                    kinged_by_move = True
                else:
                    # not kinged by this move, inherit the kinged from previous moves
                    kinged_by_move = kinged

                # the recursive step
                helper(valid_nxt_list, curr_path, curr_board, kinged_by_move)

                curr_board.undo_move(nxt_move)
                curr_path.pop()

        # update the output_list
        helper(nxt_move_list, [], self._experimentboard, False)

        return Movesequence_list

    def _assign_priority(self, mseq, strategy_list) -> None:
        """
        update the priority of the MoveSequences according to a set of strategies

        Parameters:
            mseq(Movesequence): the MoveSequence about to be updated
            strategy_list(List[Tuple(Functionsm, float)]): a list of functions that are going to be applied for the update of the priority and their corresponding weights

        Return: None
        """
        # update the priority with respect to every strategy
        for strat_func, weight in strategy_list:
            mseq.set_priority(strat_func(mseq, weight))

    def _distance(pos1, pos2) -> float:
        """
        Calculated the distane between two position on the board

        Parameters:
            pos1(Tuple[int, int]): the (x, y) on the board of the starting point
            pos2(Tuple[int, int]): the (x, y) on the board of the end point

        Return: float: the calculated the distance from the 
        """
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[0] - pos2[2])**2)

    def _corner_priority(self, mseq, weight) -> float:
        """
        update the priority of the MoveSequence with the consideration of attacking the opponent's double corner when 

        It would only cause our pieces to be more inclined to move attack opponent's double corner when opponent's double corner is not vacant

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be updated
            weight(float): a float that determine how much of an influence this strategy should be playing among all the strategies

        Return: float: the new priority for mseq according to the corner strategy
        """
        # get the original and the end position of a MoveSequence
        origin_pos = mseq.get_origin_position()
        end_pos = mseq.get_end_position()

        # get the position of our double corner and the opponent's double corner according to bot's own piece color
        if self._own_color == PieceColor.RED:
            oppo_double_pos = (0, 0)

        elif self._own_color == PieceColor.BLACK:
            oppo_double_pos = (self._experimentboard.get_board_width(),
                               self._experimentboard.get_board_width())

        attack_score = 0
        for oppo_piece in self._experimentboard.get_color_avail_pieces(self._oppo_color):
            if self._distance(oppo_piece, oppo_double_pos) <= math.sqrt(5):
                # if there exists any opponent piece that is within 2 steps to opponents double corner, more inclined to move towards oppo's double corner
                attack_score = self._distance(
                    oppo_double_pos, origin_pos) - self._distance(oppo_double_pos, end_pos)

        return mseq.get_priority() + weight * attack_score

    def _baseline_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of holding the baseline. 

        More specifically, we are more inclined to hold the anchor checkers on the baseline as defense. The anchor checkers are the checkers that is on every other square starting from our double corner. For example, if we have an 8-columns board, so 4 checkers each row, the anchor checkers would be the first and the third checkers on our baseline row counting from the double corner

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be updated
            weight(float): a float that determine how much of an influence this strategy should be playing among all the strategies

        Return: float: the new priority for mseq according to the hold base line strategy
        """
        # set up the original position of the MoveSequence
        origin_pos = mseq.get_origin_position()
        # initialize a list that's going to take the anchor positions
        anchor_pos_list = []
        # get the borad witdh
        boardwidth = self._experimentboard.get_board_width()

        # determine the anchor positions according to our piece color
        if self._own_color == PieceColor.RED:
            # we control the red piece
            for n in range(boardwidth/2 + 1):
                anchor_pos_list.append(
                    (2 * n, boardwidth))
        elif self._own_color == PieceColor.BLACK:
            # we control the black piece
            for n in range(boardwidth/2):
                anchor_pos_list.append((2 * n + 1, 0))

        baseline_score = 0
        if origin_pos in anchor_pos_list:
            # if the MoveSequence is going to move an anchor checker, decrease the baseline_score
            baseline_score -= 1

        return mseq.get_priority() + weight * baseline_score

    def _king_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of getting a king

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be updated
            weight(float): a float that determine how much of an influence this strategy should be playing among all the strategies

        Return: float: the new priority for mseq according to the kinging strategy
        """
        king_score = 0
        if mseq.is_kinged():
            # the MoveSequence is kinging a piece
            king_score = 1

        return mseq.get_priority() + weight * king_score

    def _sacrifice_priority(self, mseq, weight) -> List[MoveSequence]:
        """
        update the priority of the available MoveSequence with the consideration
        of sacrifice

        Sometimes making a move means sacrificing the piece we are moving, we don't want to do this blindly so this function serves as a restricting method so that we don't blindly sacrifice our pieces for no reason.

        However, we are more willing to sacrifice pieces when we are leading

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be updated
            weight(float): a float that determine how much of an influence this strategy should be playing among all the strategies

        Return: float: the new priority for mseq according to the sacrificing strategy
        """
        # construct an instance of the opponent
        Opponent = OppoBot(self._oppo_color, self._own_color,
                           self._experimentboard)

        oppo_jump = Opponent.get_induced_jump_mseq()
        if oppo_jump:
            # this MoveSequence leads to a sacrifice

            # get the initial number of pieces for each side and the current number of pieces for each side
            num_piece = self._experimentboard.get_board_width()/2 - 1
            my_pieces = self._experimentboard.get_color_avail_pieces(
                self._own_color)
            oppo_pieces = self._experimentboard.get_color_avail_pieces(
                self._oppo_color)

            # sacrifice core is bigger when (1)more pieces are captured (2)The more the opponent pieces is more than mine
            sacrifice_score = len(
                oppo_jump) * (num_piece - (len(my_pieces) - len(oppo_pieces)))
            return mseq.get_priority() - weight * sacrifice_score

        # this MoveSequence doesn't lead to a sacrifice
        return mseq.get_priority()

    def _captured_priority(self, mseq, weight) -> float:
        """
        update the priority of the  available MoveSequence with the consideration of capturing as many opponent pieces as possible

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be updated
            weight(float): a float that determine how much of an influence this strategy should be playing among all the strategies

        Return: float: the new priority for mseq according to the capture priority
        """
        return mseq.get_priority() + weight * len(mseq.get_move_list())

    def _push_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of pushing forward

         Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be updated
            weight(float): a float that determine how much of an influence this strategy should be playing among all the strategies

        Return: float: the new priority for mseq according to the push priority
        """
        # get the original and end position for a MoveSequence
        origin_pos = mseq.get_origin_position()
        end_pos = mseq.get_end_position()

        if self._own_color == PieceColor.RED:
            # we control the red piece
            push_score = origin_pos[1] - end_pos[1]
        elif self._own_color == PieceColor.BLACK:
            # we control the black piece
            push_score = end_pos[1] - origin_pos[1]

        return mseq.get_priority() + weight * push_score

    def _stick_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the consideration of not leaving a single piece out

        We want to favor MoveSequences that lead to the moved piece at least having one piece of our side around it.

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be updated
            weight(float): a float that determine how much of an influence this strategy should be playing among all the strategies

        Return: float: the new priority for mseq according to the stick strategy
        """
        # get the piece that is moved in this MoveSequence
        target_piece = mseq.get_target_piece()

        # get the end position of the target piece and construct the four possible positions that could be having a piece around it
        piece_pos = target_piece.get_position()
        near_region = [(piece_pos[0] - 1, piece_pos[0] - 1), (piece_pos[0] - 1, piece_pos[0] + 1),
                       (piece_pos[0] + 1, piece_pos[0] - 1), (piece_pos[0] + 1, piece_pos[0] + 1)]

        # check whether there exists a piece in the near region of the target piece
        for piece in self._experimentboard.get_color_avail_pieces(self._own_color):
            if piece.get_position() in near_region:
                # there exists a piece in the near region
                return mseq.get_priority()

        # there's no piece around the near region
        return mseq.get_priority() - weight

    def _center_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSeuqnce with the consideration
        of occupying the center

        For typical 8 * 8 checkerboards, the center refers to the 8 positions in the center 4 columns and the center 2 columns. We want to push into the center regions because we want to avoid staying on the side of the board Therefore, to generalize this to a w * w checkerboards, the center region shall be column 3 to column w -2 and the center rows that are without any pieces at the beginning of the round

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be updated
            weight(float): a float that determine how much of an influence this strategy should be playing among all the strategies

        Return: float: the new priority for mseq according to the center strategy
        """
        # get the original position and the end position of the MoveSequence
        origin_pos = mseq.get_origin_position()
        end_pos = mseq.get_end_position()

        # get the board width
        boardwidth = self._experimentboard.get_board_width()

        centering_score = 0
        # specify the center region
        center = [range(2, boardwidth - 2),
                  range(boardwidth/2 - 1, boardwidth + 1)]
        if origin_pos[0] not in center[0] and origin_pos[1] not in center[1]:
            # the original position is not in the center region
            if end_pos[0] in center[0] and end_pos[1] in center[1]:
                # the end position is in center region
                centering_score = 1

        return mseq.get_priority() + weight * centering_score

    def _winning_priority(self, mseq) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of the existence of a winning move. 

        If there exists a winning move in the given move sequence, this MoveSequence is automatically taken

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be updated

        Return: float: the new priority for mseq according to the winning strategy, if the MoveSequence doesn't contain a winning move, we return the original priority, otherwise, we return inf
        """
        # get all the moves that opponents can make if taking this MoveSequence
        oppo_moves = self._experimentboard.get_oppo_avail_moves()

        if oppo_moves:
            # the MoveSequence contains no winning move
            return mseq.priority
        else:
            # the MoveSequence contains a winning move
            return math.inf

    def _lose_priority(self, mseq) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of the existence of a losing move.

        A losing move is defined as an move that will lead to the existence of a winning move for the opponent, i.e., the opponent can win next round. 

        If there exists a losing move in a MoveSequence, we avoid taking that MoveSequence. However, if all the MoveSequences contains a losing move, we randomly select a move(at that point the game would already be over)

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be updated

        Return: float: the new priority for mseq according to the lose strategy, if the MoveSequence doesn't contain a losing move, we return the original priority, otherwise, we return -math.inf
        """
        # construct an instance of the opponent
        Opponent = OppoBot(self._oppo_color, self._own_color,
                           self._experimentboard)

        # check whether there is a winning move for the opponent if we take this MoveSequence
        if Opponent.contains_winning_mseq():
            return -math.inf
        else:
            return mseq.get_priority()

    def force_priority(self) -> float:
        """
        update the priority of an avialable MoveSequence when that MoveSequence leads to forcing 

        To be more precise, sometimes a MoveSequence will lead to a sacrifice, but sometimes this sacrifice is a part of the strategy called forcing. Basically, we force the opponent to capture our pieces only to build up a bridge for us to capture their pieces in our next round.

        We call the forced jump and consecutive moves of the Opponent the induced jump MoveSequence, and our MoveSequence that can capture this piece moved by the induced jump MoveSequence in the following round response MoveSequence.

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be updated
            weight(float): a float that determine how much of an influence this strategy should be playing among all the strategies

        Return: float: the new priority for mseq according to the forcing strategy
        """
        # construct an instance of the opponent
        Opponent = OppoBot(self._oppo_color, self._own_color,
                           self._experimentboard)

        # get the induced jump MoveSequence of the opponent
        oppo_mseq = Opponent.get_induced_jump_mseq()
        if oppo_mseq:
            # if there is this induced jump MoveSequence, update the board to the state that assumes the opponent has taken this move
            for move in oppo_mseq:
                self._experimentboard.complete_move(move)

            target_piece = oppo_mseq.get_target_piece()

            # get what would our available MoveSequence be for the next turn if we forced the Opponent's induced jump MoveSequence
            nxt_turn_mseq = self._get_mseq_list([])

            # initialize a list to take the updated priority of Movesequences that are respnse MoveSequences
            response_priority = []
            for mseq in nxt_turn_mseq:
                if mseq.get_target_piece() == target_piece:
                    # this MoveSequence is a response Movesequence
                    response_priority.append(self._captured_priority(mseq, 1))

            # restore the board to the current round before we anticipate any opponents moves
            for move in reversed(oppo_mseq):
                self._experimentboard.undo_move(move)

            # return the priority that corresponds to the most pieces captured in the response MoveSequence
            return max(response_priority)

        # our MoveSequence this round is not leading to an induced jump MoveSequence
        return mseq.get_priority()


class OppoBot(SmartBot):
    """
    Represent a bot used to try what will the opponent do if the SmartBot has taken a MoveSequence.
    Note that this bot is strictly for anticipation purposes of the SmartBot when making decisions. It works under the premise that the SmartBot has taken a specific MoveSequence and is used to show the corresponding reaction to this MoveSequence that the opponent would have
    """

    def __init__(self, own_color, oppo_color, checkersboard, last_mseq) -> None:
        """
        Construct a bot that represents the opponent

        Parameters:
            own_color(PieceColor): the color of the piece that the bot is in control of
            oppo_color(PieceColor): the color of the piece that the opponent is in control of
            checkerboard(CheckersBoard): the checkerboard
            last_mseq(MoveSequence): represents the move sequence that we asssumed to be taken by the SmartBot

        Return: None
        """
        super().__init__(own_color, oppo_color, checkersboard)

        # initialize the move sequence assumed to be taken by the SmartBot
        self._last_mseq = last_mseq

    def contains_winning_mseq(self) -> bool:
        """
        Examine whether there exists a MoveSequence that contains a winning move

        Parameters: None

        Return: bool: True if there exists a winning MoveSequence, False Otherwise
        """
        # get all the possible move sequences and examine whether they contain winning moves
        mseq_list = self._get_mseq_list([self._winning_priority,])

        for mseq in mseq_list:
            if mseq.get_priority() == math.inf:
                # there exists a winning MoveSequence
                return True
        return False

    def get_induced_jump_mseq(self) -> Union[MoveSequence, None]:
        """
        If the MoveSequence assumed to be taken by the SmartBot, which led to the OppoBot to be having a MoveSequence with the first move being a Jump over the piece that was moved in the MoveSequence by the SmartBot, and jump is the only available move of the Opponent, then return that Jump, otherwise, return None

        Parameters: None

        Return: Union[MoveSequence, None]: the MoveSequence with the first move beingt the jump induced by the last MoveSequence done by the SmartBot, or None if such induced jump doesn't exist or is not the only available move fro OppoBot
        """
        # get all the MoveSequences available for the OppoBot
        mseq_list = self._get_mseq_list([])

        if len(mseq_list) == 1:
            # only one MoveSequence
            first_move = mseq_list[0].get_move_list()[0]
            if isinstance(first_move, Jump):
                if first_move.get_captured_piece() == self._last_mseq.get_target_piece():
                    # the first move of the MoveSequence is a Jump through the piece just moved by the SmartBot
                    return mseq_list[0]
        return None
