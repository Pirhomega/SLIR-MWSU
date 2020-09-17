from constants import RESOURCES_FOLDER, OUTPUT_FOLDER, ITERATOR_LIMIT, GRID_SIZE
from math import ceil, sqrt
from PIL import Image
# from wand.image import Image

class Visualizer():
    """
    class:      Visualizer
    input:      None
    purpose:    Using PIL, we create a .png image of the individual's positions in the simulation
                grid. Each individual is represented by an image corresponding to their state of health
                (e.g. susceptible -> 0.png). We will paste in their image onto a black image called `canvas`.
                If there are multiple individuals in a simulation grid cell, we break down the cell into an
                NxN mini grid, where N (number of state-of-health images) is equal to the ceiling of the square
                root of the number of individuals in the simulation cell.
    """
    def __init__(self):
        # open the background image to which we will paste the individuals' tiles,
        #       appending each modified image to `images`. `images` starts with a 
        #       defining image that will signifiy the beginning of the gif if looped
        #       infinitely
        self.canvas = Image.open(RESOURCES_FOLDER+"/bkgd.png")
        self.images = [Image.open(RESOURCES_FOLDER+"/beginning.png")]
        self.tiles = [Image.open(RESOURCES_FOLDER+"/0.png"),
                        Image.open(RESOURCES_FOLDER+"/1.png"),
                        Image.open(RESOURCES_FOLDER+"/2.png"),
                        Image.open(RESOURCES_FOLDER+"/3.png"),
                        Image.open(RESOURCES_FOLDER+"/4.png")]

    # each cell could be composed of an `NxN` grid to display all individuals in the spot. We will calculate the dimensions of the grid by
    # taking the square root of the number of individuals in the spot and taking the ceiling of the result. That value will be N.
    def visualize(self, sim_matrices):
        # we don't want to make any changes to the base canvas, which is a black square image.
        #       If we didn't make a copy to modify, the state from the day before would be visible
        #       on the following day (i.e. not good)
        canvas_copy = self.canvas.copy()
        # calculate how large a tile should be in pixels to fit GRID_SIZE times GRID_SIZE
        #       of them in the simulation grid
        default_tile_size = ceil(1000/GRID_SIZE)
        # loop through entire effective area of simulation grid and form the state image
        for row in range(1, ITERATOR_LIMIT):
            for col in range(1, ITERATOR_LIMIT):
                # Each cell of the simulation grid can hold multiple individuals. Therefore, we
                #       need to find the new size of each tile so we can fit them all in that cell.
                N = ceil(sqrt(max(1, len(sim_matrices[row][col]))))
                mini_tile_size = int(default_tile_size / N)
                # within each cell of the simulation grid there will be rows and cols
                mini_row = 0
                mini_col = 0
                # for each individual in this cell, paste the correct tile in
                for individual in sim_matrices[row][col]:
                    tile = self.tiles[individual.state_of_health].resize((mini_tile_size, mini_tile_size))
                    # if we've filled a row inside the cell, jump to the beginning of the next row
                    if mini_col == N:
                        mini_row += 1
                        mini_col = 0
                    # paste the tile representing the individual's state of health to the canvas
                    canvas_copy.paste(tile, \
                        box=((col-1)*default_tile_size + (mini_tile_size*mini_col), \
                            (row-1)*default_tile_size + (mini_tile_size*mini_row)))
                    mini_col += 1
        # save the changes made to the image
        canvas_copy.save(OUTPUT_FOLDER+"/final_sim_state.png", quality=95)
        # append the day's state to the list of day states
        self.images.append(canvas_copy)

    def finish_and_save_gif(self):
        # save the list of simulation images as a gif
        self.images[0].save(OUTPUT_FOLDER+'/simulation.gif', save_all=True, append_images=self.images[1:], \
            duration=200, loop=0)
        