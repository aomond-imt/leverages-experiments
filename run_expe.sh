source venv/bin/activate
python3 run_experiments.py expe_parameters.yaml
cd ../leverages-results || exit
source venv/bin/activate
python3 create_csv.py
Rscript bar_plot.r
