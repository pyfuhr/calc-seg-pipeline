import numpy as np
import pandas as pd

def transponse(M):
    return [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]


def calculate_Fm(d, infile, Eb_in_a, outfile):
    Ebina = np.loadtxt(f"project/{d['projname']}/{Eb_in_a}")
    Eseg = np.loadtxt(f"project/{d['projname']}/{infile}") / Ebina
    Eseg = Eseg[Eseg < 0]
    print(np.average(Eseg))
    np.savetxt(f"project/{d['projname']}/{outfile}", np.array((np.average(Eseg), )))

# calculate_Fm({'projname': 'test'}, 'Eseg_pred', 'Eb_in_a', 'Fm')
def get_masses_from_specs(specs):
    df = pd.read_csv('elements.csv')
    if isinstance(specs, str):
        specs = [specs, ]
    ret = []
    for i in specs:
        ret.append(float(df[df['Symbol']==i]['AtomicMass'].iloc[0]))
    return ret

def get_atomicnum_from_specs(specs):
    df = pd.read_csv('elements.csv')
    if isinstance(specs, str):
        specs = [specs, ]
    ret = []
    for i in specs:
        ret.append(int(df[df['Symbol']==i]['AtomicNumber'].iloc[0]))
    return ret