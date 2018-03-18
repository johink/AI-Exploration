from math import log, sqrt
from random import choice
from time import time

from agents.agent import Agent


class MCTSAgent(Agent):
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
        super().__init__(agent_id)
        self.root = self.Node(None, None)


    def search(self, state, max_time = .5):
        """
        Searches for the optimal action to take by running max_runs
        number of playouts and recording the results.
        """
        runs = 0
        start_time = time()

        while time() - start_time < max_time:
            current_state = state.copy()
            current_state, current_node, game_over = self._selection(current_state, self.root)
            if not game_over:
                new_state, new_node = self._expansion(current_state, current_node)
                winning_id = self._simulation(new_state)
                self._backpropagation(winning_id, new_node)
            else:
                winning_id = self._simulation(current_state)
                self._backpropagation(winning_id, current_node)
            runs += 1

        next_action = self.root.max_trials()
        return next_action

    def take_action(self, action):
        try:
            self.root = self.root.get_child(action)
        except KeyError:
            #print("Restarting Tree")
            self.root = self.Node(None, None)

    def _selection(self, state, node):
        """
        Progresses through the tree of Nodes, starting at node, until a leaf
        is found.
        """
        unexplored_actions = set(state.get_legal_actions(state.current_agent_id)) - set(node.children.keys())
        terminal = state.is_terminal()
        while not unexplored_actions and not terminal:
            action = node.UCB(state, self.root.trials)  # root.trials == total number of trials

            state.take_action(action)
            node = node.get_child(action)

            unexplored_actions = set(state.get_legal_actions(state.current_agent_id)) - set(node.children.keys())
            terminal = state.is_terminal()

        return state, node, terminal

    def _expansion(self, state, node):
        """
        Handles creation of a new leaf in the Node tree.
        """
        action = choice([action for action in state.get_legal_actions(state.current_agent_id) if action not in node.children])
        new_child = self.Node(node, state.current_agent_id)
        node.add_child(action, new_child)

        state.take_action(action)

        return state, new_child

    def _simulation(self, state):
        """
        Plays out the game to its conclusion and returns the result.
        """
        while not state.is_terminal():
            action = self._random_simulation(state)
            #action = self._directed_ttt_simulation(state)
            state.take_action(action)
        return state.get_winning_id()

    def _random_simulation(self, state):
        """
        Randomly chooses actions to progress the state with no logic.
        """
        action = state.generate_random_action()
        return action

    def _directed_ttt_simulation(self, state):
        """
        Chooses moves based on the following policy:
        1) Take any board winning positions
        2) Take any board losing positions
        3) Take random action
        """
        winning_actions = self._find_winning_actions(state)
        if winning_actions:
            action = choice(winning_actions)
        else:
            losing_actions = self._find_losing_actions(state)
            if losing_actions:
                action = choice(losing_actions)
            else:
                action = self._random_simulation(state)
        return action

    def _find_winning_actions(self, state):
        return state.find_all_winning_actions(self.agent_id)

    def _find_losing_actions(self, state):
        return state.find_all_losing_actions(self.agent_id)

    def _backpropagation(self, winning_id, node):
        """
        Propogates simluation result up the tree of nodes.
        """
        while node is not None:
            node.update_node(winning_id)
            node = node.parent

    def _get_extreme_actions(self):
        maxi = None
        mini = None
        for action in self.root.children:
            node = self.root.children[action]
            value = node._value_estimate()
            if maxi is None or value > maxi._value_estimate():
                maxi = node
            if mini is None or value < mini._value_estimate():
                mini = node
        return maxi, mini

    def __str__(self):
        return "AgentID:Max:[{}], Min:[{}]".format(*self._get_extreme_actions())

    class Node:
        """
        Used internally by the agent to keep track of the results of trials
        after taking certain actions.
        """
# steam pooped itself, are you there John?
# Hello?  Is it John you're looking for?
# I can see it in your eyes.  I can see it in your smile.

# my IDE is open wide ^_-
# I'm dying over here.  I heard, "Did you want to..."

# How does Thursday work?  aka two days from today
# Sure, we can get a quick jump in this.

# Okay, so we'll watch lesson 1 videos on our own time and then meet up to create something related to it (gridworld?)
# Yep.  What time Thursday?

# Noon?  My time
# Dealio

# Okay.  Sounds good.  BYE CHAD!  ^_-
# Sweet.

# I'll push up the changes in the next few minutes, BYE JOHN!







        EXP_PARAM = sqrt(2)

        def __init__(self, parent, agent_id):
            self.parent = parent
            self.children = dict() # action : node
            self.trials = 0
            self.wins = 0
            self.agent_id = agent_id

        def add_child(self, action, node):
            self.children[action] = node

        def update_node(self, winning_id):
            """
            Updates node using simulation result during backpropagation step.
            """
            if self.agent_id is not None and winning_id == self.agent_id:
                self.wins += 1
            self.trials += 1

        def _value_estimate(self):
            return self.wins / self.trials

        def max_trials(self):
            """
            Returns the minimum action at the node given the current children.
            """
            value_func = lambda x: self.get_child(x).trials
            return max(self.children, key=value_func)

        def UCB(self, state, total_trials):
            """
            Chooses an action based on an exploitation vs exploration function
            expressed as:

            num wins at node / num trials node +
                exploration parameter *
                    sqrt(ln(total trials) / num trials at node)
            """
            valid_actions = state.get_legal_actions(state.current_agent_id)
            results = {}

            for action in valid_actions:
                value_estimate = self.get_child(action)._value_estimate()
                exploration_estimate = self.EXP_PARAM * sqrt(log(total_trials) / self.trials)

                results[action] = value_estimate + exploration_estimate

            return max(results.keys(), key=results.get)

        def get_child(self, action):
            return self.children[action]

        def has_children(self):
            return bool(self.children)

        def __str__(self):
                return "ID:{},{}/{}".format(self.agent_id, self.wins, self.trials)
