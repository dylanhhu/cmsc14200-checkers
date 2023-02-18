from enum import Enum
from typing import Tuple, List, Dict
from checkers import *


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
        self._checkersboeard = checkersboard

    def get_avail_move(self) -> List[Move]:
        """
        get all the available moves for all pieces according to the color
        that the bot is in control of

        Parameters: None

        Return: List[Move]: a list of all the moves available
        """

        # return a list of all moves available
        return self._checkersboeard.get_player_moves(self._own_color)

    def complete_move(self, move_list) -> None:
        """
        complete a list of moves that is decided to be taken by the bot, if
        any of the move is invalid, raise an exception

        Parameters: 
            move_list(List[Move]): the move list that is decided to be taken

        Return: None
        """
        # initialize a list of the possible next steps to take
        valid_nxt_list = self.get_avail_move()

        # take the moves consecutively in the move_list
        for nxt_move in move_list:
            # verify whether the nxt_move is a valid move to take
            if nxt_move in valid_nxt_list:
                # valid, take the move, and update the possible next steps to take
                valid_nxt_list = self._checkersboeard.complete_move(nxt_move)
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


class SmartBot(Bot):
    """
    Represents a bot that is capable of selecting moves according
    to some strategies in a certain group of strategies, including:
    1) more inclined to attack the double corner 
    2) more inclined to protect the single corner
    3) more inclined to hold the base line
    4) more inclined to get kings
    5) more inclined to trade pieces when leading
    6) more inclined to pick the move that capture the most opponent pieces
    8) more inclined to push forward 
    9) more inclined to occupy the center
    10) able to conduct the wining move if possible
    11) able to avoid a lossing move if possible

    citations for the strategies:
    https://www.ultraboardgames.com/checkers/tips.php
    https://www.youtube.com/watch?v=Lfo3yfrbUs0
    https://www.gamblingsites.com/skill-games/checkers/
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

    def _init_move_list(self) -> List[(List[Move], CheckersBoard)]:
        """
        initialize a list of tuples of consequtive moves that 
        we can take and the resultant board state

        Parameters: None

        Return: List[(List[Move], CheckersBoard)]: 
                the first element in the tuple represent a sequence of 
                moves, and the second element represents the corresponding 
                end board state after taking that sequence of moves
        """
        nxt_move_list = self.get_avail_move()
        output_list = []

        def helper(move_list, curr_path, curr_board) -> None:
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
            if not move_list:
                # if there's no move in the list, reached the end
                # of one potential move list, add this move list and
                # the corresponding board state to the output_list
                output_list.append((curr_path[:], curr_board))

            # traverse through all the possible next moves, take the moves
            # on a cloned board and recursively call helper
            for nxt_move in move_list:
                # update the path and the board state
                curr_path.append(nxt_move)
                update_board = curr_board.clone()
                valid_nxt_list = update_board.complete(nxt_move)

                # the recursive step
                helper(valid_nxt_list, curr_path, update_board)

                curr_path.pop()

        # update the output_list
        helper(nxt_move_list, [], self._checkersboeard.clone())

        return output_list

    def _corner_weight(self, weighted_avail_moves) -> List[(Move, int)]:
        """
        update the weight of each available move with the consideration
        of attacking the double corner and holding the single corner

        Parameters:
            weighted_avail_moves(List[Move, int]): a list of available moves with
                                                   their corrent weight

        Return: List[(Move, int)]: the updated list of weighted available moves
        """
        raise NotImplementedError

    def _baseline_weight(self, weighted_avail_moves) -> List[(Move, int)]:
        """
        update the weight of each available move with the consideration
        of holding the baseline

        Parameters:
            weighted_avail_moves(List[Move, int]): a list of available moves with
                                                   their corrent weight

        Return: List[(Move, int)]: the updated list of weighted available moves
        """
        raise NotImplementedError

    def _king_weight(self, weighted_avail_moves) -> List[(Move, int)]:
        """
        update the weight of each available move with the consideration
        of getting a king 

        Parameters:
            weighted_avail_moves(List[Move, int]): a list of available moves with
                                                   their corrent weight

        Return: List[(Move, int)]: the updated list of weighted available moves
        """
        raise NotImplementedError

    def _trading_weight(self, weighted_avail_moves) -> List[(Move, int)]:
        """
        update the weight of each available move with the consideration
        of trading 

        Parameters:
            weighted_avail_moves(List[Move, int]): a list of available moves with
                                                   their corrent weight

        Return: List[(Move, int)]: the updated list of weighted available moves
        """
        raise NotImplementedError

    def _capture_weight(self, weighted_avail_moves) -> List[(Move, int)]:
        """
        update the weight of each available move with the consideration
        of capturing as many opponent pieces as possible

        Parameters:
            weighted_avail_moves(List[Move, int]): a list of available moves with
                                                   their corrent weight

        Return: List[(Move, int)]: the updated list of weighted available moves
        """
        raise NotImplementedError

    def _push_weight(self, weighted_avail_moves) -> List[(Move, int)]:
        """
        update the weight of each available move with the consideration
        of pushing forward

        Parameters:
            weighted_avail_moves(List[Move, int]): a list of available moves with
                                                   their corrent weight

        Return: List[(Move, int)]: the updated list of weighted available moves
        """
        raise NotImplementedError

    def _center_weight(self, weighted_avail_moves) -> List[(Move, int)]:
        """
        update the weight of each available move with the consideration
        of occupying the center

        Parameters:
            weighted_avail_moves(List[Move, int]): a list of available moves with
                                                   their corrent weight

        Return: List[(Move, int)]: the updated list of weighted available moves
        """
        raise NotImplementedError

    def _winning_weight(self, weighted_avail_moves) -> List[(Move, int)]:
        """
        update the weight of each available move with the consideration
        of the existence of a winning move

        Parameters:
            weighted_avail_moves(List[Move, int]): a list of available moves with
                                                   their corrent weight

        Return: List[(Move, int)]: the updated list of weighted available moves
        """
        raise NotImplementedError

    def _capture_weight(self, weighted_avail_moves) -> List[(Move, int)]:
        """
        update the weight of each available move with the consideration
        of the existence of a losing move

        Parameters:
            weighted_avail_moves(List[Move, int]): a list of available moves with
                                                   their corrent weight

        Return: List[(Move, int)]: the updated list of weighted available moves
        """
        raise NotImplementedError
