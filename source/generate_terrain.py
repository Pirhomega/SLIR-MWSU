import pygame, sys

### YOU COULD ALSO FIND OUT HOW USERS CAN UNDO ALL EXITS ASSOCIATED WITH A PATCH WHEN THEY UNDO
###     A PATCH. THAT WAY, WHEN THEY DRAW A PATCH OVER A PREVIOUS EXIT, THE EXIT DOESN'T APPEAR
###     FOR THAT NEW PATCH.
### LASTLY, OUTPUT EXIT LOCATIONS AS A DICTIONARY FOR SIM_PARAMS.JSON

def populate_gridline_list(gridline_list, grid_x, grid_y, grid_factor_x, grid_factor_y):
    """
    Purpose:    Appends pygame rectangles to draw to the screen and form a grid
    Input:      `gridline_list`: a list to hold pygame rectangles
                `grid_x`: the number of columns in the simulation grid
                `grid_y`: the number of rows in the simulation grid
                `grid_factor_x`: the simulation grid cell width in number of pixels
                `grid_factor_y`: the simulation grid cell height in number of pixels
    Output:     `gridline_list`: a list filled with pygame rectangles
    """
    # create vertical and horizontal lines to display a `grid_x` by `grid_y` grid
    for col in range(grid_x):
        gridline_list.append(pygame.Rect(col*grid_factor_x, 0, 1, 1000))
    for row in range(grid_y):
        gridline_list.append(pygame.Rect(0, row*grid_factor_y, 1000, 1))
    return gridline_list

def create_terrain_grid(patches, exits, grid_x, grid_y, grid_factor_x, grid_factor_y):
    """
    Purpose:    Convert all patches and exits drawn in the pygame window into
                rectangles and opening in the rectangles in a .txt file
    Input:      `patches`: a list of pygame rectangles that represent enclosed
                locations of the terrain
                `exits`: a list of pygame rectangles that represent entrances
                `grid_x`: the number of columns in the simulation grid
                `grid_y`: the number of rows in the simulation grid
                `grid_factor_x`: the simulation grid cell width in number of pixels
                `grid_factor_y`: the simulation grid cell height in number of pixels
                and exits into and from the enclosed locations
    Output:     None
    """
    # create a 2D list of 1s to represent the simulation terrain
    terrain_grid = [([1] * grid_x) for _ in range(grid_y)]
    # represent the boundaries of the enclosed locations with zeros
    #   in the `terrain_grid` 2D list
    for patch_rect in patches:
        # graphics coordinates have are in the form (x,y) with (0,0)
        #   starting at the top left of the window. So, the terms
        #   'top' and 'bottom' refer to a 'y' value, and 'left' and
        #   'right' to an 'x' value
        top_y = int(patch_rect.top/grid_factor_y)
        left_x = int(patch_rect.left/grid_factor_x)
        bottom_y = int(patch_rect.bottom/grid_factor_y)
        right_x = int(patch_rect.right/grid_factor_x)
        # draw two horizontal lines of zeros to represent the top and bottom
        #   of the enclosed space
        for col in range(left_x,right_x+1):
            terrain_grid[top_y][col] = 0
            terrain_grid[bottom_y][col] = 0
        # draw two vertical lines of zeros to represent the left and right
        #   of the enclosed space
        for row in range(top_y, bottom_y+1):
            terrain_grid[row][left_x] = 0
            terrain_grid[row][right_x] = 0
    # draw the exits by filling in all values in each exit rectangle's bounds with 1's
    for exit_rect in exits:
        top_y = int(exit_rect.top/grid_factor_y)
        left_x = int(exit_rect.left/grid_factor_x)
        bottom_y = int(exit_rect.bottom/grid_factor_y)
        right_x = int(exit_rect.right/grid_factor_x)

        for col in range(left_x,right_x+1):
            for row in range(top_y, bottom_y+1):
                terrain_grid[row][col] = 1
    return terrain_grid

def output_to_file(grid_x, grid_y, terrain_grid):
    """
    Purpose:    Output `terrain_grid` to a .txt file
    Input:      `grid_x`: the number of columns in the simulation grid
                `grid_y`: the number of rows in the simulation grid
                `terrain_grid`: a 2D list of 1s and 0s
    Output:     None
    """
    # output `terrain_grid` to a file
    with open('./resources/terrain_temp.txt', 'w') as outfile:
        for row in range(grid_y):
            for col in range(grid_x):
                outfile.write(str(terrain_grid[row][col]))
            outfile.write('\n')

