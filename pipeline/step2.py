import ovito.io
from subprocess import Popen, PIPE
import ase.io
import string
from utils import get_masses_from_specs

def reorder_index(d, infile, outfile):
    system = ovito.io.import_file(f"project/{d['projname']}/{infile}", sort_particles=True)
    ovito.io.export_file(system, f"project/{d['projname']}/{outfile}", "lammps/data")

def convert_format(d, infile, informat=None, outfile=None, outformat=None):
    system = ase.io.read(f"project/{d['projname']}/{infile}", format=informat)
    system.write(f"project/{d['projname']}/{outfile}", outformat)

def convert_format2(d, infile, outfile):
    cmd = ['atomsk', f"project/{d['projname']}/{infile}", f"project/{d['projname']}/{outfile}"]
    print("Run:", " ".join(cmd))
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    o, e = p.communicate()
    p.returncode

def minimize_polycrystal(d, infile, protential_type, potential, atomtypes, outfile, energy_file):
    with open('scripts/minimize_v2', 'r') as fr:
        with open(f'project/{d['projname']}/minimizelmp', 'w') as fw:
            src = string.Template(fr.read())
            dfile = {'infile': f'project/{d['projname']}/{infile}'}
            dfile['masses'] = "\n".join([f"mass {i+1} {mass}" for i, mass in enumerate(get_masses_from_specs(atomtypes))])
            dfile['potential_type'] = protential_type
            dfile['potential'] = f'potentials/{potential}'
            dfile['atom_specs'] = " ".join(atomtypes)
            dfile['energy_outfile'] = f'project/{d['projname']}/{energy_file}'
            dfile['outfile'] = f'project/{d['projname']}/{outfile}'
            fw.write(src.safe_substitute(dfile))
    p = Popen(["mpiexec", "--np", f"{d['cores']}", "bin/lammps/bin/lmp", "-i", f"project/{d['projname']}/minimizelmp"])
    o, e = p.communicate()
    with open(f"project/{d['projname']}/{energy_file}", 'r') as f:
        energy = float(f.read().split('\n')[-2].split(' = ')[-1])
    return energy

def relax_polycrystal(d, infile, protential_type, potential, atomtypes, init_temp, start_temp, stop_temp, 
                      end_temp, heat_time, relax_time, cool_time, outfile):
    with open('scripts/thermal_an_v2', 'r') as fr:
        with open(f'project/{d['projname']}/thermal_an', 'w') as fw:
            src = string.Template(fr.read())
            dfile = {'infile': f'project/{d['projname']}/{infile}'}
            dfile['masses'] = "\n".join([f"mass {i+1} {mass}" for i, mass in enumerate(get_masses_from_specs(atomtypes))])
            dfile['potential_type'] = protential_type
            dfile['potential'] = f'potentials/{potential}'
            dfile['atom_specs'] = " ".join(atomtypes)
            dfile['init_temp'] = str(init_temp)
            dfile['start_temp'] = str(start_temp)
            dfile['stop_temp'] = str(stop_temp)
            dfile['end_temp'] = str(end_temp)
            dfile['heat_time'] = str(heat_time)
            dfile['relax_time'] = str(relax_time)
            dfile['cool_time'] = str(cool_time)
            dfile['outfile'] = f'project/{d['projname']}/{outfile}'
            fw.write(src.safe_substitute(dfile))
    p = Popen(["mpiexec", "--np", f"{d['cores']}", "bin/lammps/bin/lmp", "-i", f"project/{d['projname']}/thermal_an"])
    o, e = p.communicate()