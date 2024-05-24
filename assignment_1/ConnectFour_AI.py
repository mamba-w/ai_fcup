import random
import math

WIN_X = 512
WIN_O = -512
DRAW = 0
MOVE_BONUS_X = 16
MOVE_BONUS_O = -16
SEGMENT_VALUES = {-3: -50, -2: -10, -1: -1, 0: 0, 1: 1, 2: 10, 3: 50}

# Define the Connect Four game board
class ConnectFour:
    def __init__(self):
        self.board = [['.' for _ in range(7)] for _ in range(6)]  # Initialize the game board with empty spaces
        self.current_player = 'X'  # Set the starting player as X

    def display_board(self):
        for row in self.board:  # Iterate over each row in the board
            print(' '.join(row))  # Print the current row with spaces between tokens
        print()  # Print an empty line after displaying the board

    def drop_token(self, col):
        for row in range(5, -1, -1):  # Iterate from the bottom row to the top row
            if self.board[row][col] == '.':  # Check if the current cell is empty
                self.board[row][col] = self.current_player  # Place the current player's token in the cell
                return True  # Return True indicating a successful token drop
        return False  # Return False indicating the column is full and token cannot be dropped

    def switch_player(self):
        self.current_player = 'X' if self.current_player == 'O' else 'O'  # Switch the current player

    def check_winner(self):
        # Check for winning combinations horizontally, vertically, and diagonally
        for row in range(6):
            for col in range(7):
                if self.board[row][col] != '.':
                    if (self.check_line(row, col, 1, 0) or
                        self.check_line(row, col, 0, 1) or
                        self.check_line(row, col, 1, 1) or
                        self.check_line(row, col, 1, -1)):
                        return self.board[row][col]  # Return the winning player
        if all(cell != '.' for row in self.board for cell in row):
            return 'Draw'  # Return 'Draw' if the board is full and no player wins
        return None  # Return None if there is no winner yet

    def check_line(self, row, col, dr, dc):
        token = self.board[row][col]
        for _ in range(3):
            row += dr
            col += dc
            if row < 0 or row >= 6 or col < 0 or col >= 7 or self.board[row][col] != token:
                return False
        return True

# Evaluate a segment of four tokens
def evaluate_segment(segment):
    x_count = segment.count('X')
    o_count = segment.count('O')
    if x_count == 4:
        return WIN_X
    elif o_count == 4:
        return WIN_O
    elif x_count == 0:
        return SEGMENT_VALUES[-o_count]
    elif o_count == 0:
        return SEGMENT_VALUES[x_count]
    else:
        return 0  

# Evaluate the entire game board
def evaluate(board):
    score = 0  # Initialize the score to zero

    # Evaluate segments horizontally
    for row in board:
        for i in range(len(row) - 3):
            segment = row[i:i+4]  # Extract a segment of four tokens
            score += evaluate_segment(segment)  # Evaluate the segment and update the score

    # Evaluate segments vertically
    for col in range(len(board[0])):
        for i in range(len(board) - 3):
            segment = [board[j][col] for j in range(i, i+4)]  # Extract a segment of four tokens
            score += evaluate_segment(segment)  # Evaluate the segment and update the score

    # Evaluate segments diagonally (top-left to bottom-right)
    for i in range(len(board) - 3):
        for j in range(len(board[0]) - 3):
            segment = [board[i+k][j+k] for k in range(4)]  # Extract a segment of four tokens
            score += evaluate_segment(segment)  # Evaluate the segment and update the score

    # Evaluate segments diagonally (bottom-left to top-right)
    for i in range(3, len(board)):
        for j in range(len(board[0]) - 3):
            segment = [board[i-k][j+k] for k in range(4)]  # Extract a segment of four tokens
            score += evaluate_segment(segment)  # Evaluate the segment and update the score

    # Add move bonus
    num_x = sum(row.count('X') for row in board)  # Count the number of 'X' tokens on the board
    num_o = sum(row.count('O') for row in board)  # Count the number of 'O' tokens on the board
    score += MOVE_BONUS_X if num_x == num_o else MOVE_BONUS_O  # Add a bonus score based on the difference in token counts

    return score  # Return the final evaluation score


# A* search algorithm to find the best move
def astar_search(connect_four):
    best_score = float('-inf')
    best_move = None
    for col in range(7):
        temp_connect_four = ConnectFour()
        temp_connect_four.board = [row[:] for row in connect_four.board]
        if temp_connect_four.drop_token(col):
            score = evaluate(temp_connect_four.board)
            if score > best_score:
                best_score = score
                best_move = col
    return best_move

