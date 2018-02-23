from enum import Enum
from random import choice
import numpy as np
import time


class State:
    """
    Base class to enforce the interface required by MCTSAgent.
    """

    def __init__(self, action_space, agent_id_list):
        self.action_space = action_space

    def get_valid_actions(self):
        return self.action_space

    def take_action(self, action):
        """
        Returns an updated state based on the given action
        """
        raise NotImplementedError

    def take_random_action(self):
        random_action = choice(self.get_valid_actions)
        return self.take_action(random_action)

    def win(self, agent_id):
        """
        Returns True if the given agent has won the game, False otherwise.
        """
        raise NotImplementedError

    def final(self):
        """
        Returns True if the game is in a terminal state, False otherwise.
        """
        raise NotImplementedError


class TTTMove(Enum):
    BLANK = 1
    X = 10
    O = 100

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return TTTMove.__add__(self, other)

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return TTTMove.__mul__(self, other)

    def __str__(self):
        name = str(self.name)
        if name == "BLANK":
            name = " "
        return name

    def __repr__(self):
        return self.__str__()


class NestedTTT(State):

    class Board:
        def __init__(self):
            self.board = np.full((3,3), TTTMove.BLANK)

        def take_action(self, action, r, c):
            self.board[r, c] = action

        def check_winner(self):
            """
            Check for a winner by summing over columns, rows, and diagonals
            Enum values cannot overlap, so 3 times Enum value means we have 3 in a row
            """
            for team in [TTTMove.X, TTTMove.O]:
                if (np.any(self.board.sum(axis = 1) == team * 3) or
                   np.any(self.board.sum(axis = 0) == team * 3) or
                   np.diag(self.board).sum() == team * 3 or
                   np.diag(self.board[::-1]).sum() == team * 3):
                    return team

            return None

    def __init__(self):
        self.outer_board = self.Board()
        self.inner_boards = [[self.Board() for _ in range(3)] for _ in range(3)]
        self.game_over = False

    def get_state(self):
        return self.board

    def take_action(self, action, location):
        """
        Take an action on the inner board, which will update the outer board if
        it is a winning move.  If the outer board is now won, return 1 to indicate
        the player has won the game, otherwise return None
        """
        r, c, ir, ic = location
        self.inner_boards[r][c].take_action(action, ir, ic)
        winner = self.inner_boards[r][c].check_winner()
        if winner is not None:
            self.outer_board.board[r, c] = winner
            if self.outer_board.check_winner():
                return 1

        return None

    def __str__(self):
        result = []
        for i in range(3):
            for j in range(3):
                result.append(" | ".join([str(inner_board.board[j]) for inner_board in self.inner_boards[i]]))
            if i < 2:
                result.append("-"*20)
        return "\n".join(result)



# could make Agent base class that enforces needed interface for some
# simulator class that runs games with agents

class MCTSAgent:
    """
    Planning agent that makes decisions based on Monte Carlo Tree Search.
    Computes a number of trials using the following steps, then chooses the
    optimal action:

        Selection       -   Start at root, use UCB to choose actions until action does not produce child
        Expansion       -   Create new node
        Simulation      -   Play out game until reaching a terminal state
        Backpropagation -   Update win/trial counters for new node and all parents
    """

    EXP_PARAM = 2 ** .5
    NEW_NODE_TRIALS = 0.1       # what should this be?

    class Node:
        """
        Used internally by the agent to keep track of the results of trials
        after taking certain actions.
        """
        def __init__(self, parent, adversarial = False):
            self.parent = parent
            self.children = dict() # action : node
            self.trials = 0
            self.wins = 0

        def update_node(self, win):
            """
            Updates node using simulation result during backpropagation step.
            """
            if win ^ adversarial: # either win+maximizing or lose+minimizing
                self.wins += 1
            self.trials += 1

        def value_estimate(self):
            return self.wins / self.trials

        def max_value_estimate(self):
            """
            Returns maximum action at the node given the current children.
            """
            return max(self.children, key=lambda x: self.children.get_child(x).value_estimate())

        def UCB(self, state, total_trials):
            """
            Chooses an action based on an exploitation vs exploration function
            expressed as:

            num wins at node / num trials node +
                exploration parameter *
                    sqrt(ln total trials / num trials at node)
            """
            valid_actions = state.get_valid_actions()
            results = {}

            for action in valid_actions:
                value_estimate = 0
                exploration_estimate = EXP_PARAM * (np.log(total_trials) / NEW_NODE_TRIALS) ** .5
                if action in self.children:
                    value_estimate = self.get_child(action).value_estimate()
                    exploration_estimate = EXP_PARAM * (np.log(total_trials) / self.trials) ** .5

                results[action] = value_estimate + exploration_estimate

            return max(results.keys(), key=results.get)

        def get_child(self, action):
            return self.children[action]

        def has_children(self):
            return bool(self.children)


    def __init__(self, state, agent_id):
        self.state = state
        self.root = self.Node(None, False)
        self.agent_id = agent_id

    def search(self, max_runs = 1000, max_time = 2):
        """
        Searches for the optimal action to take by running max_runs
        number of playouts.
        """
        runs = 0
        time = time.time()

        while runs < max_runs:  # and time.time() - time < 2
            current_state, current_node = self.selection()
            new_node = self.expansion(current_state, current_node)
            win = self.simulation(current_state)
            self.backpropagation(win, new_node)

        best_action = self.root.max_value_estimate()
        return best_action

    def take_action(self, action):
        self.state = self.state.take_action(action)
        self.root = self.root.get_child(action)

    def selection(self):
        current_state = self.state
        current_node = self.root

        while current_node.has_children():
            action = current_node.UCB(state, self.root.trials)  # root.trials == total number of trials
            current_state = current_state.take_action(action)
            current_node = current_node.get_child(action)

        return current_state, current_node

    def expansion(self, state, node):
        # create a new node for some action ?? where does that action come from
        node.add_child(action, self.Node(node, not node.adversarial))
        new_child = node.get_child(action)
        return new_child

    def simulation(self, state):
        """
        Plays out the game to its conclusion and returns the result.
        """
        while not state.final():
            state = state.take_random_action()

        return state.win(self.agent_id)   # need some reference to agent to determine win or lose

    def backpropagation(self, win, node):
        """
        Propogates simluation result up the tree of nodes.
        """
        while node is not None:
            node.update_node(win)
            node = node.parent
