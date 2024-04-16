from copy import deepcopy

#similar to read_input method from read.py
def input(n, path="input.txt"):
    with open(path, 'r') as f:
        lines = f.readlines()
        player_of_type = int(lines[0])
        previous_state = [[int(y) for y in line.rstrip('\n')] for line in lines[1:n+1]]
        current_state = [[int(y) for y in line.rstrip('\n')] for line in lines[n+1: 2*n+1]]
        return player_of_type, previous_state, current_state

#similar to write_output method from output.py
def output(result, path="output.txt"):
    out = ""
    if result == "PASS":
    	out = "PASS"
    else:
	    out += str(result[0]) + ',' + str(result[1])
    with open(path, 'w') as f:
        f.write(out)

class Board:
    def __init__(self, n):
        self.size = n
        self.dead_pieces = []
    #similar to set_board from host.py
    def setboard(self, player_type, previous_board, board):
        #size
        size = self.size
        for i in range(size):
            for j in range(size):
                #chess present in previous but not there in current, so add it to dead pieces array
                if previous_board[i][j] == player_type and board[i][j] != player_type: 
                    self.dead_pieces.append((i, j))
        self.previous = previous_board
        self.board = board

    
    #similar to compare_board from host.py
    def compare(self, b1, b2):
        size = self.size
        for i in range(size):
            for j in range(size):
                if b1[i][j] != b2[i][j]:
                    return False
        return True

    #similar to copy_board method from host.py
    def copy(self):
        return deepcopy(self)

    #similar to detect_neighbor from host.py
    def find_neighbor(self, i, j):
        neigh = []
        if i > 0:
            neigh.append((i-1, j))
        if i < self.size - 1:
            neigh.append((i+1, j))
        if j > 0:
            neigh.append((i, j-1))
        if j < self.size - 1:
            neigh.append((i, j+1))
        return neigh

    #similar to detect_neighbor_ally from host.py
    def find_similar_neighbor(self, i, j):
        board = self.board
        neighbors = self.find_neighbor(i, j)
        group = []
        piece = board[i][j]
        for piece_i,piece_j in neighbors:
            if board[piece_i][piece_j] == piece:
                group.append((piece_i,piece_j))
        return group

    #similar to ally_dfs from host.py
    def similar_neighbor(self, i, j):
        stack = [(i, j)]
        members = []
        while stack:
            top = stack.pop()
            members.append(top)
            neighbors = self.find_similar_neighbor(top[0], top[1])
            for each in neighbors:
                if each not in stack and each not in members:
                    stack.append(each)
        return sorted(members)

    #similar to find_liberty from host.py
    def liberty(self, i, j):
        board = self.board
        members = self.similar_neighbor(i, j)
        count = 0
        for member in members:
            neighbors = self.find_neighbor(member[0], member[1])
            for each in neighbors:
                if board[each[0]][each[1]] == 0:
                    return True
        return False

    #similar to find_died_pieces method from host.py
    def total_dead_pieces(self, player_type):
        board = self.board
        dead_pieces = []

        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == player_type:
                    if not self.liberty(i, j):
                        dead_pieces.append((i,j))
        return dead_pieces

    
    #similar to remove_died_pieces from host.py
    def remove_dead_pieces(self, player_type):
        dead_pieces = self.total_dead_pieces(player_type)
        if not dead_pieces:
            return []
        self.remove_pieces(dead_pieces)
        return dead_pieces

    #similar to remove_certain_pieces from host.py
    def remove_pieces(self, positions):
        board = self.board
        for x,y in positions:
            board[x][y] = 0
        #no need to use update board here
        self.board = board

    #similar to place_chess from host.py
    def place(self, i, j, player_type):
        board = self.board
        if not self.valid_place(i, j, player_type):
            return False
        self.previous_board = deepcopy(board)
        board[i][j] = player_type
        self.updateBoard(board)
        return True

    #similar to valid_place_check method from host.py
    def valid_place(self, i, j, player_type, test_check=False):
        board = self.board
        if not (i >= 0 and i < len(board)):
            return False
        if not (j >= 0 and j < len(board)):
            return False
        if board[i][j] != 0:
            return False
        test_go = self.copy()
        test_board = test_go.board
        test_board[i][j] = player_type
        #test_go.updateBoard(test_board)
        test_go.board = test_board
        if test_go.liberty(i, j):
            return True
        test_go.remove_dead_pieces(3 - player_type)
        if not test_go.liberty(i, j):
            return False
        else:
            if self.dead_pieces and self.compare(self.previous, test_go.board):
                return False
        return True

    #similar to update_board method from host.py
    def updateBoard(self, new_board):
        self.board = new_board

