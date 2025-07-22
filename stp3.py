#add impurity and calculate energy
debug = print

import os, multiprocessing
import ase.io
import ovito as ov
import numpy as np
from dscribe.descriptors.soap import SOAP
from tqdm import tqdm
from stp2 import reorder_crystal

q = multiprocessing.Queue()
projname = 'ag10nm'

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
    nparticles = len(select.array)
    gb_atoms_indices = []

    print(np.sum(select.array==1))
    print(nparticles)
    for index in range(nparticles):
        if int(select.array[index]) == int(1):
            gb_atoms_indices.append(index)
    return np.array(gb_atoms_indices)

def start_subcalc(id, system, cores, species, soap_cutoff, n_max, l_max, sigma, cnt:multiprocessing.Value) -> None:
    soap = SOAP(
        species=species,
        periodic=True,
        r_cut=soap_cutoff,
        n_max=n_max,
        l_max=l_max,
        sigma=sigma
    )
    global q
    if id==0:
        for i in tqdm(range(id, len(system), cores)):
            q.put((i, soap.create(system, centers=[i, ])[0]))
    else:
        for i in range(id, len(system), cores):
            q.put((i, soap.create(system, centers=[i, ])[0]))
    cnt.value -= 1

def get_soap_system(infile, soap_cutoff, n_max, l_max, atomic_number, atom_sigma=1, cores=4):
    pipeline = ov.io.import_file(f'project/{projname}/{infile}')
    data = pipeline.compute()
    system = ov.io.ase.ovito_to_ase(data)
    system.set_pbc([1,1,1])
    system.set_atomic_numbers(np.ones(len(system))*int(atomic_number))
    species = [atomic_number]
    procs = []
    global q
    cnt = multiprocessing.Value('d', 0)
    for i in range(cores):
        p = multiprocessing.Process(target=start_subcalc, args=(i, system, 
        cores, species, soap_cutoff, n_max, l_max, atom_sigma, cnt))
        p.start()
        procs.append(p)
        cnt.value += 1
    
    while cnt.value > 0:
        print('\r', cnt.value, end='\r')
        
    with open(f'project/{projname}/soap.lst', 'w') as f:
        while not q.empty():
            print('Entry left:', q.qsize(), end='\r')
            row = q.get()
            f.write(f'{row[0]} {" ".join(map(str, row[1]))}\n')

#print(get_soap_system('Ag_15nm_minimized.cfg', 6, 12, 12, 47, cores=54))