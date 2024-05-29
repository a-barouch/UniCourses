DEAD = 0
ALIVE = 1

import random



def flip_coin(rate):
    return 1 if random.random() < rate else 0


class Cell:
    life_status = DEAD

    def __init__(self, row, col, age, lonely):
        self.row = row
        self.col = col
        self.type = "SEXUAL"
        self.new_status = DEAD
        self.is_preyed = False
        self.movement_prob = 0.5
        self.life_time = 5
        self.age = age
        self.lonely = lonely

    # def valid_indices(self, i, j, board):
    #     if i >= 0 and j >= 0:  # non negative index
    #         if i != self.row or j != self.col:  # not current cell
    #             if i < board.num_rows and j < board.num_cols:  # not exceeding board boundaries
    #                 return True
    #     return False

    def valid_indices(self, i, j, board):
        if i >= 0 and j >= 0:  # non negative index
            if i != self.row or j != self.col:  # not current cell
                if i < board.num_rows and j < board.num_cols:  # not exceeding board boundaries
                    return True
        return False

    def calc_updated_life_stat(self, board):
        self.new_status = self.life_status

        # count alive neighbors of all types and of self type
        total_alive, total_alive_for_repr = self.count_live_neighbors(board)

        # death caused by overpopulation
        if self.life_status == ALIVE:
            if total_alive > 3:
                self.new_status = DEAD
            elif total_alive < 2 and self.lonely:
                self.new_status = DEAD
            elif not self.life_time and self.age:
                self.new_status = DEAD
            else:
                self.new_status = ALIVE

        # creation of a new cell by reproduction
        if total_alive_for_repr == 3 and self.get_life_status() == DEAD:
            self.new_status = ALIVE
            if self.age:
                self.life_time = 5
            self.is_preyed = False
        # remove time left
        if self.get_life_status() == ALIVE and self.age:
            self.life_time -= 1
        return self.new_status

    def count_live_neighbors(self, board):
        total_alive, total_alive_for_repr = 0, 0
        for i in range(self.row - 1, self.row + 2):
            for j in range(self.col - 1, self.col + 2):
                if board.no_boundary:
                    i, j = board.mod_idx(i, j)
                if self.valid_indices(i, j, board):
                    cur = board.mat[i][j]
                    if cur.type == self.type:
                        total_alive_for_repr += cur.get_life_status()
                    total_alive += cur.get_life_status()
        return total_alive, total_alive_for_repr

    def move(self, board):
        dead_neighbors = []
        if flip_coin(self.movement_prob) and self.new_status == ALIVE:
            # iterate over neighbors
            for i in range(self.row - 1, self.row + 2):
                for j in range(self.col - 1, self.col + 2):
                    if board.no_boundary:
                        i, j = board.mod_idx(i, j)
                    if self.valid_indices(i, j, board):  # check if indices inside the board and not oneself
                        cur_neighbor = board.mat[i][j]
                        if cur_neighbor.new_status == DEAD:
                            dead_neighbors.append(cur_neighbor)
            if len(dead_neighbors) == 0:
                return
            new_location = random.choice(dead_neighbors)
            return new_location
        return None

    def get_life_status(self):
        return self.life_status

    def set_life_status(self, use_calculated_status, status_to_set=None, board=None):

        # set new status after full iteration of the board
        if use_calculated_status:
            self.life_status = self.new_status

            # create Cell object after death
            if self.life_status == DEAD or self.is_preyed:
                self.life_status = DEAD
                row = self.row
                col = self.col
                board.mat[row][col] = Cell(row, col, self.age, self.lonely)
                board.mat[row][col].life_status = DEAD

        # set by given status
        else:
            self.life_status = status_to_set
