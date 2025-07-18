#2 atom neural specta without W
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import pickle as pkl

projname = 'ag10nm'
print(f'Using proj "{projname}"')
if not os.path.isdir(f'project/{projname}'):
    print('WARNING: proj doesnt exsist.')
    exit()
else:
    if not input("Use this project (Yes/No(any))? ").lower().startswith('y'):
        exit()

def train_lr(soap_vectors:np.array, energy_spectra, n_pca=10, points=100):
    assert points > len(energy_spectra), "Point more then energies"
    if not os.path.isdir(f'project/{projname}/models'):
        os.mkdir(f'project/{projname}/models')
    xy_left = pd.DataFrame(soap_vectors) # first - id, then vector
    xy_right = pd.DataFrame(energy_spectra) # first - id, then one energy
    xy = pd.merge(xy_left, xy_right, 'inner', on='id')
    # xy structure: id, *soap_vectors, energy
    X_train, X_test, y_train, y_test = train_test_split(xy.iloc[:, 1:-1], xy.iloc[:, -1], test_size=0.9, random_state=42)

    nn = LinearRegression()
    nn.fit(X_train, y_train)

    with open(f'project/{projname}/models/nn.pkl', 'wb') as f:
        pkl.dump(nn, f)

    mae_train = mean_absolute_error(y_train, nn.predict(X_train))
    mae_test  = mean_absolute_error(y_test, nn.predict(X_test))
    mae_all   = mean_absolute_error(xy.iloc[:, -1], nn.predict(xy.iloc[:, :-1]))
    rms_all   = mean_squared_error(xy.iloc[:, -1], nn.predict(xy.iloc[:, :-1]))

    print("Train MAE    = %.2f kJ/mol"%(mae_train))
    print("Test MAE     = %.2f kJ/mol"%(mae_test))
    print("Dataset MAE  = %.2f kJ/mol"%(mae_all))
    print("Dataset RMS  = %.2f kJ/mol"%(rms_all))

    pca_x = PCA(n_components=n_pca, svd_solver="full")
    xpca_all = pca_x.fit_transform(xy_left.iloc[:, 1:].values)
    xpca = pca_x.transform(xy.iloc[:, 1:-1].values)

    kmeans = KMeans(n_clusters=100, random_state=123)
    kmeans.fit(xpca)

    with open(f'project/{projname}/models/nn_ac.pkl', 'wb') as f:
        pkl.dump(nn_accelerated, f)

    X_trainpca, X_testpca, y_trainpca, y_testpca = train_test_split(xpca, xy.iloc[:, -1], test_size=0.9, random_state=42)

    nn_accelerated = LinearRegression()
    nn_accelerated.fit(X_testpca, y_testpca)

    mae_train_pca = mean_absolute_error(y_trainpca, nn_accelerated.predict(X_trainpca))
    mae_all_pca   = mean_absolute_error(xy.iloc[:, -1], nn_accelerated.predict(xpca))

    print("Accelerated model: Train MAE    = %.2f kJ/mol"%(mae_train_pca))
    print("Accelerated model: Dataset MAE  = %.2f kJ/mol"%(mae_all_pca))

    y_pred = nn_accelerated.predict(xpca)

    with open(f'project/{projname}/y_pred', 'w') as f:
        for i in y_pred:
            f.write(f'{i}\n')
