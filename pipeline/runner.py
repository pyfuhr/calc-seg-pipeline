import yaml
from step1 import create_monocrystal, create_polycrystal
from step2 import reorder_index, convert_format, convert_format2, minimize_polycrystal, relax_polycrystal
from step5 import train_lr, predict_lr
with open('test.yaml', 'r') as f:
    d = yaml.safe_load(f)

def run(d):
    pipeline:dict = d['pipeline']
    for d_func, d_args in pipeline.items():
        match d_func:
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
            case 'train_lr':
                args = d_args.copy()
                train_lr(d, **args)
            case 'predict_lr':
                args = d_args.copy()
                predict_lr(d, **args)
            case _:
                print(-1)

run(d)