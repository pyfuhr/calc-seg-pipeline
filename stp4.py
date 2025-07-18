# calculate energy

from subprocess import Popen, PIPE
from stp2 import minimize_polycrystal
from stp3 import add_impurity

projname = 'ag10nm'
print(f'Using proj "{projname}"')
if not os.path.isdir(f'project/{projname}'):
    print('WARNING: proj doesnt exsist.')
    exit()
else:
    if not input("Use this project (Yes/No(any))? ").lower().startswith('y'):
        exit()

def replace_atom_and_minimize(infile, imp_id,  impat_num2):
    add_impurity(infile, imp_id, impat_num2, 'replim', projnm=projname)
    minimize_polycrystal('replim', 'Ag-Ni.eam.fs', ['Ag', 'Ni'], 'replim_min')
    #here magic where i get potential energy (TODO)
    energy = 0
    return energy

def calculate_spectra(infile, gb_file, impat2_num, base_energy):
    enegries = []
    with open(f'project/{projname}/{gb_file}', 'r') as f:
        gbs = [int(i.rstrip()) for i in f.readlines()]
    for i in gbs:
        energy = replace_atom_and_minimize(infile, i, impat2_num)
        enegries.append(energy-base_energy)

