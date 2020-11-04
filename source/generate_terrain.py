import pygame, sys

### NEXT ORDER OF BUSINESS IF TO FIND OUT WHY THE PATCHES DON'T PRINT TO THE OUTFILE ENTIRELY
### YOU COULD ALSO FIND OUT HOW USERS CAN UNDO ALL EXITS ASSOCIATED WITH A PATCH WHEN THEY UNDO
###     A PATCH. THAT WAY, WHEN THEY DRAW A PATCH OVER A PREVIOUS EXIT, THE EXIT DOESN'T APPEAR
###     FOR THAT NEW PATCH.
### LASTLY, OUTPUT EXIT LOCATIONS AS A DICTIONARY FOR SIM_PARAMS.JSON

def create_text(patches, exits):
    grid_y, grid_x = int(sys.argv[1]), int(sys.argv[2])
    terrain_grid = [([1] * grid_x) for _ in range(grid_y)]
    grid_factor_x, grid_factor_y = int(1000/grid_y), int(1000/grid_x)
    for patch_rect in patches:
        top_y = int(patch_rect.top/grid_factor_y)
        left_x = int(patch_rect.left/grid_factor_x)
        bottom_y = int(patch_rect.bottom/grid_factor_y)
        right_x = int(patch_rect.right/grid_factor_x)

        for col in range(left_x,right_x+1):
            terrain_grid[top_y][col] = 0
            terrain_grid[bottom_y][col] = 0
            
        for row in range(top_y, bottom_y+1):
            terrain_grid[row][left_x] = 0
            terrain_grid[row][right_x] = 0
    for exit_rect in exits:
        top_y = int(exit_rect.top/grid_factor_y)
        left_x = int(exit_rect.left/grid_factor_x)
        bottom_y = int(exit_rect.bottom/grid_factor_y)
        right_x = int(exit_rect.right/grid_factor_x)

        for col in range(left_x,right_x+1):
            for row in range(top_y, bottom_y+1):
                terrain_grid[row][col] = 1

    with open('./resources/terrain_temp.txt', 'w') as outfile:
        for row in range(grid_y):
            for col in range(grid_x):
                outfile.write(str(terrain_grid[row][col]))
            outfile.write('\n')


def main():
    pygame.init()
    running = True

    size = 1000,1000

    screen = pygame.display.set_mode(size)
    num_clicks_patch = 0
    num_clicks_exit = 0
    mouse_pos_patch = ()
    mouse_pos_exit = ()
    patch_tl = ()
    patch_br = ()
    exit_tl = ()
    exit_br = ()
    patch_list = []
    exit_list = []

    while running:
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
                # if the user clicks ONLY the right mouse button, they are creating
                #   an exit.
                if mouse_depressed[2] and not mouse_depressed[0]:
                    mouse_pos_exit = pygame.mouse.get_pos()
                    num_clicks_exit += 1
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
                        patch_list.pop()
                    else:
                        patch_tl = ()
                        num_clicks_patch = 0
                if keys_depressed[pygame.K_LSHIFT] and keys_depressed[pygame.K_LCTRL] and keys_depressed[pygame.K_z]:
                    # if the user has begun to create a new exit, they can
                    #   cancel it by hitting CTRL+SHIFT+Z. Otherwise, CTRL+SHIFT+Z removes a
                    #   exit that has already been drawn
                    if exit_list and num_clicks_exit == 0:
                        exit_list.pop()
                    else:
                        exit_tl = ()
                        num_clicks_exit = 0

        # if the user has clicked the mouse once, store the mouse position
        #   as the top left of the rectangle to be drawn
        if num_clicks_patch == 1:
            patch_tl = mouse_pos_patch
        # if the user has clicked the mouse for the second time, 
        elif num_clicks_patch == 2:
            patch_br = mouse_pos_patch
            patch_list.append(pygame.Rect(patch_tl[0], patch_tl[1], patch_br[0]-patch_tl[0], patch_br[1]-patch_tl[1]))
            num_clicks_patch = 0
        
        # if the user has clicked the mouse once, store the mouse position
        #   as the top left of the rectangle to be drawn
        if num_clicks_exit == 1:
            exit_tl = mouse_pos_exit
        # if the user has clicked the mouse for the second time, 
        elif num_clicks_exit == 2:
            exit_br = mouse_pos_exit
            exit_list.append(pygame.Rect(exit_tl[0], exit_tl[1], exit_br[0]-exit_tl[0], exit_br[1]-exit_tl[1]))
            num_clicks_exit = 0

        screen.fill("black")
        for patch in patch_list:
            pygame.draw.rect(screen, "white", patch, width=1)
        for exit in exit_list:
            pygame.draw.rect(screen, "black", exit)

        
        pygame.display.flip()
    pygame.quit()
    create_text(patch_list, exit_list)


if __name__ == "__main__":
    main()