'''
Create the seed file pwgseeds.dat for a given number of batches and given processes, which is needed for running POWHEG with the manyseedsflag 
'''

import sys
import os
import random
import string

def make_seeds(nbatches, run_dir):
    seed_file = os.path.join(run_dir, "pwgseeds.dat")
    make_seeds = True
    if os.path.exists(seed_file):
        print(f"A seed file already exists in your run directory - do you want to regenerate the seeds for your current run?")
        choice = input("y/n ")
        if choice[0].lower() == "y":
            os.remove(seed_file)
        else:
            make_seeds = False

    if not make_seeds:
        # check that enough seeds are available if not regenerated
        with open(seed_file, "r") as f:
            n_seeds = len(f.readlines())
        if n_seeds >= nbatches:
            return seed_file
        else:
            print(f"Not enough seeds in the current seed file, aborting.")
            exit()

    if make_seeds:
        print(f"Regenerating {nbatches} seeds...")
        with open(seed_file, "w") as f:
            for i in range(nbatches):
                f.write(f"{random.randint(0, 99999999)}\n")
        return seed_file
    
