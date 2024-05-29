import board
import tkinter as tk
import time
import matplotlib.pyplot as plt

if __name__ == '__main__':
    STATISTIC_MODE = False
    THRESHOLD_MODE = False
    # GAME PARAMETERS:
    root = None
    ALIVE_PROB = 0.25
    IS_GUI = True
    ROWS = 50
    COLUMNS = 50
    TYPE_PROB_LIST = (0, 50, 0)
    ASEXUAL_REPR=0.22
    MOVE = True  # default False
    AGE = True  # default False
    LONELY = False  # default True
    NO_BOUNDARY = True  # default false

    if STATISTIC_MODE:
        IS_GUI = False
        NUM_ITERATIONS = 100
        NUM_PLAYS = 100
        sexual_wins, asexual_wins, extinction = 0, 0, 0
        for i in range(NUM_PLAYS):
            my_board = board.Board(root=root, alive_prob=ALIVE_PROB, gui=IS_GUI, rows=ROWS, cols=COLUMNS,
                                   type_prob_list=TYPE_PROB_LIST,
                                   move=MOVE, age=AGE, lonely=LONELY, no_boundary=NO_BOUNDARY, asexual_reproduction = ASEXUAL_REPR)
            for j in range(NUM_ITERATIONS):
                my_board.update_board()
            sexual, asexual, predator = my_board.get_statistics()
            if sexual > asexual:
                sexual_wins += 1
            elif asexual > sexual:
                asexual_wins += 1
            elif asexual == sexual == 0:
                extinction += 1

        print("Total Sexual Wins: " + str(sexual_wins))
        print("Total Asexual Wins: " + str(asexual_wins))
        print("Extinctions: " + str(extinction))

    elif THRESHOLD_MODE:
        IS_GUI = False
        NUM_ITERATIONS = 300
        NUM_PLAYS = 10
        threshold_min = 0.1
        threshold_max = 0.4
        import numpy as np
        thresholds = list(np.arange(threshold_min, threshold_max, 0.01))
        wins_in_thresh = []
        for thresh in thresholds:
            sexual_wins, asexual_wins, extinction = 0, 0, 0
            for play in range(NUM_PLAYS):
                my_board = board.Board(root=root, alive_prob=ALIVE_PROB, gui=IS_GUI, rows=ROWS, cols=COLUMNS,
                                       type_prob_list=TYPE_PROB_LIST,
                                       move=MOVE, age=AGE, lonely=LONELY, no_boundary=NO_BOUNDARY, asexual_reproduction = thresh)
                for j in range(NUM_ITERATIONS):
                    my_board.update_board()
                sexual, asexual, predator = my_board.get_statistics()
                if sexual > asexual:
                    sexual_wins += 1
                elif asexual > sexual:
                    asexual_wins += 1
            wins_in_thresh.append(asexual_wins)
        plt.scatter(x=thresholds, y=wins_in_thresh, color='black')
        plt.xlabel("asexual reproduction rate")
        plt.ylabel("asexual wins (10 games)")
        plt.title("Added Predators, Added Movement")
        plt.legend()
        plt.show()



    else:
        if IS_GUI:  # show board on screen
            root = tk.Tk()
        my_board = board.Board(root=root, alive_prob=ALIVE_PROB, gui=IS_GUI, rows=ROWS, cols=COLUMNS,
                               type_prob_list=TYPE_PROB_LIST,
                               move=MOVE, age=AGE, lonely=LONELY, no_boundary=NO_BOUNDARY, asexual_reproduction = ASEXUAL_REPR)
        i = 0
        sexual_list, asexual_list, predator_list = [], [], []
        while True:
            # if i % 10 == 0:
            print("Iteration " + str(i))
            sexual, asexual, predator = my_board.get_statistics()
            sexual_list.append(sexual)
            asexual_list.append(asexual)
            predator_list.append(predator)
            # time.sleep(0.5)
            my_board.update_board()
            i += 1
            if i % 100 == 0:
                plt.plot(list(range(len(sexual_list))), sexual_list, color='black', label='sexual')
                plt.plot(list(range(len(sexual_list))), asexual_list, color='blue', label='asexual')
                plt.plot(list(range(len(sexual_list))), predator_list, color='red', label='predator')
                plt.xlabel("iteration")
                plt.ylabel("count")
                plt.title("Run: Added Predators, Reproduction rate: "+str(ASEXUAL_REPR))
                # plt.legend()
                plt.show()

        my_board.root.mainloop()

    # for row in self.mat:
    #     for col in row:
    #         print("{:8.0f}".format(col.life_status), end=" ")
    #     print("")
    # self.mat[1][0].set_life_status(1, False)
    # self.mat[1][1].set_life_status(1, False)
    # self.mat[1][2].set_life_status(1, False)
