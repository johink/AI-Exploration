from ttt_move import TTTMove
from ttt_view import TTTView


class TTTViewController:
    """
    Controls the GUI for the TTT game and provides and interface for the 
    simulator to send/receive inputs/game actions.
    """

    def __init__(self, board_size):
        self.view = self.initialize_view(board_size)

    def initialize_view(self, board_size);
        view = TTTView(board_size)
        view.set_button_commands(self._board_button)
        return view

    def _board_button(self, button, row, col):
        """
        Generates a function that:
        If the button is a legal move, calls for update to the game state 
        and updates the button text.
        """
        def f():
            self._is_legal_move(button)
            # TODO
        return f

    def _is_legal_move(self, button):
        return button["text"] == str(TTTMove.BLANK)
