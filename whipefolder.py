import os
import glob

def whipe_folder():
    files = glob.glob('images/*')
    for f in files:
        os.remove(f)