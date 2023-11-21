import math
import subprocess, os
import sys
import traceback
from contextlib import redirect_stdout
from multiprocessing import Process, cpu_count, shared_memory
from multiprocessing.pool import Pool

import esds
import numpy as np
import yaml

from topologies import clique, chain, ring, star, grid

from shared_methods import verify_results

env_with_pythonpath = os.environ.copy()
env_with_pythonpath["PYTHONPATH"] = env_with_pythonpath["PYTHONPATH"] + ":" + os.path.dirname(os.path.realpath(__file__))
FREQ_POLLING = 1
LORA_BW = 50_000


tests_topologies = {
    "solo_on": clique(1, LORA_BW),
    "use_provide": clique(2, LORA_BW),
    "overlaps_sending": clique(3, LORA_BW),
    "actions_overflow": clique(2, LORA_BW),
    "chained_one_provide": chain(3, LORA_BW),
    "chained_three_provides": chain(3, LORA_BW),
    "ring_one_provide": ring(4, LORA_BW),
    "ring_three_aggregators": ring(6, LORA_BW),
    "chained_aggregator_use": chain(5, LORA_BW),
    "concurrent_tasks": clique(4, LORA_BW),
    "grid-9": grid(9, LORA_BW),
}


def compute_neighborhood(topology):
    node_neighbors = []
    for node_id, other_nodes in enumerate(topology):
        neighbors = []
        for other_node_id in range(len(other_nodes)):
            if node_id != other_node_id:
                if topology[node_id][other_node_id] > 0:
                    neighbors.append(other_node_id)
        node_neighbors.append(neighbors)

    return node_neighbors


def run_simulation(test_name, tasks_list):
    B, L = tests_topologies[test_name]
    s = esds.Simulator({"eth0": {"bandwidth": B, "latency": L, "is_wired": False}})
    node_neighbors = compute_neighborhood(B)
    nodes_count = len(tasks_list.keys())
    arguments = {
        "stress_conso": 1.358,
        "idle_conso": 1.339,
        "comms_conso": 0.16,
        "bandwidth": 6250,
        "results_dir": f"/tmp/{test_name}",
        "nodes_count": nodes_count,
        "uptimes_schedule_name": f"tplgy-tests/{test_name}.json",
        "tasks_list": tasks_list,
        "neighbor_nodes": node_neighbors,
        "topology": B,
        "s": shared_memory.SharedMemory(f"shm_cps_{test_name}", create=True, size=nodes_count)
    }
    sys.path.append("..")
    for node_num in range(nodes_count):
        s.create_node(f"on_pull", interfaces=["eth0"], args=arguments)

    s.run(interferences=False)
    arguments["s"].close()
    arguments["s"].unlink()


def run_test(test_name):
    with open(f"tplgy-tests/{test_name}.yaml") as f:
        test_args = yaml.safe_load(f)

    tasks_list, expected_result = test_args["tasks_list"], test_args["expected_result"]

    # Launch and log experiment
    os.makedirs(f"/tmp/{test_name}", exist_ok=True)
    with open(f"/tmp/{test_name}/debug.txt", "w") as f:
        with redirect_stdout(f):
            run_simulation(test_name, tasks_list)

    test_dir = f"/tmp/{test_name}"
    errors = verify_results(expected_result, test_dir)
    if len(errors) == 0:
        print(f"{test_name}: ok")
    else:
        print(f"{test_name}: errors: \n" + "\n".join(errors))


def main():
    all_p = []
    for test_name in tests_topologies.keys():
        p = Process(target=run_test, args=(test_name,))
        p.start()
        all_p.append(p)

    for k in all_p:
        k.join()


if __name__ == "__main__":
    main()
