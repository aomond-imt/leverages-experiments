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
import numpy as np
import yaml
from execo_engine import ParamSweeper, sweep

import shared_methods


def tasks_list_observer(nb_sec_deps, nb_obs):
    return [
        [[(f"obs{obs_num}_dep{dep_num}", 10, None)] for dep_num in range(nb_sec_deps)]
        for obs_num in range(nb_obs)
    ]


def tasks_list_aggregator(nb_sec_deps, nb_obs):
    return [
        [[(f"agg_obs{obs_num}_dep{dep_num}", 10, f"obs{obs_num}_dep{dep_num}")] for dep_num in range(nb_sec_deps) for obs_num in range(nb_obs)]
    ]


def topology(n_obs, n_hops, bw):
    n_nodes = n_obs * n_hops + 1
    L = np.full((n_nodes, n_nodes), 0)
    B = [[bw]*(n_obs+1) + [0]*n_obs*(n_hops-1)]
    for node_num in range(1, n_nodes):
        node_bws = [0]*n_nodes
        node_bws[max(node_num-n_obs,0)] = bw    # previous
        node_bws[node_num] = bw                 # self
        if node_num+n_obs < n_nodes:
            node_bws[node_num+n_obs] = bw       # next
        B.append(node_bws)
    return np.asarray(B), L


def _update_schedules_with_rn(rn_num, all_uptimes_schedules, B):
    rn_scheds = []
    for n_num, edge_bw in enumerate(B[rn_num]):
        if edge_bw > 0:
            rn_scheds.extend(all_uptimes_schedules[n_num])
    all_uptimes_schedules[rn_num] = sorted(rn_scheds)


def run_simulation(expe_dir, test_expe, toggle_log, sweeper):
    parameters = sweeper.get_next()
    while parameters is not None:
        root_results_dir = f"{expe_dir}/leverages-results/simulation_metrics"
        n_obs, n_hops, n_deps = parameters["n_obs"], parameters["n_hops"], parameters["n_deps"]
        n_nodes = n_obs * n_hops + 1

        expe_key = f"{parameters['type_comms']}-{n_obs}-{n_hops}-{n_deps}-{parameters['data_size']}"
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
            B, L = topology(n_obs, n_hops, shared_methods.BANDWIDTH)
            smltr = esds.Simulator({"eth0": {"bandwidth": B, "latency": L, "is_wired": False}})

            with open(uptimes_schedule_name) as f:
                all_uptimes_schedules = json.load(f)  # Get complete view of uptimes schedules for aggregated_send optimization

            # Uptime schedules with RN
            obs_tasks = tasks_list_observer(n_deps, n_obs)
            agg_tasks = tasks_list_aggregator(n_deps, n_obs)
            tasks_list = agg_tasks + [[[]]]*(n_nodes-1)
            first_obs_num = n_obs*(n_hops-1) + 1
            obs_task_num = 0
            for obs_num in range(first_obs_num, n_nodes):
                tasks_list[obs_num] = obs_tasks[obs_task_num]
                obs_task_num += 1

            node_arguments = {
                "results_dir": expe_results_dir,
                "nodes_count": n_nodes,
                "all_uptimes_schedules": all_uptimes_schedules,
                "tasks_list": tasks_list,
                "topology": B,
                "type_comms": parameters["type_comms"],
                "data_size": parameters["data_size"] / n_deps,
                "s": shared_memory.SharedMemory(f"shm_cps_{time.time_ns()}", create=True, size=n_nodes)
            }

            # Setup and launch simulation
            print(f"Starting {parameters}")
            start_time = time.perf_counter()
            for node_num in range(n_nodes):
                smltr.create_node("on_pull", interfaces=["eth0"], args={**node_arguments, "rn_num": -1})
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
    # TMP ad-hoc
    try:
        os.remove("../esds-sweeper/inprogress")
        os.remove("../esds-sweeper/done")
        os.remove("../esds-sweeper/sweeps")
    except FileNotFoundError:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument('expe_parameters')
    parser.add_argument('-v', action="store_true")
    parser.add_argument('--save-sweeps', action="store_true")
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
        "type_comms": expe_parameters["type_comms"],
        "n_deps": expe_parameters["n_deps"],
        "n_obs": expe_parameters["n_obs"],
        "n_hops": expe_parameters["n_hops"],
        "data_size": expe_parameters["data_size"],
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

