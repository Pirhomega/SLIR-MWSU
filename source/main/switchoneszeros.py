from constants import GRID_SIZE
with open("C:/Users/Owner/Desktop/SLIR-MWSU/resources/terrain.txt", 'r') as input:
    with open("C:/Users/Owner/Desktop/SLIR-MWSU/resources/terrain1.txt", 'w') as output:
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                inputnum = input.read(1)
                if inputnum == '1':
                    output.write('0')
                elif inputnum == '0':
                    output.write('1')
                else:
                    output.write('\n')