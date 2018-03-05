from random import choice


class Game:
    """
    Base class to enforce the interface required by the simulator.
    """

    def __init__(self, agent_ids):
        self.agent_ids = agent_ids
        self.agent_turn = 0

    def get_legal_actions(self):
        """
        Returns a list of the actions in the action space that are still legal.
        """
        raise NotImplementedError

    def take_action(self, action):
        """
        Returns an updated state based on the given action
        """
        raise NotImplementedError

    def generate_random_action(self):
        random_action = choice(self.get_legal_actions())
        return random_action

    def win_check(self, agent_id):
        """
        Returns True if the given agent has won the game, False otherwise.
        """
        raise NotImplementedError

    def is_terminal(self):
        """
        Returns True if the game is in a terminal state, False otherwise.
        """
        raise NotImplementedError

    def increment_agent_turn(self):
        """
        Moves to the next agent's id, wrapping around at the end of the list.
        """
        self.agent_turn += 1
        if self.agent_turn == len(self.agent_ids):
            self.agent_turn = 0
