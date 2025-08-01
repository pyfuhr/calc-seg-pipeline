from types import FunctionType
import ase.io
from pipeline.utils import get_atomicnum_from_specs
import numpy as np
from tqdm import tqdm
from pipeline.metabuilder import create_meta

def add_impurity(d, infile, imp_id, atomtypes, outfile):
    atoms = ase.io.read(f'project/{d["projname"]}/{infile}', format='lammps-data')
    atomic_numbers = get_atomicnum_from_specs(atomtypes)
    atnums = atoms.get_atomic_numbers()
    for i in imp_id:
        atnums[i] = atomic_numbers[1]
    atoms.set_atomic_numbers(atnums)
    atoms.write(f'project/{d["projname"]}/{outfile}', format='lammps-data')

def replace_and_minimize(d, infile, imp_id, minimize_func:FunctionType, potential, minimize_args, atomtypes, energy_file):
    "minimiz_func_args: d, infile, potential, atomtypes, outfile, energy_file, kwargs -> should return energy"
    add_impurity(infile, imp_id, atomtypes, 'tmp_imp_file')
    energy = minimize_func(d=d, infile='tmp_imp_file', potential=potential, atomtypes=atomtypes,
                           outfile='tmp_imp_file_min', energy_file=energy_file, **minimize_args)
    return energy

def calculate_spectra(d, infile, gb_file, atomtypes, base_energy, minimize_func:FunctionType, potential, minimize_args, outfile):
    create_meta(f'project/{d["projname"]}/{outfile}',
                    [f'project/{d["projname"]}/{gb_file}', f'project/{d["projname"]}/{base_energy}'],
                    f'calculate energy spectra. \nAtomtypes{atomtypes}\nFunction: {minimize_func}\nPotentail: {potential}'
                    f'\nOther args: {minimize_args}')
    enegries = []
    base_energy = np.loadtxt(base_energy)
    gblst = np.loadtxt(gb_file).astype(np.int32)
    for i in tqdm(gblst):
        energy = replace_and_minimize(d, infile, i, minimize_func, potential, minimize_args, atomtypes, 'tmpE')
        enegries.append(energy-base_energy)
        np.savetxt(f'project/{d["projname"]}/{outfile}', enegries)
    return enegries