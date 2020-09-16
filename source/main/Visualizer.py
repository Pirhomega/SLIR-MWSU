from constants import RESOURCES_FOLDER, OUTPUT_FOLDER, ITERATOR_LIMIT, GRID_SIZE
from math import ceil, sqrt
from PIL import Image
# from wand.image import Image

class Visualizer():
    def __init__(self):
        # open the background image to which we will paste the individuals' tiles,
        #       appending each modified image to `images`. `images` starts with a 
        #       defining image that will signifiy the beginning of the gif if looped
        #       infinitely
        self.canvas = Image.open(RESOURCES_FOLDER+"/bkgd.png")
        self.images = [Image.open(RESOURCES_FOLDER+"/beginning.png")]

    # each cell could be composed of an `NxN` grid to display all individuals in the spot. We will calculate the dimensions of the grid by
    # taking the square root of the number of individuals in the spot and taking the ceiling of the result. That value will be N.
    def visualize(self, sim_matrices):
        canvas_copy = self.canvas.copy()
        default_tile_size = ceil(1000/GRID_SIZE)
        for row in range(1, ITERATOR_LIMIT):
            for col in range(1, ITERATOR_LIMIT):
                N = ceil(sqrt(max(1, len(sim_matrices[row][col]))))
                mini_tile_size = int(default_tile_size / N)
                mini_row = 0
                mini_col = 0
                for individual in sim_matrices[row][col]:
                    tile = Image.open(RESOURCES_FOLDER+'/'+str(individual.state_of_health)+".png")
                    temp = tile.resize((mini_tile_size, mini_tile_size))
                    if mini_col == N:
                        mini_row += 1
                        mini_col = 0
                    # paste the tile representing the individual's state of health to the canvas
                    canvas_copy.paste(temp, \
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
        