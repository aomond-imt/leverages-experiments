import json, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--id_run', required=False, default=0)
parser.add_argument('--node_1', required=False, default=0)
parser.add_argument('--node_2', required=False, default=1)
parser.add_argument('--all', action="store_true")
parser.add_argument('-n', default=None)
args = parser.parse_args()
id_run, node_1, node_2, print_all, max_upt_num = args.id_run, args.node_1, args.node_2, args.all, args.n

with open(f"../uptimes_schedules/{id_run}-60.json") as f:
    scheds = json.load(f)
    sched_1 = scheds[node_1]
    sched_2 = scheds[node_2]

for upt_num, (upt_1, upt_2) in enumerate([*zip(sched_1, sched_2)][:max_upt_num]):
    ovlp = max(min(upt_1, upt_2) - max(upt_1, upt_2) + 60, 0)
    if ovlp > 0 or (ovlp == 0 and print_all):
        print(f"Upt {upt_num}: {ovlp:.2f}s")

