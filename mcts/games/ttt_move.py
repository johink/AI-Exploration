from enum import Enum


class TTTMove(Enum):
    BLANK = 1
    X = 2
    O = 3

    def __str__(self):
        name = str(self.name)
        if name == "BLANK":
            name = " "
        return name

    def __repr__(self):
        return self.__str__()
