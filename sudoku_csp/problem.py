class SudokuProblem:
    def __init__(self, initial_assignments, n = 9):
        if int(n ** .5) != n ** .5:
            raise ValueError("Board width must be a perfect square")
        self.n = n
        self.sqrt_n = int(n ** .5)
        self.initial_assignments = initial_assignments
        self.board = self.create_board(self.initial_assignments)
        self.domain = set(range(1, self.n+1))
        self.variables = {(x, y) for x in range(self.n) for y in range(self.n)}

    def create_board(self, assignments = None):
        board = [[0 for _ in range(self.n)] for _ in range(self.n)]
        if assignments is not None:
            for (row, col), value in assignments:
                board[row][col] = value
        return board

    def check_assignment(self, assignments):
        board = self.create_board(assignments)
        return self.check_horizontal(board) and self.check_cage(board) and self.check_vertical(board)

    def check_solved(self, assignments):
        return len(assignments) == self.n ** 2 and self.check_assignment(assignments)

    def check_horizontal(self, board):
        for row in board:
            seen = set()
            for value in row:
                if value in seen and value != 0:
                    return False
                elif value != 0:
                    seen.add(value)
        return True

    def check_cage(self, board):
        for i in range(self.n):
            start_row = i // self.sqrt_n * self.sqrt_n
            start_col = i % self.sqrt_n * self.sqrt_n
            seen = set()
            for j in range(start_row, start_row + self.sqrt_n):
                for k in range(start_col, start_col + self.sqrt_n):
                    if board[j][k] in seen and board[j][k] != 0:
                        return False
                    elif board[j][k] != 0:
                        seen.add(board[j][k])
        return True

    def check_vertical(self, board):
        for i in range(self.n):
            seen = set()
            for j in range(self.n):
                value = board[j][i]
                if value in seen:
                    return False
                elif value != 0:
                    seen.add(value)
        return True
