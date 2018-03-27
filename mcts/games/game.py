from copy import deepcopy
from random import choice


class Game:
    """
    Base class to enforce the game interface required by the simulator and
    agents to play.
    """

    def __init__(self, num_agents):
        self.num_agents = num_agents
        self.current_agent_id = 0

    def copy(self):
        """
        Returns a copy of the state, so that agents can manipulate it as
        they decide on actions.
        """
        return deepcopy(self)

    def get_legal_actions(self, agent_id):
        """
        Returns a list of the actions in the action space that are still
        legal for the given agent.
        """
        raise NotImplementedError()

    def is_action_legal(self, action):
        """
        Returns a boolean indicating if the action is valid and legal.
        """
        raise NotImplementedError()

    def take_action(self, action):
        """
        Updates the state of the board in place.
        """
        raise NotImplementedError()

    def generate_random_action(self):
        random_action = choice(self.get_legal_actions(self.current_agent_id))
        return random_action

    def get_winning_id(self):
        """
        Returns agent_id of player that won the game, or None otherwise.
        """
        raise NotImplementedError()

    def is_terminal(self):
        """
        Returns a boolean indicating if the game is in a terminal state.
        """
        raise NotImplementedError()

    @classmethod
    def progress_game(cls, func):
        """
        Decorator for use by sub-classes, to call _increment_current_agent_id
        without an explicit method call.
        """
        def f(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self._increment_current_agent_id()
            return result
        return f

    def _increment_current_agent_id(self):
        """
        Increments the attribute while ensuring it stays within range
        [0, self.num_agents).
        """
        self.current_agent_id += 1
        if self.current_agent_id == self.num_agents:
            self.current_agent_id = 0
