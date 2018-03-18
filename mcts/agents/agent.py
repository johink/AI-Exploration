

class Agent:
    """
    Base class to enforce the agent interface required by the simulator.
    """

    def __init__(self, agent_id):
        self.agent_id = agent_id

    def search(self, state):
        """
        Searches for the next action to take using a strategy provided by 
        the implementation.
        """
        raise NotImplementedError()

    def take_action(self, action):
        """
        Progresses its internal state, if necessary, by the given action.
        """
        raise NotImplementedError()
