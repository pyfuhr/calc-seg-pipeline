import pandas as pd
from sklearn.decomposition import PCA

def extract_pca(d, infile, pca_num, outfile):
    soap = pd.read_csv(f"project/{d['projname']}/{infile}", sep=' ', header=None)
    soap = soap.set_index(0)
    soap.sort_index(inplace=True)
    pca_x = PCA(n_components=pca_num, svd_solver="full")
    pca = pca_x.fit_transform(soap.iloc[:, 1:].values)
    pca = pd.DataFrame(pca)
    pca['id'] = soap.index

    pca.to_csv(f"project/{d['projname']}/{outfile}")

extract_pca({'projname': 'test'}, 'soap.lst', 10, 'pca.lst')