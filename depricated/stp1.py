#generate polycrystal
debug = print

from subprocess import Popen, PIPE
import os, glob

def create_monocrystal(type:str='fcc', a:int=4.08, spec:str='Ag'):
    # https://atomsk.univ-lille.fr/doc/en/mode_create.html
    if os.path.isfile(f'project/{projname}/{spec}_mono.xsf'):
        os.remove(f'project/{projname}/{spec}_mono.xsf')
    p = Popen(['bin/atomsk/atomsk', '--create', type, str(a), spec, f'project/{projname}/result_mono.xsf'], stdout=PIPE, stderr=PIPE)
    o, e = p.communicate()
    return f'result_mono.xsf'

def create_voronoi(typefile, size=100, crystals=8):
    with open(f'project/{projname}/param.txt', 'w') as f:
        f.write(f'box {size} {size} {size}\nrandom {crystals}')
    # atomsk --polycrystal fcc_unitcell.xsf voronoi_random.txt fcc_polycrystal.cfg lmp
    for file in glob.glob(f'result*', root_dir=f'project/{projname}'):
        print(file)
    p = Popen(['bin/atomsk/atomsk', '--polycrystal', f'project/{projname}/{typefile}', f'project/{projname}/param.txt', f'project/{projname}/result.lmp', '-wrap'], stdout=PIPE, stderr=PIPE)
    o, e = p.communicate()
    return f'project/{projname}/result.lmp'