# Node class for Monte Carlo Tree Search
class Node:
    def __init__(self, state, parent=None):
        self.state = state  # Stores the game state associated with this node
        self.parent = parent  # Stores the parent node of this node. If no parent is provided, it defaults to None
        self.children = []  # A list to store child nodes of this node. Initially empty
        self.visits = 0  # Tracks the number of times this node has been visited during simulations in the Monte Carlo Tree Search (MCTS) algorithm
        self.wins = 0  # Tracks the number of simulated wins from this node during MCTS simulations

    def is_fully_expanded(self):
        return len(self.children) == 7  # Checks if the node has fully expanded, meaning it has generated child nodes for all possible actions

    def add_child(self, child_state):
        child_node = Node(child_state, parent=self)  # Adds a new child node to the current node
        self.children.append(child_node)  # Appends the newly created child node to the list of children
        return child_node  # Returns the newly created child node

    def is_terminal(self):
        return self.state.check_winner() is not None  # Checks if the game state associated with the node is terminal, meaning the game has ended

    def uct_value(self, total_visits, c=1.0):
        if self.visits == 0:
            return float('inf')  # Returns positive infinity if the node has not been visited to encourage exploration of unvisited nodes
        exploitation = self.wins / self.visits  # Calculates the exploitation term, the ratio of wins to visits for the node
        exploration = c * math.sqrt(math.log(total_visits) / self.visits)  # Calculates the exploration term based on the number of visits to the parent node
        return exploitation + exploration  # Returns the Upper Confidence Bound for Trees (UCT) value of the node, balancing between exploitation and exploration

# Backpropagate the simulation result through the tree
def backpropagate(node, result):
    while node:
        node.visits += 1  # Increment the visit count of the current node
        if result == 'X':
            node.wins -= 1  # Decrement the win count of the node if the result is a win for 'X'
        elif result == 'O':
            node.wins += 1  # Increment the win count of the node if the result is a win for 'O'
        node = node.parent  # Move to the parent node for further backpropagation

# Select the next node for exploration using UCT
def select(node):
    while node.is_fully_expanded() and not node.is_terminal():
        node = best_child(node)  # Select the best child node based on UCT value until a leaf or unexpanded node is reached
    if not node.is_fully_expanded() and not node.is_terminal():
        return expand(node)  # If the node is not fully expanded and not a terminal state, expand it
    return node  # Return the selected node

# Expand the tree by adding a new node
def expand(node):
    col = random.randint(0,6)
    new_state = ConnectFour()
    new_state.board = [row[:] for row in node.state.board]
    new_state.switch_player()
    new_state.drop_token(col)
    new_node = node.add_child(new_state)
    return new_node

# Choose the best child node based on UCT values
def best_child(node):
    total_visits = sum(child.visits for child in node.children)
    return max(node.children, key=lambda child: child.uct_value(total_visits))

# Simulate a game until completion and return the result
def simulate(connect_four):
    new_connect_four = ConnectFour()
    new_connect_four.board = [row[:] for row in connect_four.board]
    new_connect_four.current_player = connect_four.current_player
    
    best_move = None
    best_score = float('-inf')
    
    for col in range(7):
        if new_connect_four.drop_token(col):
            score = evaluate(new_connect_four.board)
            if score > best_score:
                best_score = score
                best_move = col
            new_connect_four.board = [row[:] for row in connect_four.board]
    
    return best_move

# Monte Carlo Tree Search algorithm
def mcts_search(connect_four, num_simulations=10000):
    root = Node(connect_four)
    for _ in range(num_simulations):
        node_to_explore = select(root)
        simulated_move = simulate(node_to_explore.state)
        backpropagate(node_to_explore, simulated_move)
    return simulated_move

# Main function to run the game
def main():
    # Choose the algorithm
    algorithm_choice = input("Choose the algorithm:\n1. A*\n2. Monte Carlo\nEnter the number of the algorithm you want to use: ")

    if algorithm_choice == '1':
        algorithm = astar_search
    elif algorithm_choice == '2':
        algorithm = mcts_search
    else:
        print("Invalid choice. Please enter '1' for A* or '2' for Monte Carlo.")
        return

    connect_four = ConnectFour()  # Initialize the game
    while True:
        connect_four.display_board()  # Display the current board
        winner = connect_four.check_winner()  # Check for a winner
        if winner:
            if winner == 'Draw':
                print("It's a draw!")  # Display draw message
            else:
                print(f"Player {winner} wins!")  # Display winner message
            break
        if connect_four.current_player == 'X':
            print("It's now X's turn.")  # Display X's turn message
            while True:
                col = int(input("Make a move by choosing your column (0-6): "))  # Ask for user input
                if 0 <= col <= 6:  # Check if the column is within the valid range
                    break
                else:
                    print("Invalid column number. Please enter a number between 0 and 6.")  # Display error message
            if connect_four.drop_token(col):  # Drop X's token in the column
                connect_four.switch_player()  # Switch to the next player
        else:
            print("Computer (O) is thinking...")  # Display O's turn message
            col = algorithm(connect_four)  # Find the best move using the selected algorithm
            if connect_four.drop_token(col):   # Drop O's token in the column
                connect_four.switch_player()   # Switch to the next player

if __name__ == "__main__":
    main()

