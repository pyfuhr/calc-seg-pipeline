#!.venv/bin/python
from pipeline.runner import run

import argparse
import yaml

parser = argparse.ArgumentParser(
                    prog='Segregation Pipeline',
                    description='Uses to compute segregation energy for polycrystal')
parser.add_argument('config')
args = parser.parse_args()

with open(args.config, 'r') as f:
    d = yaml.safe_load(f)

run(d)