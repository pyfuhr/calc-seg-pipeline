from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle as pkl
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pipeline.metabuilder import create_meta

def train_lr(d, x_file, y_file, gb_file, outfile, metrics=None):
    create_meta(f'project/{d["projname"]}/{outfile}',
                    [f'project/{d["projname"]}/{x_file}', f'project/{d["projname"]}/{y_file}', 
                     f'project/{d["projname"]}/{gb_file}', ],
                    f'train linear regression model')
    xy_left = pd.read_csv(f"project/{d['projname']}/{x_file}", usecols=[1,2,3,4,5,6,7,8,9,10,11]) # pca vector, then id
    xy_left = xy_left.set_index('id')
    xy_right = pd.read_csv(f"project/{d['projname']}/{y_file}", sep=' ', header=None, names=['id', 'val']) # first - id, then one energy
    xy = pd.merge(xy_left, xy_right, 'inner', on='id')
    # xy structure: id, *soap_vectors, energy
    X_train, X_test, y_train, y_test = train_test_split(xy.iloc[:, 1:-1], xy.iloc[:, -1], test_size=0.9, random_state=42)

    nn = LinearRegression()
    nn.fit(X_train, y_train)

    with open(f"project/{d['projname']}/{outfile}", 'wb') as f:
        pkl.dump(nn, f)

    mae_train = mean_absolute_error(y_train, nn.predict(X_train))
    mae_test  = mean_absolute_error(y_test, nn.predict(X_test))
    mae_all   = mean_absolute_error(xy.iloc[:, -1], nn.predict(xy.iloc[:, 1:-1]))
    rms_all   = mean_squared_error(xy.iloc[:, -1], nn.predict(xy.iloc[:, 1:-1]))

    print("Train MAE    = %.2f kJ/mol"%(mae_train))
    print("Test MAE     = %.2f kJ/mol"%(mae_test))
    print("Dataset MAE  = %.2f kJ/mol"%(mae_all))
    print("Dataset RMS  = %.2f kJ/mol"%(rms_all))

    low  = -40
    high = 40
    lims = [low,high]
    intv = 20

    y_predict = nn.predict(xy.iloc[:, 1:-1])
    data = {'TRUE': xy.iloc[:, -1], 
            'PRED': y_predict}

    g = sns.JointGrid(data=pd.DataFrame(data), x='TRUE', y='PRED', space=0, height=2.5)
    g.ax_joint.plot(lims, lims, '--k', linewidth=0.5)  
    g = g.plot_joint(sns.kdeplot, color="C0", fill=True, thresh=0.05, n_levels=20)
    g = g.plot_marginals(sns.kdeplot, color="C0")

    g.ax_marg_x.set_xlim(lims[0], lims[1])
    g.ax_marg_y.set_ylim(lims[0], lims[1])

    g.ax_joint.plot(lims, lims, '--k', linewidth=0.5) 

    g.ax_joint.set_xticks(np.arange(low, high+intv, intv).astype(int))
    g.ax_joint.set_yticks(np.arange(low, high+intv, intv).astype(int))

    g.ax_joint.text(0.05, 0.95, "MAE=%.1f kJ/mol"%(mae_all), horizontalalignment='left', verticalalignment='top', transform=g.ax_joint.transAxes)
    g.set_axis_labels("True [kJ/mol]", "Predicted [kJ/mol]")
    plt.show()
    plt.savefig('img.png')

def predict_lr(d, infile, gb_file, model_file, outfile, metrics=None, learn_file=None):
    create_meta(f'project/{d["projname"]}/{outfile}',
                    [f'project/{d["projname"]}/{infile}', f'project/{d["projname"]}/{gb_file}', 
                     f'project/{d["projname"]}/{model_file}', ],
                    f'predict energies')
    xy_left = pd.read_csv(f"project/{d['projname']}/{infile}", usecols=[1,2,3,4,5,6,7,8,9,10,11]) # pca vector, then id
    xy_left = xy_left.set_index('id')
    gbs = np.loadtxt(f"project/{d['projname']}/{gb_file}").astype(int)
    xy_left = xy_left.iloc[gbs, :]
    
    with open(f"project/{d['projname']}/{model_file}", 'rb') as f:
        nn = pkl.load(f)

    y_pred = nn.predict(xy_left)# / 9.295834754835594 # AgCu
    np.savetxt(f"project/{d['projname']}/{outfile}", y_pred)
    fig, ax = plt.subplots(figsize=(2.5,2.5))
    ax.hist(y_pred, bins=100, alpha=0.5, color="red", label="Predict")
    ax2 = ax.twinx()
    if not learn_file is None:
        ax2.hist(np.loadtxt(f"project/{d['projname']}/{learn_file}").T[1], bins=100, alpha=0.5, color="green", label="True")

    plt.show()
    plt.savefig('img_dif.png')


#train_lr({'projname': 'test'}, 'pca.lst', 'Eseg_best_calc.txt', None, 'AgNi-nn.pkl')
#predict_lr({'projname': 'test'}, 'pca.lst', 'GBs.lst', 'AgNi-nn.pkl', 'Eseg_pred', None)
