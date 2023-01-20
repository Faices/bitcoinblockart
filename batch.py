from functions import *

def generate_list(end):
    return list(range(500000, end+1, 1000))

block_list = generate_list(550000)

print("Start Programm:")
for i in block_list:
    run(save_image_jpg = False, save_image_svg = True, post_instagram = False, block_heigth = i)
    time.sleep(random.randint(0,1))
print("End Programm:")
