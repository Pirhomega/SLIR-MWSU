from sys import argv
from constants import GRID_SIZE, RESOURCES_FOLDER
with open(RESOURCES_FOLDER+"terrain.txt", 'w') as output:
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            output.write(argv[2])
        output.write('\n')