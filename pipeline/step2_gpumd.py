import string
from subprocess import Popen, PIPE
from random import choice
from string import ascii_lowercase, digits
import os
from pipeline.step2 import convert_format
import shutil
import re
import pandas as pd
from pipeline.metabuilder import create_meta

def get_last_energy(d, path, en_file):
    fpath = os.path.join(f"project/{d['projname']}/{path}", 'thermo.out')
    df = pd.read_csv(fpath, sep=r'\s+', header=None, usecols=[0, 1, 2],names=['T', 'Ek', 'Ep'])
    energy = df['Ep'].iloc[-1]
    with open(f"project/{d['projname']}/{en_file}", 'w') as f:
        f.write(str(float(energy)))
    return float(energy)

def make_orthogonal(d, infile):
    with open(f"project/{d['projname']}/{infile}", 'r') as f:
        data = f.read()
    s = re.search(r"Lattice=.([\-\d\\.]+\s?){9}.", data).group()
    s = s.split('=')[-1].replace('\"', '').split(' ')
    sarr = [s[0], 0, 0, 0, s[4], 0, 0, 0, s[8]]
    sstr = 'Lattice=\"' + ' '.join(map(str, sarr)) + '\"'
    data = re.sub(r"Lattice=.([\-\d\\.]+\s?){9}.", sstr, data)
    with open(f"project/{d['projname']}/{infile}", 'w') as f:
        f.write(data)

def relax_polycrystal(d, infile, intype, potential, atomtypes, init_temp, start_temp, stop_temp, 
                      end_temp, heat_time, relax_time, cool_time, elastic_mod, outfile, tmp_name=False):
    'elastic modulus in GPa (for silver its 83)'
    create_meta(f'project/{d["projname"]}/{outfile}',
                    [f'project/{d["projname"]}/{infile}', ],
                    f'Thermal relaxing using gpumd\nPotential: {potential}'
                    f'Atomtypes: from exyz file\nTemperatures: {(init_temp, start_temp, stop_temp, end_temp)}'
                    f'Time(heating, relaxing, cooling): {(heat_time, relax_time, cool_time)}\nElastic modulus: {elastic_mod}')    
    # atomtypes
    with open('scripts/thermal_an_gpumd', 'r') as fr:
        dfile = {}
        symbols = digits+ascii_lowercase
        if tmp_name:
            path = tmp_name
        else:
            path = ''.join([choice(symbols) for i in range(10)])
        if os.path.isdir(f"project/{d['projname']}/{path}"): shutil.rmtree(f"project/{d['projname']}/{path}")
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
        convert_format(d, infile, intype, f'{path}/model.xyz', 'extxyz')
    os.chdir(f"project/{d['projname']}/{path}")
    print("New path:", path)
    p = Popen(["gpumd", ])
    p.wait()
    os.chdir('../../..')
    shutil.copyfile(f"project/{d['projname']}/{path}/dump.xyz", f"project/{d['projname']}/{outfile}")

def minimize_polycrystal(d, infile, intype, potential, atomtypes, outfile, energy_file, minimize_vol=False, tmp_name=False):
    create_meta(f'project/{d["projname"]}/{outfile}',
                    [f'project/{d["projname"]}/{infile}', ],
                    f'Minimize polycrystal using lammps\nPotential: {potential}'
                    f'Atomtypes: from exyz file\nEnergy stored to {energy_file}\nMinimize volume:{minimize_vol}')
    symbols = digits+ascii_lowercase
    if tmp_name:
        path = tmp_name
    else:
        path = ''.join([choice(symbols) for i in range(10)])
    if os.path.isdir(f"project/{d['projname']}/{path}"): shutil.rmtree(f"project/{d['projname']}/{path}")
    os.mkdir(f"project/{d['projname']}/{path}")
    shutil.copyfile(f"potentials/{potential}", f"project/{d['projname']}/{path}/{potential}")
    convert_format(d, infile, intype, f'{path}/model.xyz', 'extxyz')
    with open('scripts/minimize_gpumd', 'r') as fr:
        with open(f"project/{d['projname']}/{path}/run.in", 'w') as fw:
            src = string.Template(fr.read())
            dfile = {'potential': f'{potential}'}
            dfile['minvol'] = ('1' if minimize_vol else '')
            fw.write(src.safe_substitute(dfile))
        os.chdir(f"project/{d['projname']}/{path}")
    print("New path:", path)
    p = Popen(["gpumd", ])
    p.wait()
    os.chdir('../../..')
    shutil.copyfile(f"project/{d['projname']}/{path}/dump.xyz", f"project/{d['projname']}/{outfile}")
    return get_last_energy(d, path, energy_file)

#convert_format2({'projname': 'test'}, 'result_min', 'res.xyz')
#relax_polycrystal({'projname': 'test'}, 'res.xyz', 'Unep1.txt', None, 0,  700, 700, 0, int(1e6), int(1e7), int(1e6))

