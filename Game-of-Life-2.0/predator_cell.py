from cell import Cell
import random

DEAD = 0
ALIVE = 1


def create_obj(row,col):
    return Predator(row,col)

class Predator(Cell):

    def __init__(self, row, col, age):
        Cell.__init__(self, row, col, age, lonely=False)
        self.type = "PREDATOR"
        self.radius = 2


    def calc_updated_life_stat(self, board):
        self.new_status = self.life_status
        eatable_neighbors = []
        mateable_neigbors = []
        dead_neighbors = []
        if self.get_life_status() == ALIVE:
            # iterate over neighbors
            for i in range(self.row - self.radius, self.row + self.radius+1):
                for j in range(self.col - self.radius, self.col + + self.radius+1):
                    if board.no_boundary:
                        i, j = board.mod_idx(i, j)
                    if self.valid_indices(i, j, board):  # check if indices inside the board and not oneself
                        cur_neighbor = board.mat[i][j]
                        if cur_neighbor.get_life_status() == ALIVE:
                            # find potential mates
                            if cur_neighbor.type == "PREDATOR":
                                mateable_neigbors.append(cur_neighbor)
                            # find potential prey
                            else:
                                eatable_neighbors.append(cur_neighbor)
                        # find location for reproduction
                        else:
                            dead_neighbors.append(cur_neighbor)
            # the predator did not find anything to prey upon
            if len(eatable_neighbors) == 0:
                self.new_status = DEAD
            else:
                # killing the prey
                meal = random.choice(eatable_neighbors)
                meal.new_status = DEAD
                meal.is_preyed = True

                # reproduction with another predator
                if len(dead_neighbors) > 0 and len(mateable_neigbors) > 0:
                    child = random.choice(dead_neighbors)
                    row = child.row
                    col = child.col
                    board.mat[row][col] = Predator(row, col, self.age)
                    board.mat[row][col].new_status = ALIVE
                    # print("Parent row: " + str(self.row) + " Parent col: " + str(self.col))
                    # print("Child row: " + str(row) + " Child col: " + str(col) + "\n")
        return self.new_status
