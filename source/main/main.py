###################################################################################################

# Cellular Automata SLIR Simulation
# Fall 20202
# School and Mentors: Midwestern State University, Drs. Tina Johnson and Terry Griffin
# Programmer: Corbin Matamoros
# Program Description:
#       This program uses the SLIR model to simulate disease spread at Midwestern State University.
#       See the README.md and report.docx for more detail.

###################################################################################################

from random import randint, choices
from time import time
# from numpy import zeros
from Individual import Individual
from Visualizer import Visualizer
from constants import PARAMS, OUTPUT_FOLDER, NUM_ROWS_FULL, NUM_COLS_FULL, ITERATOR_LIMIT, CONTACT_TYPE, MAKE_GIF

# the 2D simulation grid
# sim_matrices = zeros((NUM_ROWS_FULL, NUM_COLS_FULL), dtype=object)
sim_matrices = [([0] * NUM_COLS_FULL) for row in range(NUM_ROWS_FULL)]

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

    # initialize all grids to be empty lists
    for a in range(NUM_ROWS_FULL):
        for b in range(NUM_COLS_FULL):
            sim_matrices[a][b] = []

    # These following two while loops will only place individuals randomly in the grid so as to leave
    #       a border of empty lists around the grid's outside. E.G.
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
    # disperse all initially infected individuals randomly throughout the grid
    y = PARAMS["init_infected"]
    while y > 0:
        randx = randint(1, NUM_ROWS_FULL-2)
        randy = randint(1, NUM_COLS_FULL-2)
        # create an Individual object with its identifier, age, their age's mortality rate, and state
        age = choices(ages, age_weights)[0]
        age_chance = PARAMS["age_dist_disease"][age]
        sim_matrices[randx][randy].append(Individual(individual_counter, int(age), age_chance, 2, (randx, randy)))
        y -= 1
        individual_counter += 1

    # disperse all susceptible individuals (which is total population minus the initial infectious individuals)
    #       randomly throughout the first grid but only place them in unoccupied locations
    y = PARAMS["population"] - PARAMS["init_infected"]
    while y > 0:
        randx = randint(1, NUM_ROWS_FULL-2)
        randy = randint(1, NUM_COLS_FULL-2)
        # create an Individual object with its identifier, age, their age's mortality rate, and state
        age = choices(ages, age_weights)[0]
        age_chance = PARAMS["age_dist_disease"][age]
        sim_matrices[randx][randy].append(Individual(individual_counter, int(age), age_chance, 0, (randx, randy)))
        y -= 1
        individual_counter += 1

##############################################################################################################
#                                              MAIN SIMULATION BLOCK
##############################################################################################################

    # main simulation block
    # open a 'csv' file for outputting the daily reports, explained later
    with open(OUTPUT_FOLDER+"/CAoutput.csv", 'w') as outfile:
        # used to find how much time it takes to create each day's image
        debug_timer_vis = 0.0
        if MAKE_GIF:
            # instantiate visualizer class to create gif of simulation
            sim_gif = Visualizer()
        # length of simulation in days
        num_days = 0
        # output the csv file headers
        outfile.write("day,susceptible,latent,infectious,recovered\n")
        
        # loop until there are no individuals in the latent nor infectious stages
        while state_list[1] or state_list[2]:
            print("Day", num_days)
            # outputs the beginning-of-day state of the grid to csv output file
            outfile.write(str(num_days)+','+str(state_list[0])+','+str(state_list[1])+','+str(state_list[2])+','+str(state_list[3])+'\n')
            # resets the counters for each state of health category in `state_list`
            state_list = [0, 0, 0, 0]
            # loop through entire grid using these top two nested for loops
            for row in range(1, ITERATOR_LIMIT):
                for col in range(1, ITERATOR_LIMIT):
                    # traverse the list of individuals "sitting" in this particular grid location
                    for individual in sim_matrices[row][col]:
                        # if the individual is not susceptible, there's no need to check their neighbors
                        #       to see how many exposure points they'll be getting. But since the
                        #       method `flag_for_update` requires parameter, just give it zero
                        num_exposure_points = 0
                        # however, if the individual is susceptible, make the call to `check_neighbors`
                        if not individual.state_of_health:
                            num_exposure_points = checkNeighbors((row, col))
                        # analyze the individual's state of health and set for updating if necessary
                        individual.flag_for_update(num_exposure_points)

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
            # comment `debug_print()` out when not in debug mode
            # debug_print()
            if MAKE_GIF:
                # create an image the simulation state and append to a list of images to later
                #       turn into a gif
                debug_start_timer = time()
                sim_gif.visualize(sim_matrices)
                # images.append(visualize(canvas.copy()))
                debug_timer_vis += time() - debug_start_timer
        # output the last day's numbers to csv file
        outfile.write(str(num_days)+','+str(state_list[0])+','+str(state_list[1])+','\
            +str(state_list[2])+','+str(state_list[3])+'\n')
        print("Output dumped to .csv file in `output` folder.")
        if MAKE_GIF:
            print("Preparing the .gif of the simulation.")
            debug_start_timer = time()
            sim_gif.finish_and_save_gif()
            debug_timer_vis += time() - debug_start_timer
            print("The visualizations took", debug_timer_vis)
        print("Simulation finished!")

###################################################################################################
#                                              FUNCTIONS
###################################################################################################

# count how many infectious neighbors an individual has
def checkNeighbors(location):
    num_exposure_points = 0
    # if using the von Neumann method, just check the north, south, east, and west neighbors
    for person in sim_matrices[location[0]][location[1]+1]:
        if person.state_of_health == 2:
            num_exposure_points += (1.0 * person.exposure_points_factor)
    for person in sim_matrices[location[0]-1][location[1]]:
        if person.state_of_health == 2:
            num_exposure_points += (1.0 * person.exposure_points_factor)
    for person in sim_matrices[location[0]][location[1]-1]:
        if person.state_of_health == 2:
            num_exposure_points += (1.0 * person.exposure_points_factor)
    for person in sim_matrices[location[0]+1][location[1]]:
        if person.state_of_health == 2:
            num_exposure_points += (1.0 * person.exposure_points_factor)
    # if using the Moore method, consider the corner neighbors as well as the von Neumann ones
    if not CONTACT_TYPE:
        for person in sim_matrices[location[0]-1][location[1]+1]:
            if person.state_of_health == 2:
                num_exposure_points += (1.0 * person.exposure_points_factor)
        for person in sim_matrices[location[0]-1][location[1]-1]:
            if person.state_of_health == 2:
                num_exposure_points += (1.0 * person.exposure_points_factor)
        for person in sim_matrices[location[0]+1][location[1]-1]:
            if person.state_of_health == 2:
                num_exposure_points += (1.0 * person.exposure_points_factor)
        for person in sim_matrices[location[0]+1][location[1]+1]:
            if person.state_of_health == 2:
                num_exposure_points += (1.0 * person.exposure_points_factor)
    return num_exposure_points

####################################################################################
#                                   DEBUG CODE                                     #
####################################################################################
def debug_print():
    # print the entire grid, including the borders
    for x in range(NUM_COLS_FULL):
        for y in range(NUM_ROWS_FULL):
            print('[', end='')
            for individual in sim_matrices[x][y]:
                print(individual.state_of_health, end=',')
            print(']', end='')
        print('\n')
    print('-------------------------------')


# the `int main()` of the program
if __name__ == "__main__":
    # gonna use this to find the execution time
    debug_timer = time()
    # start the simulation
    main()
    # find the total execution time
    print("Entire simulation took", time() - debug_timer)
