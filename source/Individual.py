"""
Module:     Individual.py
Purpose:    To separate the `Individual` class from the main code for easier reading.
            See doc string for the class for more info
"""

from random import random, randint, seed, choices
from constants import DISEASE_LIST, PATCHES, NUM_PATCHES, terrain_grid

class Individual:
    '''
    class:      Individual
    purpose:    represents an individual in the SLIR simulation.
    input:
                `iden`: unique, identification integer (must be greater than or equal to zero) for class object
                `age`: in years, an integer value selected from the keys defined in the 'age_dist' field in `params.json`
                `mortality`: a float value representing the ratio of deaths per person in an age group defined in
                    'age_dist_disease' field in `params.json`
                `state`: the individual's state of health, an integer value between zero and three
                `location`: an integer tuple representing the individual's row and column location in the simulation grid
    variables:  `state_of_health`, `id`, `age`, `mortality`, `location`, `tendency`, `days_in_state`,
                `days_in_latent`, `days_in_infectious`, `exposure_points`, `mask_wearer`, `quarantiner`,
                `symptomatic`, `change`, `updated`
    functions:  `flag_for_update`, `check_if_latent`, `check_if_infectious`, `check_if_removed`, `apply_changes`, 
                `select_new_location`
    '''
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
    def __init__(self, iden, state, possible_ages, ages_dist, disease_type=0):
        # sets the random generator seed
        seed(a=None, version=2)
        # can be 0 (susceptible), 1 (latent), 2 (infectious), 3 (recovered), or 4 (immune)
        self.state_of_health = [0] * len(DISEASE_LIST)
        if state != 0:
            self.state_of_health[disease_type] = state

        # unique identification number for this individual
        self.id = iden

        # determine the individual's age
        age = choices(possible_ages, ages_dist)[0]
        # if a random number is lower than the mortality rate of the individual's age group
        #       they will die when recovered.
        self.die_when_recovered = []

        # individual's initial location in the simulation grid.
        self.location = self.chooseLocation()
        # location this individual wants to travel to eventually
        self.tendency = self.chooseLocation()

        # this instruction will take the bulk of the initialization time
        self.path = terrain_grid.find_shortest_path(self.location,self.tendency)

        # number of units of time this individual has spent in their current state
        self.days_in_state = [0] * len(DISEASE_LIST)
        # number of days this individual will suffer in the latent stage of each disease
        self.days_in_latent = []

        # number of days this individual will suffer in the infectious stage of each disease
        self.days_in_infectious = []

        # number of days this individual will retain immunity from each disease
        self.immunity_duration = []

        # the factor that, when multiplied by the exposure_points to be added to an individual,
        #   determines if they get a reduced number or not. E.G. when an infected individual
        #   is wearing a mask, they will have a reduced effect on the susceptible ones around
        #   them.
        self.prevention_factor = []
        # the fact the individual does or does not quarantine when they know they're infected
        #   'and-ing' with `bool(random() < SYMP_CHANCE)` says, "if the person knows they're sick,
        #   they'll isolate. But if they don't show symptoms, they won't know they're sick
        #   so they won't isolate"
        self.quarantiner = []
        # the fact the individual will wear a mask when they know they are infected with a particular
        #   disease
        self.mask_wearer = []

        # initialize all parameters that differ based on the disease for each disease
        for disease in range(len(DISEASE_LIST)):
            self.days_in_latent.append((randint(DISEASE_LIST[disease]["LATENT_PERIOD_MIN"], DISEASE_LIST[disease]["LATENT_PERIOD_MAX"])))
            self.days_in_infectious.append((randint(DISEASE_LIST[disease]["INFECTIOUS_PERIOD_MIN"], DISEASE_LIST[disease]["INFECTIOUS_PERIOD_MAX"])))
            self.immunity_duration.append((randint(DISEASE_LIST[disease]["IMMUNITY_DURATION_MIN"], DISEASE_LIST[disease]["IMMUNITY_DURATION_MAX"])))
            self.die_when_recovered.append(bool(random() < DISEASE_LIST[disease]["AGE_DIST_DISEASE"][age]))
            self.mask_wearer.append(bool(random() < DISEASE_LIST[disease]["MASK_CHANCE"]))
            # if the statement in the if condition evaulates to True, the individual wears a mask
            if bool(random() < DISEASE_LIST[disease]["MASK_CHANCE"]):
                self.prevention_factor.append(0.5)
            # otherwise, they don't wear one and suffer a higher chance of getting infected
            else:
                self.prevention_factor.append(1.0)
            self.quarantiner = bool(random() < DISEASE_LIST[disease]["QUARAN_CHANCE"]) and bool(random() < DISEASE_LIST[disease]["SYMP_CHANCE"])

        # signals a state change is necessary
        self.change = [False] * len(DISEASE_LIST)
        # signals the individual has been moved from their previous location
        self.updated = False

        # debug dump
        self.outfile = open('./debug/'+str(self.id)+'.txt', 'w')
        self.outfile.write("Latent period: "+str(self.days_in_latent)+'\nInfectious period: '+str(self.days_in_infectious)+'\nImmunity duration: '+str(self.immunity_duration)+'\n\n')


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

    def flag_for_update(self, is_infected):
        """
        Assess the individual's state of health and determine if they progress through the disease
            This means susceptible individuals will have their surroundings analyzed for number of infectious
              individuals, latent individuals will be checked if they transition to the infectious stage,
              as well as infectious individuals to the recovered stage.
                NOTE: the individual's member variables are not updated at this time because individuals' changes to their state
                of health in one day do not affect their neighbors until the following day. For example, an individual transitioned
                to the infectious stage in day 100. If we went ahead and updated their object variables, their susceptible neighbor
                being analyzed next in the simulation will be influenced by that change. Since changes don't take affect
                until the next day, we just flag the individual for changes and update the variables after all individuals
                in the simulation have been analyzed.
        """
        self.updated = False
        # add one day to the individual's time in their current state
        self.days_in_state = [(current_count + 1) for current_count in self.days_in_state]

        # checks if the individual has the necessary qualities to progress to the next
        #   stage of the disease (if susceptible, then they would progress to the latent stage, etc.)
        self.check_if_progressing(is_infected)

    def check_if_progressing(self, is_infected):
        """
        Purpose:    Sets the individual to transition to the next disease stage
        """
        for disease in range(len(DISEASE_LIST)):
            # if the individual has become infected as a susceptible, OR
            #       if they are latent and have stayed the duration of the latent period, OR
            #           if they are infectious and have stayed the duration of the infectious period, OR
            #               if they are recovered and have stayed the duration of the immunity period,
            #   set the `self.change` variable to True for them to move to the next stage
            if (self.state_of_health[disease] == 0 and is_infected[disease]) or \
                    (self.state_of_health[disease] == 1 and (self.days_in_state[disease] == self.days_in_latent[disease])) or \
                        (self.state_of_health[disease] == 2 and (self.days_in_state[disease] == self.days_in_infectious[disease])) or \
                            (self.state_of_health[disease] == 3 and (self.days_in_state[disease] == self.immunity_duration[disease])):
                self.change[disease] = True

    def apply_changes(self, outfile=None):
        """
        Purpose: updates the state variables of the individual
        Returns: the integer representing the individual's state of health
        """
        if not self.updated:
            for disease in range(len(DISEASE_LIST)):
                # transition the individual to the next state
                if self.change[disease]:
                    self.days_in_state[disease] = 0
                    self.state_of_health[disease] = (self.state_of_health[disease] + 1) % 4
                    self.change[disease] = False
                    # print(self.id, "transitioned from", self.state_of_health[disease]-1, "to", self.state_of_health[disease])
            # move the individual to the next spot in the grid by assigning its position
            #       as the first position in the `self.path` list
            if self.path != []:
                self.location = (self.path[0][1], self.path[0][0])
                self.path.pop(0)
            # if individual has reached their desired location (tendency), make a new one
            else:
                # changes the individual `self.tendency` to be a new location in the simulation grid
                self.tendency = self.chooseLocation()
                # find the next set of spots the Individual must use to get to their new location
                self.path = terrain_grid.find_shortest_path(self.location, self.tendency)
            # setting a variable `updated` to True prevents this individual from being analyzed again in the same day
            self.updated = True
            # # unit test that prints the state of health of every individual in the population
            # outfile.write(str(self.state_of_health)+', ')
            self.outfile.write("Days in state: "+str(self.days_in_state)+'\n')
            self.outfile.write("\n\n")
            return self.state_of_health
        return -1

    def select_new_location(self, spot):
        """
        Purpose:    Moves the individual in the simulation grid
        Input:      `spot`: 
        """
        can_move = False
        for disease in range(len(DISEASE_LIST)):
            # the individual can move if they are not recovered OR if they are recovered but still alive
            if (self.state_of_health[disease] != 3) or (self.state_of_health[disease] == 3 and not self.die_when_recovered[disease]):
                can_move = True

        if can_move:
            new_spot_row = spot[0]
            new_spot_col = spot[1]
            drow = spot[0] - self.tendency[0]
            dcol = spot[1] - self.tendency[1]
            if drow < 0:
                new_spot_row = spot[0] + 1
            elif drow > 0:
                new_spot_row = spot[0] - 1
            if dcol < 0:
                new_spot_col = spot[1] + 1
            elif dcol > 0:
                new_spot_col = spot[1] - 1
            self.location = (new_spot_row, new_spot_col)
    
    def chooseLocation(self):
        """
        selects a random location in the simulation grid or within a patch, selected at random
        """
        # Select at random one of the patches to spawn in an initially infected Individual
        randPatch = randint(0, NUM_PATCHES-1)
        # adding 1 to each random integer bound accounts for the empty grid border the user doesn't see
        randx = randint(PATCHES[str(randPatch)]["bounds"][0]+1, PATCHES[str(randPatch)]["bounds"][2]+1)
        randy = randint(PATCHES[str(randPatch)]["bounds"][1]+1, PATCHES[str(randPatch)]["bounds"][3]+1)
        return (randx, randy)
    
    def printState(self):
        print("ID:", self.id)
        print("State of health:", self.state_of_health)
        print('\n')

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
    individual = Individual()