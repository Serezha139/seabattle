from const import SQUARE_EMPTY
class Strategy:

    def get_action(self, field):
        for x in range(0, 10):
            for y in range(0, 10):
                if field[x, y] == SQUARE_EMPTY:
                    return x, y
