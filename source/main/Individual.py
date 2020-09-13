import random
from constants import NUM_ROWS, NUM_COLS, LATENT_PERIOD_MAX, LATENT_PERIOD_MIN, \
    INFECTIOUS_PERIOD_MAX, INFECTIOUS_PERIOD_MIN, MASK_CHANCE, QUARAN_CHANCE, SYMP_CHANCE, \
    MAX_EXPOSURE

class Individual:
    def __init__(self, iden, age, mortality, state, location):
        # can be 0 (susceptible), 1 (latent), 2 (infectious), 3 (recovered), or 4 (immune)
        self.state_of_health = state
        # unique identification number for this individual
        self.id = iden
        # individual's age
        self.age = age
        # the individual's mortality rate based on their age
        self.mortality = mortality
        # individual's current location in the simulation grid
        self.location = location
        # location this individual wants to travel to eventually
        self.tendency = (random.randint(1, NUM_ROWS-3), random.randint(1, NUM_COLS-3))
        # number of units of time this individual has spent in their current state
        self.days_in_state = 0
        # number of days this individual will suffer in the latent stage of the disease
        self.days_in_latent = random.randint(LATENT_PERIOD_MIN,LATENT_PERIOD_MAX)
        # number of days this individual will suffer in the infectious stage of the disease
        self.days_in_infectious = random.randint(INFECTIOUS_PERIOD_MIN,INFECTIOUS_PERIOD_MAX)
        if state != 2:
            # number of exposure points for this individual
            self.exposure_points = 0
        # the fact the individual does or does not wear a mask when they know they're infected
        self.mask_wearer = bool(random.random() < MASK_CHANCE)
        # the fact the individual does or does not quarantine when they know they're infected
        self.quarantiner = bool(random.random() < QUARAN_CHANCE)
        # the fact the individual is symptomatic when infected
        self.symptomatic = bool(random.random() < SYMP_CHANCE)
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

    # assess the individual's state of health and determine if they progress through the disease
    # This means susceptible individuals will have their surroundings analyzed for number of infectious
    #       individuals, latent individuals will be checked if they transition to the infectious stage,
    #       as well as infectious individuals to the recovered stage.
    #       NOTE: the individual's member variables are not updated at this time to prevent read-after-write hazards
    #       i.e. individuals' changes to their state of health in one day do not affect their neighbors until the following
    #       day. For example, an individual transitioned to the infectious stage in day 100. If we went ahead and updated
    #       their object variables, their susceptible neighbor being analyzed next in the simulation will be influenced
    #       by that change. Since changes don't take affect until the next day, we just flag the individual for changes and
    #       update the variables after all individuals in the simulation have been analyzed.
    def flag_for_update(self, num_surrounded):
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
            self.check_if_latent(num_surrounded)
        # if they're in the latent stage, check if they have stayed the latent period or not
        elif self.state_of_health == 1:
            self.check_if_infectious()
        # if infectious, check if they have stayed the infectious period or not
        elif self.state_of_health == 2:
            self.check_if_removed()

    def check_if_latent(self, num_surrounded):
        """
        checks if the individual has had enough exposures to become infected and join the latent stage
        """
        self.exposure_points += num_surrounded
        if self.exposure_points >= MAX_EXPOSURE:
            self.change = True
        # else:
            # print("This individual will not become latent. They've stayed", self.days_in_state, "days in susceptible stage",end='')

    def check_if_infectious(self):
        """
        checks if the individual has stayed the duration of the latent period to become infectious
        """
        if self.days_in_state == self.days_in_latent:
            self.change = True
        # else:
            # print("This individual will not become infectious. They've stayed", self.days_in_state, "days in latent stage",end='')
    
    def check_if_removed(self):
        """
        checks if the individual has stayed the duration of the infectious period to become removed (dead or alive)
        """
        if self.days_in_state == self.days_in_infectious:
            self.change = True
        # else:
            # print("This individual will not become removed. They've stayed", self.days_in_state, "days in infectious stage",end='')

    def apply_changes(self, spot):
        """
        Purpose: updates the state variables of the individual
        Returns: the integer representing the individual's state of health
        """
        if not self.updated:
            # print("Individual", self.id, "has not been updated")
            if self.change:
                self.days_in_state = 0
                self.state_of_health += 1
                self.change = False
            if spot != self.tendency:
                # print("Individual", self.id, "has not reached their tendency. They're currently at", self.location)
                self.select_new_location(spot)
                # print("Their new position is", self.location)
            else:
                # changes the individual `self.tendency` to be a new location in the simulation grid
                self.tendency = (random.randint(1, NUM_ROWS-3), random.randint(1, NUM_COLS-3))
                # print("Individual", self.id, "will now tend toward", self.tendency)
            # setting a variable `updated` to True prevents this individual from being analyzed again in the same day
            self.updated = True
            return self.state_of_health
        # return a negative one to indicate this individual has already been updated for the current simulation day
        return -1
    
    def select_new_location(self, spot):
        """
        moves the individual in the simulation grid
        """
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