"""
psuedo code:
while gamestate is in progress
    print board
    get moves
    ask for move
    do the move

handle end of game
"""
import checkers


def play_checkers():
    # Create the board with 3 rows
    b = checkers.CheckersBoard(3)

    # Set the starting player to black
    current_player = checkers.PieceColor.BLACK
    print("Welcome! Black will start:")

    # Keep playing until there is a winner:
    while True:
        # Print the board
        print(b)

        # Get moves and display to player
        print("Select a move from the list below:")
        player_moves = b.get_player_moves(current_player)
        for i in range(len(player_moves)):
            print(f"Move {i}: {player_moves[i]}")


        # Ask for a move (and re-ask if a valid move is not provided)
        move = None
        while move is None:
            i = input("> ")
            if i in range(len(player_moves)):
                i = int(i)
                move = i

        # Make the move
        b.complete_move(player_moves[i])

        # Check if another move must be made
        # if b.complete_move(player_moves[i]) == []:

        # If the game has ended break out of the loop
        if game_status != GameStatus.IN_PROGRESS:
            break

        # Update the player
        if current_player == PieceColor.BLACK:
            current_player = PieceColor.RED
        elif current_player == PieceColor.RED:
            current_player = PieceColor.BLACK

    print(b)
    print(f"The winner is {current_player}!")

if __name__ == "__main__":
    play_checkers()