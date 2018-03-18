from agents.mcts_agent import MCTSAgent
from agents.random_agent import RandomAgent
from games.nested_ttt import NestedTTT
from willsmith.simulator import Simulator

if __name__ == "__main__":
    simulator = Simulator(NestedTTT, [MCTSAgent, MCTSAgent])
    simulator.run_game()
