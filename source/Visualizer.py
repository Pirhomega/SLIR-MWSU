from math import ceil, sqrt
from os import mkdir, path
from shutil import rmtree
from PIL import Image
from imageio import get_writer, imread
from constants import DISEASE_LIST, RESOURCES_FOLDER, OUTPUT_FOLDER, ITERATOR_LIMIT, GRID_SIZE

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
        # open the background image to which we will paste the individuals' tiles,
        #       appending each modified image to `images`. `images` starts with a 
        #       defining image that will signifiy the beginning of the gif if looped
        #       infinitely
        self.canvas = Image.open(RESOURCES_FOLDER+"bkgd.png")
        self.canvas_ind = Image.open(RESOURCES_FOLDER+"bkgd_ind.png")
        # self.images = [Image.open(RESOURCES_FOLDER+"/beginning.png")]
        self.tiles = [Image.open(RESOURCES_FOLDER+"0.png"),
                        Image.open(RESOURCES_FOLDER+"1.png"),
                        Image.open(RESOURCES_FOLDER+"2.png"),
                        Image.open(RESOURCES_FOLDER+"3.png"),
                        Image.open(RESOURCES_FOLDER+"4.png")]
        self.image_num = 0
        self.temp_image_folder = OUTPUT_FOLDER+"days/"
        if path.isdir(OUTPUT_FOLDER+"days/"):
            rmtree(self.temp_image_folder)
        mkdir(self.temp_image_folder)

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

    def __generate_tile(self, state_of_health):
        # within each cell of the simulation grid there will be rows and cols
        mini_row = 0
        mini_col = 0
        N = ceil(sqrt(max(1, len(DISEASE_LIST))))
        mini_disease_tile_size = (1 / N) * 250
        copy_canvas_ind = self.canvas_ind.copy()
        for row in range(N):
            for col in range(N):
                for disease in range(len(DISEASE_LIST)):
                    tile = self.tiles[state_of_health].resize((mini_disease_tile_size, mini_disease_tile_size))
                    # if we've filled a row inside the cell, jump to the beginning of the next row
                    if mini_col == N:
                        mini_row += 1
                        mini_col = 0
                    # paste the tile representing the individual's state of health to the canvas
                    copy_canvas_ind.paste(tile, \
                        box=(col*mini_disease_tile_size, row*mini_disease_tile_size))
                    mini_col += 1
        return copy_canvas_ind

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

    def visualize(self, sim_grid):
        """
        Purpose:    Save the simulation state as a .png, where individuals are represented
                    as colored tiles and the colors reflect the state of health of an
                    individual
        Input:      `sim_grid`: a copy of the entire simulation grid
        Output:     None
        """
        # we don't want to make any changes to the base canvas, which is a black square image.
        #       If we didn't make a copy to modify, the state from the day before would be visible
        #       on the following day (i.e. not good)
        canvas_copy = self.canvas.copy()
        # calculate how large a tile should be in pixels to fit GRID_SIZE times GRID_SIZE
        #       of them in the simulation grid
        default_tile_size = ceil(5000/GRID_SIZE)
        # loop through entire effective area of simulation grid and form the state image
        for row in range(1, ITERATOR_LIMIT):
            for col in range(1, ITERATOR_LIMIT):
                # Each cell of the simulation grid can hold multiple individuals. Therefore, we
                #       need to find the new size of each tile so we can fit them all in that cell.
                #       Each cell could be composed of an `NxN` grid to display all individuals in the 
                #       spot. We will calculate the dimensions of the grid by taking the square root 
                #       of the number of individuals in the spot and taking the ceiling of the result. 
                #       That value will be N.
                N = ceil(sqrt(max(1, len(sim_grid[row][col]))))
                mini_tile_size = int(default_tile_size / N)
                # within each cell of the simulation grid there will be rows and cols
                mini_row = 0
                mini_col = 0
                # for each individual in this cell, paste the correct tile in
                for individual in sim_grid[row][col]:
                    tile = self.__generate_tile(individual.state_of_health, mini_tile_size)
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
        canvas_copy.save(OUTPUT_FOLDER+"/days/"+str(self.image_num)+".png", quality=95)
        self.image_num += 1

    def finish_and_save_gif(self, num_days):
        # save the list of simulation images as a gif
        with get_writer(OUTPUT_FOLDER+'/simulation.gif', mode='I') as writer:
            image = imread(RESOURCES_FOLDER+'/beginning.png')
            writer.append_data(image)
            for filename in range(num_days):
                image = imread(self.temp_image_folder+str(filename)+'.png')
                writer.append_data(image)
                print("Processed day", filename, end='\r', flush=True)
        rmtree(self.temp_image_folder)
