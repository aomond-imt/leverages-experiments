import contextlib
import json
import math
import os
import sys
import traceback
import argparse
from multiprocessing import cpu_count, shared_memory, Process
import time
from os.path import exists

import esds
import yaml
from execo_engine import ParamSweeper, sweep

import shared_methods
from topologies import clique, chain, ring, star, grid, tasks_list_agg_0, tasks_list_grid_fav, tasks_list_agg_middle, \
    tasks_list_grid_nonfav, tree, tasks_list_tree_fav, tasks_list_tree_nonfav, tasks_list_starchain_fav, \
    tasks_list_starchain_nonfav, starchain

tasks_list_tplgy = {
    "star-fav": (tasks_list_agg_0, star),
    "star-nonfav": (tasks_list_agg_middle, star),
    "clique-fav": (tasks_list_agg_0, clique),
    "ring-fav": (tasks_list_agg_0, ring),
    "chain-fav": (tasks_list_agg_middle, chain),
    "chain-nonfav": (tasks_list_agg_0, chain),
    "grid-fav": (tasks_list_grid_fav, grid),
    "grid-nonfav": (tasks_list_grid_nonfav, grid),
    "tree-fav": (tasks_list_tree_fav, tree),
    "tree-nonfav": (tasks_list_tree_nonfav, tree),
    "starchain-fav": (tasks_list_starchain_fav, starchain),
    "starchain-nonfav": (tasks_list_starchain_nonfav, starchain),
}


def _update_schedules_with_rn(rn_num, all_uptimes_schedules, B):
    rn_scheds = []
    for n_num, edge_bw in enumerate(B[rn_num]):
        if edge_bw > 0:
            rn_scheds.extend(all_uptimes_schedules[n_num])
    all_uptimes_schedules[rn_num] = sorted(rn_scheds)


def run_simulation(expe_dir, test_expe, toggle_log, sweeper):
    parameters = sweeper.get_next()
    while parameters is not None:
        root_results_dir = f"{expe_dir}/leverages-results/{['paper', 'tests'][test_expe]}"
        expe_key = f"{parameters['tplgy_name']}-{parameters['rn_type']}-{parameters['leverage']}-{parameters['nodes_count']}"
        results_dir = f"{expe_key}/{parameters['id_run']}"
        expe_results_dir = f"{root_results_dir}/{results_dir}"
        os.makedirs(expe_results_dir, exist_ok=True)

        try:
            if not test_expe:
                uptimes_schedule_name = f"uptimes_schedules/{parameters['id_run']}-{shared_methods.UPT_DURATION}.json"
            else:
                uptimes_schedule_name = f"tests/expes-tests/{parameters['tplgy_name']}-{parameters['rn_type']}.json"
                if not exists(uptimes_schedule_name):
                    print(f"No test found for {parameters['tplgy_name']}")
                    continue

            # Setup parameters
            nodes_count = parameters["nodes_count"]
            tasks_list_func, tplgy_func = tasks_list_tplgy[parameters["tplgy_name"]]
            B, L = tplgy_func(nodes_count, shared_methods.BANDWIDTH)
            smltr = esds.Simulator({"eth0": {"bandwidth": B, "latency": L, "is_wired": False}})

            with open(uptimes_schedule_name) as f:
                all_uptimes_schedules = json.load(f)  # Get complete view of uptimes schedules for aggregated_send optimization

            # Uptime schedules with RN
            agg_num, rn_num, tasks_list = tasks_list_func(nodes_count - 1)
            if parameters["rn_type"] in ["rn_agg", "rn_not_agg"]:
                if parameters["rn_type"] == "rn_agg":
                    rn_num = agg_num
                _update_schedules_with_rn(rn_num, all_uptimes_schedules, B)
            if parameters["rn_type"] == "no_rn":
                rn_num = -1

            node_arguments = {
                "results_dir": expe_results_dir,
                "nodes_count": nodes_count,
                "all_uptimes_schedules": all_uptimes_schedules,
                "tasks_list": tasks_list,
                "topology": B,
                "leverage": parameters["leverage"],
                "s": shared_memory.SharedMemory(f"shm_cps_{time.time_ns()}", create=True, size=nodes_count)
            }

            # Setup and launch simulation
            print(f"Starting {parameters}")
            start_time = time.perf_counter()
            for node_num in range(nodes_count):
                smltr.create_node("on_pull", interfaces=["eth0"], args={**node_arguments, **{"rn_num": rn_num}})
            stdout = None if toggle_log is None else open(f"/tmp/{expe_key}.txt", "w")
            with contextlib.redirect_stdout(stdout):
                smltr.run(interferences=False)
            if stdout: stdout.close()
            node_arguments["s"].close()
            try:
                node_arguments["s"].unlink()
            except FileNotFoundError as e:
                traceback.print_exc()

            # If test, verification
            if test_expe:
                with open(f"tests/expes-tests/{parameters['tplgy_name']}-{parameters['rn_type']}.yaml") as f:
                    expected_results = yaml.safe_load(f)["expected_result"]
                errors = shared_methods.verify_results(expected_results, expe_results_dir)
                if len(errors) == 0:
                    print(f"{results_dir}: ok")
                else:
                    print(f"{results_dir}: errors: \n" + "\n".join(errors))
            else:
                print(f"{results_dir}: done in {round(time.perf_counter() - start_time, 2)}s")

            # Go to next parameter
            sweeper.done(parameters)
        except Exception as exc:
            traceback.print_exc()
            sweeper.skip(parameters)
        finally:
            parameters = sweeper.get_next()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('expe_parameters')
    parser.add_argument('-v', action="store_true")
    args = parser.parse_args()

    with open(args.expe_parameters) as f:
        expe_parameters = yaml.safe_load(f)

    test_expe, expe_dir = expe_parameters["test_expe"] == "True", expe_parameters["expe_dir"]
    if test_expe:
        print("Testing")
    else:
        print("Simulation start")

    id_run_min, id_run_max = expe_parameters["id_run_boundaries"].values()
    expe_parameters_sweep = {
        "tplgy_name": expe_parameters["tplgy_name"],
        "nb_seq_deps": expe_parameters["nb_seq_deps"],
        "leverage": expe_parameters["leverage"],
        "rn_type": expe_parameters["rn_type"],
        "nodes_count": expe_parameters["nodes_count"],
        "id_run": [*range(id_run_min, id_run_max)],
    }
    # Create parameters list/sweeper
    if not test_expe:
        persistence_dir = f"{expe_dir}/esds-sweeper"
        sweeps = sweep(expe_parameters_sweep)
    else:
        persistence_dir = f"/tmp/test-{int(time.time())}"
        sweeps = sweep({"tplgy_name": expe_parameters_sweep["tplgy_name"], "rn_type": ["no_rn", "rn_agg", "rn_not_agg"], "nodes_count": [6], "id_run": [0]})

    # Sweeper read/write is thread-safe even on NFS (https://mimbert.gitlabpages.inria.fr/execo/execo_engine.html?highlight=paramsweeper#execo_engine.sweep.ParamSweeper)
    sweeper = ParamSweeper(
        persistence_dir=persistence_dir, sweeps=sweeps, save_sweeps=True
    )

    nb_cores = int(cpu_count() * 0.7)
    processes = []
    for _ in range(nb_cores):
        p = Process(target=run_simulation, args=(expe_dir, test_expe, args.v, sweeper))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


if __name__ == "__main__":
    main()

