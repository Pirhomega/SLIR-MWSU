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

# loop through all diseases in the parameters file and store their parameters in the list
DISEASE_LIST = []
for disease_num in PARAMS["diseases"]:
    DISEASE_LIST.append({
        "INIT_INFECTIOUS": PARAMS[disease_num]["init_infected"],
        "AGE_DIST_DISEASE": PARAMS[disease_num]["age_dist_disease"],
        "LATENT_PERIOD_MIN": PARAMS[disease_num]["latent_period_min"],
        "LATENT_PERIOD_MAX": PARAMS[disease_num]["latent_period_max"],
        "INFECTIOUS_PERIOD_MIN": PARAMS[disease_num]["infectious_period_min"],
        "INFECTIOUS_PERIOD_MAX": PARAMS[disease_num]["infectious_period_max"],
        "TRANS_RATE": PARAMS[disease_num]["max_exposure"],
        "MASK_CHANCE": PARAMS[disease_num]["mask_wearer"],
        "QUARAN_CHANCE": PARAMS[disease_num]["separator"],
        "SYMP_CHANCE": PARAMS[disease_num]["symptomatic"],
        "CONTACT_TYPE": PARAMS[disease_num]["neighborhood"],
        "IS_SLIS": PARAMS["SLIS"],
        "IMMUNITY_DURATION_MIN": PARAMS["immunity_duration_min"],
        "IMMUNITY_DURATION_MAX": PARAMS["immunity_duration_max"]
    })

# the size of the simulation grid with a one-cell border added to all four sides
NUM_ROWS_FULL = PARAMS["simulation"]["num_row"]+2
NUM_COLS_FULL = PARAMS["simulation"]["num_col"]+2
# the size of the simulation grid without the one-cell border
GRID_SIZE = PARAMS["simulation"]["num_row"]
# variable that will keep any for-loops using it from traversing through the one-cell 
#       border of the simulation grid, i.e. it will prevent crashes caused by references
#       out of list bounds
ITERATOR_LIMIT = GRID_SIZE+1

# number of individuals in the simulation
POPULATION = PARAMS["simulation"]["population"]

# age distribution of the population
AGE_DIST = PARAMS["simulation"]["age_dist"]

# the maximum number of days the simulation will run
SIM_MAX = PARAMS["simulation"]["sim_max"]

# locations in simulation grid where individuals will travel to and from
PATCHES = PARAMS["simulation"]["patches"]
# the number of patches in the simulation
NUM_PATCHES = len(PATCHES)

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
            # loop through entire terrain file and convert all chars to integers
            for row in rows:
                terrain_grid_row = []
                for col in row:
                    if col.isdigit():
                        terrain_grid_row.append(int(col))
                self.terrain_grid.append(terrain_grid_row)
        # instantiate the Grid object using the newly converted terrain_grid
        #       The pathfinding library requires this special object to work
        self.grid = Grid(matrix=self.terrain_grid)
        # define the A* pathfinding algorithm as the one we use. Another option is Dijkstra's
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    def find_shortest_path(self, location, destination):
        """
        Purpose:    create a list of spots in a 2D grid that define the shortest path
                    between two spots
        Input:      Starting location (`location`) and Ending location (`destination`)
        Output:     A list of spots/locations in the 2D grid
        """
        self.grid.cleanup()
        self.start = self.grid.node(location[1],location[0])
        self.end = self.grid.node(destination[1],destination[0])
        path_list, _ = self.finder.find_path(self.start, self.end, self.grid)
        return path_list
    def print_path_to_file(self, path_list):
        """
        Purpose:    Test function that prints the terrain with the shortest path between two nodes
                        to the console
        Input:      List of spots in terrain grid that define the shortest path between
                        two nodes.
        Output:     None
        """
        print(self.grid.grid_str(path=path_list, start=self.start, end=self.end))

# instantiate the Obstacle_grid once and let everyone just import it
terrain_grid = Obstacle_grid()

if __name__ == "__main__":
    # unit tests
    grid = Obstacle_grid()
    path_list = grid.find_shortest_path((94,75),(3,9))
    grid.mark_path(path_list)
    grid.print_path_to_file(path_list)
