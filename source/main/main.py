#!~/miniconda/python.exe
###################################################################################################

# Cellular Automata SLIR Simulation
# Fall 20202
# School and Mentors: Midwestern State University, Drs. Tina Johnson and Terry Griffin
# Programmer: Corbin Matamoros
# Program Description:
#       This program uses the SLIR and SLIS model to simulate disease spread at Midwestern State University.
#       See the README.md and report.docx for more detail.

###################################################################################################

from random import randint, choices, seed
from time import time
# from numpy import zeros
from Individual import Individual
from Visualizer import Visualizer
from constants import PARAMS, SIM_MAX, OUTPUT_FOLDER, NUM_ROWS_FULL, NUM_COLS_FULL, ITERATOR_LIMIT, CONTACT_TYPE, MAKE_GIF

# the 2D simulation grid
sim_grid = [([0] * NUM_COLS_FULL) for row in range(NUM_ROWS_FULL)]

# the 2D simulation grid's sister grid, the one that holds the exposure points for each cell
expo_points_grid = [([0] * NUM_COLS_FULL) for row in range(NUM_ROWS_FULL)]

# the `if __name__ == "__main__":` at the very bottom of this script calls this function
def main():
    # sets the random generator seed
    seed(a=None, version=2)
    # list to track the number of individuals in the susceptible, latent, infectious, and recovered stages
    # The uncommented `state_list` declaration is a less abstract version of the following instructions:
    #       num_susceptible = PARAMS["population"] - PARAMS["init_infected"]
    #       num_infectious = PARAMS["init_infected"]
    #       num_latent = 0
    #       num_recovered = 0
    #       state_list = [number_of_susceptible, number_of_latent, number_of_infectious, number_of_recovered]
    state_list = [PARAMS["population"] - PARAMS["init_infected"], 0, PARAMS["init_infected"], 0]

    # initialize all grids to be empty lists
    for a in range(NUM_ROWS_FULL):
        for b in range(NUM_COLS_FULL):
            sim_grid[a][b] = []

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

    # instantiate the initially infectious individuals and get them placed in the grid
    num_init_infected = PARAMS["init_infected"]
    # used to give each individual in the population a unique ID
    individual_counter = 1
    while num_init_infected > 0:
        # create an Individual object with its identifier, their state of health state, the list of possible ages,
        #       the age distributions, and the ratio of deaths for each age
        infected_person = Individual(individual_counter, 2, ages, age_weights)
        sim_grid[infected_person.location[0]][infected_person.location[1]].append(infected_person)
        num_init_infected -= 1
        individual_counter += 1

    # instantiate the rest of the population (the susceptible individuals) and get them placed in the grid
    y = PARAMS["population"] - PARAMS["init_infected"]
    while y > 0:
        susceptible_person = Individual(individual_counter, 2, ages, age_weights)
        sim_grid[susceptible_person.location[0]][susceptible_person.location[1]].append(susceptible_person)
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
        # instantiate visualizer class to create gif of simulation if the user wants
        if MAKE_GIF:
            sim_gif = Visualizer()
        # length of simulation in days
        num_days = 0
        # output the csv file headers
        outfile.write("day,susceptible,latent,infectious,recovered\n")
        
        # loop at least 200 days and until there are no individuals in the latent nor infectious stages
        while num_days < SIM_MAX and (state_list[1] or state_list[2]):
            print("Processing day", num_days, end='\r', flush=True)
            # outputs the beginning-of-day state of the grid to csv output file
            outfile.write(str(num_days)+','+str(state_list[0])+','+str(state_list[1])+','+str(state_list[2])+','+str(state_list[3])+'\n')
            # resets the counters for each state of health category in `state_list`
            state_list = [0, 0, 0, 0]
            # Calculate each `sim_grid` cell's exposure point total and store in `expo_points_grid`
            calculate_expo_total()
            # loop through entire grid using these top two nested for loops
            for row in range(1, ITERATOR_LIMIT):
                for col in range(1, ITERATOR_LIMIT):
                    # traverse the list of individuals "sitting" in this particular grid location
                    for individual in sim_grid[row][col]:
                        # if the individual is not susceptible, there's no need to check their neighbors
                        #       to see how many exposure points they'll be getting. But since the
                        #       method `flag_for_update` requires a parameter, just give it zero
                        num_exposure_points = 0.0
                        # however, if the individual is susceptible (their state of health is '0', 
                        #       hence the 'not' in the if statement), make the call to `check_neighbors`
                        if not individual.state_of_health:
                            num_exposure_points = checkNeighbors((row, col))
                        # analyze the individual's state of health and set for updating if necessary
                        individual.flag_for_update(num_exposure_points)

            # loop through entire grid again and update all individuals' object variables
            for row in range(1, ITERATOR_LIMIT):
                for col in range(1, ITERATOR_LIMIT):
                    # `individual_count` is the number of individuals in the current spot in the simulation grid.
                    #       I tried using the `for individual in sim_grid[row][col]`, but when I think when I
                    #       try to remove an individual from the list to move them to their next location in the sim grid,
                    #       the loop doesn't evaluate any other individual's in the list because it thinks it has already
                    #       reached the end of it. Like, when there's two individuals in the list, I update the first one's object variables,
                    #       move it to its next location, leaving the second one waiting to be looped over. The for loop only sees one
                    #       element left, so it thinks it has already evaluated it. Get the point? No? Oh well.
                    x = 0
                    while x < len(sim_grid[row][col]):
                        results = sim_grid[row][col][x].apply_changes((row, col))
                        # update the object variables of the individual and add them to the state_list tally if they haven't already
                        if results != -1:
                            state_list[results] += 1
                        # only copy to and remove an individual if they didn't move to a different location in the grid
                        if sim_grid[row][col][x].location != (row, col):
                            # append them to the list in their new location
                            sim_grid[sim_grid[row][col][x].location[0]][sim_grid[row][col][x].location[1]].append(sim_grid[row][col][x])
                            # remove them from the list in their old location
                            sim_grid[row][col].remove(sim_grid[row][col][x])
                            x -= 1
                        x += 1
            num_days += 1
            # comment `debug_print()` out when not in debug mode
            # debug_print()
            if MAKE_GIF:
                # create an image the simulation state and append to a list of images to later
                #       turn into a gif
                debug_start_timer = time()
                sim_gif.visualize(sim_grid)
                # images.append(visualize(canvas.copy()))
                debug_timer_vis += time() - debug_start_timer
        # output the last day's numbers to csv file
        outfile.write(str(num_days)+','+str(state_list[0])+','+str(state_list[1])+','\
            +str(state_list[2])+','+str(state_list[3])+'\n')
        print("Finished mathematical portion of simulation.")
        print("Output dumped to .csv file in `output` folder.")
        if MAKE_GIF:
            print("Preparing the .gif of the simulation.")
            debug_start_timer = time()
            # we do `num_days+1` to include the last day's simulation state
            sim_gif.finish_and_save_gif(num_days)
            debug_timer_vis += time() - debug_start_timer
            print("The visualization processing took", debug_timer_vis, "seconds")

