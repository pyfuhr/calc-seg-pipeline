from step1 import create_monocrystal, create_polycrystal
from step2 import reorder_index, convert_format, convert_format2, minimize_polycrystal, relax_polycrystal
from step3 import get_gb_ids, select_points, soap, extract_pca
from step4 import add_impurity, replace_and_minimize, calculate_spectra
from step5 import train_lr, predict_lr

import argparse
parser = argparse.ArgumentParser(
                    prog='Segregation Pipeline',
                    description='What the program does',
                    epilog='Text at the bottom of help')

d_global = globals().copy()
for i in list(d_global.keys()):
    if i.startswith('__'):
        del d_global[i]

import yaml

with open('test.yaml', 'r') as f:
    d = yaml.safe_load(f)

def run(d):
    global d_global
    pipeline:dict = d['pipeline']
    for d_func, d_args in pipeline.items():
        match d_func:
            #  step 1
            case 'create_monocrystal':
                args = d_args.copy()
                if d_args['atomtypes'] == False:
                    args['atomtypes'] = [d["specs"][0], ]
                elif isinstance(d_args['atomtypes'], list):
                    if isinstance(d_args['atomtypes'][0], int):
                        args['atomtypes'] = []
                        for i in d_args['atomtypes']:
                            args['atomtypes'].append(d['specs'][i])
                    elif isinstance(d_args['atomtypes'][0], str):
                        pass
                    else: raise Exception('cant process create_monocrystal from list')
                else: raise Exception('cant process create_monocrystal because not list')
                create_monocrystal(d, **args)
            case 'create_polycrystal':
                args = d_args.copy()
                create_polycrystal(d, **args)
            # step 2
            case 'reorder_index':
                args = d_args.copy()
                reorder_index(d, **args)
            case 'convert_format':
                args = d_args.copy()
                convert_format(d, **args)
            case 'convert_format_atomsk':
                args = d_args.copy()
                convert_format2(d, **args)
            case 'minimize_polycrystal':
                args = d_args.copy()
                if d_args['atomtypes'] == False:
                    args['atomtypes'] = [d["specs"][0], ]
                elif isinstance(d_args['atomtypes'], list):
                    if isinstance(d_args['atomtypes'][0], int):
                        args['atomtypes'] = []
                        for i in d_args['atomtypes']:
                            args['atomtypes'].append(d['specs'][i])
                    elif isinstance(d_args['atomtypes'][0], str):
                        pass
                    else: raise Exception('cant process minimize from list')
                else: raise Exception('cant process minimize because not list')
                minimize_polycrystal(d, **args)
            case 'relax_polycrystal':
                args = d_args.copy()
                if d_args['atomtypes'] == False:
                    args['atomtypes'] = [d["specs"][0], ]
                elif isinstance(d_args['atomtypes'], list):
                    if isinstance(d_args['atomtypes'][0], int):
                        args['atomtypes'] = []
                        for i in d_args['atomtypes']:
                            args['atomtypes'].append(d['specs'][i])
                    elif isinstance(d_args['atomtypes'][0], str):
                        pass
                    else: raise Exception('cant process minimize from list')
                else: raise Exception('cant process minimize because not list')
                relax_polycrystal(d, **args)
            # step 3
            case 'get_gb_ids':
                args = d_args.copy()
                get_gb_ids(d, **args)
            case 'soap':
                args = d_args.copy()
                soap(d, **args)
            case 'extract_pca':
                args = d_args.copy()
                extract_pca(d, **args)
            case 'select_points':
                args = d_args.copy()
                select_points(d, **args)
            # step 4
            case 'add_impurity':
                args = d_args.copy()
                add_impurity(d, **args)
            case 'replace_and_minimize':
                args = d_args.copy()
                args = d_global[d_args['minimize_func']]
                replace_and_minimize(d, **args)
            case 'get_gb_ids':
                args = d_args.copy()
                args = d_global[d_args['minimize_func']]
                get_gb_ids(d, **args)
            # step 5
            case 'train_lr':
                args = d_args.copy()
                train_lr(d, **args)
            case 'predict_lr':
                args = d_args.copy()
                predict_lr(d, **args)
            case _:
                print(-1)
        if args.get('outfile', False):
            with open(f'project/{d["projname"]}/{args["outfile"]}.meta', 'w') as f:
                yaml.dump(args+d["specs"], f)

run(d)