import json, sys

# grab the parameters file from the command line
PARAMS = {}
with open(sys.argv[1], 'r') as f:
    PARAMS = json.loads(f.read())

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
# constants pertaining to the simulation, such as
#       grid dimensions
NUM_ROWS = PARAMS["num_row"]+2
NUM_COLS = PARAMS["num_col"]+2
GRID_SIZE = PARAMS["num_row"]
# variable that will keep any for-loops using it from traversing the border of a grid
ITERATOR_LIMIT = NUM_ROWS-1
