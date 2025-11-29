import copy
import random
# import time

class TeekoPlayer:
    """ An object representation for an AI game player for the game Teeko.
    """
    pieces = ['b', 'r']
    max_depth = 3

    def __init__(self):
        """ Initializes a TeekoPlayer object by randomly selecting red or black as its
        piece color.
        """
        self.board = [[' ' for j in range(5)] for i in range(5)]
        self.my_piece = random.choice(self.pieces)
        self.opp = self.pieces[0] if self.my_piece == self.pieces[1] else self.pieces[1]

    def make_move(self, state):
        """ 
        Selects a (row, col) space for the next move. You may assume that whenever
        this function is called, it is this player's turn to move.

        Args:
            state (list of lists): should be the current state of the game as saved in
                this TeekoPlayer object. Note that this is NOT assumed to be a copy of
                the game state and should NOT be modified within this method (use
                place_piece() instead). Any modifications (e.g. to generate successors)
                should be done on a deep copy of the state.

                In the "drop phase", the state will contain less than 8 elements which
                are not ' ' (a single space character).

        Return:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

        Note that without drop phase behavior, the AI will just keep placing new markers
            and will eventually take over the board. This is not a valid strategy and
            will earn you no points.
        """
        # Check phase
        total_pieces = sum(1 for row in state for cell in row if cell != ' ')
        drop_phase = total_pieces < 8
        
        # Adaptive depth based on game phase
        if drop_phase:
            if total_pieces <= 4:
                search_depth = 3  # Very early game - too many options
            elif total_pieces <= 6:
                search_depth = 4
            else:
                search_depth = 5  # Fewer empty spots, can go deeper
        else:
            search_depth = 5  # Move phase has limited moves per piece
        
        # Store original and temporarily override
        original_depth = self.max_depth
        self.max_depth = search_depth

        # We will take decisions based on the value generated here
        score, best_state = self.minimax(state, 0, float('-inf'), float('inf'))

        self.max_depth = original_depth
        move = []

        

        if drop_phase:
            # Only return row, col without source
            for i in range(5):
                for j in range(5):
                    if (state[i][j] != best_state[i][j]):
                        move.append((i, j))
                        return move
        else:
            source = None
            dest = None
            for i in range(5):
                for j in range(5):
                    # We will check the self.my_piece which is in the wrong place
                    if state[i][j] == ' ' and best_state[i][j] == self.my_piece:
                        dest = (i, j)
                    if state[i][j] == self.my_piece and best_state[i][j] == ' ':
                        source = (i, j)
                    if dest and source:
                        break
                if dest and source:
                    break

            if dest and source:
                move.append(dest)
                move.append(source)

        return move

    def succ(self, state, my_piece) -> list: 
        """
        Generate a list of valid successors for the current game state 
        on placing your piece. (defined by self.my_piece)

        This naively creates successors without awareness of win conditions.
        """
        
        successor_states = []
        # Check if we are in the "drop" phase
        total_pieces = sum(1 for row in state for cell in row if cell != ' ')
        drop_phase = total_pieces < 8

        if drop_phase:
            # If we are in drop phase simply append to successor states current state list with one of the empty slots replaced with black
            for row_idx in range(len(state)):
                for col_idx in range(len(state[0])):
                    if state[row_idx][col_idx] == ' ':
                        state_copy = copy.deepcopy(state)
                        state_copy[row_idx][col_idx] = my_piece
                        successor_states.append(state_copy)
        else:
            # If not in drop phase then for every position where the piece equals my piece we add its position after 
            # moving one step horizontally, vertically, diagonally - if those spots are available. 
            # We cannot wrap around.  

            #  Build our position matrix
            piece_locs = [(i, j) for i in range(5) for j in range(5) if state[i][j] == my_piece]
            
            for x, y in piece_locs:
                # First check if our x+1 will be less than length of the rows, only then do the permutations with it
                directions = [
                    (-1, -1), (-1, 0), (-1, +1),
                    (0, -1), (0, +1),
                    (+1, -1), (+1, 0), (+1, +1)
                ]
                for dx, dy in directions:
                    new_x = x + dx
                    new_y = y + dy
                    if (0 <= new_x < len(state) and 
                        0<= new_y < len(state[0]) and 
                        state[new_x][new_y] == ' '):
                         
                        state_copy = copy.deepcopy(state)
                        state_copy[new_x][new_y] = my_piece
                        state_copy[x][y] = ' '
                        successor_states.append(state_copy)
        return successor_states
    
    def opponent_move(self, move):
        """ Validates the opponent's next move against the internal board representation.
        You don't need to touch this code.

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.
        """
        # validate input
        if len(move) > 1:
            source_row = move[1][0]
            source_col = move[1][1]
            if source_row != None and self.board[source_row][source_col] != self.opp:
                self.print_board()
                print(move)
                raise Exception("You don't have a piece there!")
            if abs(source_row - move[0][0]) > 1 or abs(source_col - move[0][1]) > 1:
                self.print_board()
                print(move)
                raise Exception('Illegal move: Can only move to an adjacent space')
        if self.board[move[0][0]][move[0][1]] != ' ':
            raise Exception("Illegal move detected")
        # make move
        self.place_piece(move, self.opp)

    def place_piece(self, move, piece):
        """ Modifies the board representation using the specified move and piece

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

                This argument is assumed to have been validated before this method
                is called.
            piece (str): the piece ('b' or 'r') to place on the board
        """
        if len(move) > 1:
            self.board[move[1][0]][move[1][1]] = ' '
        self.board[move[0][0]][move[0][1]] = piece

    def print_board(self):
        """ Formatted printing for the board """
        for row in range(len(self.board)):
            line = str(row)+": "
            for cell in self.board[row]:
                line += cell + " "
            print(line)
        print("   A B C D E")

    def evaluate_line(self, line : list, my_piece, opponent_piece) -> float:
        """Evaluate a given row/column/diagonal/square considering if the opponent is blocking us here. Outputs a score"""
        my_count = line.count(my_piece)
        opp_count = line.count(opponent_piece)
        empty_count = line.count(' ')

        if opp_count > 0 and my_count > 0:
            # Mixed line - reward blocking penalize opp development
            block_bonus = 0.75 if opp_count == 3 and empty_count == 1 else 0.0
            
            # Slightly penalize if opponent is building a threat (this will be positive if my_count>opp_count)
            return block_bonus + 0.15*my_count - 0.25*opp_count + 0.05 * empty_count
        
        if my_count == 3 and empty_count == 1:
            return 0.75 # Winning move found
        elif my_count == 2 and empty_count >= 2:
            return 0.50 # Still good but not dominating
        elif my_count == 1:
            return 0.25 # Eh - so so
        else:
            return 0.0
    
    def evaluate_square(self, square : list, my_piece, opponent_piece) -> float:
        # Unpack for readability
        a, b, c, d = square

        my_count = square.count(my_piece)
        opp_count = square.count(opponent_piece)
        empty_count = square.count(' ')

        if my_count > 0 and opp_count > 0:
            # Opponent forming a dominant mini-structure → penalty
            threat_penalty = 0.25 * opp_count

            # Blocking the opponent gives slight bonus
            block_bonus = 0.15 * my_count
            score = block_bonus - threat_penalty + 0.05*empty_count
            return max(min(score, 0.4), -0.4)


        # --- 2. Purely mine or purely empty or purely opponent ---
        score = 0.0

        # Weight pairs (strongest signal in 2x2 squares)
        pair_bonus = 0.22

        # Horizontal pairs
        if a == my_piece and b == my_piece: score += pair_bonus
        if c == my_piece and d == my_piece: score += pair_bonus

        # Vertical pairs
        if a == my_piece and c == my_piece: score += pair_bonus
        if b == my_piece and d == my_piece: score += pair_bonus

        # Diagonal pairs (slightly more valuable for forward pressure)
        diag_bonus = 0.28
        if a == my_piece and d == my_piece: score += diag_bonus
        if b == my_piece and c == my_piece: score += diag_bonus

        # Singles (light value)
        score += 0.10 * my_count

        # Reward empty synergy potential
        score += 0.05 * empty_count

        return min(score, 0.9)
    
    def heuristic_game_value(self, state) -> float:
        """ 
        Define the heuristic game value of the current board state taking into account players
        and opponents

        Args:
        state (list of lists): either the current state of the game as saved in
            this TeekoPlayer object, or a generated successor state.

        Returns:
            float heuristic_val (heuristic computed for the game state)
        """

        # First determine if its a terminal or non terminal state by checking with game_value
        heuristic_val = self.game_value(state)
        if heuristic_val != 0:
            return float(heuristic_val)

        opponent_piece = 'r' if self.my_piece == 'b' else 'b'      

        # We only need the heuristic if the given state is not a terminal state, otherwise we just return the maximal positive or maximal negative value.
        # I am choosing to implement this heuristic by assigning a higher score the closer we are to victory. 
        # If we have 3 pieces in the correct position then it has a score of 0.75, if 2 pieces than 0.5 and if 1 piece than 0.25. 
        # The state would be evaluated against all the possible win condtions. 
        # Additionally we will score the opponent as well using the same criteria 0.75 if the opponent has 3 pieces correct and so on. 
        # The final heuristic will be the difference between the AI's heur value and the opponent's heur value.
        my_score = {"horizontal":[], "vertical":[], "diagonal":[],"square":[]}
        opponent_score = {"horizontal":[], "vertical":[], "diagonal":[], "square":[]}

        # Rows
        for i in range(5):
            for j in range(2):
                row_window = state[i][j:j+4]
                score = self.evaluate_line(row_window, self.my_piece, opponent_piece)
                opp_score = self.evaluate_line(row_window, opponent_piece, self.my_piece)
                my_score["horizontal"].append(score)
                opponent_score["horizontal"].append(opp_score)

        # Columns    
        for i in range(2):
            for j in range(5):
                col_window = [state[i+k][j] for k in range(4)]
                score = self.evaluate_line(col_window, self.my_piece, opponent_piece)
                opp_score = self.evaluate_line(col_window, opponent_piece, self.my_piece)
                my_score["vertical"].append(score)
                opponent_score["vertical"].append(opp_score)

        # Down-right diagonals
        for i in range(2):
            for j in range(2):
                diag_window = [state[i+k][j+k] for k in range(4)]
                score = self.evaluate_line(diag_window, self.my_piece, opponent_piece)
                opp_score = self.evaluate_line(diag_window, opponent_piece, self.my_piece)
                my_score["diagonal"].append(score)
                opponent_score["diagonal"].append(opp_score)
                
        # Down-left diagonals
        for i in range(2):
            for j in range(4, 2, -1):
                diag_window = [state[i+k][j-k] for k in range(4)]
                score = self.evaluate_line(diag_window, self.my_piece, opponent_piece)
                opp_score = self.evaluate_line(diag_window, opponent_piece, self.my_piece)
                my_score["diagonal"].append(score)
                opponent_score["diagonal"].append(opp_score)

        for i in range(4):
            for j in range(4):
                square_window = [state[i][j], state[i][j+1], state[i+1][j], state[i+1][j+1]]
                score = self.evaluate_square(square_window, self.my_piece, opponent_piece)
                opp_score = self.evaluate_square(square_window, opponent_piece, self.my_piece)
                my_score["square"].append(score)
                opponent_score["square"].append(opp_score)

        def top_two_sum(bucket_list):
            if not bucket_list:
                return 0.0, 0.0
            sorted_vals = sorted(bucket_list)
            top = sorted_vals[-1]
            second = sorted_vals[-2] if len(sorted_vals) >= 2 else 0.0
            return top, second

        my_values = []
        opp_values = []
        for direction in ("horizontal","vertical","diagonal","square"):
            t, s = top_two_sum(my_score[direction])
            my_values.append(t)
            my_values.append(0.25 * s)   # store fractional second-best contribution
            ot, os = top_two_sum(opponent_score[direction])
            opp_values.append(ot)
            opp_values.append(0.25 * os)

        
        my_heur = sum(my_values)
        opp_heur = sum(opp_values)

        center_bonus = 0.0
        if state[2][2] == self.my_piece:
            center_bonus += 0.03
        elif state[2][2] == opponent_piece:
            center_bonus -= 0.03
        
        # Adjacent to center
        adjacent_center = [(1,2), (2,1), (2,3), (3,2)]
        for i, j in adjacent_center:
            if state[i][j] == self.my_piece:
                center_bonus += 0.02
            elif state[i][j] == opponent_piece:
                center_bonus -= 0.02
        corners_center = [(1,1), (1,3), (3,1), (3,3)]
        for i, j in corners_center:
            if state[i][j] == self.my_piece:
                center_bonus += 0.015
            elif state[i][j] == opponent_piece:
                center_bonus -= 0.015

        return my_heur - opp_heur + center_bonus
 
    def game_value(self, state) -> int:
        """ 
        Checks the current board status for a win condition

        Args:
        state (list of lists): either the current state of the game as saved in
            this TeekoPlayer object, or a generated successor state.

        Returns:
            int: 1 if this TeekoPlayer wins, -1 if the opponent wins, 0 if no winner
        """
        # We first check if we have horizontal, vertical or diagonal placement of either b or r
        # If not then check if we have a 2x2 placement
        opponent_piece = 'r' if self.my_piece == 'b' else 'b'

        # Check if a horizontal win_con has been achieved
        for row in state:
            for j in range(2):
                if(all(row[j+k] == self.my_piece for k in range(4))):
                    return 1
                if(all(row[j+k] == opponent_piece for k in range(4))):
                    return -1
        
        # Check if a vertical win con has been achieved
        for i in range(2):
            for j in range(5):
                if(all(state[i+k][j] == self.my_piece for k in range(4))):
                    return 1
                if(all(state[i+k][j] == opponent_piece for k in range(4))):
                    return -1
                
        # Check for diagonal win-cons     
        # Down-right direction
        for i in range(2):
            for j in range(2):
                if(all(state[i+k][j+k] == self.my_piece for k in range(4))):
                    return 1
                if(all(state[i+k][j+k] == opponent_piece for k in range(4))):
                    return -1      
        # Down-left direction        
        for i in range(2):
            for j in range(4, 2, -1):
                if(all(state[i+k][j-k] == self.my_piece for k in range(4))):
                    return 1
                if(all(state[i+k][j-k] == opponent_piece for k in range(4))):
                    return -1
        for i in range(4):
            for j in range(4):
                # Check if we have a 2x2 win condition
                if(state[i][j] == state[i][j+1] == state[i+1][j] == state[i+1][j+1]):
                    if(state[i][j] == self.my_piece):
                        return 1
                    elif(state[i][j] == opponent_piece):
                        return -1
                
        return 0
    
    def minimax(self, state, depth, alpha, beta) -> tuple:
        """
        Complete the helper function to implement min-max as described in the writeup
        """

        # Check terminal state
        game_val = self.game_value(state)
        opponent_piece = 'r' if self.my_piece == 'b' else 'b'
        if (game_val!= 0):
            return (float(game_val), state)
        # Check if our max depth has been hit
        elif(depth >= self.max_depth):
            return (self.heuristic_game_value(state), state)
        else:
            # Assuming our program is always the max player
            if(depth%2 == 0): # AI turn
                successors = self.succ(state, self.my_piece)
                if not successors:
                    return self.heuristic_game_value(state), state
                best_state = None
                best_value = float('-inf')
                for successor in successors:
                    value, _ = self.minimax(successor, depth+1, alpha, beta)
                    
                    if value > best_value:
                        best_value = value
                        best_state = successor
                    
                    alpha = max(alpha, best_value)
                    if alpha >= beta: # alpha pruning
                        break # Prune the rest, as our beta will dominate the subtree
                return best_value, best_state # Will never return none, as we pass in with float(-inf), thus the very first successor will replace best_state
            else:
                successors = self.succ(state, opponent_piece)
                if not successors:
                    return self.heuristic_game_value(state), state
                best_state = None
                best_value = float('inf')
                for successor in successors:
                    value, _ = self.minimax(successor, depth+1, alpha, beta)
                    
                    if value < best_value:
                        best_value = value
                        best_state = successor
                    beta = min(beta, best_value)
                    if alpha >= beta: # beta pruning
                        break
                return best_value, best_state # Will never return none, as we pass in with float(inf), thus the very first successor will replace best_state




