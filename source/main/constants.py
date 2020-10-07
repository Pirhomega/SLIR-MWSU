"""
    Module:     constants.py
    Purpose:    To separate the constants used in `main()` from the main code for easier reading.
"""

from json import loads
from sys import argv
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# grab the parameters file from the command line
PARAMS = {}
with open(argv[1], 'r') as f:
    PARAMS = loads(f.read())

RESOURCES_FOLDER = PARAMS["resources"]
OUTPUT_FOLDER = PARAMS["output"]

# disease parameters
LATENT_PERIOD_MIN = PARAMS["latent_period_min"]
LATENT_PERIOD_MAX = PARAMS["latent_period_max"]
INFECTIOUS_PERIOD_MIN = PARAMS["infectious_period_min"]
INFECTIOUS_PERIOD_MAX = PARAMS["infectious_period_max"]
MAX_EXPOSURE = PARAMS["max_exposure"]
MASK_CHANCE = PARAMS["mask_wearer"]
QUARAN_CHANCE = PARAMS["separator"]
SYMP_CHANCE = PARAMS["symptomatic"]
CONTACT_TYPE = PARAMS["vonNeumann"]
MAKE_GIF = PARAMS["visualize"]
IS_SLIS = PARAMS["SLIS"]
SIM_MAX = PARAMS["sim_max"]
AGE_DIST_DISEASE = PARAMS["age_dist_disease"]
IMMUNITY_DURATION_MIN = PARAMS["immunity_duration_min"]
IMMUNITY_DURATION_MAX = PARAMS["immunity_duration_max"]

# constants pertaining to the simulation, such as
#       grid dimensions
NUM_ROWS_FULL = PARAMS["num_row"]+2
NUM_COLS_FULL = PARAMS["num_col"]+2
GRID_SIZE = PARAMS["num_row"]

# locations in simulation grid where individuals will travel to and from
PATCHES = PARAMS["patches"]
# the number of patches in the simulation
NUM_PATCHES = len(PATCHES)

# variable that will keep any for-loops using it from traversing the border of a grid
ITERATOR_LIMIT = NUM_ROWS_FULL-1

# facts:
#       If 6000 people were evenly spaced in MSU's 255 acre land, each person would get 1851.67 sqft

# the terrain grid class that we'll use for Individual's pathfinding
class Obstacle_grid():
    def __init__(self):
        # in the end, `self.terrain_grid` will be a 2D array of values where zeros are obstacles
        #       and all values greater than zero are edge weights for all edges connected to that node
        self.terrain_grid = []
        with open(RESOURCES_FOLDER+"terrain.txt") as input:
            rows = input.readlines()
            for row in rows:
                terrain_grid_row = []
                for col in row:
                    if col.isdigit():
                        terrain_grid_row.append(int(col))
                self.terrain_grid.append(terrain_grid_row)
        self.grid = Grid(matrix=self.terrain_grid)
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    def find_shortest_path(self, location, destination):
        self.grid.cleanup()
        self.start = self.grid.node(location[1],location[0])
        self.end = self.grid.node(destination[1],destination[0])
        path_list, _ = self.finder.find_path(self.start, self.end, self.grid)
        return path_list
    def mark_path(self, path_list):
        for location in path_list:
            self.terrain_grid[location[0]][location[1]] = 5
    def print_path_to_file(self, path_list):
        print(self.grid.grid_str(path=path_list, start=self.start, end=self.end))

# instantiate the Obstacle_grid once and let everyone just import it
terrain_grid = Obstacle_grid()

if __name__ == "__main__":
    grid = Obstacle_grid()
    path_list = grid.find_shortest_path((94,75),(3,9))
    grid.mark_path(path_list)
    grid.print_path_to_file(path_list)
