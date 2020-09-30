"""
    Module:     constants.py
    Purpose:    To separate the constants used in `main()` from the main code for easier reading.
"""

from json import loads
from sys import argv

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