############################################################################
#
# THE FOLLOWING CODE IS FOR SAMPLE GAMEPLAY ONLY
#
############################################################################
def main():
    print('Hello, this is Samaritan')
    ai = TeekoPlayer()
    piece_count = 0
    turn = 0

    # drop phase
    while piece_count < 8 and ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            # start_time = time.time()
            move = ai.make_move(ai.board)
            # end_time = time.time()
            # print("Time taken to make move: " + str(end_time-start_time))
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved at "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                player_move = input("Move (e.g. B3): ")
                while player_move[0] not in "ABCDE" or player_move[1] not in "01234":
                    player_move = input("Move (e.g. B3): ")
                try:
                    ai.opponent_move([(int(player_move[1]), ord(player_move[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        piece_count += 1
        turn += 1
        turn %= 2

    # move phase - can't have a winner until all 8 pieces are on the board
    while ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            # start_time = time.time()
            move = ai.make_move(ai.board)
            # end_time = time.time()
            # print("Time taken to make move: " + str(end_time-start_time))
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved from "+chr(move[1][1]+ord("A"))+str(move[1][0]))
            print("  to "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                move_from = input("Move from (e.g. B3): ")
                while move_from[0] not in "ABCDE" or move_from[1] not in "01234":
                    move_from = input("Move from (e.g. B3): ")
                move_to = input("Move to (e.g. B3): ")
                while move_to[0] not in "ABCDE" or move_to[1] not in "01234":
                    move_to = input("Move to (e.g. B3): ")
                try:
                    ai.opponent_move([(int(move_to[1]), ord(move_to[0])-ord("A")),
                                    (int(move_from[1]), ord(move_from[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        turn += 1
        turn %= 2

    ai.print_board()
    if ai.game_value(ai.board) == 1:
        print("AI wins! Game over.")
    else:
        print("You win! Game over.")


if __name__ == "__main__":
    main()
