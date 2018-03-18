from games.nested_ttt import NestedTTT
from games.ttt_move import TTTMove
from games.ttt_view import TTTView


class TTTViewController:
    """
    Controls the GUI for the TTT game and provides and interface for the 
    simulator to send/receive inputs/game actions.
    """

    def __init__(self):
        self.view = self.initialize_view()

    def initialize_view(self);
        view = TTTView()
        view.set_button_commands(self._board_button)
        return view

    def _board_button(self, button, row, col, inner_row, inner_col):
        """
        Generates a function that:
        If the button is a legal move, calls for update to the game state 
        and updates the button text.
        """
        def f():
            # get current player move
            # form action with move/row/col/irow/icol
            # attempt to take action for current player
            # if the action was taken, update the button text
            # otherwise maybe a pop-up
        return f
