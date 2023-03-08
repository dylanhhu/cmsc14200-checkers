from bot import SmartLevel, SmartBot, RandomBot
from checkers import (PieceColor, CheckersBoard, Position, Piece, Move,
                      GameStatus)
from colorama import Fore, Back, Style
    

def initialize():
    """
    Starts the game.

    Args:
        None

    Returns:
        None
    """
    print('Welcome to Checkers!')
    #print("How many rows of pieces would you like to play with today?")
    #rows = None
    #while not str(rows) in '12345':
    #    rows = input('> ')
    #    if rows == '':
    #        rows = 3
    play_checkers(3, 'human')

def print_board(b):
    """
    Prints a string representation of the board.

    Args:
        b: Board

    Returns:
        None
    """
    # column numbers
    board = '\n    ' + ' '.join(f'{i}' for i in range(b._width)) + '\n'
    # top border
    board += '    ' + '_' * (b._width * 2 ) + '\n'

    for row in range(b._height):
        # row numbers
        board += str(row) + '  |'

        for col in range(b._width):
            position = (col, row)

            # check for a piece in this position
            if position in b._pieces:
                piece = b._pieces[position]
                if piece._color == PieceColor.RED:
                    board += Back.BLACK + Fore.RED + Style.BRIGHT + '●' +\
                          Style.RESET_ALL + Back.BLACK + ' '
                else:
                    board += Back.BLACK + Fore.BLACK+ Style.BRIGHT + '●' +\
                          Style.RESET_ALL + Back.BLACK + ' '
            else:
                # if no piece, fill with black or white
                if (col % 2) != row % 2:
                    board += Style.RESET_ALL + Back.BLACK + '  ' + Style.RESET_ALL
                else:
                    board += Style.RESET_ALL + Back.WHITE + '  ' + Style.RESET_ALL

        board += Style.RESET_ALL + '|\n'

    # bottom border
    board += '    ' + '‾' * (b._width * 2) + '\n'

    print(board)

def get_move(player_type, moves):
    #if player_type == 'bot':

    if player_type == 'human': 
        # Ask for a move (and re-ask if a valid move is not provided)
        move = None
        while move is None:
            i = input('> ')
            if i != '' and int(i) in range(len(moves)):
                i = int(i)
                move = i
    return move

def play_checkers(r, opp_type):
    # create the board with r rows
    b = CheckersBoard(r)

    # set the starting player to black
    current_player = PieceColor.BLACK
    print('Black will start:')

    # keep playing until there is a winner:
    while True:
        # print the board
        print_board(b)

        # get current player color
        current_color = "Black" if current_player == PieceColor.BLACK else "Red"

        # get moves and display to player
        print(current_color + ', please select a move from the list below:')
        player_moves = b.get_player_moves(current_player)
        for i in range(len(player_moves)):
            print(f'Move {i}: {player_moves[i]}')

        # get move from player
        move = get_move(opp_type, player_moves)

        # make the move
        b.complete_move(player_moves[move])

        # check to see if another move must be made
        # if b.complete_move(player_moves[i]) == []:

        # if the game has ended, break out of the loop
        if b.get_game_state() != GameStatus.IN_PROGRESS:
            break

        # update the player color
        if current_player == PieceColor.BLACK:
            current_player = PieceColor.RED
        elif current_player == PieceColor.RED:
            current_player = PieceColor.BLACK

    print_board(b)
    if b.get_game_state() == GameStatus.RED_WINS:
        print('Red has won!')
    elif b.get_game_state() == GameStatus.BLACK_WINS:
        print('Black has won!')
    else:
        print('''It's a draw!''')
    print('Thanks for playing!')

if __name__ == '__main__':
    initialize()