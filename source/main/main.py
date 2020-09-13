# Cellular Automata Program 1
# Computational Epidemiology - Summer II 2020
# Dr. Johnson
# Programmer: Corbin Matamoros
# Program Description:
#       This program will use a cellular automaton to simulate disease spread in a closed population using the SLIR model.
#       Each day, a report will be generated and sent to an output file. The report will contain the locations of the
#       individuals at the end of each day, as well as the number of infectious, latent, and recovered individuals.

import random
import numpy as np
from math import ceil, sqrt
from PIL import Image
from Individual import Individual
from constants import PARAMS, NUM_ROWS, NUM_COLS, GRID_SIZE, ITERATOR_LIMIT, CONTACT_TYPE

sim_matrices = np.zeros((NUM_ROWS, NUM_COLS), dtype=object)

# the `if __name__ == "__main__":` at the very bottom of this script calls this function
def main():
    # list to track the number of individuals in the susceptible, latent, infectious, and recovered stages
    # The uncommented `state_list` declaration is a less abstract version of the following instructions:
    #       num_susceptible = PARAMS["population"] - PARAMS["init_infected"]
    #       num_infectious = PARAMS["init_infected"]
    #       num_latent = 0
    #       num_recovered = 0
    #       state_list = [number_of_susceptible, number_of_latent, number_of_infectious, number_of_recovered]
    state_list = [PARAMS["population"] - PARAMS["init_infected"], 0, PARAMS["init_infected"], 0]

    # used to give each individual in the population a unique ID
    individual_counter = 1

    # # if the population value is too large to fit in the simulation grid, warn the user and end program
    # if PARAMS["population"] > GRID_SIZE*GRID_SIZE:
    #     print("The population -", PARAMS["population"], "- is too great to fit within the grid borders.\nPlease select a population less than or equal to", GRID_SIZE*GRID_SIZE)
    # else:
    # initialize all grids to be empty lists
    for a in range(NUM_ROWS):
        for b in range(NUM_COLS):
            sim_matrices[a][b] = []

    # These following two while loops will only place individuals randomly in the first grid so as to leave
    #       a border of zeros around the grid's outside. E.G.
    #       GRID A ->   |0 0 0 0 0| (the 'X' spots are usable; the '0' spots aren't)
    #                   |0 X X X 0|
    #                   |0 X X X 0|
    #                   |0 X X X 0|
    #                   |0 0 0 0 0|

    # create two lists of the population's possible ages and their distribution
    ages = []
    age_weights = []
    for key in PARAMS["age_dist"]:
        ages.append(key)
        age_weights.append(PARAMS["age_dist"][key])
    # disperse all initially infected individuals randomly throughout the first grid,
    #       but only place them in unoccupied locations
    y = PARAMS["init_infected"]
    while y > 0:
        randx = random.randint(1, NUM_ROWS-2)
        randy = random.randint(1, NUM_COLS-2)
        # create an Individual object with its identifier, age, their age's mortality rate, and state
        age = random.choices(ages, age_weights)[0]
        age_chance = PARAMS["age_dist_disease"][age]
        sim_matrices[randx][randy].append(Individual(individual_counter, int(age), age_chance, 2, (randx, randy)))
        y -= 1
        individual_counter += 1

    # disperse all susceptible individuals (which is total population minus the initial infectious individuals)
    #       randomly throughout the first grid but only place them in unoccupied locations
    y = PARAMS["population"] - PARAMS["init_infected"]
    while y > 0:
        randx = random.randint(1, NUM_ROWS-2)
        randy = random.randint(1, NUM_COLS-2)
        # create an Individual object with its identifier, age, their age's mortality rate, and state
        age = random.choices(ages,age_weights)[0]
        age_chance = PARAMS["age_dist_disease"][age]
        sim_matrices[randx][randy].append(Individual(individual_counter, int(age), age_chance, 0, (randx, randy)))
        y -= 1
        individual_counter += 1

