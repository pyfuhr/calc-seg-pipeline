# Installing
```bash
git clone https://github.com/pyfuhr/calc-seg-pipeline
cd calc-seg-pipeline
python -m venv .venv # create virtual environment
source .venv/bin/activate # activate venv for bash
pip install -r requirements.txt
```

# Usage
Edit yaml in project root directory <br>
Examlpe yaml file with list commands

```yaml
projname: "test"
specs: ["Ag", "Ni"]
cores: 54

pipeline:
    convert_format:
        infile: "result_ord"
        informat: "lammps-data"
        outformat: "xyz"
        outfile: "result_ord_x"
    relax_polycrystal:
        infile: "Ag_10nm_reord.lmp"
        potential_type: "eam/fs"
        potetntial: "Ag-Ni.eam.fs
        atomtypes: ["Ag"]
        init_temp: 0.1
        start_temp: 700
        stop_temp: 700
        end_temp: 0.1
        heat_time: 1e5
        relax_time: 1e6
        cool_time: 1e6
        outfile: "Ag_10nm_reord_relax.lmp"

not_all_command_under_implemented_now
pipeline_commands:
    - create_monocrystal
    - create_polycrystal
    - reorder_index
    - convert_format
    - convert_format_atomsk
    - minimize_polycrystal
    - relax_polycrystal
    - get_gb_ids
    - soap
    - extract_pca
    - select_points
    - add_inpurity
    - replace_and_minimize
    - calculate_spectra
    - train_lr
    - predict_lr
    - utils
```

Then edit filename in pipeline/runner.py in 5 row (todo add normal iface)
