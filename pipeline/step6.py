from numba import njit
import numpy as np
import ase.io
from pipeline.metabuilder import create_meta
from pipeline.utils import transponse, get_atomicnum_from_specs
from tqdm import tqdm
from dscribe.descriptors import SOAP
import pickle as pkl
from joblib import Parallel, delayed
import os
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
import pandas as pd

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

def calc_part(d, id, system, part:list, atomtypes, cutoff, n_max,l_max,sigma):
    species = get_atomicnum_from_specs(atomtypes)

    soap = SOAP(species=species, periodic=True, r_cut=cutoff, 
                n_max=n_max, l_max=l_max, sigma=sigma)
    atomic_number1, atomic_number2 = species
    system = system.copy()
    out1 = []
    out2 = []
    x_id = []

    for row in (part if id!=0 else tqdm(part)):
        a1 = row[0]
        for a2 in row[1]:
            atomic_numbers = np.ones(len(system))*int(atomic_number1)
            atomic_numbers[a2-1] = int(atomic_number2)
            system.set_atomic_numbers(atomic_numbers)
            out1.append(soap.create(system, centers=[a1-1], n_jobs=1))
            atomic_numbers = np.ones(len(system))*int(atomic_number1)
            atomic_numbers[a1-1] = int(atomic_number2)
            system.set_atomic_numbers(atomic_numbers)
            out2.append(soap.create(system, centers=[a2-1], n_jobs=1))
            x_id.append((a1-1,a2-1))  

    a = np.array([out1[i][:, soap.get_location(('Ag', 'Ni'))] for i in range(len(out1))])
    b = np.array([out2[i][:, soap.get_location(('Ag', 'Ni'))] for i in range(len(out2))])
    c = np.array([out1[i][:, soap.get_location(('Ag', 'Ag'))] for i in range(len(out1))])
    dd = np.array([out2[i][:, soap.get_location(('Ag', 'Ag'))] for i in range(len(out2))])
    desc = np.concatenate((a,b,c,dd), axis=-1).squeeze()

    if not os.path.isdir(f'project/{d['projname']}/nsoappart'):
        os.mkdir(f'project/{d['projname']}/nsoappart')
    with open(f'project/{d['projname']}/nsoappart/neight_part{id}.pkl', 'wb') as f:
        pkl.dump((desc, x_id), f)

def soap_neigboor(d, infile, gb_file, neighboor_file, atomtypes, n_max, l_max, sigma, cores):
    processes = cores * 25
    system = ase.io.read(f"project/{d['projname']}/{infile}")
    pairs = {}
    with open(f"project/{d['projname']}/{gb_file}", 'r') as fgb:
        with open(f"project/{d['projname']}/{neighboor_file}", 'r') as fng:
            atoms = [int(i) for i in fgb.read().split('\n')[:-1]]
            neighs = [list(map(int, i)) for i in fng.read().split('\n')[:-1]]
            for at, ng in zip(atoms, neighs):
                if ng[0] == -1: continue
                pairs[at] = ng

    split_pairs = [[] for i in range(processes)]
    lkey = list(pairs.keys())
    for i in range(len(lkey)):
        split_pairs[i%processes].append((lkey[i], pairs[lkey[i]]))
    Parallel(cores)(delayed(calc_part)(i, system.copy(), split_pairs[i].copy(), atomtypes, n_max, l_max, sigma) for i in range(processes))

def connect_parts(d, path, outfile):
    if os.path.isfile(outfile):
        os.remove(outfile)
    os.system(f'touch {outfile}')
    for file in os.listdir(path):
        arr = []
        with open(path+file, 'rb') as f:
            desc, atoms = pkl.load(f)
            for at, dsc in zip(atoms, desc):
                arr.extend(at, dsc)
        with open(outfile, 'a') as f:
            for i in arr:
                f.write(','.join(map(str, i)))
    
def extract_pairs_pca(d, infile, pca_num, outfile):
    soap = pd.read_csv(f"project/{d['projname']}/{infile}", sep=' ', header=None)
    pca_x = PCA(n_components=pca_num, svd_solver="full")
    pca = pca_x.fit_transform(soap.iloc[:, 2:].values)
    pca = pd.DataFrame(pca)
    pca['at1'] = soap[0]
    pca['at2'] = soap[1]

    pca.to_csv(f"project/{d['projname']}/{outfile}")

def select_pairs(d, infile, points_num, outfile, random_state=42):
    
    xpca_all = pd.read_csv(f"project/{d['projname']}/{infile}", header=None)
    kmeans = KMeans(n_clusters=points_num, random_state=random_state)
    kmeans.fit(xpca_all.iloc[:, 2:])

    best_lae_indices, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, xpca_all.iloc[:, 2:])

    with open(f"project/{d['projname']}/{outfile}", 'w') as f:
        for i in best_lae_indices:
            f.write(f"{' '.join(xpca_all.iloc[:2].values[i].tolist())}\n")