from functions import *

def generate_list(end):
    return list(range(408001, end+1, 1000))

block_list = generate_list(750000)

for i in block_list:
    run(block_heigth=i,save_image=True)
    time.sleep(random.randint(0,1))

