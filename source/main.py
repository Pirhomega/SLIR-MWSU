###################################################################################################

# Cellular Automata SLIR Simulation Framework
# Fall 20202
# School and Mentors: Midwestern State University, Drs. Tina Johnson and Terry Griffin
# Programmer: Corbin Matamoros
# Program Description:
#       This program uses the SLIR and SLIS model to simulate disease spread at Midwestern State University.
#       See the README.md and report.docx for more detail.

###################################################################################################

from time import time
from Visualizer import Visualizer
from Cellular_Automaton import Cellular_Automaton
from constants import OUTPUT_FOLDER, MAKE_GIF

# the `if __name__ == "__main__":` at the very bottom of this script calls this function
def main():
    # instantiate the cellular automaton class so we can begin the simulation
    simulation_grid = Cellular_Automaton()

    # used to find how much time it takes to create each day's image
    debug_timer_vis = 0.0

    # boolean that `simulation_grid` will set to True if the simulation should terminate
    sim_ended = False
    
    # open a 'csv' file for outputting the daily reports (the number of susceptible, latent, infectious,
    #       and recovered individuals at the end of the day)
    outfile = open(OUTPUT_FOLDER+"CAoutput.csv", 'w')
    # output the header of the .csv output file
    outfile.write("day|susceptible|latent|infectious|recovered|dead\n")

    # instantiate visualizer class to create gif of simulation if the user wants
    if MAKE_GIF:
        print("Instantiating visualizer object")
        sim_gif = Visualizer()
        print("Complete")

    # loop at least SIM_MAX days and until there are no individuals in the latent nor infectious stages
    state_list = []
    day = 0
    while not sim_ended:
        # get the state of the simulation for the current day
        day, state_list = simulation_grid.start_of_day_metrics()
        # outputs the beginning-of-day state of the grid to csv output file
        write_to_output(outfile, day, state_list)

        # process for the next day in the simulation
        print("Processing day", day, end='\r', flush=True)
        # process day needs to handle every disease since main does not "know" there
        #       are multiple diseases
        sim_ended = simulation_grid.process_day()

        if MAKE_GIF:
            debug_timer_vis += make_days_image(sim_gif, simulation_grid.sim_grid)
    # get the state of the simulation for the last day
    day, state_list = simulation_grid.start_of_day_metrics()
    # output the last day's numbers to csv file
    write_to_output(outfile, day, state_list)
    if MAKE_GIF:
        finish_visualization(sim_gif, day, debug_timer_vis)

####################################################################################
#                                   FUNCTIONS                                      #
####################################################################################

def make_days_image(sim_gif, sim_grid):
    """
    Purpose:    Produce a picture of the simulation state, using colored images
                to represent individuals in the different stages of the disease(s)
    Input:      `sim_gif`: the object of the Visualizer class
                `sim_grid`: the 2D simulation grid (automaton)
    Output:     The time in seconds for the visualization of one day
    """
    debug_start_timer = time()
    sim_gif.visualize(sim_grid)
    return time() - debug_start_timer

def write_to_output(outfile, day, state_list):
    """
    Purpose:    Print to the output file the data from the current simulation day
    Input:      `state_list`: A list of the current day, and the number of susceptible, 
                infectious, latent, recovered, and dead individuals
    Output:     None
    """
    outfile.write(str(day)+'|'+str(state_list[0])+'|'+str(state_list[1])+'|'+str(state_list[2])+'|'+str(state_list[3])+'|'+str(state_list[4])+'\n')

def finish_visualization(sim_gif, last_day, debug_timer_vis):
    """
    Purpose:    Concatenate all the images produced by `make_days_image` into a gif
    Input:      `sim_gif`: the object of the Visualizer class
                `last_day`: an integer representing the last day of the simulation
                `debug_timer_vis`: a float of a running timer used to time the 
                visualization processing
    Output:     None
    """
    print("Preparing the .gif of the simulation.")
    debug_start_timer = time()
    sim_gif.finish_and_save_gif(last_day)
    debug_timer_vis += time() - debug_start_timer
    print("The visualization processing took", debug_timer_vis, "seconds")

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



# Verified functionality
#   1. state_list produces the correct count of each disease
#   2. Infections occur correctly
#   3. Individuals progress from latent to infectious to recovered correctly