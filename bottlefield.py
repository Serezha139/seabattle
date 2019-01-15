import numpy as np
import itertools as it
import random
from const import *

class Ship:
    def __init__(self, point_list: list):
        self.yard_statuses = {}
        for x, y in point_list:
            self.yard_statuses[(x, y)] = STATUS_ALIVE

    def attack_ship(self, a_x, a_y):
        for x, y in self.yard_statuses.keys():
            if x == a_x and y == a_y and self.yard_statuses[(x, y)] == STATUS_ALIVE:
                self.yard_statuses[(x, y)] = STATUS_DEAD
                return True

    def check_dead(self):
        if STATUS_ALIVE not in self.yard_statuses.values():
            return True

    def get_points_around(self):
        ship_points = list(self.yard_statuses.keys())
        x_min = min([p[0] for p in ship_points])
        x_max = max([p[0] for p in ship_points])
        y_min = min([p[1] for p in ship_points])
        y_max = max([p[1] for p in ship_points])
        tmp_points = it.product(list(range(x_min - 1, x_max + 2)), list(range(y_min - 1, y_max + 2)))

        points_around = [(x, y) for x, y in tmp_points
                         if x in range(0, 10) and y in range(0, 10) and (x, y) not in ship_points]
        return points_around

    @property
    def is_dead(self):
        return self.check_dead()


class Battlefield:
    def __init__(self, auto_generate_ships=True):
        self.field = np.zeros((10, 10))
        self.field_for_enemy = np.zeros((10, 10))
        self.ships = []
        if auto_generate_ships:
            self.add_ships()

    def _get_new_ship_points(
            self,
            x: int,
            y: int,
            direction: int,
            ship_name
    ):
        def get_end(c, length):
            return (c - length, c) if c > 4 else (c, c + length)

        if ship_name == ONE_YARD_SHIP:
            return[(x, y)]
        s_length = SHIP_NAME_LENGTH[ship_name] - 1
        if direction:
            x, x_end = get_end(x, s_length)
            points = [(x, y) for x in range(x, x_end + 1)]
        else:
            y, y_end = get_end(y, s_length)
            points = [(x, y) for y in range(y, y_end + 1)]
        return points

    def _try_to_place_ship(self, x, y, direction, ship_name):
        points = self._get_new_ship_points(x, y, direction, ship_name)
        new_ship = Ship(points)
        p_around = new_ship.get_points_around()
        can_place = True
        for x, y in points:
            if self.field[x, y] != SQUARE_EMPTY:
                can_place = False
                break
        for x, y in p_around:
            if can_place:
                self.field[x, y] = SQUARE_TMP
            else:
                if self.field[x, y] not in (SQUARE_TMP, SQUARE_SHIP_ALIVE):
                    self.field[x, y] = SQUARE_EMPTY
        if can_place:
            self.ships.append(new_ship)
            for x, y in points:
                self.field[x, y] = SQUARE_SHIP_ALIVE
        return can_place

    def add_ships(self):
        for sn in SHIP_NAMES:
            placed = False
            while not placed:
                x = random.randint(0, 9)
                y = random.randint(0, 9)
                direction = random.randint(0, 1)
                placed = self._try_to_place_ship(x, y, direction, sn)

        for (x, y), value in np.ndenumerate(self.field):
            if value == SQUARE_TMP:
                self.field[x, y] = SQUARE_EMPTY


    def attack_battlefield(self, a_x, a_y):
        #returns true if ship was attacked
        if self.field[a_x, a_y] == SQUARE_SHIP_ALIVE:
            for ship in self.ships:
                if ship.attack_ship(a_x, a_y):
                    self.field[a_x, a_y] = SQUARE_SHIP_DEAD
                    self.field_for_enemy[a_x, a_y] = SQUARE_SHIP_DEAD
                    if ship.is_dead:
                        self.mark_points_around(ship)
                    return True

        elif self.field[a_x, a_y] == SQUARE_EMPTY:
            self.field[a_x, a_y] = SQUARE_FIRED
            self.field_for_enemy[a_x, a_y] = SQUARE_SHIP_DEAD

    def mark_points_around(self, s: Ship):
        for x, y in s.get_points_around():
            self.field[x, y] = SQUARE_FIRED
            self.field_for_enemy[x, y] = SQUARE_FIRED

    @property
    def game_over(self):
        return self.check_game_over()

    def check_game_over(self):
        for ship in self.ships:
            if not ship.is_dead:
                return False
        return True


class SeaBattleGame:
    def __init__(self):
        self.battlefield = Battlefield()

    def play_game(self):
        from strategy import Strategy
        s = Strategy()
        move_number = 0
        while not self.battlefield.game_over:
            x, y = s.get_action(self.battlefield.field_for_enemy)
            self.battlefield.attack_battlefield(x, y)
            move_number += 1
        print (self.battlefield.field_for_enemy)
        print('Game ended in %s moves' % move_number)

game = SeaBattleGame().play_game()

