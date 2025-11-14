from subprocess import Popen, PIPE
import shutil as sh
import yaml
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(filename='calc.log', level=logging.INFO)

for inpurity in ["V", "Au", "Cr", "Pb", "Pd", "Pt", "Ti"]:
    logger.info(f'Start calculate inpurity {inpurity}')
    if not os.path.isdir(f'project/Ag{inpurity}'):
        sh.copytree('project/AgW', f'project/Ag{inpurity}')
    with open('spectra.yaml', 'r') as f:
        d = yaml.safe_load(f)
    with open('spectra.yaml', 'w') as f:
        d['projname'] = f'Ag{inpurity}'
        d['specs'] = ["Ag", inpurity]
        yaml.safe_dump(d, f)
    
    try:
        p = Popen(['/media/user/HDD/feodor_ppl/calc-seg-pipeline/.venv/bin/python', 'main.py', 'spectra.yaml'], stderr=PIPE, stdout=PIPE)
        for line in p.stdout:
            print(f"Subprocess output: {line.strip()}")
        p.wait()
        out, err = p.communicate()
        retcode = str(p.returncode)

        logger.info(f'Calculate of {inpurity} is ended with code {retcode}')
        if retcode != 0:
            logger.info(f'Error {err.decode()}')
    except Exception as e:
        logger.error(e)
    
