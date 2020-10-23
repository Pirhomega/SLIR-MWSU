"""
    Module:     Obstacle.py
    Purpose:    To create terrain for the individuals in the simulation to traverse,
                and enable pathfinding in the individuals
"""

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from constants import RESOURCES_FOLDER, Grid

# the terrain grid class that we'll use for Individual's pathfinding
class Obstacle_Grid():
    def __init__(self):
        # in the end, `self.terrain_grid` will be a 2D array of values where zeros are obstacles
        #       and all values greater than zero are edge weights for all edges connected to that node
        self.terrain_grid = []
        with open(RESOURCES_FOLDER+"terrain.txt") as input:
            rows = input.readlines()
            # loop through entire terrain file and convert all chars to integers
            for row in rows:
                terrain_grid_row = []
                for col in row:
                    if col.isdigit():
                        terrain_grid_row.append(int(col))
                self.terrain_grid.append(terrain_grid_row)
        # instantiate the Grid object using the newly converted terrain_grid
        #       The pathfinding library requires this special object to work
        self.grid = Grid(matrix=self.terrain_grid)
        # define the A* pathfinding algorithm as the one we use. Another option is Dijkstra's
        self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

    def find_shortest_path(self, location, destination):
        """
        Purpose:    create a list of spots in a 2D grid that define the shortest path
                    between two spots
        Input:      Starting location (`location`) and Ending location (`destination`)
        Output:     A list of spots/locations in the 2D grid
        """
        self.grid.cleanup()
        self.start = self.grid.node(location[1],location[0])
        self.end = self.grid.node(destination[1],destination[0])
        path_list, _ = self.finder.find_path(self.start, self.end, self.grid)
        return path_list

    def print_path_to_file(self, path_list):
        """
        Purpose:    Test function that prints the terrain with the shortest path between two nodes
                    to the console
        Input:      List of spots in terrain grid that define the shortest path between
                    two nodes.
        Output:     None
        """
        print(self.grid.grid_str(path=path_list, start=self.start, end=self.end))