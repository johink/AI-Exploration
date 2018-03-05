from enum import Enum


class TTTMove(Enum):
    BLANK = 1
    X = 10
    O = 100

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return TTTMove.__add__(self, other)

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return TTTMove.__mul__(self, other)

    def __str__(self):
        name = str(self.name)
        if name == "BLANK":
            name = " "
        return name

    def __repr__(self):
        return self.__str__()
