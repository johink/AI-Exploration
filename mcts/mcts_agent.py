from math import log, sqrt
from random import choice
from time import time


class MCTSAgent:
    """
    Planning agent that makes decisions based on Monte Carlo Tree Search.
    Computes a number of playouts using the following steps, then chooses the
    optimal action:

        Selection       -   Start at root, use UCB to choose actions until action does not produce child
        Expansion       -   Create new node
        Simulation      -   Play out game until reaching a terminal state
        Backpropagation -   Update win/trial counters for new node and all parents
    """


    def __init__(self, agent_id):
        self.root = self.Node(None, False)
        self.agent_id = agent_id

    def search(self, state, max_runs = 1000, max_time = 2):
        """
        Searches for the optimal action to take by running max_runs
        number of playouts and recording the results.
        """
        runs = 0
        start_time = time()

        while runs < max_runs:  # and time() - start_time < 2
            #print(runs)
            current_state = state.copy()
            current_state, current_node = self.selection(current_state, self.root)
            new_node = self.expansion(current_state, current_node)
            win = self.simulation(current_state)
            self.backpropagation(win, new_node)
            runs += 1

        best_action = self.root.max_value_estimate()
        return best_action

    def take_action(self, action):
        # need to handle case where we have not expanded that action
        # and it does not exist in the Node tree
        try:
            self.root = self.root.get_child(action)
        except KeyError as ke:
            print(ke)
            raise RuntimeError("KeyError, ending game.")

    def selection(self, state, node):
        """
        Progresses through the tree of Nodes until a leaf is found.
        """
        while len(set(state.get_legal_actions()) - set(node.children)) == 0:
            action = node.UCB(state, self.root.trials)  # root.trials == total number of trials
            state.take_action(action)
            node = node.get_child(action)

        return state, node

    def expansion(self, state, node):
        """
        Handles creation of a new leaf in the Node tree.
        """
        # check for if we are in a terminal state before adding nodes ??
        action = choice([action for action in state.get_legal_actions() if action not in node.children])
        new_child = self.Node(node, not node.adversarial)
        node.add_child(action, new_child)
        return new_child

    def simulation(self, state):
        """
        Plays out the game to its conclusion and returns the result.
        """
        while not state.is_terminal():
            action = state.generate_random_action()
            state.take_action(action)

        return state.win_check(self.agent_id)

    def backpropagation(self, win, node):
        """
        Propogates simluation result up the tree of nodes.
        """
        while node is not None:
            node.update_node(win)
            node = node.parent


    class Node:
        """
        Used internally by the agent to keep track of the results of trials
        after taking certain actions.
        """

        EXP_PARAM = sqrt(2)
        NEW_NODE_TRIALS = 0.1       # what should this be?


        def __init__(self, parent, adversarial = False):
            self.parent = parent
            self.children = dict() # action : node
            self.trials = 0
            self.wins = 0
            self.adversarial = adversarial

        def add_child(self, action, node):
            self.children[action] = node

        def update_node(self, win):
            """
            Updates node using simulation result during backpropagation step.
            """
            if win ^ self.adversarial: # either win+maximizing or lose+minimizing
                self.wins += 1
            self.trials += 1

        def value_estimate(self):
            return self.wins / self.trials

        def max_value_estimate(self):
            """
            Returns maximum action at the node given the current children.
            """
            value_func = lambda x: self.get_child(x).value_estimate()
            return max(self.children, key=value_func)

        def UCB(self, state, total_trials):
            """
            Chooses an action based on an exploitation vs exploration function
            expressed as:

            num wins at node / num trials node +
                exploration parameter *
                    sqrt(ln total trials / num trials at node)
            """
            valid_actions = state.get_legal_actions()
            results = {}

            for action in valid_actions:
                value_estimate = 0
                exploration_estimate = self.EXP_PARAM * sqrt(log(total_trials) / self.NEW_NODE_TRIALS)
                if action in self.children:
                    value_estimate = self.get_child(action).value_estimate()
                    exploration_estimate = self.EXP_PARAM * sqrt(log(total_trials) / self.trials)


                results[action] = value_estimate + exploration_estimate

            return max(results.keys(), key=results.get)

        def get_child(self, action):
            return self.children[action]

        def has_children(self):
            return bool(self.children)
