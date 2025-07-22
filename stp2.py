#minimize and to polycrystal
debug = print

from subprocess import Popen, PIPE
import os
import ovito as ov
import ovito.io

projname = 'ag10nm'
print(f'Using proj "{projname}"')
if not os.path.isdir(f'project/{projname}'):
    print('WARNING: proj doesnt exsist.')
    exit()

def reorder_crystal(infile, outfile):
    system = ovito.io.import_file(f"project/{projname}/{infile}", sort_particles=True)
    ovito.io.export_file(system, f"project/{projname}/{outfile}", "lammps/data")

def minimize_polycrystal(path_file_to_min:str, path_potential:str, specs:list[str], path_to_out:str, 
                         masses:list[int]=[108, 59], cores:int=4):
    with open('scripts/minimize', 'r') as fr:
        with open(f'project/{projname}/minimizelmp', 'w') as fw:
            src = fr.read()
            src = src.replace('<path_to_atoms>', f'project/{projname}/{path_file_to_min}')
            src = src.replace('<path_to_potential>', f'potentials/{path_potential}')
            src = src.replace('<path_to_dump>', f'project/{projname}/dump')
            src = src.replace('<specs>', f'{" ".join(specs)}')
            src = src.replace('<path_to_res>', f'project/{projname}/{path_to_out}')
            src = src.replace('<mass>', f'{"\n".join([f"mass {i+1} {mass}" for i, mass in enumerate(masses)])}')
            fw.write(src)
    p = Popen(["mpiexec", "--np", f"{cores}", "bin/lammps/bin/lmp", "-i", f"project/{projname}/minimizelmp"])
    o, e = p.communicate()
    with open('out.lmp', 'r') as f:
        energy = float(f.read().split('\n')[-2].split(' = ')[-1])
    return energy

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
    return f"project/{projname}/thermal_an"