###################################################################################################
#                                              FUNCTIONS
###################################################################################################

# runs through each cell in `sim_grid`, iterating through each individual found in the cell,
#       and summing the exposure points, storing the result in the identical row and column
#       in `expo_points_grid`. This strategy uses more memory than an earlier one which, for
#       every individual in the `sim_grid`, recalculated the exposure points sum for a neighboring
#       cell N times (where N is the number of susceptible individuals in the cell). That's a lot
#       of wasted CPU time.
def calculate_expo_total():
    # loop through entire simulation grid, i.e. every individual
    for row in range(1, ITERATOR_LIMIT):
        for col in range(1, ITERATOR_LIMIT):
            num_exposure_points = 0.0
            for person in sim_grid[row][col]:
                # if the individual is both infectious and not isolating
                #       add their exposure points to the sum
                if person.state_of_health == 2 and not person.quarantiner:
                    num_exposure_points += (person.exposure_points_factor)
            # store exposure points for the cell in `expo_points_grid`
            expo_points_grid[row][col] = num_exposure_points

# count how many infectious neighbors an individual has
def checkNeighbors(location):
    row, col = location
    # grab the exposure points from the individuals in the same cell (they count too)
    #       (yeah yeah I know this isn't strictly von Neumann or whatever deal with it)
    num_exposure_points = expo_points_grid[row][col]
    # if using the von Neumann method, just check the north, south, east, and west neighbors
    num_exposure_points += expo_points_grid[row][col+1] + expo_points_grid[row-1][col] + \
                                expo_points_grid[row][col-1] + expo_points_grid[row+1][col]
    # if using the Moore method, add the corner neighbors exposure points to the von Neumann ones
    if not CONTACT_TYPE:
        num_exposure_points += expo_points_grid[row-1][col+1] + expo_points_grid[row-1][col-1] + \
                                expo_points_grid[row+1][col-1] + expo_points_grid[row+1][col+1]
    return num_exposure_points

####################################################################################
#                                   DEBUG CODE                                     #
####################################################################################
def debug_print():
    # print the entire grid, including the borders
    for x in range(NUM_COLS_FULL):
        for y in range(NUM_ROWS_FULL):
            print('[', end='')
            for individual in sim_grid[x][y]:
                print(individual.state_of_health, end=',')
            print(']', end='')
        print('\n')
    print('-------------------------------')

####################################################################################
#                                   WHERE IT STARTS                                #
####################################################################################

# the `int main()` of the program
if __name__ == "__main__":
    # gonna use this to find the execution time
    debug_timer = time()
    # start the simulation
    main()
    # find the total execution time
    print("Entire simulation took", time() - debug_timer, "seconds")
