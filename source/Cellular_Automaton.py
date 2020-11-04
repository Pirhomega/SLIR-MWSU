"""
Module:     cellular_automaton.py
Purpose:    To create a cellular automaton for the purpose of modeling the spread of disease
"""

from random import random, seed
from constants import POPULATION, DISEASE_LIST, NUM_COLS_FULL, NUM_ROWS_FULL, AGE_DIST, ITERATOR_LIMIT, SIM_MAX
from Individual import Individual

class Cellular_Automaton():
    """
    A cellular automaton that will be used to simulate disease spread in a population
    """
    """
                     /$$           /$$   /$$                          
                    |__/          |__/  | $$                          
                    /$$ /$$$$$$$  /$$ /$$$$$$                        
                    | $$| $$__  $$| $$|_  $$_/                        
                    | $$| $$  \ $$| $$  | $$                          
                    | $$| $$  | $$| $$  | $$ /$$                      
                    | $$| $$  | $$| $$  |  $$$$/                      
    /$$$$$$ /$$$$$$|__/|__/  |__/|__/   \___/   /$$$$$$ /$$$$$$      
    |______/|______/                            |______/|______/
    """
    def __init__(self):
        # length of simulation in days
        self.num_days = 0

        # population variables
        self.population = POPULATION

        self.state_list = [([0] * len(DISEASE_LIST)) for state in range(5)]

        # These following two while loops will only place individuals randomly in the grid so as to leave
        #       a border of empty lists around the grid's outside. E.G.
        #       GRID A ->   |0 0 0 0 0| (the 'X' spots are usable; the '0' spots aren't)
        #                   |0 X X X 0|
        #                   |0 X X X 0|
        #                   |0 X X X 0|
        #                   |0 0 0 0 0|
        # the 2D simulation grid
        self.sim_grid = [([0] * NUM_COLS_FULL) for row in range(NUM_ROWS_FULL)]
        self.infectious_count_grid = [([0] * NUM_COLS_FULL) for row in range(NUM_ROWS_FULL)]
        print("Created main simulation grid")

        # initialize simulation grid indices to be empty lists
        # initialize infectious_count_grid indices to be zero-lists of length equal
        #   to the number of diseases to be modeled in the simulation
        for row in range(NUM_ROWS_FULL):
            for col in range(NUM_COLS_FULL):
                self.sim_grid[row][col] = []
                self.infectious_count_grid[row][col] = ([0] * len(DISEASE_LIST))
        print("Initialized main simulation grid")

        # create two lists of the population's possible ages and their distribution
        ages = []
        age_weights = []
        for key in AGE_DIST:
            ages.append(key)
            age_weights.append(AGE_DIST[key])

        # Used to give each individual in the population a unique ID
        individual_counter = 1

        # instantiate the initially infectious individuals and get them placed in the grid
        print("Populating grid with infectious individuals")
        infectious_count, individual_counter = self.__populate_with_infectious(individual_counter, ages, age_weights)

        # instantiate the rest of the population (the susceptible individuals) and get them placed in the grid
        print("Populating grid with susceptible individuals")
        self.__populate_with_susceptibles(individual_counter, ages, age_weights, infectious_count)

        # populate `infectious_count_grid`
        self.__count_num_infectious()

        # outfile for debugging purposes
        self.outfile = open("population.txt", 'w')

        print("Populated main simulation grid with initially infected and susceptible Individuals")

    """
     /$$$$$$$            /$$                        /$$                     /$$      /$$             /$$     /$$                       /$$                
    | $$__  $$          |__/                       | $$                    | $$$    /$$$            | $$    | $$                      | $$                
    | $$  \ $$  /$$$$$$  /$$ /$$    /$$  /$$$$$$  /$$$$$$    /$$$$$$       | $$$$  /$$$$  /$$$$$$  /$$$$$$  | $$$$$$$   /$$$$$$   /$$$$$$$  /$$$$$$$      
    | $$$$$$$/ /$$__  $$| $$|  $$  /$$/ |____  $$|_  $$_/   /$$__  $$      | $$ $$/$$ $$ /$$__  $$|_  $$_/  | $$__  $$ /$$__  $$ /$$__  $$ /$$_____/      
    | $$____/ | $$  \__/| $$ \  $$/$$/   /$$$$$$$  | $$    | $$$$$$$$      | $$  $$$| $$| $$$$$$$$  | $$    | $$  \ $$| $$  \ $$| $$  | $$|  $$$$$$       
    | $$      | $$      | $$  \  $$$/   /$$__  $$  | $$ /$$| $$_____/      | $$\  $ | $$| $$_____/  | $$ /$$| $$  | $$| $$  | $$| $$  | $$ \____  $$      
    | $$      | $$      | $$   \  $/   |  $$$$$$$  |  $$$$/|  $$$$$$$      | $$ \/  | $$|  $$$$$$$  |  $$$$/| $$  | $$|  $$$$$$/|  $$$$$$$ /$$$$$$$/      
    |__/      |__/      |__/    \_/     \_______/   \___/   \_______/      |__/     |__/ \_______/   \___/  |__/  |__/ \______/  \_______/|_______/  
    """

    def __populate_with_infectious(self, individual_counter, ages, age_weights):
        """
        Purpose:    Populates the simulation grid with the initially infectious individuals
                    for all diseases to be modeled
        Input:      the id for the Individual (`individual_counter`), the population's list of ages
                    (`ages`), and the age distribution of the population ("age_weights")
        Output:     None
        """
        total_infectious = 0
        for disease in range(len(DISEASE_LIST)):
            num_infectious = DISEASE_LIST[disease]["INIT_INFECTIOUS"]
            total_infectious += num_infectious
            while num_infectious > 0:
                # create an Individual object with its identifier, their state of health state, the list of possible ages,
                #       the age distributions, the ratio of deaths for each age, and the type of disease
                infected_person = Individual(individual_counter, 2, ages, age_weights, disease)

                self.sim_grid[infected_person.location[0]][infected_person.location[1]].append(infected_person)

                print("Disease", str(disease) + ":", num_infectious, "left...", end='\r', flush=True)

                num_infectious -= 1
                individual_counter += 1
        return total_infectious, individual_counter

    def __populate_with_susceptibles(self, individual_counter, ages, age_weights, infectious_count):
        """
        Purpose:    Populates the simulation grid with the susceptible individuals,
                    which is just the population minus the initially infected
        Input:      the id for the Individual (`individual_counter`), the population's list of ages
                    (`ages`), and the age distribution of the population ("age_weights")
        Output:     None
        """
        y = self.population - infectious_count
        while y > 0:
            # here, we don't pass the `disease` param like we did in `__populate_with_infectious` because
            #   a susceptible person is disease agnostic. They can contract any disease.
            susceptible_person = Individual(individual_counter, 0, ages, age_weights)
            self.sim_grid[susceptible_person.location[0]][susceptible_person.location[1]].append(susceptible_person)

            print(y, "left...", end='\r', flush=True)

            y -= 1
            individual_counter += 1

    def __count_num_infectious(self):
        """
        Purpose:    Count the number of infectious people in a cell
        Input:      A row-column tuple identifying a row and column in the simulation grid
        Output:     None
        """
        # for row in range(0,100):
        #     for col in range(0,100):
        #         for disease in self.infectious_count_grid[row][col]:
        #             if disease:
        #                 print("There's an infectious in", row, col)
        # # print(self.infectious_count_grid)
        # print('\n')
        for row in range(1, ITERATOR_LIMIT):
            for col in range(1, ITERATOR_LIMIT):
                # for each day, the `self.infectious_count_grid` must be reset to all zeros
                #   otherwise each spot's infectious count will be incremented upon the previous
                #   day's count
                self.infectious_count_grid[row][col] = ([0] * len(DISEASE_LIST))
                for individual in self.sim_grid[row][col]:
                    for disease in range(len(DISEASE_LIST)):
                        if individual.state_of_health[disease] == 2:
                            self.infectious_count_grid[row][col][disease] += 1

    """
     /$$$$$$$            /$$       /$$ /$$                 /$$      /$$             /$$     /$$                       /$$                
    | $$__  $$          | $$      | $$|__/                | $$$    /$$$            | $$    | $$                      | $$                
    | $$  \ $$ /$$   /$$| $$$$$$$ | $$ /$$  /$$$$$$$      | $$$$  /$$$$  /$$$$$$  /$$$$$$  | $$$$$$$   /$$$$$$   /$$$$$$$  /$$$$$$$      
    | $$$$$$$/| $$  | $$| $$__  $$| $$| $$ /$$_____/      | $$ $$/$$ $$ /$$__  $$|_  $$_/  | $$__  $$ /$$__  $$ /$$__  $$ /$$_____/      
    | $$____/ | $$  | $$| $$  \ $$| $$| $$| $$            | $$  $$$| $$| $$$$$$$$  | $$    | $$  \ $$| $$  \ $$| $$  | $$|  $$$$$$       
    | $$      | $$  | $$| $$  | $$| $$| $$| $$            | $$\  $ | $$| $$_____/  | $$ /$$| $$  | $$| $$  | $$| $$  | $$ \____  $$      
    | $$      |  $$$$$$/| $$$$$$$/| $$| $$|  $$$$$$$      | $$ \/  | $$|  $$$$$$$  |  $$$$/| $$  | $$|  $$$$$$/|  $$$$$$$ /$$$$$$$/      
    |__/       \______/ |_______/ |__/|__/ \_______/      |__/     |__/ \_______/   \___/  |__/  |__/ \______/  \_______/|_______/  
    """

    def start_of_day_metrics(self):
        """
        Purpose:        Returns the simulation state
        Input:          None
        Output:         Number of population who are susceptible, latent, infectious, recovered, and dead
        """
        return self.num_days, self.state_list

    def process_day(self):
        """
        Purpose:        Iterates through every cell in the cellular automaton and performs
                        standard stuff
        Input:          None
        Output:         None
        """
        # reset the state_list since the simulation recounts the number of susceptibel, latent, etc.
        #   individuals each simulated day
        self.state_list = [([0] * len(DISEASE_LIST)) for state in range(5)]
        for row in range(1, ITERATOR_LIMIT):
            for col in range(1, ITERATOR_LIMIT):
                # traverse the list of individuals "sitting" in this particular grid location
                for individual in self.sim_grid[row][col]:
                    # make the call to `infect` and flag the individual if they are ready to progress
                    #   to the next stage of the disease
                    individual.flag_for_update(self.infect((row, col)))

        # loop through entire grid again and update all individuals' object variables
        self.outfile.write("Day: "+str(self.num_days)+'\n')
        for row in range(1, ITERATOR_LIMIT):
            for col in range(1, ITERATOR_LIMIT):
                x = 0
                while x < len(self.sim_grid[row][col]):
                    # update the object variables of the individual
                    self.outfile.write(str(self.sim_grid[row][col][x].id)+" went from "+str(self.sim_grid[row][col][x].state_of_health)+' to ')
                    individual_health = self.sim_grid[row][col][x].apply_changes()
                    if individual_health != -1:
                        self.outfile.write(str(individual_health)+'\n')

                        # if the individual is susceptible to all diseases. This special case exists because
                        #   the `susceptible` element in `self.state_list` is a list of len(DISEASE_LIST) size.
                        #   There is only one pool of susceptibles; there aren't different susceptible pools from
                        #   which each disease takes. Therefore, each element in the `susceptible` element in 
                        #   `self.state_list` has the same value
                        if individual_health == [0]*len(DISEASE_LIST):
                            # print(self.sim_grid[row][col][x].id, "is perfectly healthy.")
                            self.state_list[0] = [x + 1 for x in self.state_list[0]]
                            # print("The new susceptible count is:", self.state_list[0])
                        # Otherwise, this individual is infected with a disease, so don't increment the `susceptible`
                        #   element; increment the disease element in each of the states in `self.state_list`
                        else:
                            # print(self.sim_grid[row][col][x].id, ": Here's their health:", individual_health)
                            for disease in range(len(DISEASE_LIST)):
                                # do not increment the `susceptible` element in `self.state_list`
                                if individual_health[disease] > 0:
                                    self.state_list[individual_health[disease]][disease] += 1
                    # if the current position of the individual in the simulation grid doesn't match
                    #   their position in the Individual object (indicating they will move to a different
                    #   spot for the next day), move them to their new position and remove them from the 
                    #   old.
                    if self.sim_grid[row][col][x].location != (row, col):
                        # append them to the list in their new location
                        self.sim_grid[self.sim_grid[row][col][x].location[0]][self.sim_grid[row][col][x].location[1]].append(self.sim_grid[row][col][x])
                        # remove them from the list in their old location
                        self.sim_grid[row][col].remove(self.sim_grid[row][col][x])
                        # Here's an example of why we decrement x after moving an object to a new grid location
                        #   instead of just incrementing `x` like any other while loop would. Let's assume 
                        #   there are three objects in this simulation grid position. We just removed one object 
                        #   and moved it to it's new location, leaving two. If we had just incremented `x` (`x` 
                        #   would then be 1), we would then access the second object of the two left in this position. 
                        #   Let's continue. We move that object to its new location. Increment `x` again (`x` now 
                        #   equals 2). There's still one object we haven't iterated over, but the list length is now 1
                        #   while `x` is 2, killing the while loop. That's why we decrement `x` whenever we move an 
                        #   object to a new grid location.
                        x -= 1
                    x += 1
        # update the num_infectious grid for the next simulation day
        self.__count_num_infectious()
        self.num_days += 1

        self.outfile.write('\n')

        # the simulation will terminate whenever it has run SIM_MAX number of days
        #   or there are no individuals in the latent or infectious stages
        latent_infectious_present = False
        # loop through all diseases and check if there are any latent or infectious individuals
        #   If there are none, the OR result will be False. If there is at least 1 latent or
        #   infectious person in the entire simulation, the OR result will be True.
        # We negate `self.state_list[1][disease]` and `self.state_list[2][disease]` to always return
        #   False if there are individuals possessing that state
        for disease in range(len(DISEASE_LIST)):
            # latent = self.state_list[1][disease]
            # infectious = self.state_list[2][disease]
            # temp = latent_infectious_present
            latent_infectious_present = latent_infectious_present or self.state_list[1][disease] or self.state_list[2][disease]
        if self.num_days == SIM_MAX or not latent_infectious_present:
            return True
        return False

    def infect(self, location):
        """
        Purpose:        Iterate through all neighboring cells of a single Individual in 
                        `location` and use the `transmission_rate` parameter from the
                        parameter file to determine if the Individual becomes infected.
        Input:          A row-column tuple identifying a row and column in the simulation grid
        Output:         True if the Individual becomes infected. False otherwise.
        """
        row, col = location

        single_cell_sum = 0
        vonNeumann_sum = 0
        moore_sum = 0
        num_infectious_neighbors = []
        is_infected = []

        # unit test: prints the entire neighborhood of a spot
        for mini_row in range(row-1,row+2):
            for mini_col in range(col-1,col+2):
                self.outfile.write('[')
                for individual in self.sim_grid[mini_row][mini_col]:
                    self.outfile.write(str(individual.id)+':'+str(individual.state_of_health))
                self.outfile.write(']')
            self.outfile.write('\n')
        
        #########################################################################################
        #   THIS PROCESS COULD BE MADE MORE EFFICIENT BY ONLY RUNNING IF THE INDIVIDUAL IS      #
        #   SUSCEPTIBLE IN A PARTICULAR DISEASE. THE ONLY PROBLEM: IF THE PERSON IS             #
        #   SUSCEPTIBLE IN ONE DISEASE BUT NOT THE OTHER, HOW CAN I STILL PRODUCE IS_INFECTED   #
        #   THAT'S INDEXABLE FOR A PARTICULAR DISEASE WHEN NUM_INFECTIOUS_NEIGHBORS HAS THE     #
        #   NEIGHBOR COUNT APPENDED TO IT?                                                      #
        #########################################################################################

        for disease in range(len(DISEASE_LIST)):
            # count the number of infectious individuals in the same cell as the Individual
            #   This strat is not a part of the von Neumann or Moore neighborhood, but
            #   Individuals in the same cell are considered neighbors in this simulation
            # `single_cell_sum` becomes a list of integers, each index storing the number of
            #   infectious individuals for each disease being modeled
            #   e.g. single_cell_sum = [0, 3] if there are two diseases being modelled and three
            #   infectious individuals of disease #2 are in that cell
            single_cell_sum = self.infectious_count_grid[row][col][disease]
            # if using the von Neumann method, sum the number of infectious neighbors in the
            #   north, south, east, and west cells
            if DISEASE_LIST[disease]["NEIGHBORHOOD"] > 0:
                vonNeumann_sum = self.infectious_count_grid[row][col+1][disease] + \
                    self.infectious_count_grid[row-1][col][disease] + \
                    self.infectious_count_grid[row][col-1][disease] + \
                    self.infectious_count_grid[row+1][col][disease]

            # if using the Moore method, add the number of infectious neighbors in the corner cells
            if DISEASE_LIST[disease]["NEIGHBORHOOD"] == 2:
                moore_sum = self.infectious_count_grid[row-1][col+1][disease] + \
                    self.infectious_count_grid[row-1][col-1][disease] +\
                    self.infectious_count_grid[row+1][col-1][disease] + \
                    self.infectious_count_grid[row+1][col+1][disease]

            # this reflects the total number of infectious individuals for each disease
            #   based on the neighborhood stategy
            num_infectious_neighbors.append(single_cell_sum + vonNeumann_sum + moore_sum)

        # print("There are", num_infectious_neighbors, "in position", location)
        # someone getting infected is determined by chance based on the number
        #   of infectious individuals in the neighborhood. For N infectious people
        #   in your neighborhood, you have N * TRANS_RATE chance of getting infected
        seed(a=None, version=2)
        # for every disease in the disease list, determine if the individual becomes infected
        for disease in range(len(DISEASE_LIST)):
            random_value = random()
            chance_infection = num_infectious_neighbors[disease]*DISEASE_LIST[disease]["TRANS_RATE"]
            self.outfile.write(str(random_value)+'<'+str(chance_infection)+'? | ')
            is_infected.append(bool(random_value < chance_infection))
        self.outfile.write('\n')
        # In the end, return a list where each element is a boolean, True if individual becomes
        #   infected, False otherwise
        # print("is_infected:", is_infected)
        for disease in range(2):
            self.outfile.write(str(num_infectious_neighbors[disease])+', ')
            self.outfile.write(str(is_infected[disease])+', ')
        self.outfile.write('\n\n')
        
        return is_infected

    # def get_sim_grid(self):
    #     """
    #     Purpose:    Pythonically returns a "copy" of the simulation grid for the 
    #                 day during which this method was called
    #     Input:      None
    #     Output:     A "copy" of the simulation grid
    #     """
    #     return self.sim_grid

    def debug_print(self):
        # print the entire grid, including the borders
        for x in range(NUM_COLS_FULL):
            for y in range(NUM_ROWS_FULL):
                print('[', end='')
                for individual in self.sim_grid[x][y]:
                    print(individual.state_of_health, end=',')
                print(']', end='')
            print('\n')
        print('-------------------------------')

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
    CA = Cellular_Automaton()
