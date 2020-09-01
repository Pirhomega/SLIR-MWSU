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
from Individual import Individual
from constants import PARAMS, NUM_ROWS, NUM_COLS, GRID_SIZE, ITERATOR_LIMIT, CONTACT_TYPE

# Create the two grids for the simulation
# Each index represents a location an individual can occupy
# The first 2D array / grid represents the current state of the simulation
# The second grid will represent the state of the disease spread based on the first grid
# Each element in the grid represents a location in the world as a tuple with the following schema:
    # (a, b, c, d, e) = (location state, days latent, days infectious, time exposed, individual id)
        # 'a' can be 1 (occupied by susceptible individual), 2 (occupied by latent individual), 
        #       3 (occupied by infectious individual), 4 (occupied by recovered individual).
        #       If an element is just a zero, the location is unoccupied
        # 'b' is an integer between 0 and the latent period, inclusive
        # 'c' is an integer between 0 and the infectious period, inclusive
        # 'd' is a float value that represents the time someone maintained close contact with an infectious individual
        # 'e' is a number given to an individual to identify them in the end-of-day report
        # if an element is (0,0,0,0,0), the location is unoccupied
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

    # if the population value is too large to fit in the simulation grid, warn the user and end program
    if PARAMS["population"] > GRID_SIZE*GRID_SIZE:
        print("The population -", PARAMS["population"], "- is too great to fit within the grid borders.\nPlease select a population less than or equal to", GRID_SIZE*GRID_SIZE)
    else:
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
        with open("CAoutput.csv", 'w') as outfile:
            # output the csv file headers
            outfile.write("day,susceptible,latent,infectious,recovered\n")
            # length of simulation in days
            num_days = 0
            # loop until there are no individuals in the latent nor infectious stages
            while state_list[1] or state_list[2]:
                # print("Day:", num_days)
                # print(state_list)
                # outputs the beginning-of-day state of the grid to csv output file
                outfile.write(str(num_days)+','+str(state_list[0])+','+str(state_list[1])+','+str(state_list[2])+','+str(state_list[3])+'\n')
                # resets the counters for each state of health category in `state_list`
                state_list = [0, 0, 0, 0]
                # loop through entire grid using these top two nested for loops
                temp = 0
                for row in range(1, ITERATOR_LIMIT):
                    for col in range(1, ITERATOR_LIMIT):
                        # print('[',end='')
                        # traverse the list of individuals "sitting" in this particular grid location
                        for individual in sim_matrices[row][col]:
                            # print(individual.id, individual.state_of_health, end=',')
                            temp += 1
                            # analyze the individual's state of health and set for updating if necessary
                            individual.flag_for_update(checkNeighbors((row, col)))
                #         print(']',end='')
                #     print('\n')
                # print('\n')
                print("This should be 5", temp)
                # loop through entire grid again and update all individuals' object variables
                for row in range(1, ITERATOR_LIMIT):
                    for col in range(1, ITERATOR_LIMIT):
                        # print(len(sim_matrices[row][col]),end='')
                        # `individual_count` is the number of individuals in the current spot in the simulation grid.
                        #       I tried using the `for individual in sim_matrices[row][col]`, but when I think when I
                        #       try to remove an individual from the list to move them to their next location in the sim grid,
                        #       the loop doesn't evaluate any other individual's in the list because it thinks it has already
                        #       reached the end of it. Like, when there's two individuals in the list, I update the first one's object variables,
                        #       move it to its next location, leaving the second one waiting to be looped over. The for loop only sees one
                        #       element left, so it thinks it has already evaluated it. Get the point? No? Oh well.
                        individual_count = len(sim_matrices[row][col])
                        print(individual_count)
                        x = 0
                        while x < len(sim_matrices[row][col]):
                        # for x in range(0, individual_count):
                            # list_len += 1
                            # if not individual.updated:
                            print("this is x:", x)
                            print("this is length of list:", len(sim_matrices[row][col]))
                            results = sim_matrices[row][col][x].apply_changes((row, col))
                            # print("This individual is:", results)
                            # update the object variables of the individual and add them to the state_list tally if they haven't already
                            if results != -1:
                                # print(individual)
                                # print(results)
                                state_list[results] += 1
                            # only copy to and remove an individual if they didn't move to a different location in the grid
                            if sim_matrices[row][col][x].location != (row, col):
                                # append them to the list in their new location
                                sim_matrices[sim_matrices[row][col][x].location[0]][sim_matrices[row][col][x].location[1]].append(sim_matrices[row][col][x])
                                # remove them from the list in their old location
                                sim_matrices[row][col].remove(sim_matrices[row][col][x])
                                x -= 1
                            x += 1
                                # individual_count -= 1
                        # print(list_len, end='')
                #         print(' ', end='')
                #     print('\n')
                # print('\n')
                print("-----------------")
                num_days += 1
            # output the last day's numbers to csv file
            outfile.write(str(num_days)+','+str(state_list[0])+','+str(state_list[1])+','+str(state_list[2])+','+str(state_list[3])+'\n')

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

# the `int main()` of the program
if __name__ == "__main__":
    main()
