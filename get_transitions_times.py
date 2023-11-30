import json
import os
with open(f"{os.environ['HOME']}/concerto-d-projects/experiment_files/parameters/transitions_times/transitions_times-1-30-deps12-1.json") as f:
    tt = json.load(f)["transitions_times"]


l = []
for t_ss, t_sp in zip(tt["server"]["t_ss"], tt["server"]["t_sp"]):
    l += round(t_ss + t_sp, 2),

print(l)

m = []
for dep_num in range(30):
    m.append((tt[f"dep{dep_num}"]["t_du"], tt[f"dep{dep_num}"]["t_dr"]))

print(m)
