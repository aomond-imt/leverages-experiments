import os

import yaml

INTERFACE_NAME = "eth0"
IDLE_CONSO = 1.339
STRESS_CONSO = 2.697
COMMS_CONSO = 0.16
BANDWIDTH = 50_000
UPT_DURATION = 60
COORD_NAME = "update"
FREQ_POLLING = 1


def is_isolated_uptime(node_num, hour_num, all_uptime_schedules, nodes_count, topology, rn_num):
    """
    Optimization method for simulation
    :return: True if an uptime never overlap with a neighbor during the hour
    """
    if node_num == rn_num:
        return False

    uptime_start = all_uptime_schedules[node_num][hour_num]
    uptime_end = uptime_start + UPT_DURATION
    # print(f"-- node {node_num}, {hour_num} round, {uptime_start}s/{uptime_end}s --")
    for n_node_num, node_schedule in enumerate(all_uptime_schedules[:nodes_count]):
        if topology[node_num][n_node_num] > 0:
            if n_node_num == rn_num:
                return False
            if n_node_num != node_num and topology[node_num][n_node_num] > 0:
                n_uptime_start = node_schedule[hour_num]
                n_uptime_end = n_uptime_start + UPT_DURATION
                overlap_duration = min(uptime_end, n_uptime_end) - max(uptime_start, n_uptime_start)
                # print(f"With node {n_node_num}: {n_uptime_start}s/{n_uptime_end}s, res: {res} {res > 0}")
                if overlap_duration > 0:
                    return False

    return True


def c(api):
    return api.read("clock")


def is_time_up(api, deadline):
    return c(api) + 0.0001 >= deadline  # Add epsilon to compensate float operations inaccuracy


def remaining_time(api, deadline):
    return max(deadline - c(api), 0)


def is_finished(s):
    return all(buf_flag == 1 for buf_flag in s.buf)


def verify_results(expected_result, test_dir):
    errors = []
    # Check result for each node
    for node_num, expected_node_results in expected_result.items():
        # Load node results
        with open(f"{test_dir}/{node_num}.yaml") as f:
            result = yaml.safe_load(f)

        # Check exact results
        for key in ["finished_reconf", "tot_reconf_duration"]:
            if round(result[key], 2) != round(expected_node_results[key], 2):
                errors.append(f"Error {key} node {node_num}: expected {expected_node_results[key]} got {result[key]}")

        # Results with approximation tolerance due to communications
        for key in ["global_termination_time", "local_termination_time", "tot_uptimes_duration"]:
            delta = abs(result[key] - expected_node_results[key])
            if delta > FREQ_POLLING * 5:
                errors.append(f"Error {key} node {node_num}: expected a delta of minus or equal {FREQ_POLLING * 5}, got {delta} (expected {expected_node_results[key]} got {result[key]}")

    return errors
