#minimize and to polycrystal
debug = print

from subprocess import Popen, PIPE
import os, glob, shutil

projname = 'ag10nm'
if not os.path.isdir(f'project/{projname}'):
    print('WARNING: proj doesnt exsist.')
else:
    if not input("Use this project (Yes/No(any))? ").lower().startswith('y'):
        exit()

def minimize_polycrystal(path_file_to_min:str, path_potential:str, specs:list[str], path_to_out:str, cores:int=4):
    with open('scripts/minimize', 'r') as fr:
        with open(f'project/{projname}/minimizelmp', 'w') as fw:
            src = fr.read()
            src = src.replace('<path_to_atoms>', f'project/{projname}/{path_file_to_min}')
            src = src.replace('<path_to_potential>', f'potentials/{path_potential}')
            src = src.replace('<specs>', f'{" ".join(specs)}')
            src = src.replace('<path_to_res>', f'project/{projname}/{path_to_out}')
            fw.write(src)
    p = Popen(["mpiexec", "--np", f"{cores}", "bin/lammps/bin/lmp", "-i", f"project/{projname}/minimizelmp"])
    o, e = p.communicate()

def thermal_annealing(path_file_to_ann:str, path_potential:str, specs:list[str], path_to_out:str,
                      init_temp, start_temp, stop_temp, end_temp, heat_time, ann_time, cool_time, cores:int=4):
    with open('scripts/thermal_an', 'r') as fr:
        with open(f'project/{projname}/thermal_an', 'w') as fw:
            src = fr.read()
            src = src.replace('<path_to_atoms>', f'project/{projname}/{path_file_to_ann}')
            src = src.replace('<path_to_potential>', f'potentials/{path_potential}')
            src = src.replace('<specs>', f'{" ".join(specs)}')

            src = src.replace('<init_temp>', f'{init_temp}')
            src = src.replace('<start_temp>', f'{start_temp}')
            src = src.replace('<stop_temp>', f'{stop_temp}')
            src = src.replace('<end_temp>', f'{end_temp}')
            src = src.replace('<heat_time>', f'{heat_time}')
            src = src.replace('<ann_time>', f'{ann_time}')
            src = src.replace('<cool_time>', f'{cool_time}')

            src = src.replace('<path_to_res>', f'project/{projname}/{path_to_out}')
            fw.write(src)
    p = Popen(["mpiexec", "--np", f"{cores}", "bin/lammps/bin/lmp", "-i", f"project/{projname}/thermal_an"])
    o, e = p.communicate()

#minimize_polycrystal('result.lmp', 'Ag-Ni.eam.fs', ['Ag'], 'result_min')
thermal_annealing('result_min', 'Ag-Ni.eam.fs', ['Ag'], 'result_ann', 0.1, 700, 700, 0.1, 20, 300, 30, cores=54)