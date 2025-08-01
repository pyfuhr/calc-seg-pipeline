from numba import njit
import numpy as np
import ase.io
from pipeline.metabuilder import create_meta
from pipeline.utils import transponse

@njit
def calc_neigh(rs, gb_ids, print_each, cutoff): 
    # Marchiy G. code for calculating neighboors for atoms in GB
    # modified a little by ph
    # central atom, coordination, neighbor_ids'
    out = []
    ncount = 0
    visited_bonds = []
    N = len(rs)
    ids = np.array([i for i in range(N)])
    for particle_index in range(N):
        if particle_index % print_each == 0:
            print(round(100*particle_index/N, 1), '%')
        list_post = [] 
        ind = ids[particle_index]
        if ind in gb_ids:
            r = rs[particle_index]
            dr = np.sqrt(np.sum((rs-r)*(rs-r), axis=1))
            msk = (dr < cutoff)*(dr>0)
            ind_ns = ids[msk]
            for ind_n in ind_ns:
                if (ind_n in gb_ids) and (not (ind_n, ind) in visited_bonds):
                    list_post.append(ind_n)
                    visited_bonds.append((ind, ind_n))
            ncount += len(list_post)
            out.append((ind, len(list_post), list_post))
    return out, ncount

def select_neighboor(d, infile, GB_file, cutoff, outfile):
    create_meta(f'project/{d["projname"]}/{outfile}',
                    [f'project/{d["projname"]}/{GB_file}'],
                    f'select neighboors, cutoff={cutoff}')
    atoms = ase.io.read(f"project/{d['projname']}/{infile}", format='lammps-data')
    gbs = np.loadtxt(f"project/{d['projname']}/{GB_file}")
    out, n = calc_neigh(atoms.get_positions(), gbs, 1000, cutoff)
    out2 = transponse(out)[2]
    with open(f'project/{d["projname"]}/{outfile}', 'w') as f:
        for row in out2:
            if row:
                f.write(' '.join(map(str, row))+'\n')
            else:
                f.write('-1\n')
