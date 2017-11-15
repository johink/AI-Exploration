from tkinter import Button, END, Entry, StringVar, Tk


class MainWindow:
    BOX_WIDTH = 2
    
    def __init__(self, board):
        self.root = Tk()
        self.button = None

        self.board_boxes = []
        self.create_board_gui(board)

    def start(self):
        self.root.mainloop()

    def create_board_gui(self, board):
        for row in range(len(board)):
            new_row = []
            for col in range(len(board[row])):
                box = Entry(self.root, width=MainWindow.BOX_WIDTH)
                box.grid(row=row, column=col)

                new_row.append(box)
            self.board_boxes.append(new_row)

        self.button = Button(self.root, text="Start solving")
        self.button.grid(row=(len(board)+1), column=0, columnspan=len(board))

    def clear_board(self):
        for row in range(len(self.board_boxes)):
            for col in range(len(self.board_boxes[row])):
                self.board_boxes[row][col].delete(0, END)

    def update_gui(self, assignments):
        self.clear_board()
        for assignment in assignments:
            coord, value = assignment
            row, col = coord
            self.board_boxes[row][col].insert(0, str(value))

    def get_initial_assignments(self):
        assignments = []
        for row in range(len(self.board_boxes)):
            for col in range(len(self.board_boxes[row])):
                value = self.board_boxes[row][col].get()
                if value != "":
                    assignments.append(((row,col), int(value)))
        return assignments

    def add_button_command(self, command):
        self.button.config(command = command)