##############################################################################################################
#                                              MAIN SIMULATION BLOCK
##############################################################################################################

    # main simulation block
    # open a 'csv' file for outputting the daily reports, explained later
    with open("../output/CAoutput.csv", 'w') as outfile:
        # length of simulation in days
        num_days = 0
        print(num_days)
        # output the csv file headers
        outfile.write("day,susceptible,latent,infectious,recovered\n")
        # loop until there are no individuals in the latent nor infectious stages
        while state_list[1] or state_list[2]:
            # outputs the beginning-of-day state of the grid to csv output file
            outfile.write(str(num_days)+','+str(state_list[0])+','+str(state_list[1])+','+str(state_list[2])+','+str(state_list[3])+'\n')
            # resets the counters for each state of health category in `state_list`
            state_list = [0, 0, 0, 0]
            # loop through entire grid using these top two nested for loops
            temp = 0
            for row in range(1, ITERATOR_LIMIT):
                for col in range(1, ITERATOR_LIMIT):
                    # traverse the list of individuals "sitting" in this particular grid location
                    for individual in sim_matrices[row][col]:
                        temp += 1
                        # analyze the individual's state of health and set for updating if necessary
                        individual.flag_for_update(checkNeighbors((row, col)))
            # loop through entire grid again and update all individuals' object variables
            for row in range(1, ITERATOR_LIMIT):
                for col in range(1, ITERATOR_LIMIT):
                    # `individual_count` is the number of individuals in the current spot in the simulation grid.
                    #       I tried using the `for individual in sim_matrices[row][col]`, but when I think when I
                    #       try to remove an individual from the list to move them to their next location in the sim grid,
                    #       the loop doesn't evaluate any other individual's in the list because it thinks it has already
                    #       reached the end of it. Like, when there's two individuals in the list, I update the first one's object variables,
                    #       move it to its next location, leaving the second one waiting to be looped over. The for loop only sees one
                    #       element left, so it thinks it has already evaluated it. Get the point? No? Oh well.
                    x = 0
                    while x < len(sim_matrices[row][col]):
                        results = sim_matrices[row][col][x].apply_changes((row, col))
                        # update the object variables of the individual and add them to the state_list tally if they haven't already
                        if results != -1:
                            state_list[results] += 1
                        # only copy to and remove an individual if they didn't move to a different location in the grid
                        if sim_matrices[row][col][x].location != (row, col):
                            # append them to the list in their new location
                            sim_matrices[sim_matrices[row][col][x].location[0]][sim_matrices[row][col][x].location[1]].append(sim_matrices[row][col][x])
                            # remove them from the list in their old location
                            sim_matrices[row][col].remove(sim_matrices[row][col][x])
                            x -= 1
                        x += 1
            num_days += 1
            ##################################################
            # print the entire grid, including the borders
            for x in range(6):
                for y in range(6):
                    print('[',end='')
                    for individual in sim_matrices[x][y]:
                        print(individual.state_of_health,end=',')
                    print(']',end='')
                print('\n')
            print('-------------------------------')
            ##################################################
        visualize()
        # output the last day's numbers to csv file
        outfile.write(str(num_days)+','+str(state_list[0])+','+str(state_list[1])+','+str(state_list[2])+','+str(state_list[3])+'\n')
        # each cell could be composed of an `NxN` grid to display all individuals in the spot. We will calculate the dimensions of the grid by
        # taking the square root of the number of individuals in the spot and taking the ceiling of the result. That value will be N.

##############################################################################################################
#                                              FUNCTIONS
##############################################################################################################

# count how many infectious neighbors an individual has
def checkNeighbors(location):
    count = 0
    # if using the von Neumann method, just check the north, south, east, and west neighbors
    for person in sim_matrices[location[0]][location[1]+1]:
        if person.state_of_health == 2:
            count += 1
    for person in sim_matrices[location[0]-1][location[1]]:
        if person.state_of_health == 2:
            count += 1
    for person in sim_matrices[location[0]][location[1]-1]:
        if person.state_of_health == 2:
            count += 1
    for person in sim_matrices[location[0]+1][location[1]]:
        if person.state_of_health == 2:
            count += 1
    # if using the Moore method, consider the corner neighbors
    if not CONTACT_TYPE:
        for person in sim_matrices[location[0]-1][location[1]+1]:
            if person.state_of_health == 2:
                count += 1
        for person in sim_matrices[location[0]-1][location[1]-1]:
            if person.state_of_health == 2:
                count += 1
        for person in sim_matrices[location[0]+1][location[1]-1]:
            if person.state_of_health == 2:
                count += 1
        for person in sim_matrices[location[0]+1][location[1]+1]:
            if person.state_of_health == 2:
                count += 1
    return count

def visualize():
    # open the background image to which we will paste the individuals' tiles
    canvas = Image.open("../../resources/bkgd.png")
    default_tile_size = ceil(1000/GRID_SIZE)
    for row in range(1, ITERATOR_LIMIT):
        for col in range(1, ITERATOR_LIMIT):
            print("[",end='')
            N = ceil(sqrt(max(1,len(sim_matrices[row][col]))))
            mini_tile_size = int(default_tile_size / N)
            mini_row = 0
            mini_col = 0
            for individual in sim_matrices[row][col]:
                print(individual.state_of_health,end=',')
                tile = Image.open("../../resources/"+str(individual.state_of_health)+".png")
                temp = tile.resize((mini_tile_size,mini_tile_size))
                if mini_row == N:
                    mini_row += 1
                    mini_col = 0
                canvas.paste(temp, box=((row-1)*default_tile_size + (mini_tile_size*mini_row), (col-1)*default_tile_size + (mini_tile_size*mini_col)))
                mini_col += 1
            print(']',end='')
        print('\n')
    print('----------------------')
    canvas.save("testbooger.png",quality=95)


# the `int main()` of the program
if __name__ == "__main__":
    main()
