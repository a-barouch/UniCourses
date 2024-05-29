import cell
import asex_cell
import predator_cell
import random
import tkinter as tk

TYPES = ['SEXUAL', 'ASEXUAL', 'PREDATOR']
DEAD = 0
ALIVE = 1


def flip_coin(life_rate):
    return 1 if random.random() < life_rate else 0


class Board:

    def __init__(self, root, alive_prob, gui, rows=10, cols=10, type_prob_list=(1, 0, 0), move=True, age=True,
                 lonely=False, no_boundary=False, asexual_reproduction = 0.5):
        if type_prob_list is None:
            type_prob_list = [1, 0, 0]
        self.num_rows = rows
        self.num_cols = cols
        self.age = age
        self.lonely = lonely
        self.asexual_repr = asexual_reproduction
        self.mat = [[cell.Cell(i, j, self.age, self.lonely) for j in range(self.num_cols)] for i in
                    range(self.num_rows)]
        self.randomize_cells(alive_prob, type_prob_list)
        self.gui = gui
        self.move = move
        self.no_boundary = no_boundary


        # CODE FOR GUI
        if self.gui:
            self.root = root
            self.canvas = tk.Canvas(bg='blue', width=500, height=500)
            self.canvas.pack()
            self.point_size = 500 / self.num_rows
            self.rects = [[0 for i in range(self.num_cols)] for j in range(self.num_rows)]
            self.init_gui_board()
        # CODE FOR GUI

    # CODE FOR GUI
    def init_gui_board(self):
        x, y = 0, 0
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if self.mat[i][j].get_life_status() == DEAD:
                    self.rects[i][j] = self.canvas.create_rectangle(x, y, x + self.point_size,
                                                                    y + self.point_size,
                                                                    fill="white")
                else:
                    if self.mat[i][j].type == "SEXUAL":
                        self.rects[i][j] = self.canvas.create_rectangle(x, y, x + self.point_size,
                                                                        y + self.point_size,
                                                                        fill="black")
                    elif self.mat[i][j].type == "ASEXUAL":
                        self.rects[i][j] = self.canvas.create_rectangle(x, y, x + self.point_size,
                                                                        y + self.point_size,
                                                                        fill="blue")
                    elif self.mat[i][j].type == "PREDATOR":
                        self.rects[i][j] = self.canvas.create_rectangle(x, y, x + self.point_size,
                                                                        y + self.point_size,
                                                                        fill="red")
                x += self.point_size
            x = 0
            y += self.point_size
        self.root.update_idletasks()
        self.root.update()

    # CODE FOR GUI

    def update_board(self):
        # CODE FOR GUI
        if self.gui:
            self.root.update_idletasks()
            self.root.update()
        # CODE FOR GUI

        # calculate new cells life based on last board configuration
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.mat[i][j].calc_updated_life_stat(self)
        if self.move: self.apply_movement()
        # update all cells life status after full iteration over board
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.mat[i][j].set_life_status(use_calculated_status=True, board=self)

                # CODE FOR GUI
                if self.gui:
                    if self.mat[i][j].get_life_status() == DEAD:
                        self.canvas.itemconfigure(self.rects[i][j], fill="white")
                    else:
                        if self.mat[i][j].type == "SEXUAL":
                            self.canvas.itemconfigure(self.rects[i][j], fill="black")
                        elif self.mat[i][j].type == "ASEXUAL":
                            self.canvas.itemconfigure(self.rects[i][j], fill="blue")
                        elif self.mat[i][j].type == "PREDATOR":
                            self.canvas.itemconfigure(self.rects[i][j], fill="red")
                        elif self.mat[i][j].moved:
                            self.canvas.itemconfigure(self.rects[i][j], fill="yellow")
                # CODE FOR GUI

    def apply_movement(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                new_location = self.mat[i][j].move(self)
                if new_location is not None:
                    new_location.new_status = self.mat[i][j].new_status
                    if self.mat[i][j].type == "SEXUAL":
                        new_obj = cell.Cell(new_location.row, new_location.col, self.age, self.lonely)
                    elif self.mat[i][j].type == "ASEXUAL":
                        new_obj = asex_cell.Asex(new_location.row, new_location.col, self.age, self.lonely, self.asexual_repr)
                    elif self.mat[i][j].type == "PREDATOR":
                        new_obj = predator_cell.Predator(new_location.row, new_location.col, self.age)
                    self.mat[new_location.row][new_location.col] = new_obj
                    new_obj.new_status = ALIVE
                    self.mat[self.mat[i][j].row][self.mat[i][j].col] = cell.Cell(self.mat[i][j].row, self.mat[i][j].col,
                                                                                 self.age, self.lonely)

    # create cells of different types and life status by given probabilities
    def randomize_cells(self, life_rate, type_prob_list):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                cell_type = random.choices(TYPES, weights=type_prob_list)[0]
                if cell_type == 'SEXUAL':
                    self.mat[i][j] = cell.Cell(i, j, self.age, self.lonely)
                elif cell_type == 'ASEXUAL':
                    self.mat[i][j] = asex_cell.Asex(i, j, self.age, self.lonely, self.asexual_repr)
                elif cell_type == 'PREDATOR':
                    self.mat[i][j] = predator_cell.Predator(i, j, self.age)
                status = flip_coin(life_rate)
                self.mat[i][j].set_life_status(use_calculated_status=False, status_to_set=status)

    def mod_idx(self, i, j):
        return i % self.num_rows, j % self.num_cols

    def get_statistics(self):
        alive = 0
        dead = 0
        sexual = 0
        asexual = 0
        predator = 0
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                cur = self.mat[i][j].get_life_status()
                alive += cur
                dead += (1 - cur)
                if self.mat[i][j].get_life_status() and self.mat[i][j].type == "SEXUAL":
                    sexual += 1
                elif self.mat[i][j].get_life_status() and self.mat[i][j].type == "ASEXUAL":
                    asexual += 1
                elif self.mat[i][j].get_life_status() and self.mat[i][j].type == "PREDATOR":
                    predator += 1

        print("Sexual count: " + str(sexual))
        print("Asexual count: " + str(asexual))
        print("Predator count: " + str(predator))
        print("Alive count: " + str(alive))
        print("Dead count: " + str(dead) + "\n")
        return sexual, asexual, predator
