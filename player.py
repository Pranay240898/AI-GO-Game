
from copy import deepcopy




def input(n, path="input.txt"):
    with open(path, 'r') as f:
        lines = f.readlines()
        type_of_player = int(lines[0])
        previous_state = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n+1]]
        current_state = [[int(x) for x in line.rstrip('\n')] for line in lines[n+1: 2*n+1]]
        return type_of_player, previous_state, current_state


def output(result, path="output.txt"):
    outpt = ""
    if result == "PASS":
    	outpt = "PASS"
    else:
	    outpt += str(result[0]) + ',' + str(result[1])

    with open(path, 'w') as f:
        f.write(outpt)

class GO:
    def __init__(self, n):
        """
        Go game.

        :param n: size of the board n*n
        """
        self.size = n
        #self.previous_board = None # Store the previous board
        self.X_move = True # X chess plays first
        self.died_pieces = [] # Intialize died pieces to be empty
        self.n_move = 0 # Trace the number of moves
        self.max_move = n * n - 1 # The max movement of a Go game
        self.komi = n/2 # Komi rule
        self.verbose = False # Verbose only when there is a manual player

    def init_board(self, n):
        '''
        Initialize a board with size n*n. 

        :param n: width and height of the board.
        :return: None.
        '''
        board = [[0 for x in range(n)] for y in range(n)]  # Empty space marked as 0
        # 'X' pieces marked as 1
        # 'O' pieces marked as 2
        self.board = board
        self.previous_board = deepcopy(board)

    def set_board(self, piece_type, previous_board, board):
        '''
        Initialize board status.
        :param previous_board: previous board state.
        :param board: current board state.
        :return: None.
        '''

        # 'X' pieces marked as 1
        # 'O' pieces marked as 2

        for i in range(self.size):
            for j in range(self.size):
                if previous_board[i][j] == piece_type and board[i][j] != piece_type:
                    self.died_pieces.append((i, j))

        # self.piece_type = piece_type
        self.previous_board = previous_board
        self.board = board

    def compare_board(self, board1, board2):
        for i in range(self.size):
            for j in range(self.size):
                if board1[i][j] != board2[i][j]:
                    return False
        return True

    def copy_board(self):
        '''
        Copy the current board for potential testing.

        :param: None.
        :return: the copied board instance.
        '''
        return deepcopy(self)

    def detect_neighbor(self, i, j):
        '''
        Detect all the neighbors of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbors row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = []
        # Detect borders and add neighbor coordinates
        if i > 0: neighbors.append((i-1, j))
        if i < len(board) - 1: neighbors.append((i+1, j))
        if j > 0: neighbors.append((i, j-1))
        if j < len(board) - 1: neighbors.append((i, j+1))
        return neighbors

    def detect_neighbor_ally(self, i, j):
        '''
        Detect the neighbor allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbored allies row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = self.detect_neighbor(i, j)  # Detect neighbors
        group_allies = []
        # Iterate through neighbors
        for piece in neighbors:
            # Add to allies list if having the same color
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j):
        '''
        Using DFS to search for all allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the all allies row and column (row, column) of position (i, j).
        '''
        stack = [(i, j)]  # stack for DFS serach
        ally_members = []  # record allies positions during the search
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1])
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def find_liberty(self, i, j):
        '''
        Find liberty of a given stone. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: boolean indicating whether the given stone still has liberty.
        '''
        board = self.board
        ally_members = self.ally_dfs(i, j)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    return True
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return False

    def find_died_pieces(self, piece_type):
        '''
        Find the died stones that has no liberty in the board for a given piece type.

        :param piece_type: 1('X') or 2('O').
        :return: a list containing the dead pieces row and column(row, column).
        '''
        board = self.board
        died_pieces = []

        for i in range(len(board)):
            for j in range(len(board)):
                # Check if there is a piece at this position:
                if board[i][j] == piece_type:
                    # The piece die if it has no liberty
                    if not self.find_liberty(i, j):
                        died_pieces.append((i,j))
        return died_pieces

    def remove_died_pieces(self, piece_type):
        '''
        Remove the dead stones in the board.

        :param piece_type: 1('X') or 2('O').
        :return: locations of dead pieces.
        '''

        died_pieces = self.find_died_pieces(piece_type)
        if not died_pieces: return []
        self.remove_certain_pieces(died_pieces)
        return died_pieces

    def remove_certain_pieces(self, positions):
        '''
        Remove the stones of certain locations.

        :param positions: a list containing the pieces to be removed row and column(row, column)
        :return: None.
        '''
        board = self.board
        for piece in positions:
            board[piece[0]][piece[1]] = 0
        self.update_board(board)

    def place_chess(self, i, j, piece_type):
        '''
        Place a chess stone in the board.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the placement is valid.
        '''
        board = self.board

        valid_place = self.valid_place_check(i, j, piece_type)
        if not valid_place:
            return False
        self.previous_board = deepcopy(board)
        board[i][j] = piece_type
        self.update_board(board)
        # Remove the following line for HW2 CS561 S2020
        # self.n_move += 1
        return True

    def valid_place_check(self, i, j, piece_type, test_check=False):
        '''
        Check whether a placement is valid.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1(white piece) or 2(black piece).
        :param test_check: boolean if it's a test check.
        :return: boolean indicating whether the placement is valid.
        '''   
        board = self.board
        verbose = self.verbose
        if test_check:
            verbose = False

        # Check if the place is in the board range
        if not (i >= 0 and i < len(board)):
            if verbose:
                print(('Invalid placement. row should be in the range 1 to {}.').format(len(board) - 1))
            return False
        if not (j >= 0 and j < len(board)):
            if verbose:
                print(('Invalid placement. column should be in the range 1 to {}.').format(len(board) - 1))
            return False
        
        # Check if the place already has a piece
        if board[i][j] != 0:
            if verbose:
                print('Invalid placement. There is already a chess in this position.')
            return False
        
        # Copy the board for testing
        test_go = self.copy_board()
        test_board = test_go.board

        # Check if the place has liberty
        test_board[i][j] = piece_type
        test_go.update_board(test_board)
        if test_go.find_liberty(i, j):
            return True

        # If not, remove the died pieces of opponent and check again
        test_go.remove_died_pieces(3 - piece_type)
        if not test_go.find_liberty(i, j):
            if verbose:
                print('Invalid placement. No liberty found in this position.')
            return False

        # Check special case: repeat placement causing the repeat board state (KO rule)
        else:
            if self.died_pieces and self.compare_board(self.previous_board, test_go.board):
                if verbose:
                    print('Invalid placement. A repeat move not permitted by the KO rule.')
                return False
        return True
        
    def update_board(self, new_board):
        '''
        Update the board with new_board

        :param new_board: new board.
        :return: None.
        '''   
        self.board = new_board

