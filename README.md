# Installation
Clone this repository: `git clone https://github.com/aomond-imt/journal-pdc-experiments.git` \
Note: The uptimes_schedules/ dir is very heavy (>600MB) which might slow down clone 

`pip install -r requirements.txt` (preferably in a virtualenv)

# Configuration

Select simulation parameters. Copy `expe_parameters_example.yaml` and add/update simulation parameters.\
A reference to all simulation parameters is given in `expe_parameters_journal.yaml`:

Notably, modify `<expe_dir>` which will contains: this cloned repo, the experiments progression, the results.

# Run experiments

Tested with `python3.9` and `python3.10` in `ubuntu-22.04`\
Execute `run_experiments.py` with simulation parameter file, example:

`python3 run_experiments.py expe_parameters_example.yaml`

**Note:** The [`ParamSweeper`](https://mimbert.gitlabpages.inria.fr/execo/execo_engine.html#execo_engine.sweep.ParamSweeper)
from `execo_engine` module is used to track experiments progression for each experiment 
(to_do, in_progress, done, fail).\
To reset the progression: `rm -r <expe_dir>/esds-sweeper`

# Results

Results path: `<expe_dir>/results-reconfiguration-esds/topologies/paper`
