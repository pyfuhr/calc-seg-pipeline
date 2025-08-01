import pandas as pd
from sklearn.decomposition import PCA
import ovito as ov
from pipeline.utils import get_atomicnum_from_specs
import numpy as np
import multiprocessing
from dscribe.descriptors.soap import SOAP
from tqdm import tqdm
from time import sleep
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from pipeline.metabuilder import create_meta

q_step3 = multiprocessing.Queue()

def start_subcalc(id, system, cores, species, soap_cutoff, n_max, l_max, sigma, cnt) -> None:
    soap = SOAP(
        species=species,
        periodic=True,
        r_cut=soap_cutoff,
        n_max=n_max,
        l_max=l_max,
        sigma=sigma
    )
    global q_step3
    if id==0:
        for i in tqdm(range(id, len(system), cores)):
            q_step3.put((i, soap.create(system, centers=[i, ])[0]))
    else:
        for i in range(id, len(system), cores):
            q_step3.put((i, soap.create(system, centers=[i, ])[0]))
    cnt.value -= 1

def soap(d, infile, soap_cutoff, n_max, l_max, sigma, atomtypes, outfile, cores=False):
    create_meta(f'project/{d["projname"]}/{outfile}',
                    [f'project/{d["projname"]}/{infile}',],
                    f'Calculate soap vector\nSoap constants (cutoff, n, l, sigma): {(soap_cutoff, n_max, l_max, sigma)}\n'
                    f'Atomtypes{atomtypes}')
    '''first - spec of matrix, second - spec of impurity'''
    pipeline = ov.io.import_file(f'project/{d["projname"]}/{infile}')
    data = pipeline.compute()
    system = ov.io.ase.ovito_to_ase(data)
    system.set_pbc([1,1,1])
    atomnumbers = get_atomicnum_from_specs(atomtypes)
    system.set_atomic_numbers(np.ones(len(system))*int(atomnumbers[0]))
    species = atomnumbers
    procs = []
    global q
    cores = (cores if cores else d['cores'])
    cnt = multiprocessing.Value('d', 0)
    for i in range(cores):
        p = multiprocessing.Process(target=start_subcalc, args=(i, system, 
        cores, species, soap_cutoff, n_max, l_max, sigma, cnt))
        p.start()
        procs.append(p)
        cnt.value += 1
    
    while cnt.value > 0:
        sleep(1)
        
    with open(f"project/{d['projname']}/{outfile}", 'w') as f:
        while not q_step3 .empty():
            print('Entry left:', q_step3.qsize(), end='\r')
            row = q_step3 .get()
            f.write(f'{row[0]} {" ".join(map(str, row[1]))}\n')

def get_gb_ids(d, infile, cutoff, outfile):
    create_meta(f'project/{d["projname"]}/{outfile}',
                    [f'project/{d["projname"]}/{infile}',],
                    f'Get grain border atom\nCutoff: {cutoff}')
    node = ov.io.import_file(f'project/{d["projname"]}/{infile}')
    fixed_mode = ov.modifiers.CommonNeighborAnalysisModifier.Mode.FixedCutoff
    modifier1 = ov.modifiers.CommonNeighborAnalysisModifier(mode=fixed_mode, cutoff=cutoff)
    node.modifiers.append(modifier1)
    data = node.compute()
    node.modifiers.append(ov.modifiers.ExpressionSelectionModifier(expression="StructureType != %i"%(1)))
    data = node.compute()
    select = data.particles['Selection']
    nparticles = len(select.array)
    gb_atoms_indices = []
    for index in range(nparticles):
        if int(select.array[index]) == int(1):
            gb_atoms_indices.append(index)
    np.savetxt(f'project/{d["projname"]}/{outfile}', np.array(gb_atoms_indices, dtype=np.int32))

def extract_pca(d, infile, pca_num, outfile):
    create_meta(f'project/{d["projname"]}/{outfile}',
                    [f'project/{d["projname"]}/{infile}', ],
                    f'PCA num: {pca_num}')
    soap = pd.read_csv(f"project/{d['projname']}/{infile}", sep=' ', header=None)
    soap = soap.set_index(0)
    soap.sort_index(inplace=True)
    pca_x = PCA(n_components=pca_num, svd_solver="full")
    pca = pca_x.fit_transform(soap.iloc[:, 1:].values)
    pca = pd.DataFrame(pca)
    pca['id'] = soap.index

    pca.to_csv(f"project/{d['projname']}/{outfile}")

def select_points(d, infile, gb_file, points_num, outfile, random_state=42):
    create_meta(f'project/{d["projname"]}/{outfile}',
                    [f'project/{d["projname"]}/{gb_file}', ],
                    f'Select {points_num} points\nRandom state: {random_state}')
    ind = np.loadtxt(f"project/{d['projname']}/{gb_file}").astype(np.int32)
    xpca_all = pd.read_csv(f"project/{d['projname']}/{infile}", usecols=[1,2,3,4,5,6,7,8,9,10,11])
    xpca_all['idc'] = xpca_all['id'].copy()
    xpca_all.set_index('id',inplace=True)
    xpca_gb = xpca_all.iloc[ind]
    print(xpca_gb)
    kmeans = KMeans(n_clusters=points_num, random_state=random_state)
    kmeans.fit(xpca_gb.iloc[:, :-1])

    best_lae_indices, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, xpca_gb.iloc[:, :-1])

    with open(f"project/{d['projname']}/{outfile}", 'w') as f:
        for i in best_lae_indices:
            f.write(f"{xpca_gb['idc'].values[i]}\n")

#extract_pca({'projname': 'test'}, 'soap.lst', 10, 'pca.lst')
#get_gb_ids({'projname': 'test'}, 'Ag_15nm_minimized.cfg', 3.5, 'lower.lst')
#select_points({'projname': 'test'}, 'pca.lst', 'lower.lst', 200, 'GBs_best.lst')