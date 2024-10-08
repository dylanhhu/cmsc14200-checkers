"""
This file is for testing the winning rate of the robot. It runs a specified 
number of games with the random bot vs the smart bot. We highly recommend row 
numbers from 2 to 9 as this is what's required in the design requirement and 
there's no guarantee that the bot will finish a game in a relatively small 
period of time, in which case the bot would be set to SmartLevel of SIMPLE.

The bot's smart level is responsive to the size of the board: the smarter the 
bot gets, the more time to play the game. Therefore, it makes more sense to
implement bots with fewer strategies

To run the the test, run the command in the following form in the terminal:
'python3 src/test_bot.py 6 50'
this stands for running a test with 50 games on a board with 6 rows per player

I will list the average time for each game for different rows per player below 
for reference:
    rows per player             average time
    2                           0.07s
    3                           0.30s
    4                           1.52s
    5                           3.82s
    6                           1.23s
    7                           3.19s
    8                           6.09s
    9                           11.23s

citations: 
    https://www.geeksforgeeks.org/command-line-arguments-in-python/
    https://www.codecademy.com/resources/docs/python/modules/tqdm
"""
import sys
from tqdm import trange
from typing import Tuple
from bot import *
from checkers import GameStatus, PieceColor

# this is a dict that map the size of the board (depicted by rows per player)
# with the bot smart level that is going to be implemented
# change the smart level if you want to test out how different smart level bots
# react to different board size
size_bot_dict = {
    2: SmartLevel.HARD,
    3: SmartLevel.HARD,
    4: SmartLevel.HARD,
    5: SmartLevel.HARD,
    6: SmartLevel.MEDIUM,
    7: SmartLevel.MEDIUM,
    8: SmartLevel.SIMPLE,
    9: SmartLevel.SIMPLE,
}


def complete_move(bot) -> None:
    """
    complete a list of moves that is decided to be taken by a bot, if
    any of the move is invalid, raise an exception

    for test only, the bot will not be completing the move by itself

    Parameters:
        bot(Union[RandomBot, SmartBot]): the bot that is going to make the 
            move in the it choses

    Return: None
    """
    # take the moves consecutively in the move list that the bot chooses
    for nxt_move in bot.choose_move_list():
        bot._checkersboard.complete_move(nxt_move)


def bot_test(game_num, row_num) -> Tuple[float, float]:
    """
    This function implements test on a bot to get the winning rate under for 
    the SmartBot over the Random Bot on a board over a board with each side 
    having "row_num" of rows. The winning rate will be calculated after rep_num 
    of games are played.

    Parameters:
        game_num(int): number of games that are going to be played
        row_num(int): number of rows per player

    Return: Tuple(float, float): the winning rate, draw rate for the row_num
    """
    # initialize a winning counter and and a draw counter for the smart bot
    smart_win_counter = 0
    draw_counter = 0

    # initialize the smart level of the smart bot corresponding to this row num
    if row_num in range(2, 10):
        # rows per player number in recommended range
        smart_level = size_bot_dict[row_num]
    else:
        # not in recommended range, default the smart level to simple
        smart_level = SmartLevel.SIMPLE

    for i in trange(game_num, file=sys.stdout):
        # initialize a board according to the row num
        board = CheckersBoard(row_num)

        # get the current game state
        game_state = board.get_game_state()
        # initialize a flag that indicates whose turn it is
        turn = PieceColor.BLACK

        while game_state == GameStatus.IN_PROGRESS:
            # check whose turn it is
            if turn == PieceColor.BLACK:
                # initialize a random bot to take up the black side
                rand_bot = RandomBot(PieceColor.BLACK, board)
                # complete a move chosen by the random bot for this round and
                # update the game state
                complete_move(rand_bot)
                game_state = board.get_game_state()

                # change the turn
                turn = PieceColor.RED

            elif turn == PieceColor.RED:
                # intialize a SmartBot to take up the red side. Note that
                # you can change how many strategies to use by changing the
                # SmartLevel
                smart_bot = SmartBot(PieceColor.RED, board, smart_level)
                # complete a move chosen by the smart bot for this round and
                # update the game state.
                complete_move(smart_bot)

                # change the turn
                turn = PieceColor.BLACK

        # update the win counter and draw counter for the smart bot each game
        if board.get_game_state() == GameStatus.RED_WINS:
            smart_win_counter += 1
        elif board.get_game_state() == GameStatus.DRAW:
            draw_counter += 1

    # return the winning rate and draw rate of the smart bot
    return (smart_win_counter/game_num, draw_counter/game_num)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        # initialize row_num and game_num
        row_num = int(sys.argv[1])
        game_num = int(sys.argv[2])

        # run the test
        win_rate, draw_rate = bot_test(game_num, row_num)

        # gives out result
        msg = f"winning rate of the smart bot on a board with {row_num} rows\
 per player: {win_rate}, draw_rate = {draw_rate} "
        print(msg)

    else:
        # the number of parameters doesn't match
        msg = 'the number of parameters passed in is not 2'
        raise ValueError(msg)