def main():
    pygame.init()
    running = True

    size = 1000,1000

    # these are the width and height of the simulation grid
    grid_x, grid_y = int(sys.argv[1]), int(sys.argv[2])
    # this is how many pixels per cell in the simulation grid
    #   We need to use the grid factor because the pygame window is not
    #   the same width and height of the simulation grid size. Therefore,
    #   we scale the pygame window down to fit the simulation size
    grid_factor_x, grid_factor_y = int(1000/grid_x), int(1000/grid_y)

    screen = pygame.display.set_mode(size)
    # used to track either the setting of the topleft of a rectangle,
    #   or the bottom right (if bottom right, the rectangle is completed)
    num_clicks_patch = 0
    num_clicks_patch_temp = 0
    num_clicks_exit = 0
    num_clicks_exit_temp = 0
    # the position of the mouse when the left or right mouse button is clicked
    mouse_pos_patch = ()
    mouse_pos_exit = ()
    # the position of the patch's top left corner in pixels
    patch_tl = ()
    # the position of the patch's bottom right corner in pixels
    patch_br = ()
    # the position of the exits's top left corner in pixels
    exit_tl = ()
    # the position of the exits's bottom right corner in pixels
    exit_br = ()
    # a list of patches as pygame rectangles that are being displayed
    #   on screen
    patch_list = []
    # a list of patches removed from the screen. The user can recall these
    #   with a keybind
    patch_discard_list = []
    # a list of exits as pygame rectangles that are being displayed
    #   on screen
    exit_list = []
    # a list of exits removed from the screen. The user can recall these
    #   with a keybind
    exit_discard_list = []
    # a list of 1 pixel-wide pygame rectangles that are drawn to the screen
    #   to create grid lines
    gridline_list = []

    # populate `gridline_list`
    gridline_list = populate_gridline_list(gridline_list, grid_x, grid_y, grid_factor_x, grid_factor_y)

    # main game loop will run until the user clicks the exit button in the top right corner (Windows)
    while running:
        # event loop
        for event in pygame.event.get():
            # if the user hits the window's exit button, stop the app
            if event.type == pygame.QUIT:
                running = False
            # if the user hits the mouse button in the app window
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_focused():
                # return a list of booleans for the three major buttons on a mouse:
                #   left mouse, right mouse, and middle mouse. If an element is True,
                #   the corresponding button is pressed
                mouse_depressed = pygame.mouse.get_pressed(num_buttons=3)
                # if the user clicks ONLY the left mouse button, they are creating
                #   a patch.
                if mouse_depressed[0] and not mouse_depressed[2]:
                    # get the mouse's position with respect to the window
                    mouse_pos_patch = pygame.mouse.get_pos()
                    num_clicks_patch += 1
                    num_clicks_patch_temp = num_clicks_patch
                # if the user clicks ONLY the right mouse button, they are creating
                #   an exit.
                if mouse_depressed[2] and not mouse_depressed[0]:
                    mouse_pos_exit = pygame.mouse.get_pos()
                    num_clicks_exit += 1
                    num_clicks_exit_temp = num_clicks_exit
            if event.type == pygame.KEYDOWN and pygame.key.get_focused():
                # return a list of booleans for all the keys on the keyboard
                #   If an element is True, the corresponding key is pressed
                keys_depressed = pygame.key.get_pressed()
                # if the user presses CTRL+Z, remove the previously added patches
                #   from most recent to least recent
                if keys_depressed[pygame.K_LCTRL] and keys_depressed[pygame.K_z] and not keys_depressed[pygame.K_LSHIFT]:
                    # if the user has begun to create a new patch, they can
                    #   cancel it by hitting CTRL+Z. Otherwise, CTRL+Z removes a
                    #   patch that has already been drawn
                    if patch_list and num_clicks_patch == 0:
                        patch_discard_list.append(patch_list.pop())
                        print("Number of patches:", len(patch_list))
                    else:
                        patch_tl = ()
                        num_clicks_patch = 0
                        num_clicks_patch_temp = 0
                        print("Undid patch topleft!")
                # if the user pressed CTRL+SHIFT+Z, remove the previously added exits
                #   from most recent to least recent
                elif keys_depressed[pygame.K_LSHIFT] and keys_depressed[pygame.K_LCTRL] and keys_depressed[pygame.K_z]:
                    # if the user has begun to create a new exit, they can
                    #   cancel it by hitting CTRL+SHIFT+Z. Otherwise, CTRL+SHIFT+Z removes a
                    #   exit that has already been drawn
                    if exit_list and num_clicks_exit == 0:
                        exit_discard_list.append(exit_list.pop())
                        print("Number of exits:", len(exit_list))
                    else:
                        exit_tl = ()
                        num_clicks_exit = 0
                        num_clicks_exit_temp = 0
                        print("Undid exit topleft!")
                # if the user presses CTRL+Y, restore the previously removed patch
                #   from the discard patch list from most recent to least recent
                if keys_depressed[pygame.K_LCTRL] and keys_depressed[pygame.K_y] and not keys_depressed[pygame.K_LSHIFT]:
                    # the user can only restore a deleted patch if they haven't
                    #   started drawing another one. Easy fix for this: press CTRL+Z
                    #   to undo the topleft of the already-begun patch, then do CTRL+Y
                    if patch_discard_list and num_clicks_patch == 0:
                        patch_list.append(patch_discard_list.pop())
                        print("Number of patches:", len(patch_list))
                # if the user pressed CTRL+SHIFT+Y, restore the previously removed exit
                #   from the discard exit list from most recent to least recent
                elif keys_depressed[pygame.K_LSHIFT] and keys_depressed[pygame.K_LCTRL] and keys_depressed[pygame.K_y]:
                    # the user can only restore a deleted exit if they haven't
                    #   started drawing another one. Easy fix for this: press CTRL+SHIFT+Z
                    #   to undo the topleft of the already-begun exit, then do CTRL+SHIFT+Y
                    if exit_discard_list and num_clicks_exit == 0:
                        exit_list.append(exit_discard_list.pop())
                        print("Number of exits:", len(exit_list))

        # if the user has clicked the mouse once, store the mouse position
        #   as the top left of the rectangle to be drawn
        if num_clicks_patch_temp == 1:
            patch_tl = mouse_pos_patch
            num_clicks_patch_temp = 0
            print("Patch topleft set at", patch_tl)
        # if the user has clicked the mouse for the second time, 
        elif num_clicks_patch_temp == 2:
            patch_br = mouse_pos_patch
            patch_list.append(pygame.Rect(patch_tl[0], patch_tl[1], patch_br[0]-patch_tl[0], patch_br[1]-patch_tl[1]))
            num_clicks_patch = 0
            num_clicks_patch_temp = 0
            print("Number of patches:", len(patch_list))
        
        # if the user has clicked the mouse once, store the mouse position
        #   as the top left of the rectangle to be drawn
        if num_clicks_exit_temp == 1:
            exit_tl = mouse_pos_exit
            num_clicks_exit_temp = 0
            print("Exit topleft set at", exit_tl)
        # if the user has clicked the mouse for the second time, 
        elif num_clicks_exit_temp == 2:
            exit_br = mouse_pos_exit
            exit_list.append(pygame.Rect(exit_tl[0], exit_tl[1], exit_br[0]-exit_tl[0], exit_br[1]-exit_tl[1]))
            num_clicks_exit = 0
            num_clicks_exit_temp = 0
            print("Number of exits:", len(exit_list))

        # first blacken the screen
        screen.fill("black")
        # draw the grid lines
        for gridline in gridline_list:
            pygame.draw.rect(screen, "blue", gridline)
        # draw the patches on top of the grid lines
        for patch in patch_list:
            pygame.draw.rect(screen, "white", patch, width=1)
        # then draw the exits over the grid lines and patches
        for exit in exit_list:
            pygame.draw.rect(screen, "red", exit)

        # this updates the contents of the surface
        pygame.display.flip()

        # if the user has clicked the exit button, ask them if they either want to create
        #   the terrain or completely exit the editor. Give them a second chance if they
        #   want to quit. That way they don't accidentally lose their progress.
        if not running:
            response = input("Would you like to create the terrain with this model? (y/n) ")
            if response == 'y':
                # create the terrain grid from the rectangles drawn in the pygame window
                terrain_grid = create_terrain_grid(patch_list, exit_list, grid_x, grid_y, grid_factor_x, grid_factor_y)
                # draw converted rectangles to the .txt file
                output_to_file(grid_x, grid_y, terrain_grid)
            elif response == 'n':
                second_response = input("Are you sure? (Y/N) ")
                if second_response == "Y":
                    print("Quitting terrain editor.")
                elif second_response == "N":
                    running = True
                    print("Continuing terrain editor.")
                else:
                    running = True
                    print("Invalid response ('Y' or 'N' only, please). Continuing terrain editor.")
            else:
                running = True
                print("Invalid response ('y' or 'n' only, please). Continuing terrain editor.")
    pygame.quit()

if __name__ == "__main__":
    main()