#evaluation function
def evaluate(player,enemy):
    player_star = 0
    enemy_star = 0
    player_edge = 0
    enemy_edge = 0
    middle_player = 0
    middle_enemy = 0
    player_liberty_count = 0
    enemy_liberty_count = 0
    board = go.board
    for i in range(go.size):
        for j in range(go.size):
            if board[i][j] == player:
                if go.liberty(i,j):
                    player_liberty_count += 1
            if board[i][j] == enemy:
                if go.liberty(i,j):
                    enemy_liberty_count += 1
    for i in range(0,5):
        if board[i][0] == enemy:
            enemy_edge += 1
        if board[i][4] == enemy:
            enemy_edge += 1
        if board[0][i] == enemy:
            enemy_edge += 1
        if board[4][i] == enemy:
            enemy_edge += 1
        if board[i][0] == player:
            player_edge += 1
        if board[i][4] == player:
            player_edge += 1
        if board[0][i] == player:
            player_edge += 1
        if board[4][i] == player:
            player_edge += 1  
    dead_player = len(go.total_dead_pieces(player))
    dead_enemy = len(go.total_dead_pieces(enemy))
    for i in range(1,4):
        for j in range(1,4):
            if board[i][j] == enemy:
                middle_enemy += 1
            if board[i][j] == player:
                middle_player += 1
    for i in range(1,4):
        if board[2][i] == enemy:
            middle_enemy += 1
        if board[i][2] == enemy:
            middle_enemy += 1
        if board[2][i] == player:
            middle_player += 1
        if board[i][2] == player:
            middle_player += 1
    for i in range(0,5,2):
        for j in range(0,5,2):
            if board[i][j] == player:
                player_star += 1
            if board[i][j] == enemy:
                enemy_star += 1
    for i in range(1,4,2):
        for j in range(1,4,2):
            if board[i][j] == player:
                player_star += 1
            if board[i][j] == enemy:
                enemy_star += 1
    #we get good values from dead enemy, middle element, liberty count, star patterns of player and enemy edge point
    #we get bad values from player edge, dead player, middle enemy, enemy liberty count and enemy star pattern
    eval = (player_liberty_count)- (player_edge) - (20*dead_player) + (middle_player) + player_star + enemy_edge + (120*dead_enemy) - middle_enemy - enemy_liberty_count - enemy_star
    return eval

# the minimax function
def minimax(depth,isMax,player,enemy,alpha,beta):
    if depth == 1 :
        score = evaluate(player,enemy)
        return score
    if isMax: 
        value = -1000
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place(i, j, player, test_check = True):
                    go.place(i,j,player)
                    value = max(value,minimax(depth+1,False,player,enemy,alpha,beta))
                    go.remove_pieces([(i,j)])
                    alpha = max(alpha, value)
                    if value >= beta:
                        return value
                    if value > alpha:
                        alpha = value
        if value == -1000:
            return evaluate(player,enemy)
        else:
            return 
    else:
        value = 10000 
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place(i, j, enemy, test_check = True):
                    go.place(i,j,enemy)
                    value = min(value,minimax(depth+1,True,player,enemy,alpha,beta))
                    go.remove_pieces([(i,j)])
                    beta = min(beta, value)
                    if value <= alpha:
                        return value
                    if value < beta:
                        beta = value
        if value == 10000:
            return evaluate(player,enemy)
        else:
            return value

#finding the bestmove for our player
def best_move(possible_indices,player_type):
    alpha = -1000
    beta =  1000
    bestvalue = -1000
    Pos = None
    if player_type == 1:
        player = 1
        enemy = 2
    else:
        player = 2
        enemy = 1
    for each in possible_indices:
        go.place(each[0],each[1],player_type)
        movevalue = minimax(0,False,player,enemy,alpha,beta)
        go.remove_pieces([(each)])
        if movevalue != 10000 and movevalue != -1000:
            if (movevalue > bestvalue):
                bestvalue = movevalue
                Pos = each
    if Pos == None or Pos == -1000:
        return "PASS"
    else:
        return Pos

class Player:
    def give_output(self, go, player_type):
        possible_indices = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place(i, j, player_type, test_check = True):
                    possible_indices.append((i,j))
        value = best_move(possible_indices,player_type)
        return value

if __name__ == "__main__":
    N = 5
    player_type, previous, board = input(N)
    go = Board(N)
    go.setboard(player_type, previous, board)
    player = Player()
    action = player.give_output(go, player_type)
    output(action)