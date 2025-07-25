import string
from subprocess import Popen, PIPE
from random import choice
from string import ascii_lowercase, digits
import os
from pipeline.step2 import convert_format
import shutil

def relax_polycrystal(d, infile, potential, atomtypes, init_temp, start_temp, stop_temp, 
                      end_temp, heat_time, relax_time, cool_time, elastic_mod, outfile):
    'elastic modulus in GPa (for silver its 83)'
    # atomtypes
    with open('scripts/thermal_an_gpumd', 'r') as fr:
        dfile = {}
        symbols = digits+ascii_lowercase
        path = ''.join([choice(symbols) for i in range(10)])
        os.mkdir(f"project/{d['projname']}/{path}")
        with open(f"project/{d['projname']}/{path}/run.in", 'w') as fw:
            shutil.copyfile(f"potentials/{potential}", f"project/{d['projname']}/{path}/{potential}")
            src = string.Template(fr.read())
            #infile = f'project/{d['projname']}/{infile}'
            dfile['elastic_mod'] = f'{elastic_mod}'
            dfile['potential'] = f'{potential}'
            dfile['init_temp'] = str(init_temp)
            dfile['start_temp'] = str(start_temp)
            dfile['stop_temp'] = str(stop_temp)
            dfile['end_temp'] = str(end_temp)
            dfile['heat_time'] = str(heat_time)
            dfile['relax_time'] = str(relax_time)
            dfile['cool_time'] = str(cool_time)
            fw.write(src.safe_substitute(dfile))
        convert_format(d, infile, 'lammps-data', f'{path}/model.xyz', 'extxyz')
    os.chdir(f"project/{d['projname']}/{path}")
    print("New path:", path)
    p = Popen(["gpumd", ], stdout=PIPE, stderr=PIPE)
    o, e = p.communicate()
#convert_format2({'projname': 'test'}, 'result_min', 'res.xyz')
#relax_polycrystal({'projname': 'test'}, 'res.xyz', 'Unep1.txt', None, 0,  700, 700, 0, int(1e6), int(1e7), int(1e6))