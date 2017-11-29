# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood().asList()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        power_pellets = currentGameState.getCapsules()

        ghost_dists = [util.manhattanDistance(newPos, ghostState.getPosition()) for ghostState in newGhostStates]
        pellet_dists = [util.manhattanDistance(newPos, pelletPos) for pelletPos in power_pellets]
        food_dists = [util.manhattanDistance(newPos, foodPos) for foodPos in newFood]

        ghost_score = 0
        for ghostState, scaredTime in zip(newGhostStates, newScaredTimes):
            ghost_dist = util.manhattanDistance(newPos, ghostState.getPosition())
            if ghost_dist == 0:
                if scaredTime:
                    ghost_score = 10
                else:
                    ghost_score = -200
                break

            if ghost_dist == 1 and scaredTime == 0:
                ghost_score = -5
                break

            if scaredTime >= ghost_dist:
                ghost_score = 2

        if pellet_dists and min(pellet_dists) < 3 and min(ghost_dists) < 4 and max(newScaredTimes) == 0:
            pellet_score = 10. / min(pellet_dists)
        else:
            pellet_score = 0

        if not food_dists:
            food_score = 100
        else:
            food_score = 1. / min(food_dists) - len(food_dists)

        #print ghost_score, food_score, pellet_score
        return ghost_score + food_score + pellet_score

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

    def recursive_search(self, gameState, agentIndex, currentDepth, algo, alphaBeta = False):
        if currentDepth >= self.depth:
            return self.evaluationFunction(gameState)


        actions = gameState.getLegalActions(agentIndex)

        if not actions:
            return self.evaluationFunction(gameState)

        successors = [gameState.generateSuccessor(agentIndex, action) for action in actions]

        results = []

        for successor in successors:
            n_agents = successor.getNumAgents()
            if agentIndex + 1 < n_agents:
                nextAgent = agentIndex + 1
                nextDepth = currentDepth
            else:
                nextAgent = 0
                nextDepth = currentDepth + 1

            results.append(self.recursive_search(successor, nextAgent, nextDepth, algo, alphaBeta))

        if agentIndex == 0 and currentDepth == 0:
            return sorted(zip(results, actions))[-1][1]



        if algo == "minimax":
            if agentIndex == 0:
                return max(results)
            else:
                return min(results)

class MinimaxAgent(MultiAgentSearchAgent):
    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        return self.recursive_search(gameState, 0, 0, "minimax", False)



class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
