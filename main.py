import os

projname = 'ag10nm'
print(f'Using proj "{projname}"')
if not os.path.isdir(f'project/{projname}'):
    print('WARNING: proj doesnt exsist.')
    exit()

import stp1, stp2, stp3, stp4, stp5

'''s1 = create_monocrystal()
print(s1)
s2 = create_voronoi(s1)
print(s2)'''

'''s1 = stp2.minimize_polycrystal('result.lmp', 'Ag-Ni.eam.fs', ['Ag'], 'result_min', cores=54)
print(s1)
'''
s2 = stp2.thermal_annealing('result_min', 'Ag-Ni.eam.fs', ['Ag'], 'result_ann', 0.1, 700, 700, 0.1, 100000, 1000000, 100000, cores=27)
print(s2)
'''

stp3.reorder_crystal('result_min', 'reord_min')
gb_ids = stp3.get_gb_ids_and_indices('reord_min')
base_energy = stp2.minimize_polycrystal('reord_min', 'Ag-Ni.eam.fs', ['Ag'], 'reord_min', masses=[108, ], cores=54)
spectra = stp4.calculate_spectra('reord_min', gb_ids[:10], 28, base_energy, cores=54)
print(spectra)
'''