import numpy as np

from functools import reduce
from game import Game
from ttt_move import TTTMove
from copy import deepcopy
from itertools import product


class NestedTTT(Game):
    """
    Action :: ((or, oc), ((ir, ic), move))
    NestedTTTAction :: (outer_position, BoardAction)
    outer_position :: (r, c)
    BoardAction :: (position, move)
    """


    STANDARD_BOARD_SIZE = 3


    def __init__(self, agent_ids, board_size = STANDARD_BOARD_SIZE):
        self.board_size = board_size
        self.outer_board = Board(self.board_size)
        self.inner_boards = [[Board(self.board_size) for _ in range(self.board_size)] for _ in range(self.board_size)]

        bs = self.board_size
        self.legal_positions = {((r, c), (ir, ic)) for r in range(bs) for c in range(bs) for ir in range(bs) for ic in range(bs)}

        super().__init__(agent_ids)

    def copy(self):
        return deepcopy(self)

    def get_legal_actions(self):
        move = self._agent_id_to_move(self.agent_turn)
        return [(outer_pos, (inner_pos, move)) for outer_pos, inner_pos  in self.legal_positions]

    def get_state(self):
        return self.board

    def take_action(self, action, debug = False):
        """
        Applies the action to the game and updates the outer board if necessary.
        Also removes now illegal positions from self.legal_positions
        """
        outer_pos, inner_action = action
        r, c = outer_pos
        inner_pos, move = inner_action
        board_won = self.inner_boards[r][c].take_action(inner_action)
        if debug:
            print("Placing {} on board {} at position {}".format(move, outer_pos, inner_pos))
            if board_won:
                print("Board {} won by {}".format(outer_pos, move))
        if board_won:
            self.outer_board.take_action((outer_pos, move))

        if debug:
            before = len(self.legal_positions)
        self._remove_illegal_positions(outer_pos, inner_pos, board_won)
        if debug:
            print("Available moves went from {} to {}".format(before, len(self.legal_positions)))

        self.increment_agent_turn()

    def _remove_illegal_positions(self, outer_pos, inner_pos, board_won):
        """
        Clears positions from self.legal_positions based on action taken and if
        a nested game was completed.
        """
        self.legal_positions.remove((outer_pos, inner_pos))
        if board_won:
            self.legal_positions -= {(outer_pos, (r, c)) for r in range(self.board_size) for c in range(self.board_size)}

    def is_terminal(self):
        winner = self.outer_board.get_winner() is not None
        return winner or not self.get_legal_actions()

    def win_check(self, agent_id):
        """
        Determines if the player with agent_id won the game
        """
        win = False
        if self.is_terminal():
            agent_move = self._agent_id_to_move(agent_id)
            win = self.outer_board.check_if_winner((None, agent_move))
        return win

    def _agent_id_to_move(self, agent_id):
        lookup = {0 : TTTMove.X, 1 : TTTMove.O}
        return lookup[agent_id]

    def __str__(self):
        result = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                result.append(" | ".join([str(inner_board.board[j]) for inner_board in self.inner_boards[i]]))
            if i < 2:
                result.append("-"*20)
        return "\n".join(result)

class Board:

    @staticmethod
    def generate_winning_positions():
        STANDARD_BOARD_SIZE = 3
        winning_positions = set()
        other_moves = [TTTMove.BLANK, TTTMove.X, TTTMove.O]
        all_possibilities = list(product(other_moves, repeat = (STANDARD_BOARD_SIZE ** 2 - STANDARD_BOARD_SIZE)))

        for move in [TTTMove.X, TTTMove.O]:
            winner = (move,) * STANDARD_BOARD_SIZE
            for possibility in all_possibilities:
                #Creating row wins
                for r in range(STANDARD_BOARD_SIZE):
                    board = []
                    pcopy = list(possibility)
                    for i in range(STANDARD_BOARD_SIZE):
                        if i == r:
                            board.append(winner)
                        else:
                            board.append((pcopy.pop(), pcopy.pop(), pcopy.pop()))
                    winning_positions.add(tuple(board))

                #Creating column wins
                for col in range(STANDARD_BOARD_SIZE):
                    board = []
                    pcopy = list(possibility)
                    for _ in range(STANDARD_BOARD_SIZE):
                        board.append(tuple((move if curr == col else pcopy.pop() for curr in range(STANDARD_BOARD_SIZE))))
                    winning_positions.add(tuple(board))

                #Creating diagonal wins
                board = []
                pcopy = list(possibility)
                for d in range(STANDARD_BOARD_SIZE):
                    board.append(tuple(move if i == d else pcopy.pop() for i in range(STANDARD_BOARD_SIZE)))
                winning_positions.add(tuple(board))

                #Creating counter-diagonal wins
                board = []
                pcopy = list(possibility)
                for d in range(NestedTTT.STANDARD_BOARD_SIZE):
                    board.append(tuple(move if (i + d) == (STANDARD_BOARD_SIZE - 1) else pcopy.pop() for i in range(STANDARD_BOARD_SIZE)))
                winning_positions.add(tuple(board))
        return winning_positions

    # nightmare
    winning_positions = generate_winning_positions.__func__()

    def __init__(self, board_size):
        self.board_size = board_size
        self.board = np.full((self.board_size, self.board_size), TTTMove.BLANK)

    def take_action(self, action):
        """
        Applies the action to the board.
        Returns whether the board is won or not after this action.
        """
        pos, move = action
        self.board[pos] = move
        return self.check_if_winner(action)

    def get_winner(self):
        """
        Returns the move that won the board or None if it is still ongoing.
        """
        winner = None
        for move in [TTTMove.X, TTTMove.O]:
            if self.check_if_winner((None, move)):
                winner = move
                break
        return winner

    def check_if_winner(self, action):
        """
        Determine if the player with move in the action won the board.
        """
        return tuple(map(tuple, self.board)) in self.winning_positions

    def _check_axis_for_win(self, array, move):
        """
        Returns if all elements are the same as move.

        Uses the fact that sets do not contain duplicate items to
        quickly determine if there is a complete row.
        """
        move_set = set(array).union({move})
        return len(move_set) == 1
