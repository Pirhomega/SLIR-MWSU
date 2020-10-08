"""
Module:     Individual.py
Purpose:    To separate the `Individual` class from the main code for easier reading.
            See doc string for the class for more info
"""

from random import random, randint, seed, choices
from constants import NUM_ROWS_FULL, NUM_COLS_FULL, DISEASE_LIST, PATCHES, NUM_PATCHES, terrain_grid

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
    def __init__(self, iden, state, possible_ages, ages_dist):
        # sets the random generator seed
        seed(a=None, version=2)
        # can be 0 (susceptible), 1 (latent), 2 (infectious), 3 (recovered), or 4 (immune)
        self.state_of_health = state
        # unique identification number for this individual
        self.id = iden

        # determine the individual's age
        self.age = choices(possible_ages, ages_dist)[0]
        # if a random number is lower than the mortality rate of the individual's age group
        #       they will die when recovered.
        self.die_when_recovered = bool(random() < AGE_DIST_DISEASE[self.age])

        # individual's initial location in the simulation grid.
        self.location = self.chooseLocation()
        # location this individual wants to travel to eventually
        self.tendency = self.chooseLocation()
        self.path = terrain_grid.find_shortest_path(self.location,self.tendency)


        # number of units of time this individual has spent in their current state
        self.days_in_state = 0
        # number of days this individual will suffer in the latent stage of the disease
        self.days_in_latent = randint(LATENT_PERIOD_MIN, LATENT_PERIOD_MAX)
        # number of days this individual will suffer in the infectious stage of the disease
        self.days_in_infectious = randint(INFECTIOUS_PERIOD_MIN, INFECTIOUS_PERIOD_MAX)
        # number of days this individual will retain immunity from the disease
        self.immunity_duration = randint(IMMUNITY_DURATION_MIN, IMMUNITY_DURATION_MAX)
        # number of exposure points for this individual
        self.exposure_points = 0.0
        # the fact the individual does or does not wear a mask when they know they're infected
        self.mask_wearer = bool(random() < MASK_CHANCE)
        # the factor that, when multiplied by the exposure_points to be added to an individual,
        #       determines if they get a reduced number or not. E.G. when an infected individual
        #       is wearing a mask, they will have a reduced effect on the susceptible ones around
        #       them.
        self.exposure_points_factor = 1.0
        if self.mask_wearer:
            self.exposure_points_factor = 0.5
        # the fact the individual does or does not quarantine when they know they're infected
        #       'and-ing' with `bool(random() < SYMP_CHANCE)` says, "if the person knows they're sick,
        #       they'll isolate. But if they don't show symptoms, they won't know they're sick
        #       so they won't isolate"
        self.quarantiner = bool(random() < QUARAN_CHANCE) and bool(random() < SYMP_CHANCE)

        # signals a state change is necessary
        self.change = False
        # signals the individual has been moved from their previous location
        self.updated = False
        # print("ID:", self.id)
        # print("Age:", self.age)
        # print("State of health:", self.state_of_health)
        # print("Chance of dying:", self.mortality*100, '%')
        # print("Tendency:", self.tendency)
        # print("Latent period:", self.days_in_latent)
        # print("Infectious period:", self.days_in_infectious)
        # print('\n')

    def flag_for_update(self, num_exposure_points):
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
        self.days_in_state += 1
        # if they're susceptible, add the number of infectious individuals in their neighborhood to their
        #       exposure point count
        if self.state_of_health == 0:
            self.check_if_latent(num_exposure_points)
        # if they're in the latent stage, check if they have stayed the latent period or not
        elif self.state_of_health == 1:
            self.check_if_infectious()
        # if infectious, check if they have stayed the infectious period or not
        elif self.state_of_health == 2:
            self.check_if_removed()
        # if the simulation models the SLIS disease progression model
        if IS_SLIS:
            if self.state_of_health == 3:
                self.check_if_susceptible_again()

    def check_if_latent(self, num_exposure_points):
        """
        checks if the individual has had enough exposures to become infected and join the latent stage
        """
        self.exposure_points += num_exposure_points
        if self.exposure_points > MAX_EXPOSURE:
            self.change = True

    def check_if_infectious(self):
        """
        checks if the individual has stayed the duration of the latent period to become infectious
        """
        if self.days_in_state == self.days_in_latent:
            self.change = True
    
    def check_if_removed(self):
        """
        checks if the individual has stayed the duration of the infectious period to become removed (dead or alive)
        """
        if self.days_in_state == self.days_in_infectious:
            self.change = True
    
    def check_if_susceptible_again(self):
        """
        checks if the individual has stayed in the recovered stage long enough to lose immunity and
                thereby return to the susceptible stage
        """
        if self.days_in_state == self.immunity_duration:
            self.change = True

    def apply_changes(self, spot):
        """
        Purpose: updates the state variables of the individual
        Returns: the integer representing the individual's state of health
        """
        if not self.updated:
            # transition the individual to the next state
            if self.change:
                self.days_in_state = -1
                self.state_of_health = (self.state_of_health + 1) % 4
                self.change = False
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
            return self.state_of_health
        # return a negative one to indicate this individual has already been updated for the current simulation day
        return -1

    def select_new_location(self, spot):
        """
        moves the individual in the simulation grid
        """
        # only move the individual if they are not recovered OR if they are recovered but still alive
        if (self.state_of_health != 3) or (self.state_of_health == 3 and not self.die_when_recovered):
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
