from pipeline.step4 import replace_and_minimize
import numpy as np
from tqdm import tqdm
from types import FunctionType

def calculate_wspectra(d, infile, pairs_file, atomtypes, base_energy, minimize_func:FunctionType, potential, minimize_args, outfile):
    enegries = []
    base_energy = np.loadtxt(base_energy)
    pairs = np.loadtxt(pairs_file)
    for i in tqdm(pairs):
        energy = replace_and_minimize(d, infile, i, minimize_func, potential, minimize_args, atomtypes, 'tmpE')
        enegries.append(energy-base_energy)
        np.savetxt(f'project/{d["projname"]}/{outfile}', enegries)
    return enegries