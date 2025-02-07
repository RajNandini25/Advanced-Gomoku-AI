"""
Implement your AI here
Do not change the API signatures for _init_ or _call_
_call_ must return a valid action
"""
import numpy as np

class AdvancedGomokuAI:
    def __init__(self, board_size, win_size):
        self.board_size = board_size
        self.win_size = win_size

    def evaluate_board(self, state, player):
        # Enhanced evaluation of board state.
        score = 0
        for row in range(self.board_size):
            for col in range(self.board_size):
                if state.board[player, row, col] == 1:
                    score += self.evaluate_position(state, player, row, col)
        return score

    def evaluate_position(self, state, player, row, col):
        # Evaluate the position for a player in all directions.
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        total_score = 0
        for drow, dcol in directions:
            line_score, open_ends = self.evaluate_direction(state, player, row, col, drow, dcol)
            total_score += self.calculate_potential(line_score, open_ends)
        return total_score

    def evaluate_direction(self, state, player, row, col, drow, dcol):
        # Evaluate a direction from a position.
        line_score = 0
        open_ends = 0

        # Forward direction
        for i in range(1, self.win_size):
            nrow, ncol = row + i * drow, col + i * dcol
            if not (0 <= nrow < self.board_size and 0 <= ncol < self.board_size):
                break
            if state.board[player, nrow, ncol] == 1:
                line_score += 1
            elif state.board[0, nrow, ncol] == 1:  # Check for empty space
                open_ends += 1
                break
            else:
                break

        # Backward direction
        for i in range(1, self.win_size):
            nrow, ncol = row - i * drow, col - i * dcol
            if not (0 <= nrow < self.board_size and 0 <= ncol < self.board_size):
                break
            if state.board[player, nrow, ncol] == 1:
                line_score += 1
            elif state.board[0, nrow, ncol] == 1:  # Check for empty space
                open_ends += 1
                break
            else:
                break

        return line_score, open_ends

    def calculate_potential(self, line_score, open_ends):
        # Updated potential calculation with central focus.
        # Winning move
        if line_score >= self.win_size - 1:
            return 200000

        # Imminent threat or opportunity
        if line_score == self.win_size - 2:
            if open_ends == 2:
                return 20000  # Double-open four
            if open_ends == 1:
                return 10000   # Single-open four

        # Central control enhancement
        central_bonus = 1
        if line_score >= 2:
            central_bonus = 2

        # Potential setup for future moves
        if line_score >= 2:
            score = 1000 * line_score * central_bonus
            if open_ends:
                score *= 2  # Open ends are more valuable
            return score

        return 10 * (open_ends + 1) * central_bonus  # Basic score for potential



class Submission:
    def __init__(self, board_size, win_size):
        self.board_size = board_size
        self.win_size = win_size
        self.ai = AdvancedGomokuAI(board_size, win_size)

    def __call__(self, state):
        player = state.current_player()
        opponent = 3 - player

        best_score = -np.inf
        best_move = None

        # Enhanced move ordering with central focus
        move_candidates = self.get_prioritized_moves(state, central_focus=True)

        for row, col in move_candidates:
            if state.board[0, row, col] == 1:  # Check if the position is empty
                state.board[player, row, col] = 1
                score = self.ai.evaluate_board(state, player) - self.ai.evaluate_board(state, opponent)
                state.board[player, row, col] = 0  # Reset the board

                if score > best_score:
                    best_score = score
                    best_move = (row, col)

        return best_move

    def get_prioritized_moves(self, state, central_focus=False):
        # Generate move candidates with priority, focusing on central control.
        center = self.board_size // 2
        center_range = self.board_size // 4  # Define a central area
        candidates = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if state.board[0, row, col] == 1:  # Empty cell
                    priority = 0
                    if central_focus and abs(row - center) <= center_range and abs(col - center) <= center_range:
                        priority += 10  # Higher priority for central positions

                    # Additional priority based on proximity to existing stones
                    for drow in range(-1, 2):
                        for dcol in range(-1, 2):
                            nrow, ncol = row + drow, col + dcol
                            if 0 <= nrow < self.board_size and 0 <= ncol < self.board_size and state.board[0, nrow, ncol] != 1:
                                priority += 1
                    candidates.append(((row, col), priority))
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [pos for pos, _ in candidates]