# Installation
`pip install -r requirements.txt` (preferably in a virtualenv)

# Configuration

Select simulation parameters, copy and modify: `expe_parameters_journal.yaml`.
Notably, modify `<expe_dir>` which should contains: this repo, the experiments progression, the results.

# Run experiments

Tested with `python3.9` and `python3.10` in `ubuntu-22.04`\
Execute `run_experiments.py` with parameter file, example:

`python3 run_experiments.py expe_parameters_example.yaml`

**Note:** The [`ParamSweeper`](https://mimbert.gitlabpages.inria.fr/execo/execo_engine.html#execo_engine.sweep.ParamSweeper) from `execo_engine` module is used to track experiments progression (for each experiment: to_do, in_progress, done, fail).\
To reset the progression: `rm -r <expe_dir>/esds-sweeper`

# Results

Results path: `<expe_dir>/results-reconfiguration-esds/topologies/paper`
