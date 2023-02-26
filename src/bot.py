import math
import random
from copy import deepcopy
from enum import Enum
from typing import List, Tuple, Union
from checkers import Piece, Move, CheckersBoard, PieceColor, Jump, Position


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
    available moves at one turn and complete that move(for test only).

    The bot is expected to only return a list of consecutive that needs to be 
    completed to the GUI and the GUI will be completing the moves

    Note that this class in itself doesn't support any choosing of the move
    from all available moves
    """

    def __init__(self, own_color, checkersboard) -> None:
        """
        construct for a bot

        Parameters:
            own_color(PieceColor): the color of the piece that
                                   the bot is in control of
            checkerboard(CheckersBoard): the checkerboard

        Return: None
        """
        self._own_color = own_color
        self._oppo_color = PieceColor.RED if own_color == PieceColor.BLACK \
            else PieceColor.BLACK
        self._checkersboard = checkersboard
        # initialize a copy of the checkerboard
        self._experimentboard = deepcopy(self._checkersboard)

    def _get_avail_moves(self) -> List[Move]:
        """
        get all the available moves for all pieces according to the color
        that the bot is in control of

        Parameters: None

        Return: List[Move]: a list of all the moves available
        """

        # return a list of all moves available on the experiment board
        return self._experimentboard.get_player_moves(self._own_color)

    def _get_oppo_avail_moves(self) -> List[Move]:
        """
        get all the available moves for all pieces of the opponent

        Parameters: None

        Return: List[Move]: a list of all the moves available
        """

        # return a list of all moves available on the experiment board
        return self._experimentboard.get_player_moves(self._oppo_color)

    def _complete_move(self, move_list) -> bool:
        """
        complete a list of moves that is decided to be taken by the bot, if
        any of the move is invalid, raise an exception

        for test only, the bot will not be completing the move by itself

        Parameters:
            move_list(List[Move]): the move list that is decided to be taken

        Return: Bool: a flag that indicates whether our side didn't lose. False
            if lost, True if not.
        """
        # initialize a list of the possible next steps to take

        # take the moves consecutively in the move_list
        for nxt_move in move_list:
            self._checkersboard.complete_move(nxt_move)

        # there's no moves that we can take, meaning that we've lost
        if not move_list:
            print(f"{self._own_color} loses \n", self._checkersboard)
            return False

        return True


class RandomBot(Bot):
    """
    Represents a bot that is capable of selecting moves randomly
    """

    def __init__(self, own_color, checkersboard) -> None:
        """
        construct for a RandomBot

        Parameters:
            own_color(PieceColor): the color of the piece that
                                   the bot is in control of
            checkerboard(CheckersBoard): the checkerboard

        Return: None
        """
        super().__init__(own_color, checkersboard)

    def choose_move_list(self) -> List[Move]:
        """
        choose a list of the move to take randomly

        Parameters: None

        Return: Union[List[Move]]: the list of move that is chosen, or an empty 
            list when there's no move to take, which means the bot has lost
        """
        # get all the move that can be taken
        nxt_move_list = self._get_avail_moves()
        # initialize a list to contain the move that the output MoveSequence is
        # going to take
        output_move_list = []

        # keep going until reach an place where move is possible
        while nxt_move_list:
            # randomly choose a valid move
            nxt_move = random.choice(nxt_move_list)

            output_move_list.append(deepcopy(nxt_move))
            nxt_move_list = self._experimentboard.complete_move(nxt_move)

        # restore the experimental board
        for move in reversed(output_move_list):
            self._experimentboard.undo_move(move)

        return output_move_list


class MoveSequence:
    """
    Represents a sequence of moves that valid to be chosen by the robot

    This class is specially for the smartbot to use for choosing and 
    completing moves
    """

    def __init__(self, move_list) -> None:
        """
        construct a movesequence

        Parameters:
            move_list(List[Move]): a list of the moves that can be taken 
                                   consecutively
            result_board(CheckersBoard): the result board state if the moves in 
                                         the move list is taken

        Return: None
        """
        self._move_list = move_list

        # initialize the priority of the move sequence to 0
        self._priority = 0

    def get_original_position(self) -> Position:
        """
        get the original position from which the MoveSequence is going to start 

        Parameters: None

        Return: Tuple[int,int]: (x, y) on the board
        """
        return self._move_list[0].get_current_position()

    def get_end_position(self) -> Position:
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
        getter function of the mseq_list of the MoveSequence

        Parameters: None

        Return: List[Move]: the list of moves of the MoveSequence
        """
        return self._move_list

    def get_priority(self) -> float:
        """
        getter function of the priority of the MoveSequence

        Parameters: None

        Return: Float: the priority of the MoveSequence
        """
        return self._priority

    def add_priority(self, add_pri) -> None:
        """
        change the priority of a move sequence

        Parameters:
            add_pri(float): the value that is about to be added to the priority

        Return: None
        """
        self._priority += add_pri


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
    11) more inclined to chase down opponent pieces when leading in the endgame

    citations for the strategies:
    https://www.ultraboardgames.com/checkers/tips.php
    https://www.youtube.com/watch?v=Lfo3yfrbUs0
    https://www.gamblingsites.com/skill-games/checkers/
    https://medium.com/@theflintquill/checkers-eba4d8862719
    """

    def __init__(self, own_color, checkersboard, level) -> None:
        """
        construct for a smart bot

        Parameters:
            own_color(PieceColor): the color of the piece that
                the bot is in control of
            checkerboard(CheckersBoard): the checkerboard
            level(SmartLevel): how smart the bot has to be

        Return: None
        """
        super().__init__(own_color, checkersboard)

        # smart level of the bot, reflecting in how many strategies are adopted
        self._level = level

        # initialize a full list of strategies that can be implemented by the
        # bot
        # it comes with the weight that specifies how much influence should be
        # put into each strategy: List[Tuple(strategy_method, weight)]
        self._strategy_list = [
            (self._winning_priority, None),
            (self._lose_priority, None),
            (self._sacrifice_priority, 1),
            (self._captured_priority, 1),
            (self._corner_priority, 0.7),
            (self._baseline_priority, 4),
            (self._king_priority, 1),
            (self._push_priority, 1),
            (self._chase_priotiy, 0.7),
            (self._stick_priority, 1),
            (self._center_priority, 1),
            (self._force_priority, 1)
        ]
        # construct a dict for the list of stratgies to adopt for different
        # difficulty levels
        # 1) simple level bot implements only winning and lose strategies
        # 2) medium bot implements winning and lose strategies to take a winning
        # move or avoid a losing move, but it also avoid moves that will
        # sacrifice a piece and go for those that can capture more pieces
        # 3) hard level bot implements all the strategies
        self._strategy_dict = {
            SmartLevel.SIMPLE: self._strategy_list[1: 3],
            SmartLevel.MEDIUM: self._strategy_list[1: 5],
            SmartLevel.HARD: self._strategy_list
        }

        # this is just for test, include specific strategies functionsthat we
        # want to test
        self._strategy_list_test = [
            (self._chase_priotiy, 0.1)]

    def choose_move_list(self) -> List[Move]:
        """
        choose the list of move to take

        A MoveSequence would be chosen according to the smart level of the
        bot, the higher the smart level, the more strategies that the
        choosing would take into consideration

        Parameters: None

        Return: List[Move]: the list of moves that is chosen, or return [] when 
            we don't have any moves
        """

        # get the MoveSequence list with the priority specified according to
        # the stratgies adopted by the bot
        weighted_mseq_list = self._get_mseq_list(
            self._strategy_dict[self._level])

        # check whether there is any MoveSequence we can take
        if weighted_mseq_list:
            # return the move list of the movesequence with the highest priority
            # https://www.programiz.com/python-programming/methods/built-in/max

            max_priority_mseq = max(
                weighted_mseq_list,
                key=lambda m: m.get_priority()).get_move_list()

            return max_priority_mseq

        # we don't have any move to take, i.e. , we've lost
        return []

    def _get_mseq_list(self, strategy_list) -> List[MoveSequence]:
        """
        initialize a list of MoveSequences that we can take with their priority
        updated according to different strategies

        Parameters: 
            strategy_list(List[Tuple(Functionsm, float)]): a list of functions
                that updates the priority of a MoveSequence according to some
                strategy and their correponding weight

        Return: List[MoveSequence]:
                A list of all possible MoveSequences with their updated priority
        """
        # get all the immediate next moves that are possible
        nxt_move_list = self._get_avail_moves()
        Movesequence_list = []

        def helper(move_list, curr_path) -> None:
            """
            a helper funciton to recursively find out all possible move 
            sequences and update the output_list accordingly

            Parameters:
                move_list(List[Move]): a list of the next step that can be taken
                curr_path(List[Move]): a list of that keeps track of the current
                    path of moves taken
                curr_board(CheckersBoard): represent the current board state

            Return: None
            """
            if not move_list and curr_path:
                # if there's no move in the list, reached the end
                # of one potential move list, create a corresponding
                # MoveSequence and add that to the Movesequence_list with its
                # priority
                mseq = MoveSequence(
                    curr_path[:])
                self._assign_priority(mseq, strategy_list)
                Movesequence_list.append(mseq)

            # traverse through all the possible next moves, take the moves
            # on a cloned board and recursively call helper
            for nxt_move in deepcopy(move_list):
                # update the path and the board state

                curr_path.append(deepcopy(nxt_move))

                # complete the next move

                valid_nxt_list = self._experimentboard.complete_move(nxt_move)

                # the recursive step
                helper(valid_nxt_list, curr_path)

                self._experimentboard.undo_move(nxt_move)
                curr_path.pop()

        # update the output_list
        helper(nxt_move_list, [])

        return Movesequence_list

    def _assign_priority(self, mseq, strategy_list) -> None:
        """
        update the priority of the MoveSequences according to a set of 
        strategies

        Parameters:
            mseq(Movesequence): the MoveSequence about to be updated
                strategy_list(List[Tuple(Functionsm, float)]): a list of 
                functions that are going to be applied for the update of the 
                priority and their corresponding weights

        Return: None
        """
        # update the priority with respect to every strategy
        for strat_func, weight in strategy_list:
            if mseq.get_priority() not in [math.inf, -math.inf]:
                # no winning or losing MoveSequence detected yet
                if weight is not None:
                    # has a weight
                    mseq.add_priority(strat_func(mseq, weight))
                else:
                    # doesn't have a weight, namely winning_priority and
                    # lose_priority
                    mseq.add_priority(strat_func(mseq))
            elif mseq.get_priority() == math.inf:
                # exists a winning MoveSequence, take that to win the game
                break
            else:
                # the current MoveSequence is a losing mseq, already set to
                # -math.inf, pass
                pass

    def _distance(self, pos1, pos2) -> float:
        """
        Calculated the distane between two position on the board

        Parameters:
            pos1(checkers.Position): the (x, y) on the board of the starting
                point
            pos2(checkers.Position): the (x, y) on the board of the end point

        Return: float: the calculated the distance from the 
        """
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def _corner_priority(self, mseq, weight) -> float:
        """
        update the priority of the MoveSequence with the consideration of
        attacking the opponent's double corner when

        It would only cause our pieces to be more inclined to move attack
        opponent's double corner when opponent's double corner is not vacant

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be
                updated
            weight(float): a float that determine how much of an influence this
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the
            corner strategy
        """
        # get the original and the end position of a MoveSequence
        origin_pos = mseq.get_original_position()
        end_pos = mseq.get_end_position()

        # get the position of our double corner and the opponent's double
        # corner according to bot's own piece color
        if self._own_color == PieceColor.RED:
            oppo_double_pos = (0, 0)

        elif self._own_color == PieceColor.BLACK:
            oppo_double_pos = (self._experimentboard.get_board_width(),
                               self._experimentboard.get_board_width())

        attack_score = 0
        for oppo_piece in \
                self._experimentboard.get_color_avail_pieces(self._oppo_color):
            if self._distance(oppo_piece.get_position(), oppo_double_pos)\
                    <= math.sqrt(5):
                # if there exists any opponent piece that is within 2 steps to
                # opponents double corner, more inclined to move towards oppo's
                # double corner
                attack_score = self._distance(
                    oppo_double_pos, origin_pos) - \
                    self._distance(oppo_double_pos, end_pos)
        return weight * attack_score

    def _baseline_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of holding the baseline. 

        More specifically, we are more inclined to hold the anchor checkers on
        the baseline as defense. The anchor checkers are the checkers that is
        on every other square starting from our double corner. For example, if
        we have an 8-columns board, so 4 checkers each row, the anchor checkers
        would be the first and the third checkers on our baseline row counting
        from the double corner

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be
                updated
            weight(float): a float that determine how much of an influence this
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the
            hold base line strategy
        """
        # set up the original position of the MoveSequence
        origin_pos = mseq.get_original_position()
        # initialize a list that's going to take the anchor positions
        anchor_pos_list = []
        # get the borad witdh
        boardwidth = self._experimentboard.get_board_width()

        # determine the anchor positions according to our piece color
        if self._own_color == PieceColor.RED:
            # we control the red piece
            for n in range(boardwidth - 2, -1, -4):
                anchor_pos_list.append(
                    (n, boardwidth - 1))
        elif self._own_color == PieceColor.BLACK:
            # we control the black piece
            for n in range(1, boardwidth, 4):
                anchor_pos_list.append((n, 0))

        baseline_score = 0
        if origin_pos in anchor_pos_list:
            # if the MoveSequence is going to move an anchor checker, decrease
            # the baseline_score
            baseline_score -= 1

        return weight * baseline_score

    def _king_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of getting a king

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated
            weight(float): a float that determine how much of an influence this 
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the 
            kinging strategy
        """
        # get a flag that indicates whether the target piece of a moving #
        # sequence is already a king
        prev_king = mseq.get_target_piece().is_king()

        # find the baseline row that our side aim at to king
        baseline = {PieceColor.RED: 0,
                    PieceColor.BLACK:
                    self._experimentboard.get_board_width() - 1}

        if (not prev_king) and \
                mseq.get_end_position()[1] == baseline[self._own_color]:
            # the MoveSequence is a moving previously non-kinged piece to the
            # kinging row, thus kinging the piece
            king_score = 1
        else:
            # the piece was previously a king or isn't moved to the kinging row
            king_score = 0

        return weight * king_score

    def _sacrifice_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of sacrifice

        Sometimes making a move means sacrificing the piece we are moving, we 
        don't want to do this blindly so this function serves as a restricting 
        method so that we don't blindly sacrifice our pieces for no reason.

        However, we are more willing to sacrifice pieces when we are leading

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated
            weight(float): a float that determine how much of an influence this 
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the 
            sacrificing strategy
        """
        # construct an instance of the opponent
        Opponent = OppoBot(self._oppo_color,
                           self._experimentboard, mseq, self._level)

        oppo_jump_list = Opponent.get_induced_jump_mseq()
        if oppo_jump_list:
            # this MoveSequence leads to a sacrifice

            # get the initial number of pieces for each side and the current
            # number of pieces for each side
            num_piece = self._experimentboard.get_board_width()/2 - 1
            my_pieces = self._experimentboard.get_color_avail_pieces(
                self._own_color)
            oppo_pieces = self._experimentboard.get_color_avail_pieces(
                self._oppo_color)

            # intialize a list to take the sacrifice score
            score_list = []
            # traverse through all the induced jump movesequences
            for oppo_jump in oppo_jump_list:
                # depict the difference of the number of pieces between both
                # sides, always negative, the more pieces we have over the
                # opponent, the smaller the absolute value.
                difference_factor = num_piece - \
                    (len(my_pieces) - len(oppo_pieces))
                # sacrifice core is bigger when (1)more pieces are captured (2)
                # The more the opponent pieces is more than mine (3) a king is
                # captured rather than a normal piece
                score_list.append(Opponent._captured_priority(
                    oppo_jump, 1) * difference_factor)

            return - weight * max(score_list)

        # this MoveSequence doesn't lead to a sacrifice
        return 0

    def _chase_priotiy(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the 
        consideration of chasing after opponents pieces when we're in the 
        endgame

        We only consider this strategy when the opponent has relatively small 
        number of pieces remain and we are leading! Chasing after oppponent 
        when we are not leading is dangerous. Additionally, this will only be 
        implmented when the boardwidth is >= 8, or chasing would be pointless 
        and dangerous

        Note that we chase after the piece that is closest to our piece about 
        to be moved by the MoveSequence

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated
            weight(float): a float that determine how much of an influence this 
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the 
            capture priority
        """
        # check whether the board has a width longer than 8
        if self._experimentboard.get_board_width() < 8:
            # small board, don't implement this strategy
            return 0

        # get the number of the available pieces on both side
        oppo_avail_pieces = \
            self._experimentboard.get_color_avail_pieces(self._oppo_color)
        our_avail_pieces = \
            self._experimentboard.get_color_avail_pieces(self._own_color)
        oppo_avail_num = len(oppo_avail_pieces)
        our_avail_num = len(our_avail_pieces)

        # get the original number of pieces for the opponent
        oppo_total_num = self._experimentboard.get_board_width() / 2\
            * (self._experimentboard.get_board_width() / 2 - 1)

        # check the following two requirements:
        # 1) whether the available opponent pieces is less than 1/4 than the
        # original number of pieces, which means we've entered the endgame
        # 2) whether we have more than 1.5 times of pieces than the opponent,
        # which means we are still leading considerably
        if oppo_avail_num > oppo_total_num / 4 or\
                our_avail_num <= 1.5 * oppo_avail_num:
            # at least one of the requirement is not satisfied
            return 0
        else:
            # initialize a tuple used to record information about the target
            # piece we are chasing after
            # The first element is to store the distance from our piece and the
            # target piece, the second element stores the position of the
            # target piece
            target_tuple = (math.inf, 0)

            # traverse through all opponent's pieces and find the closest piece
            # to the target piece of our MoveSequence
            for oppo_piece in oppo_avail_pieces:
                dist = self._distance(oppo_piece.get_position(),
                                      mseq.get_original_position())
                if dist < target_tuple[0]:
                    # if the distance is smaller than the previously least
                    # ditance, update the target_tuple with this new target
                    # piece
                    target_tuple = (dist, oppo_piece.get_position())

            # chase_score would be higher the more the MoveSequence is moving
            # to the target piece
            chase_score = target_tuple[0] - \
                self._distance(target_tuple[1], mseq.get_end_position())
            return chase_score * weight

    def _captured_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the 
        consideration of capturing as many opponent pieces as possible. 
        Capturing a king weighs more than capturing a normal piece

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated
            weight(float): a float that determine how much of an influence this 
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the 
            capture priority
        """
        # initialize a score to record the significance of capture of this mseq
        capture_score = 0
        for move in mseq.get_move_list():
            if isinstance(move, Jump):
                # if the move is a jump, determine whether it's capturing a
                # king or a normal piece
                if move.get_captured_piece().is_king():
                    capture_score += 2
                else:
                    capture_score += 1

        return weight * capture_score

    def _push_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of pushing forward

        Note that this strategy doesn't apply to kings as the major benefit of 
        pushing forward is to get kings. 

         Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated
            weight(float): a float that determine how much of an influence this 
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the 
            push priority
        """
        # if the MoveSequence is moving a king, then pass
        if mseq.get_target_piece().is_king():
            return 0

        # get the original and end position for a MoveSequence
        origin_pos = mseq.get_original_position()
        end_pos = mseq.get_end_position()

        if self._own_color == PieceColor.RED:
            # we control the red piece
            push_score = origin_pos[1] - end_pos[1]
        elif self._own_color == PieceColor.BLACK:
            # we control the black piece
            push_score = end_pos[1] - origin_pos[1]

        return weight * push_score

    def _stick_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the 
        consideration of not leaving a single piece out

        We want to favor MoveSequences that lead to the moved piece at least 
        having one piece of our side around it.

        Note that this only address the scenario where a MoveSequence has 
        caused the piece to get not sticked with our pieces. If it was 
        originally not sticked to our pieces, this method won't penalize the 
        MoveSequence as it's not what's causing the detachment.

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated
            weight(float): a float that determine how much of an influence this 
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the 
            stick strategy
        """

        # get the end position and original position of the target piece and
        # construct the four possible positions that could be having a piece
        # around it for both cases
        end_pos = mseq.get_end_position()
        end_near_region = [(end_pos[0] - 1, end_pos[1] - 1),
                           (end_pos[0] - 1,  end_pos[1] + 1),
                           (end_pos[0] + 1, end_pos[1] - 1),
                           (end_pos[0] + 1, end_pos[1] + 1)]

        original_pos = mseq.get_original_position()
        original_near_region = [(original_pos[0] - 1, original_pos[1] - 1),
                                (original_pos[0] - 1, original_pos[1] + 1),
                                (original_pos[0] + 1, original_pos[1] - 1),
                                (original_pos[0] + 1, original_pos[1] + 1)]

        # initilize two flags to record whether the target piece was sticked to
        # our pieces and currently sticked to our pieces
        past_stick, now_stick = False, False

        # check whether there exists a piece in the near region of the target
        # piece
        for piece in \
                self._experimentboard.get_color_avail_pieces(self._own_color):
            if piece.get_position() in original_near_region:
                # there exists a piece in the original near region
                past_stick = True
            if piece.get_position() in end_near_region:
                # there exists a piece in the end near region
                now_stick = True

        if past_stick and not now_stick:
            # there's no piece around the near region, but before the
            # MoveSequence there is
            return - weight

        # either it's still sticked to a piece, or it was originally not
        # sticked to any piece before the MoveSequence
        return 0

    def _center_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSeuqnce with the consideration
        of occupying the center

        For typical 8 * 8 checkerboards, the center refers to the 8 positions 
        in the center 4 columns and the center 2 columns. We want to push into 
        the center regions because we want to avoid staying on the side of the 
        board Therefore, to generalize this to a w * w checkerboards, the 
        center region shall be column 3 to column w -2 and the center rows that 
        are without any pieces at the beginning of the round

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated
            weight(float): a float that determine how much of an influence this 
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the 
            center strategy
        """
        # get the original position and the end position of the MoveSequence
        origin_pos = mseq.get_original_position()
        end_pos = mseq.get_end_position()

        # get the board width
        boardwidth = self._experimentboard.get_board_width()

        centering_score = 0
        # specify the center region
        center = [range(2, boardwidth - 2),
                  range(int(boardwidth / 2) - 1, int(boardwidth / 2) + 1)]

        if (origin_pos[0] not in center[0]) or (origin_pos[1] not in center[1]):
            # the original position is not in the center region
            if (end_pos[0] in center[0]) and (end_pos[1] in center[1]):
                # the end position is in center region
                centering_score = 1

        return weight * centering_score

    def _winning_priority(self, mseq) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of the existence of a winning move. 

        If there exists a winning move in the given move sequence, this 
        MoveSequence is automatically taken

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated

        Return: float: the value to add to priority to mseq according to the 
            winning strategy, if the MoveSequence doesn't contain a winning 
            move, we return the original priority, otherwise, we return inf
        """
        # get all the moves that opponents can make if taking this MoveSequence
        oppo_moves = self._get_oppo_avail_moves()
        if oppo_moves:
            # the MoveSequence contains no winning move
            return 0
        else:
            # the MoveSequence contains a winning move
            return math.inf

    def _lose_priority(self, mseq) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of the existence of a losing move.

        A losing move is defined as an move that will lead to the existence of 
        a winning move for the opponent, i.e., the opponent can win next round. 

        If there exists a losing move in a MoveSequence, we avoid taking that 
        MoveSequence. However, if all the MoveSequences contains a losing move, 
        we randomly select a move(at that point the game would already be over)

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated

        Return: float: the value to add to priority to mseq according to the 
            lose strategy, if the MoveSequence doesn't contain a losing move, 
            we return the original priority, otherwise, we return -math.inf
        """
        # construct an instance of the opponent
        Opponent = OppoBot(self._oppo_color, self._experimentboard, mseq,
                           self._level)

        # check whether there is a winning move for the opponent if we take
        # this MoveSequence
        if Opponent.contains_winning_mseq():
            return - math.inf
        else:
            return 0

    def _force_priority(self, mseq, weight) -> float:
        """
        update the priority of an avialable MoveSequence when that MoveSequence 
        leads to forcing 

        To be more precise, sometimes a MoveSequence will lead to a sacrifice, 
        but sometimes this sacrifice is a part of the strategy called forcing. 
        Basically, we force the opponent to capture our pieces only to build up 
        a bridge for us to capture their pieces in our next round.

        We call the forced jump and consecutive moves of the Opponent the 
        induced jump MoveSequence, and call our MoveSequence that can capture 
        this piece moved by the induced jump MoveSequence in the following 
        round response MoveSequence.

        Note that the induced jump MoveSequence should be unique to be 
        considered in forcing strategy, if the jump is induced by the opponent 
        has a choice, forcing tends to get really complicated

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated
            weight(float): a float that determine how much of an influence this 
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the 
            forcing strategy
        """
        # construct an instance of the opponent
        Opponent = OppoBot(self._oppo_color, self._experimentboard, mseq,
                           self._level)

        # get the induced jump MoveSequence of the opponent
        oppo_mseq_list = Opponent.get_induced_jump_mseq()
        if len(oppo_mseq_list) == 1:
            # if there is this unique induced jump MoveSequence, update the
            # board to the state that assumes the opponent has taken this move
            oppo_mseq = oppo_mseq_list[0]
            oppo_move_list = oppo_mseq.get_move_list()
            for move in oppo_move_list:
                self._experimentboard.complete_move(move)

            induced_piece = self._experimentboard._pieces[
                oppo_mseq.get_end_position()]

            # get what would our available MoveSequence be for the next turn if
            # we forced the Opponent's induced jump MoveSequence
            nxt_turn_mseq = self._get_mseq_list([])

            # initialize a list to take the updated priority of Movesequences
            # that are respnse MoveSequences
            response_priority = []
            for mseq in nxt_turn_mseq:
                # get the first move in the MoveSequence
                first_move = mseq.get_move_list()[0]
                if isinstance(first_move, Jump):
                    if first_move.get_captured_piece() == induced_piece:
                        # this MoveSequence is a response Movesequence, i.e. it
                        # is a jump and capture the piece moved by the opponent
                        # in its last inducde jump MoveSequence
                        response_priority.append(
                            self._captured_priority(mseq, weight))

            # restore the board to the current round before we anticipate any
            # opponents moves
            for move in reversed(oppo_move_list):
                self._experimentboard.undo_move(move)

            # return the priority that corresponds to the most pieces captured
            # if there exists any response MoveSequence
            if response_priority:
                return max(response_priority)

        # our MoveSequence this round is not leading to an induced jump
        # MoveSequence
        return 0


class OppoBot(SmartBot):
    """
    Represent a bot used to try what will the opponent do if the SmartBot has 
    taken a MoveSequence.

    Note that this bot is strictly for anticipation purposes of the SmartBot 
    when making decisions. It works under the premise that the SmartBot has 
    taken a specific MoveSequence and is used to show the corresponding 
    reaction to this MoveSequence that the opponent would have
    """

    def __init__(self, own_color, checkersboard, last_mseq,
                 level) -> None:
        """
        Construct a bot that represents the opponent

        Parameters:
            own_color(PieceColor): the color of the piece that the bot is in 
                control of
            checkerboard(CheckersBoard): the checkerboard
            last_mseq(MoveSequence): represents the move sequence that we 
                asssumed to be taken by the SmartBot
            level(SmartLevel) : the SmartLevel that we are giving the Oppobot, 
                should be the same as the SmartBot

        Return: None
        """
        super().__init__(own_color, checkersboard, level)

        # initialize the move sequence assumed to be taken by the SmartBot
        self._last_mseq = last_mseq

    def contains_winning_mseq(self) -> bool:
        """
        Examine whether there exists a MoveSequence that contains a winning move

        Parameters: None

        Return: bool: True if there exists a winning MoveSequence, False 
            Otherwise
        """
        # get all the possible move sequences and examine whether they contain
        # winning moves
        mseq_list = self._get_mseq_list([(self._winning_priority, None)])

        for mseq in mseq_list:
            if mseq.get_priority() == math.inf:
                # there exists a winning MoveSequence
                return True
        return False

    def get_induced_jump_mseq(self) -> List[Union[MoveSequence, None]]:
        """
        If the MoveSequence assumed to be taken by the SmartBot, which led to 
        the OppoBot to be having a or more MoveSequence with the first move 
        being a Jump over the piece that was moved in the MoveSequence by the 
        SmartBot, and those jumps are the only available moves of the Opponent, 
        then return a list of those MoveSequences that contains those jumps, 
        otherwise, return None

        Parameters: None

        Return: List[Union[MoveSequence, None]]: the MoveSequence with the 
            first move beingt the jump induced by the last MoveSequence done by 
            the SmartBot, or None if such induced jump doesn't exist or is not 
            the only available move fro OppoBot
        """
        # get all the MoveSequences available for the OppoBot
        mseq_list = self._get_mseq_list([])
        # initialize an output list
        output_list = []
        for mseq in mseq_list:
            first_move = mseq.get_move_list()[0]
            # check out whether the first move is a jump
            if isinstance(first_move, Jump):
                if first_move.get_captured_piece() ==\
                        self._experimentboard._pieces[self._last_mseq.get_end_position()]:
                    # the first move of the MoveSequence is a Jump through the
                    # piece just moved by the SmartBot
                    output_list.append(mseq)

        return output_list
