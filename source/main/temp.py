from os import scandir
# from shutil import rmtree
# from imageio import get_writer, imread

OUTPUT_FOLDER = "./source/output"
temp_image_folder = OUTPUT_FOLDER+"/days/"

with get_writer(OUTPUT_FOLDER+'/simulation.gif', mode='I') as writer:
    for filename in scandir(temp_image_folder):
        print(filename.name)
        # image = imread(filename.name)
        # writer.append_data(image)
# rmtree(temp_image_folder)