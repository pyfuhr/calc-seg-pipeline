#add inpurity and calculate energy
debug = print

from subprocess import Popen, PIPE
import os, glob
from ase import Atoms
import ase.io
import ovito as ov
import numpy as np
from dscribe.descriptors.soap import SOAP
from tqdm import tqdm

projname = 'ag15nm'
if not os.path.isdir(f'project/{projname}'):
    print('WARNING: proj doesnt exsist.')
else:
    if not input("Use this project (Yes/No(any))? ").lower().startswith('y'):
        exit()

def get_gb_ids_and_indices(polycrystal):
    node = ov.io.import_file(f'project/{projname}/{polycrystal}')
    fixed_mode = ov.modifiers.CommonNeighborAnalysisModifier.Mode.FixedCutoff
    cutoff = 3.5
    modifier1 = ov.modifiers.CommonNeighborAnalysisModifier(mode=fixed_mode, cutoff=cutoff)
    node.modifiers.append(modifier1)
    data = node.compute()

    types = [0,2,3,4]
    counts = []
    for t in types:
        node.modifiers.append(ov.modifiers.ExpressionSelectionModifier(expression="StructureType == %i"%(t)))
        data = node.compute()
        select = data.particles['Selection']
        counts.append(len(select.array[select.array == 1]))

    node.modifiers.append(ov.modifiers.ExpressionSelectionModifier(expression="StructureType != %i"%(1)))
    data = node.compute()
    select = data.particles['Selection']
    pid = data.particles['Particle Identifier']
    nparticles = len(pid.array)
    gb_atoms_ids = []
    gb_atoms_indices = []

    print(np.sum(select.array==1))
    print(nparticles)
    for index in range(nparticles):
        if int(select.array[index]) == int(1):
            gb_atoms_ids.append(pid.array[index])
            gb_atoms_indices.append(index)
    return np.array(gb_atoms_ids), np.array(gb_atoms_indices)

def add_inpurity(infile, atom_id, inpuriy_atnum, outfile):
    atoms = ase.io.read(f'project/{projname}/{infile}')
    atnums = atoms.get_atomic_numbers()
    atnums[atom_id] = inpuriy_atnum
    atoms.set_atomic_numbers(atnums)
    atoms.write(f'project/{projname}/{outfile}')

def get_soap_system(infile, soap_cutoff, n_max, l_max, atomic_number, atom_sigma=1):
    #system = ase.io.read(converted_dump_file, format=converted_format)
    pipeline = ov.io.import_file(infile)
    data = pipeline.compute()
    system = ov.io.ase.ovito_to_ase(data)
    system.set_pbc([1,1,1])
    system.set_atomic_numbers(np.ones(len(system))*int(atomic_number))
    species = [atomic_number]
    #===============================
    #desc = SOAP("soap cutoff=%.2f l_max=%i n_max=%i atom_sigma=%.2f n_Z=1 Z={%i} normalise=F"%(soap_cutoff, l_max, n_max, atom_sigma, atomic_number))
    soap = SOAP(
    species=species,
    periodic=True,
    r_cut=soap_cutoff,
    n_max=n_max,
    l_max=l_max,
    sigma=atom_sigma
)
    #===============================
    #soap_arr = desc.calc_descriptor(system)
    soap_arr = []
    for i in tqdm(range(len(system))):
        soap_arr.append(soap.create(system, centers=[i, ])[0])
    return soap_arr

print(get_gb_ids_and_indices('result_min'))
