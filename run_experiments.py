import math
import os
import shutil
import traceback
from contextlib import redirect_stdout
from multiprocessing import cpu_count, shared_memory, Process
import time
from os.path import exists

import esds
import yaml
from execo_engine import ParamSweeper, sweep

import shared_methods
from topologies import clique, chain, ring, star, grid, tasks_list_agg_0, tasks_list_grid_fav, tasks_list_agg_middle

topology_sizes = {
    "clique": {"small": 6, "medium": 16, "large": 31},
    "chain": {"small": 6, "medium": 16, "large": 31},
    "ring": {"small": 6, "medium": 16, "large": 31},
    "star": {"small": 6, "medium": 16, "large": 31},
    "grid": {"small": 9, "medium": 16, "large": 25}
}

tasks_list_tplgy = {
    "star-fav": (tasks_list_agg_0, star),
    "star-nonfav": (tasks_list_agg_middle, star),
    "ring-fav": (tasks_list_agg_0, ring),
    "chain-fav": (tasks_list_agg_middle, chain),
    "chain-nonfav": (tasks_list_agg_0, chain),
    "clique-fav": (tasks_list_agg_0, clique),
    "grid-fav": (tasks_list_grid_fav, grid),
    "grid-nonfav": (tasks_list_agg_0, grid),
}


def run_simulation(test_expe):
    parameters = sweeper.get_next()
    while parameters is not None:
        print(f"Doing {parameters}")
        root_results_dir = f"{os.environ['HOME']}/results-reconfiguration-esds/topologies/{['paper', 'tests'][test_expe]}"
        results_dir = f"{parameters['coord_name']}-{parameters['tplgy']}-{parameters['topology_size']}-{shared_methods.UPT_DURATION}/{parameters['id_run']}"
        expe_results_dir = f"{root_results_dir}/{results_dir}"
        tmp_results_dir = f"/tmp/{results_dir}"
        os.makedirs(expe_results_dir, exist_ok=True)
        os.makedirs(tmp_results_dir, exist_ok=True)
        debug_file_path = f"{tmp_results_dir}/debug.txt"

        try:
            # Setup parameters
            network_topology, _ = parameters["tplgy"].split("-")
            nodes_count = topology_sizes[network_topology][parameters["topology_size"]]
            tasks_list, tplgy = tasks_list_tplgy[parameters["tplgy"]]
            B, L = tplgy(nodes_count, shared_methods.BANDWIDTH)
            smltr = esds.Simulator({"eth0": {"bandwidth": B, "latency": L, "is_wired": False}})
            t = int(time.time()*1000)

            if not test_expe:
                uptimes_schedule_name = f"uptimes_schedules/{parameters['id_run']}-{shared_methods.UPT_DURATION}.json"
            else:
                uptimes_schedule_name = f"expes-tests/{parameters['coord_name']}-{parameters['tplgy']}-{nodes_count}.json"
                if not exists(uptimes_schedule_name):
                    print(f"No test found for {parameters['coord_name']}-{parameters['tplgy']}")
                    continue

            node_arguments = {
                "results_dir": expe_results_dir,
                "nodes_count": nodes_count,
                "uptimes_schedule_name": uptimes_schedule_name,
                "tasks_list": tasks_list(parameters['coord_name'], nodes_count - 1),
                "topology": B,
                "s": shared_memory.SharedMemory(f"shm_cps_{parameters['id_run']}-{shared_methods.UPT_DURATION}-{t}", create=True, size=nodes_count)
            }

            # Setup and launch simulation
            for node_num in range(nodes_count):
                smltr.create_node("on_pull", interfaces=["eth0"], args=node_arguments)
            with open(debug_file_path, "w") as f:
                with redirect_stdout(f):
                    smltr.run(interferences=False)
            node_arguments["s"].close()
            try:
                node_arguments["s"].unlink()
            except FileNotFoundError as e:
                traceback.print_exc()

            # If test, verification
            if test_expe:
                with open(f"expes-tests/{parameters['coord_name']}-{parameters['tplgy']}-{nodes_count}.yaml") as f:
                    expected_results = yaml.safe_load(f)["expected_result"]
                errors = shared_methods.verify_results(expected_results, expe_results_dir)
                if len(errors) == 0:
                    print(f"{results_dir}: ok")
                else:
                    print(f"{results_dir}: errors: \n" + "\n".join(errors))
            else:
                print(f"{results_dir}: done")

            # Go to next parameter
            sweeper.done(parameters)
        except Exception as exc:
            traceback.print_exc()
            sweeper.skip(parameters)
        finally:
            if exists(debug_file_path):
                shutil.copy(debug_file_path, expe_results_dir)
                os.remove(debug_file_path)
            parameters = sweeper.get_next()


if __name__ == "__main__":
    test_expe = False
    parameter_list = {
        "coord_name": ["update"],
        "tplgy": [
            "star-fav",
            "star-nonfav",
            "ring-fav",
            "chain-fav",
            "chain-nonfav",
            "clique-fav",
            "grid-nonfav",
            "grid-fav",
        ],
        "topology_size": ["small", "medium", "large"],
        "id_run": [*range(30)],
    }
    sweeps = sweep(parameter_list)

    # Initialise sweeper in global scope to be copied on all processes
    sweeper = ParamSweeper(
        persistence_dir=os.path.join(shared_methods.HOME_DIR, "optim-esds-sweeper" + "-test" * test_expe), sweeps=sweeps, save_sweeps=True
    )

    if test_expe:
        print("Testing")
    else:
        print("Simulation start")

    nb_cores = math.ceil(cpu_count() * 0.5)
    processes = []
    for _ in range(nb_cores):
        p = Process(target=run_simulation, args=(test_expe,))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
