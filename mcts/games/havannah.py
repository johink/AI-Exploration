from enum import enum

from game import Game


class Color(Enum):
    BLANK = 0
    BLUE = 1
    RED = 2


class Havannah(Game):
    """
    Action :: (position, color)
    Position :: (x,y,z) or (x,y) depending on cube vs axial coordinates

    Maybe add pie rule later

    coordinates match flat-topped cube grid here:
    https://www.redblobgames.com/grids/hexagons/#coordinates-cube
    """

    BEGINNER_BOARD_SIZE = 8
    BOARD_SIZE = 10

    def __init__(self, num_agents, board_size = BEGINNER_BOARD_SIZE):
        super().__init__(num_agents)
        self.board = HavannahBoard(board_size)
        self.legal_positions = set(self.board.grid.keys())

    def get_legal_actions(self):
        """
        Returns a list of the actions in the action space that are still
        legal for the given agent.
        """
        color = self._agent_id_to_color(self.current_agent_id)
        return [(pos, color) for pos in self.legal_positions]

    def is_legal_action(self, action):
        """
        Checks that the action is using the proper color (ie matching the color
        of the current agent's turn) and that the position has not already
        been taken by another player.
        """
        pos, color = action
        return (color == self._agent_id_to_color(self.current_agent_id)) and (pos in self.legal_positions)

    @Game.progress_game
    def take_action(self, action):
        """
        Apply action to the game and remove that spot from the list of legal
        positions.
        """
        pos, color = action
        self.board.take_action(action)
        self.legal_positions -= pos

    def get_winning_id(self):
        """
        Returns agent_id of player that won the game, or None otherwise.
        """
        winner = self.board.check_winner()
        if winner is not None:
            winner = self._color_to_agent_id(winner)

        return winner

    def is_terminal(self):
        """
        Returns a boolean indicating if the game is in a terminal state.
        """
        return len(self.legal_positions == 0) or self.board.check_winner() is not None

    def _agent_id_to_color(self, agent_id):
        lookup = {0 : Color.BLUE, 1 : Color.RED}
        return lookup[agent_id]

    def _color_to_agent_id(self, color):
        lookup = {Color.BLUE : 0, Color.RED : 1}
        return lookup[color]


class HavannahBoard:
    """
    """

    def __init__(self, board_size):
        self.board_size = board_size
        self.grid = self._generate_hexes(self.board_size)

    def take_action(self, action):
        pos, color = action
        self.grid[pos] = color

    def _generate_hexes(self, board_size):
        hexes = [(x, y, z) for x in range(-board_size + 1, board_size)
                           for y in range(-board_size + 1, board_size)
                           for z in range(-board_size + 1, board_size)
                                 if x + y + z == 0]
        return {key: Color.BLANK for key in hexes}

    def check_winner(self, action):
        """
        Checks the three Havannah win conditions.
        (descriptions from Wikipedia - https://en.wikipedia.org/wiki/Havannah)
            Ring - a loop around one or more cells (no matter whether the encircled cells are occupied by any player or empty
            Bridge - which connects any two of the six corner cells of the board
            Fork -  which connects any three edges of the board; corner points are not considered parts of an edge
        """
        # needs to be updated, but can wait until after we figure out the best way to check for win conditions

        # winner = None
        # for i in range(self.num_agents):
        #     color = self._agent_id_to_color(i)
        #     if self._check_bridge(color) or self._check_fork(color) or self._check_ring(color):
        #         winner = color
        #         break
        # return winner
        pass

    def _check_bridge(self, pos, color):
        fringe = [pos]
        win = False
        visited = set()
        corner_count = 0

        while fringe and not win:
            current = fringe.pop()
            visited.add(current)
            if self._check_if_corner(current):
                corner_count += 1
                if corner_count >= 2:
                    win = True
            neighbors = [x for x in self._get_neighbors(current) if self.grid[x] == color and x not in visited]
            fringe.extend(neighbors)

        return win

    def _check_fork(self, pos, color):
        fringe = [pos]
        win = False
        visited = set()
        edge_set = set()
        unique_edge_count = 0

        while fringe and not win:
            current = fringe.pop()
            visited.add(current)
            if self._check_if_edge(current):
                edge_label = self._get_edge_label(current) # ["-x","x","-y","y","-z","z"]
                if edge_label not in edge_set:
                    unique_edge_count += 1
                    edge_set.add(edge_label)
                    if unique_edge_count >= 3:
                        win = True
            neighbors = [x for x in self._get_neighbors(current) if self.grid[x] == color and x not in visited]
            fringe.extend(neighbors)

        return win

    def _check_ring(self, pos, color):
        pass

    def _check_if_corner(self, pos):
        """
        Corner hexes are always combination of (bs -1, -bs + 1, 0)
        """
        return max(pos) == self.board_size - 1 and abs(min(pos)) == board_size - 1

    def _check_if_edge(self, pos):
        """
        edges always have one and only one coordinate that satisfies abs(coord) == bs-1
        this excludes corners, which satisfies the second part of the fork win condition
        """
        return (abs(max(pos)) == self.board_size - 1) ^ (abs(min(pos)) == self.board_size - 1)

    def _get_neighbors(self, pos):
        neighbors = []
        for delta in [(-1, 1, 0), (1, -1, 0), (-1, 0, 1), (1, 0, -1), (0, 1, -1), (0, -1, 1)]:
            new_tuple = add_tuples(pos, delta)
            if max(new_tuple) < self.board_size and min(new_tuple) > -self.board_size:
                neighbors.append(new_tuple)
        return neighbors

    def _get_edge_label(self, pos):
        index, _ = max(enumerate(pos), key = lambda x: x[1])
        mapping = {0: "x", 1: "y", 2: "z"}
        label = mapping[index]

        if abs(min(pos)) > max(pos):
            label = "-" + label

        return label

def add_tuples(a, b):
    if len(a) != len(b):
        raise ValueError("WHAT THE HELL?")
    else:
        return tuple([one + two for one, two in zip(a, b)])
