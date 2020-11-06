"""
    Module:     constants.py
    Purpose:    To separate the constants used in `main()` from the main code for easier reading.
"""

from json import loads
from sys import argv
import Obstacle

# grab the parameters file from the command line and load into a python dictionary
PARAMS = {}
with open(argv[1], 'r') as f:
    PARAMS = loads(f.read())

# paths to the resources and output folders
RESOURCES_FOLDER = PARAMS["resources"]
OUTPUT_FOLDER = PARAMS["output"]

# a boolean that's true when the user wants to visualize the simulation
MAKE_GIF = PARAMS["simulation"]["visualize"]

# loop through all diseases in the parameters file and store their parameters in the list
DISEASE_LIST = []
# this is how you iterate through the keys of a python dictionary
#   Since each key is an integer starting from zero, we can easily
#   associate a key to an index in a list (e.g. `DISEASE_LIST`)
# Here, we append another dictionary to the `DISEASE_LIST` list, so
#   when we start the simulation, we can iterate through `DISEASE_LIST`
#   when processing each cell.
for _, diseaseNumParam in PARAMS["diseases"].items():
    DISEASE_LIST.append({
        "INIT_INFECTIOUS": diseaseNumParam["init_infected"],
        "AGE_DIST_DISEASE": diseaseNumParam["age_dist_disease"],
        "LATENT_PERIOD_MIN": diseaseNumParam["latent_period_min"],
        "LATENT_PERIOD_MAX": diseaseNumParam["latent_period_max"],
        "INFECTIOUS_PERIOD_MIN": diseaseNumParam["infectious_period_min"],
        "INFECTIOUS_PERIOD_MAX": diseaseNumParam["infectious_period_max"],
        "TRANS_RATE": diseaseNumParam["transmission_rate"],
        "MASK_CHANCE": diseaseNumParam["mask_wearer"],
        "QUARAN_CHANCE": diseaseNumParam["separator"],
        "SYMP_CHANCE": diseaseNumParam["symptomatic"],
        "NEIGHBORHOOD": diseaseNumParam["neighborhood"],
        "IS_SLIS": diseaseNumParam["SLIS"],
        "IMMUNITY_DURATION_MIN": diseaseNumParam["immunity_duration_min"],
        "IMMUNITY_DURATION_MAX": diseaseNumParam["immunity_duration_max"]
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

# instantiate the Obstacle_grid once and let everyone just import it
terrain_grid = Obstacle.Obstacle_Grid()

"""
                         /$$          
                        |__/          
 /$$$$$$/$$$$   /$$$$$$  /$$ /$$$$$$$ 
| $$_  $$_  $$ |____  $$| $$| $$__  $$
| $$ \ $$ \ $$  /$$$$$$$| $$| $$  \ $$
| $$ | $$ | $$ /$$__  $$| $$| $$  | $$
| $$ | $$ | $$|  $$$$$$$| $$| $$  | $$
|__/ |__/ |__/ \_______/|__/|__/  |__/
"""

if __name__ == "__main__":
    # unit tests
    grid = Obstacle.Obstacle_Grid()
    path_list = grid.find_shortest_path((94,75),(3,9))
    grid.mark_path(path_list)
    grid.print_path_to_file(path_list)

# facts:
#       If 6000 people were evenly spaced in MSU's 255 acre land, each person would get 1851.67 sqft