def evaluate(player,enemy):
    liberty = 0
    edge = 0
    middle = 0
    star_pattern = 0
    enemy_star_pattern = 0
    enemy_edge = 0
    middle_enemy = 0
    enemy_liberty = 0
    board = go.board

    for i in range(go.size):
        for j in range(go.size):
            if board[i][j] == player:
                if go.find_liberty(i,j):
                    liberty += 1
            if board[i][j] == enemy:
                if go.find_liberty(i,j):
                    enemy_liberty += 1
    dead_player = len(go.find_died_pieces(player))
    dead_enemy = len(go.find_died_pieces(enemy))
    for i in range(0,5):
        if board[i][0] == player:
            edge += 1
        if board[i][4] == player:
            edge += 1
        if board[0][i] == player:
            edge += 1
        if board[4][i] == player:
            edge += 1

        '''enemy edge calculation'''
        if board[i][0] == enemy:
            enemy_edge += 1
        if board[i][4] == enemy:
            enemy_edge += 1
        if board[0][i] == enemy:
            enemy_edge += 1
        if board[4][i] == enemy:
            enemy_edge += 1

    '''for creating the I pattern in my move'''
    for i in range(1,4):
        if board[2][i] == player:
            middle += 1
        if board[i][2] == player:
            middle += 1
        if board[2][i] == enemy:
            middle_enemy += 1
        if board[i][2] == enemy:
            middle_enemy += 1

    '''placing the player in the 3x3 middle'''
    for i in range(1,4):
        for j in range(1,4):
            if board[i][j] == player:
                middle += 1
            if board[i][j] == enemy:
                middle_enemy += 1

    '''placing the player alternatively'''
    for i in range(0,5,2):
        for j in range(0,5,2):
            if board[i][j] == player:
                star_pattern += 1
            if board[i][j] == enemy:
                enemy_star_pattern += 1
    for i in range(1,4,2):
        for j in range(1,4,2):
            if board[i][j] == player:
                star_pattern += 1
            if board[i][j] == enemy:
                enemy_star_pattern += 1

    return (129*dead_enemy) - (edge) - (20*dead_player) + (middle) + (liberty) + star_pattern + enemy_edge - middle_enemy - enemy_liberty - enemy_star_pattern

'''minimax function'''
def minimax(depth,isMax,player,enemy,alpha,beta):
    if depth == 1 :
        score = evaluate(player,enemy)
        return score
    if isMax: #always the maximizing player
        best = -1000
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, player, test_check = True):
                    go.place_chess(i,j,player)
                    best = max(best,minimax(depth+1,False,player,enemy,alpha,beta))
                    list_parsing = list()
                    list_parsing.append((i,j))
                    go.remove_certain_pieces(list_parsing)
                    alpha = max(alpha, best)
                    if best >= beta:
                        return best
                    if best > alpha:
                        alpha = best
        if best == -1000:
            return evaluate(player,enemy)
        else:
            return best
    else:
        best = 10000
        no = 1
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, enemy, test_check = True):
                    go.place_chess(i,j,enemy)
                    best = min(best,minimax(depth+1,True,player,enemy,alpha,beta))
                    list_parsing = list()
                    list_parsing.append((i,j))
                    go.remove_certain_pieces(list_parsing)
                    beta = min(beta, best)
                    no += 1
                    if best <= alpha:
                        return best
                    if best < beta:
                        beta = best
        if best == 10000:
            return evaluate(player,enemy)
        else:
            return best

'''finding the bestmove of our player'''
def best_move(possible_indices,player_type):
    alpha = -1000
    beta =  1000
    bestvalue = -1000
    bestPos = None
    if player_type == 1:
        player = 1
        enemy = 2
    else:
        player = 2
        enemy = 1
    sno = 1
    for each in possible_indices:
        go.place_chess(each[0],each[1],player_type)
        moveval = minimax(0,False,player,enemy,alpha,beta)
        list_parsing = list()
        list_parsing.append(each)
        go.remove_certain_pieces(list_parsing)
        if moveval != 10000 and moveval != - 1000:
            if (moveval > bestvalue):
                bestvalue = moveval
                bestPos = each
    if bestPos == None or bestPos == -1000:
        return "PASS"
    else:
        return bestPos

'''Player class'''
class Player:
    def get_output(self, go, player_type):
        possible_indices = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, player_type, test_check = True):
                    possible_indices.append((i,j))
        value = best_move(possible_indices,player_type)
        return value

       


if __name__ == "__main__":
    N = 5
    player_type, previous, board = input(N)
    go = GO(N)
    go.set_board(player_type, previous, board)
    player = Player()
    action = player.get_output(go, player_type)
    output(action)
