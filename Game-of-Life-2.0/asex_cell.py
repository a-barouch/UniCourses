from cell import Cell
import random

DEAD = 0
ALIVE = 1


def flip_coin(rate):
    return 1 if random.random() < rate else 0


class Asex(Cell):

    def __init__(self, row, col, age, lonely, reproduction):
        Cell.__init__(self, row, col,age,lonely)
        self.type = "ASEXUAL"
        self.reproduction_prob = reproduction
        self.is_preyed = False
        self.lonely = True
        self.age = True
        self.age = age
        self.lonely = lonely

    def calc_updated_life_stat(self, board):

        # count alive neighbors of all types
        total_alive, _ = self.count_live_neighbors(board)

        # death caused by overpopulation
        if self.life_status == ALIVE:
            if total_alive > 3:
                self.new_status = DEAD
            elif total_alive < 2 and self.lonely:
                self.new_status = DEAD
            elif not self.life_time and self.age:
                self.new_status = DEAD
            elif self.age:
                self.life_time -= 1
            else:
                self.new_status = ALIVE
        # asexual reproduction if the cell is alive and by probability
        if self.get_life_status() == ALIVE and flip_coin(self.reproduction_prob):
            self.asexual_reproduction(board)
        return self.new_status

    def asexual_reproduction(self, board):
        dead_neighbors = []

        # find available cells to reproduction
        for i in range(self.row - 1, self.row + 2):
            for j in range(self.col - 1, self.col + 2):
                if board.no_boundary:
                    i, j = board.mod_idx(i, j)
                if self.valid_indices(i, j, board):
                    cur_neighbor = board.mat[i][j]
                    if cur_neighbor.get_life_status() == DEAD:
                        dead_neighbors.append(cur_neighbor)

        # no available cells were found
        if len(dead_neighbors) == 0:
            return

        # create a child cell in the available cell
        import secrets
        child = secrets.choice(dead_neighbors)
        row = child.row
        col = child.col
        board.mat[row][col] = Asex(row, col, self.age, self.lonely, self.reproduction_prob)
        board.mat[row][col].new_status = ALIVE
        # if row> self.row and col> self.col:
        #     print("Child: "+str(row)+", "+str(col))
        #     print("Parent: " + str(self.row) + ", " + str(self.col)+"\n")
        board.mat[row][col].is_preyed = False
        # print("Parent row: "+str(self.row)+" Parent col: "+str(self.col))
        # print("Child row: "+str(row)+" Child col: "+str(col)+"\n")
