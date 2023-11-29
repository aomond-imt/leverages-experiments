from shared_methods import is_isolated_uptime


def test_is_isolated_uptime():
    uptime_schedules = [
        [0, 300],
        [0, 300],
        [59.94, 240.01]
    ]
    uptime_schedules_no_ovlp = [
        [0,   500],
        [120, 400],
        [60,  300]
    ]
    zero_topology = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]
    full_topology = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]
    central_topology = [
        [1, 1, 0],
        [1, 1, 1],
        [0, 1, 1],
    ]
    res_zero = []
    res_full = []
    res_central = []
    res_no_ovlp = []
    for node_num in range(3):
        for hour_num in range(2):
            res_zero.append(is_isolated_uptime(node_num, hour_num, uptime_schedules, len(uptime_schedules), zero_topology))
            res_full.append(is_isolated_uptime(node_num, hour_num, uptime_schedules, len(uptime_schedules), full_topology))
            res_central.append(is_isolated_uptime(node_num, hour_num, uptime_schedules, len(uptime_schedules), central_topology))
            res_no_ovlp.append(is_isolated_uptime(node_num, hour_num, uptime_schedules_no_ovlp, len(uptime_schedules), full_topology))
    assert all(res_zero) is True
    assert any(res_full) is False
    assert any(res_central) is False
    assert all(res_no_ovlp) is True
    print("test_is_isolated_uptime done")


if __name__ == "__main__":
    test_is_isolated_uptime()
