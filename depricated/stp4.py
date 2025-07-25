# calculate energy

from stp2 import minimize_polycrystal
import os
from tqdm import tqdm
import ase.io

def add_impurity(infile, atom_id, impuriy_atnum, outfile):
    print(f'project/{projname}/{infile}')
    atoms = ase.io.read(f'project/{projname}/{infile}', format='lammps-data')
    atnums = atoms.get_atomic_numbers()
    atnums[atom_id] = impuriy_atnum
    atoms.set_atomic_numbers(atnums)
    atoms.write(f'project/{projname}/{outfile}', format='lammps-data')

def replace_atom_and_minimize(infile, imp_id,  impat_num2, cores=4):
    add_impurity(infile, imp_id, impat_num2, 'replim')
    energy = minimize_polycrystal('replim', 'Ag-Ni.eam.fs', ['Ag', 'Ni'], 'replim_min', cores=cores)
    #here magic where i get potential energy (TODO)
    return energy

def calculate_spectra(infile, gblst, impat2_num, base_energy, cores=4) -> list[int]:
    enegries = []
    for i in tqdm(gblst):
        energy = replace_atom_and_minimize(infile, i, impat2_num, cores=cores)
        enegries.append(energy-base_energy)

    return enegries