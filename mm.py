import multiprocessing 
from dscribe.descriptors.soap import SOAP
import pandas as pd
from sklearn.decomposition import PCA
import ovito as ov
import numpy as np
from dscribe.descriptors.soap import SOAP
from tqdm import tqdm
from time import sleep
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

def subcall2(i):
    print("start", i)
    return i

d={'projname': 'Nt', "cores": 20, "specs": ["Ag", "Ni"]}
infile="Ag_10nm_min2.lmp"
soap_cutoff=6.0
n_max=12
l_max=12
sigma=1
atomtypes=False
outfile="soap.lst"
cores = False
'''first - spec of matrix, second - spec of impurity'''
pipeline = ov.io.import_file(f'project/{d["projname"]}/{infile}')
del pipeline

print(1)
with multiprocessing.Pool(processes=20) as pool:
    print(2)
    y = [i for i in range(100)]
    # (i, system, species, soap_cutoff, n_max, l_max, sigma):
    x = pool.map(subcall2, y)
        
with open(f"project/{d['projname']}/{outfile}", 'w') as f:
    while not q_step3 .empty():
        print('Entry left:', q_step3.qsize(), end='\r')
        row = q_step3 .get()
        f.write(f'{row[0]} {" ".join(map(str, row[1]))}\n')