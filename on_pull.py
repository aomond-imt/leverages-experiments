import copy

import yaml
from esds.node import Node
from esds.plugins.power_states import PowerStates, PowerStatesComms

from shared_methods import is_time_up, is_isolated_uptime, remaining_time, FREQ_POLLING, c, is_finished, STRESS_CONSO, \
    IDLE_CONSO, COMMS_CONSO, INTERFACE_NAME, UPT_DURATION


def execute(api: Node):
    """
    Note:
    - Do not consume messages when executing tasks. Message can accumulate leading
      to mass responses after task is complete
    :param api:
    :return:
    """
    api.log(f"Parameters: {api.args}")
    s = api.args["s"]
    node_cons = PowerStates(api, 0)
    comms_cons = PowerStatesComms(api)
    comms_cons.set_power(INTERFACE_NAME, 0, COMMS_CONSO, COMMS_CONSO)
    tot_uptimes, tot_msg_sent, tot_msg_rcv, tot_uptimes_duration, tot_reconf_duration, tot_sleeping_duration = 0, 0, 0, 0, 0, 0
    aggregated_send = 0  # Number of send computed but not simulated
    uptimes_schedule = api.args['all_uptimes_schedules'][api.node_id]  # Node uptime schedule
    tasks_list = copy.deepcopy(api.args["tasks_list"][api.node_id])
    current_parallel_tasks = tasks_list.pop(0)  # Current tasks trying to be run
    results_dir = api.args["results_dir"]
    nodes_count = api.args["nodes_count"]
    topology = api.args["topology"]

    deps_to_retrieve = set(task_dep for _,_,task_dep in current_parallel_tasks)
    api.log(f"deps_to_retrieve: {deps_to_retrieve}")
    deps_retrieved = {None}
    local_termination = 0
    # Duty-cycle simulation
    upt_num = 0
    while upt_num < len(uptimes_schedule):
        # Sleeping period
        uptime = uptimes_schedule[upt_num]
        node_cons.set_power(0)
        api.turn_off()
        sleeping_duration = uptime - c(api)
        api.log(f"Sleeping from {c(api)} to {uptime}")
        api.wait(sleeping_duration)
        tot_sleeping_duration += sleeping_duration

        # Uptime period
        api.turn_on()
        node_cons.set_power(IDLE_CONSO)
        uptime_end = uptime + UPT_DURATION
        # Handle RN's uptimes overlaps
        while upt_num+1 < len(uptimes_schedule) and uptime_end >= uptimes_schedule[upt_num+1]:
            uptime_end += UPT_DURATION - (uptime_end - uptimes_schedule[upt_num+1])  # Shift uptime_end
            upt_num += 1

        # Coordination loop
        while not is_time_up(api, uptime_end) and not is_finished(s):
            if current_parallel_tasks is not None:
                tasks_to_do = []
                for task in current_parallel_tasks:
                    _, _, task_dep = task
                    if task_dep in deps_retrieved:
                        tasks_to_do.append(task)

                if len(tasks_to_do) > 0:
                    # Execute tasks
                    max_task_time = max(task_time for _, task_time, _ in tasks_to_do)
                    api.log(f"Executing parallel tasks {tasks_to_do}")
                    node_cons.set_power(STRESS_CONSO)
                    api.wait(max_task_time)
                    tot_reconf_duration += max_task_time
                    node_cons.set_power(IDLE_CONSO)
                    for task_name, _, _ in tasks_to_do:
                        deps_retrieved.add(task_name)

                for task in tasks_to_do:
                    current_parallel_tasks.remove(task)

                if len(current_parallel_tasks) == 0:
                    current_parallel_tasks = tasks_list.pop(0) if len(tasks_list) > 0 else None
                    s.buf[api.node_id] = int(current_parallel_tasks is None)
                    if current_parallel_tasks is not None:
                        for _, _, task_dep in current_parallel_tasks:
                            deps_to_retrieve.add(task_dep)

                    # Save metrics
                    if current_parallel_tasks is None:
                        local_termination = c(api)
                        api.log("All tasks done")
                    else:
                        api.log(f"Next parallel tasks: {current_parallel_tasks}")
                        api.log(f"deps_to_retrieve: {deps_to_retrieve}")

            if is_isolated_uptime(api.node_id, tot_uptimes, api.args['all_uptimes_schedules'], nodes_count, topology, api.args['rn_num']) and not is_finished(s) and not is_time_up(api, uptime_end):
                remaining_t = remaining_time(api, uptime_end)
                api.wait(remaining_t)
                th_aggregated_send = remaining_t / ((257 / 6250) + 0.01 + FREQ_POLLING)
                aggregated_send += int(th_aggregated_send)

                # Check if sending an additional message doesn't cross the deadline, and add it if it's the case
                if int(th_aggregated_send) - th_aggregated_send <= 257 / 6250:
                    aggregated_send += 1

                # api.log(f"Isolated uptime, simulating {th_aggregated_send} sends")

            # Ask for missing deps
            if len(deps_to_retrieve) > 0 and not is_time_up(api, uptime_end):
                api.sendt("eth0", ("req", deps_to_retrieve), 257, 0, timeout=remaining_time(api, uptime_end))
                tot_msg_sent += 1

            # Receive msgs and put them in buffer (do not put duplicates in buf)
            buf = []
            timeout = 0.01
            if not is_time_up(api, uptime_end) and not is_finished(s):
                code, data = api.receivet("eth0", timeout=timeout)
                while data is not None and not is_time_up(api, uptime_end) and not is_finished(s):
                    tot_msg_rcv += 1
                    if data not in buf:
                        # api.log(f"Add to buffer: {data}")
                        buf.append(data)
                    code, data = api.receivet("eth0", timeout=timeout)

            # Treat each received msg
            for data in buf:
                type_msg, deps = data
                if type_msg == "req":
                    deps_to_send = deps_retrieved.intersection(deps)
                    if len(deps_to_send) > 0:
                        api.log(f"Sending deps: {deps_to_send}")
                        api.sendt("eth0", ("res", deps_to_send), 257, 0, timeout=remaining_time(api, uptime_end))
                        tot_msg_sent += 1
                    deps_to_retrieve.update(deps.difference(deps_retrieved))
                if type_msg == "res":
                    for dep in deps:
                        if dep in deps_to_retrieve:
                            api.log(f"Retrieved deps: {dep}")
                            deps_retrieved.add(dep)
                            deps_to_retrieve.remove(dep)

            if not is_finished(s):
                api.wait(min(FREQ_POLLING, remaining_time(api, uptime_end)))

        tot_uptimes += 1
        tot_uptimes_duration += c(api) - uptime
        upt_num += 1

        if is_finished(s):
            api.log("All nodes finished, terminating")
            break

    # Terminate
    api.log("Terminating")
    api.turn_off()

    # Report metrics
    node_cons.set_power(0)
    node_cons.report_energy()
    comms_cons.report_energy()
    with open(f"{results_dir}/{api.node_id}.yaml", "w") as f:
        yaml.safe_dump({
            "finished_reconf": current_parallel_tasks is None,
            "global_termination_time": c(api),
            "local_termination_time": local_termination,
            "node_cons": node_cons.energy,
            "comms_cons": float(comms_cons.get_energy() + aggregated_send * (257 / 6250) * COMMS_CONSO),
            "tot_uptimes": tot_uptimes,
            "tot_msg_sent": tot_msg_sent,
            "tot_msg_rcv": tot_msg_rcv,
            "tot_aggregated_send": aggregated_send,
            "tot_uptimes_duration": tot_uptimes_duration,
            "tot_reconf_duration": tot_reconf_duration,
            "tot_sleeping_duration": tot_sleeping_duration,
        }, f)
