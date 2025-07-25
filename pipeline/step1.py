import os
from subprocess import Popen, PIPE
from glob import glob

def create_monocrystal(d, type, a, atomtypes, outfile, c=0): # TODO add nanotube
    # https://atomsk.univ-lille.fr/doc/en/mode_create.html
    latice_num = 0
    atomtypes_num = []
    if type in ['sc', 'bcc', 'CsCl', 'fcc', 'L12', 'L1_2',
                'fluorite', 'diamond', 'dia', 'zincblende', 'zb',
                'rocksalt', 'perovskite', 'per', 'A15', 'C15']: latice_num = 1
    else: latice_num = 2
    if type in ['sc', 'bcc', 'CsCl', 'fcc', 'diamond', 'dia', 'zincblende', 'zb',
                'st', 'bct', 'fct', 'L1_0', 'hcp', 'graphite']: atomtypes_num.append(1)
    if type in ['bcc', 'CsCl', 'fcc', 'L12', 'L1_2',
                'fluorite', 'diamond', 'dia', 'zincblende', 'zb',
                'rocksalt', 'A15', 'C15', 'bct', 'fct', 'L1_0', 
                'hcp', 'wurtzite', 'wz', 'graphite', 'BN', 'B12',
                'C14', 'C36']: atomtypes_num.append(2)
    if type in ['perovskite', 'per', ]: atomtypes_num.append(3)
    if latice_num == 2 and c == 0: raise Exception(f'not enough lattice constant to create {type}')
    if len(atomtypes) not in atomtypes_num: raise Exception(f'cant create {type} with this specs:{atomtypes}')
    if os.path.isfile(f'project/{d["projname"]}/{outfile}'):
        os.remove(f'project/{d["projname"]}/{outfile}')
    cmd = ['atomsk', '--create', type]
    cmd.append(str(a))
    if c: cmd.append(str(c))
    cmd.extend(atomtypes)
    cmd.append(f'project/{d["projname"]}/{outfile}')
    print("Run:", " ".join(cmd))
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    o, e = p.communicate()
    p.returncode

def create_polycrystal(d, x, y, z, grain_num, stamp_file, outfile):
    with open(f'project/{d["projname"]}/polycrystal_param.txt', 'w') as f:
        f.write(f'box {x} {y} {z}\nrandom {grain_num}')
    # atomsk --polycrystal fcc_unitcell.xsf voronoi_random.txt fcc_polycrystal.cfg lmp
    suffixes = ['_grains-com.xsf', '_id-size.txt', '_nodes.xsf', '_param.txt', '_size-dist.txt', '.'+outfile.rsplit('.', 1)[1]]
    for suffix in suffixes:
        if os.path.isfile(f"project/{d['projname']}/{outfile.rsplit('.', 1)[0]+suffix}"):
            os.remove(f'project/{d["projname"]}/{outfile.rsplit(".", 1)[0]+suffix}')
    cmd = ['atomsk', '--polycrystal']
    cmd.extend([f'project/{d["projname"]}/{stamp_file}', f'project/{d["projname"]}/polycrystal_param.txt'])
    cmd.append(f'project/{d["projname"]}/{outfile}')
    print("Run:", " ".join(cmd))
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    o, e = p.communicate()
    p.returncode

#create_monocrystal({'projname': 'test'}, 'graphite', 3.0, ['B', 'N'], 'bn.lmp', c=4.0)
#create_polycrystal({'projname': 'test'}, 100, 100, 100, 10, 'bn.lmp', 'bn_10nm.lmp')
# bin/atomsk/atomsk --polycrystal project/test/bn.lmp -box 100 100 100 -random 10
#print("finish")