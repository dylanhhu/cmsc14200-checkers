'''
This file is for the construction of classes of both a random bot and a smart 
bot. Either an instance of the random bot or the smart bot would be created in 
response to a specific turn, and the purpose of the bot is to return a sequence 
of moves that is decided to be taken in this turn.

If the bot is a random bot, it would be picking the sequence of moves randomly, 
but if it's a smart bot, it will implement different strategies based on 
different smart levels

A brief description of some of the notable classes are listed below:
- 'Bot': basic construction of a bot
- 'RandomBot': inheritance from class 'Bot', able to choose a list of moves 
    randomly
- 'MoveSequence': used to represent a valid sequence of consecutive moves to    
    take in a turn
- 'SmartBot': inheritance from class 'Bot', able to choose a list of moves      
    with considerations of a list of strategies
- 'OppoBot': inheritance from class 'SmartBot', used by the SmartBot in some 
    strategies to predict the moves that the opponent can take

A brief process of the smart bot choosing the list of move to take for one 
turn is as the following:
    1) call 'SmartBot._choose_move_list'. This method would call 'SmartBot.
    _get_mseq_list with the corresponding strategy list with the strategies 
    that is going to be adopted by the bot

    2) 'SmartBot._get_mseq_list' would run a depth first search on the current 
    board to traverse through all the possible sequences of moves: each time 
    that it reaches the end of a list of moves, it will create a MoveSequence 
    instance to represent that list of moves, and call 'SmartBot.
    _assign_priority' with that MoveSequence and a list of strategies to adopt 
    to assign a priority to that MoveSequence

    3) 'SmartBot._assign_priority' would assign a priority value to the target 
    MoveSequence based on all the strategies in the list and store that in an 
    attribute in the MoveSequence

    4) 'SmartBot._get_mseq_list' will return a list of all the MoveSequences 
    with their priority assigned to 'SmartBot._choose_move_list'

    5) 'SmartBot._choose_move_list' would randomly pick out a MoveSequence with 
    the highest priority value and return the list of moves in this MoveSequence

Citations:
    https://www.ultraboardgames.com/checkers/tips.php
    https://www.youtube.com/watch?v=Lfo3yfrbUs0
    https://www.gamblingsites.com/skill-games/checkers/
    https://medium.com/@theflintquill/checkers-eba4d8862719
    https://www.programiz.com/python-programming/methods/built-in/max
    https://stackoverflow.com/questions/57548827/       
        how-to-get-a-random-maximum-from-a-list
'''

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
    Represents a fundamental structure of the bot with basic abilities to
    get the next available move of our side and the opponent.

    Note that this class in itself doesn't support any choosing of the move
    from all available moves. This Bot will not be functioning on its own but 
    will be functioning by inherited by SmartBot and RandomBot
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
        # initialize a copy of the checkerboard that is used for experimenting
        # our moves
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

        Return: List[Move]: the list of move that is chosen, or an empty 
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
    Represents a sequence of moves that is  valid to be chosen by the robot

    This class is specially for the SmartBot to use for choosing and 
    completing moves
    """

    def __init__(self, move_list) -> None:
        """
        construct a MoveSequence

        Parameters:
            move_list(List[Move]): a list of the moves that can be taken 
                consecutively

        Return: None
        """
        self._move_list = move_list

        # initialize the priority of the move sequence to 0
        self._priority = 0

    def get_original_position(self) -> Position:
        """
        get the original position from which the MoveSequence is going to start 

        Parameters: None

        Return: Position: (x, y) on the board
        """
        return self._move_list[0].get_current_position()

    def get_end_position(self) -> Position:
        """
        get the end position to which the MoveSequence is going to head

        Parameters: None

        Return: Position: (x, y) on the board
        """
        return self._move_list[-1].get_new_position()

    def get_target_piece(self) -> Piece:
        """
        get the piece that is moved in this move sequence

        Parameters: None

        Return: Piece: the piece that is moved
        """
        return self._move_list[0].get_piece()

    def get_move_list(self) -> List[Move]:
        """
        getter function of the move_list of the MoveSequence

        Parameters: None

        Return: List[Move]: the list of moves of the MoveSequence
        """
        return self._move_list

    def get_priority(self) -> float:
        """
        getter function of the priority of the MoveSequence

        Parameters: None

        Return: float: the priority of the MoveSequence
        """
        return self._priority

    def add_priority(self, add_pri) -> None:
        """
        add the priority of a MoveSequence with a certain value

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
    2) more inclined to hold two anchor checkers in the baseline
    3) more inclined to get kings
    4) more inclined to sacrifice pieces when leading
    5) more inclined to pick the MoveSequence that capture the most opponent 
        pieces
    6) more inclined to push forward a Piece that is not a king
    7) more inclined to occupy the center
    8) able to conduct the wining move if possible
    9) able to avoid a losing move if possible
    10) more inclined to make our pieces stick together
    11) more inclined to conduct forcing when possible
    12) more inclined to chase down opponent pieces when leading in the endgame

    citations for the strategies:
    https://www.ultraboardgames.com/checkers/tips.php
    https://www.youtube.com/watch?v=Lfo3yfrbUs0
    https://www.gamblingsites.com/skill-games/checkers/
    https://medium.com/@theflintquill/checkers-eba4d8862719
    """

    def __init__(self, own_color, checkersboard, level) -> None:
        """
        construct for a SmartBot

        Parameters:
            own_color(PieceColor): the color of the piece that
                the bot is in control of
            checkerboard(CheckersBoard): the current checkerboard
            level(SmartLevel): how smart the bot has to be

        Return: None
        """
        super().__init__(own_color, checkersboard)

        # smart level of the bot, reflecting in how many strategies are adopted
        self._level = level

        # initialize two containers for 1)an opponent instance 2) a
        # MoveSequence with an induced jump in response to our MoveSequences
        # which is going to be used latter for predicting opponents moves
        # according to our moves(these two are used internally only in some
        # strategies)
        self._curr_oppo = None
        self._curr_oppo_induced = None

        # initialize a full list of strategies that can be implemented by the
        # bot
        # it comes with the weight that specifies how much influence should be
        # put into each strategy: List[Tuple(strategy_method, weight)]. It
        # should be noted that the weight can be adjusted to improve the
        # performance of the bot or to make the bot put more or less emphasis
        # on one or several strategies
        self._strategy_list = [
            (self._winning_priority, None),
            (self._lose_priority, None),
            (self._chase_priority, 0.7),
            (self._stick_priority, 1),
            (self._baseline_priority, 4),
            (self._push_priority, 1),
            (self._center_priority, 1),
            (self._sacrifice_priority, 0.05),
            (self._captured_priority, 1),
            (self._corner_priority, 0.7),
            (self._king_priority, 1),
            (self._force_priority, 1)
        ]
        # construct a dict for the list of strategies to adopt for different
        # difficulty levels
        # 1) simple level bot implements only winning and lose strategies,
        # stick together, and to chase down opponents pieces in the endgame
        # 2) medium bot implements winning and lose strategies to take a winning
        # move or avoid a losing move, but it also has a sense of chasing
        # opponent, holding the baseline and pushing while sticking to other
        # pieces
        # 3) hard level bot implements all the strategies
        self._strategy_dict = {
            SmartLevel.SIMPLE: self._strategy_list[0: 4],
            SmartLevel.MEDIUM: self._strategy_list[0: 7],
            SmartLevel.HARD: self._strategy_list
        }

    def choose_move_list(self) -> List[Move]:
        """
        choose the list of moves to take in this turn

        A list of moves would be chosen according to the smart level of the
        bot, the higher the smart level, the more strategies that the
        choosing would take into consideration.

        It will choose the list of moves with the largest priority, but if there
        are multiple lists of moves with the same largest priority. It will 
        randomly choose one to avoid the Bot acting in a fixed pattern and take 
        the game to a loop scenario

        Parameters: None

        Return: List[Move]: the list of moves that is chosen, or return [] when 
            we don't have any moves
        """

        # get the MoveSequence list with the priority specified according to
        # the strategies adopted by the bot
        weighted_mseq_list = self._get_mseq_list(
            self._strategy_dict[self._level])

        # check whether there is any MoveSequence we can take
        if weighted_mseq_list:
            # get the largest priority
            max_priority = max(mseq.get_priority()
                               for mseq in weighted_mseq_list)

            # get a random MoveSequence with the max priority
            return_mseq = random.choice([mseq for mseq in weighted_mseq_list
                                         if mseq.get_priority() ==
                                         max_priority])

            return return_mseq.get_move_list()

        # we don't have any move to take, i.e. we've lost
        return []

    def _get_mseq_list(self, strategy_list) -> List[MoveSequence]:
        """
        get a list of MoveSequences that we can take with their priority
        updated according to different strategies

        Parameters: 
            strategy_list(List[Tuple(Function, float)]): a list of functions
                that updates the priority of a MoveSequence according to some
                strategies and their corresponding weights

        Return: List[MoveSequence]:
            A list of all possible MoveSequences with their updated priority
        """
        # get all the immediate next moves that are possible
        nxt_move_list = self._get_avail_moves()
        Movesequence_list = []

        def helper(move_list, curr_path) -> None:
            """
            a helper function to recursively find out all possible move 
            sequences and update the output_list accordingly

            Parameters:
                move_list(List[Move]): a list of the next step that can be taken
                curr_path(List[Move]): a list of that keeps track of the current
                    path of moves taken

            Return: None
            """
            if not move_list and curr_path:
                # if there's no move in the list, reached the end
                # of one potential move list, create a corresponding
                # MoveSequence and add that to the Movesequence_list with its
                # priority

                mseq = MoveSequence(curr_path[:])

                # clear self._curr_oppo and self._curr_oppo_induced for the new
                # MoveSequence
                self._curr_oppo, self._curr_oppo_induced = None, None

                # assign priority and append the processed mseq into the list
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

                # restore the experiment board and the curr_path
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
            mseq(MoveSequence): the MoveSequence about to be updated
            strategy_list(List[Tuple(Function, float)]): a list of 
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
            else:
                # the current MoveSequence is a losing mseq or winning mseq,
                # there's nothing that can change the priority of the mseq
                # anymore
                break

    def _distance(self, pos1, pos2) -> float:
        """
        Calculated the distance between two positions on the board

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
        attacking the opponent's double corner

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
        # get the board width
        boardwidth = self._experimentboard.get_board_width()

        # determine the anchor positions according to our piece color
        if self._own_color == PieceColor.RED:
            # we control the red piece
            for n in range(boardwidth - 2, -1, -4):
                anchor_pos_list.append((n, boardwidth - 1))
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
        prev_king_flag = mseq.get_target_piece().is_king()

        # find the baseline row that our side aim at to king
        baseline = {PieceColor.RED: 0,
                    PieceColor.BLACK:
                    self._experimentboard.get_board_width() - 1}

        if (not prev_king_flag) and \
                mseq.get_end_position()[1] == baseline[self._own_color]:
            # the MoveSequence is a moving previously non-kinged piece to the
            # kinging row, thus kinging the piece
            king_score = 1
        else:
            # the piece was previously a king or isn't moved to the kinging row
            king_score = 0

        return weight * king_score

    def _chase_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the 
        consideration of chasing after opponents pieces when we're in the 
        endgame

        We only consider this strategy when the opponent has relatively small 
        number of pieces remain and we are leading! Chasing after the opponent 
        when we are not leading is dangerous. Additionally, this will only be 
        implemented when the board width is >= 8, or chasing would be pointless 
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
                    # distance, update the target_tuple with this new target
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

    def _sacrifice_priority(self, mseq, weight) -> float:
        """
        update the priority of the available MoveSequence with the consideration
        of sacrificing pieces

        Sometimes making a move means sacrificing the piece we are moving, we 
        don't want to do this blindly so this function serves as a restricting 
        method so that we don't blindly sacrifice our pieces for no reason.

        We call the move that the opponent is forced to take which captures the 
        piece we just moved the "induced jump". Sacrifice would only be counted 
        if such an induced jump exist and the opponent has no choice but to 
        conduct this move, i.e. our moved piece would definitely be captured

        However, we are more willing to sacrifice pieces when we are leading

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated
            weight(float): a float that determine how much of an influence this 
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the 
            sacrificing strategy
        """
        # check whether an opponent and its induced jump MoveSequence has
        # already been constructed for our mseq. If not, construct them
        if not self._curr_oppo:
            self._curr_oppo = OppoBot(self._oppo_color,
                                      self._experimentboard, mseq, self._level)
        if not self._curr_oppo_induced:
            self._curr_oppo_induced = self._curr_oppo.get_induced_jump_mseq()

        # check whether the current MoveSequence will lead to a induced jump
        if self._curr_oppo_induced:
            # this MoveSequence leads to a sacrifice

            # get the initial number of pieces for each side and the current
            # number of pieces for each side
            num_piece = (self._experimentboard.get_board_width()/2 - 1) * \
                self._experimentboard.get_board_width()/2
            my_avail_pieces = self._experimentboard.get_color_avail_pieces(
                self._own_color)
            oppo_avail_pieces = self._experimentboard.get_color_avail_pieces(
                self._oppo_color)

            # initialize a list to take the sacrifice score
            score_list = []
            # traverse through all the induced jump MoveSequences
            for oppo_jump in self._curr_oppo_induced:
                # depict the difference of the number of pieces between both
                # sides, always positive, the more pieces we have over the
                # opponent, the smaller the value.
                difference_factor = num_piece - \
                    (len(my_avail_pieces) - len(oppo_avail_pieces))
                # sacrifice core is bigger when (1)more pieces are captured (2)
                # The more the opponent pieces is more than mine (3) a king is
                # captured rather than a normal piece. This is achieved through
                # calling _captured_priority on the OppoBot to evaluate how
                # much is the lost of our sacrifice MoveSequence
                score_list.append(self._curr_oppo._captured_priority(
                    oppo_jump, 1) * difference_factor)

            return - weight * max(score_list)

        # this MoveSequence doesn't lead to a sacrifice
        return 0

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

        # check which side are we on to make sure we make push_score reflecting
        # the push for each side
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

        # initialize two flags to record whether the target piece was sticked to
        # our pieces and currently sticked to our pieces
        past_stick, now_stick = False, False

        # check whether there exists a piece in the near region of the target
        # piece
        for piece in \
                self._experimentboard.get_color_avail_pieces(self._own_color):
            if piece.get_position() == mseq.get_end_position():
                # the piece is the moved piece and should be ignored
                continue
            if past_stick and now_stick:
                # found that there exists a piece on our side both in the
                # original near region and the end region already, directly
                # return
                return 0
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
        update the priority of the available MoveSequence with the consideration
        of occupying the center

        For typical 8 * 8 checkerboards, the center refers to the 8 positions 
        in the center 4 columns and the center 2 columns. We want to push into 
        the center regions because we want to avoid staying on the side of the 
        board Therefore, to generalize this to a w * w checkerboards, the 
        center region shall be column 3 to column w - 2 and the center rows 
        that are without any pieces at the beginning of the round

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

        We only consider this strategy when there's below 4 pieces on our side 
        given that it's not very likely that the opponent can win next round if 
        we still have some pieces (most of them would have to be stuck with no 
        moves which is unlikely)

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated

        Return: float: the value to add to priority to mseq according to the 
            lose strategy, if the MoveSequence doesn't contain a losing move, 
            we return the original priority, otherwise, we return -math.inf
        """
        # get the number of pieces left
        our_avail_pieces = \
            self._experimentboard.get_color_avail_pieces(self._own_color)
        our_avail_num = len(our_avail_pieces)

        # check whether we still have more than 4 pieces
        if our_avail_num > 4:
            # we have more than 4 pieces, skip this priority
            return 0

        # check whether an opponent already been constructed for our mseq
        if not self._curr_oppo:
            # if not, construct it
            self._curr_oppo = OppoBot(self._oppo_color,
                                      self._experimentboard, mseq, self._level)

        # check whether there is a winning move for the opponent if we take
        # this MoveSequence
        if self._curr_oppo.contains_winning_mseq():
            return - math.inf
        else:
            return 0

    def _force_priority(self, mseq, weight) -> float:
        """
        update the priority of an available MoveSequence when that MoveSequence 
        leads to forcing 

        To be more precise, sometimes a MoveSequence will lead to a sacrifice, 
        but sometimes this sacrifice is a part of the strategy called forcing. 
        Basically, we force the opponent to capture our pieces only to build up 
        a bridge for us to capture their pieces in our next round.

        We call the forced jump and consecutive moves of the Opponent the 
        induced jump MoveSequence, and call our MoveSequence that can capture 
        this piece moved by the induced jump MoveSequence in the following 
        round 'response MoveSequence'.

        Note that the induced jump MoveSequence should be unique to be 
        considered in forcing strategy, if the jump is induced by the opponent 
        has a choice, forcing tends to get really complicated and we don't 
        consider this scenario

        Parameters:
            mseq(MoveSequence): a MoveSequence whose priority is about to be 
                updated
            weight(float): a float that determine how much of an influence this 
                strategy should be playing among all the strategies

        Return: float: the value to add to priority to mseq according to the 
            forcing strategy
        """
        # check whether an opponent and its induced jump MoveSequence has
        # already been constructed for our mseq. If not, construct them
        if not self._curr_oppo:
            self._curr_oppo = OppoBot(self._oppo_color,
                                      self._experimentboard, mseq, self._level)
        if not self._curr_oppo_induced:
            self._curr_oppo_induced = self._curr_oppo.get_induced_jump_mseq()

        if len(self._curr_oppo_induced) == 1:
            # if there is this unique induced jump MoveSequence, update the
            # board to the state that assumes the opponent has taken this move
            oppo_mseq = self._curr_oppo_induced[0]
            oppo_move_list = oppo_mseq.get_move_list()
            for move in oppo_move_list:
                self._experimentboard.complete_move(move)

            # get what would our available MoveSequence be for the next turn if
            # we forced the Opponent's induced jump MoveSequence
            nxt_turn_mseq = self._get_mseq_list([])

            # initialize a list to take the updated priority of MoveSequences
            # that are response MoveSequences
            response_priority = []
            for mseq in nxt_turn_mseq:
                # get the first move in the MoveSequence
                first_move = mseq.get_move_list()[0]
                if isinstance(first_move, Jump):
                    if first_move.get_captured_piece().get_position() ==\
                            oppo_mseq.get_end_position():
                        # this MoveSequence is a response MoveSequence, i.e. it
                        # is a jump and capture the piece moved by the opponent
                        # in its last induced jump MoveSequence

                        # gives the capture value that will be achieved by this
                        # response MoveSequence
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
                assumed to be taken by the SmartBot
            level(SmartLevel) : the SmartLevel that we are giving the OppoBot, 
                should be the same as the SmartBot

        Return: None
        """
        super().__init__(own_color, checkersboard, level)

        # initialize a container for the last MoveSequence that the SmartBot was
        # assumed to have taken
        self._last_mseq = last_mseq

        # initialize a list to contain all the available MoveSequences with the
        # consideration of whether there exists a winning move
        self._mseq_list = self._get_mseq_list([(self._winning_priority, None)])

    def contains_winning_mseq(self) -> bool:
        """
        Examine whether there exists a MoveSequence that contains a winning move

        Parameters: None

        Return: bool: True if there exists a winning MoveSequence, False 
            Otherwise
        """
        # get all the possible move sequences and examine whether they contain

        for mseq in self._mseq_list:
            if mseq.get_priority() == math.inf:
                # there exists a winning MoveSequence
                return True
        return False

    def get_induced_jump_mseq(self) -> List[MoveSequence]:
        """
        If the MoveSequence assumed to be taken by the SmartBot, which led to 
        the OppoBot to be having a or more MoveSequence with the first move, 
        is a Jump over the piece that was moved in the MoveSequence by the 
        SmartBot, and those jumps are the only available moves of the Opponent, 
        then return a list of those MoveSequences that contains those jumps, 
        otherwise, return an empty list

        Parameters: None

        Return: List[MoveSequence]: the MoveSequence with the 
            first move being the jump induced by the last MoveSequence done by 
            the SmartBot, or [] if such induced jump doesn't exist or is not 
            the only available move fro OppoBot
        """
        # initialize an output list
        output_list = []
        for mseq in self._mseq_list:
            first_move = mseq.get_move_list()[0]
            # check out whether the first move is a jump
            if isinstance(first_move, Jump):
                if first_move.get_captured_piece().get_position() ==\
                        self._last_mseq.get_end_position():
                    # the first move of the MoveSequence is a Jump through the
                    # piece just moved by the SmartBot
                    output_list.append(mseq)

        return output_list
