from shared_methods import is_isolated_uptime, BANDWIDTH
from topologies import star, chain, clique, ring, grid


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


def test_star():
    uptime_schedules = [[0], [30], [60]]
    nodes_count = 3
    tplgy, _ = star(nodes_count, BANDWIDTH)
    expected_result = [False, False, True]
    for node_num in range(nodes_count):
        assert expected_result[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules, nodes_count, tplgy)
    print("test_star done")


def test_chain():
    uptime_schedules = [[0], [30], [75], [15]]
    nodes_count = 4
    tplgy, _ = chain(nodes_count, BANDWIDTH)
    expected_result = [False, False, False, True]
    for node_num in range(nodes_count):
        assert expected_result[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules, nodes_count, tplgy)
    print("test_chain done")


def test_grid():
    uptime_schedules = [[0], [200], [0], [60], [200], [60], [0], [60], [0]]
    nodes_count = 9
    tplgy, _ = grid(nodes_count, BANDWIDTH)
    expected_result = [True, False, True, True, False, True, True, True, True]
    for node_num in range(nodes_count):
        assert expected_result[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules, nodes_count, tplgy)
    print("test_grid done")


def test_ring():
    uptime_schedules = [[50], [80], [125], [65], [0]]
    nodes_count = 5
    tplgy, _ = ring(nodes_count, BANDWIDTH)
    expected_result = [False, False, False, True, False]
    for node_num in range(nodes_count):
        assert expected_result[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules, nodes_count, tplgy)
    print("test_ring done")


def test_clique():
    uptime_schedules = [[50], [80], [125], [65], [0]]
    nodes_count = 5
    tplgy, _ = clique(nodes_count, BANDWIDTH)
    expected_result = [False, False, False, False, False]
    for node_num in range(nodes_count):
        assert expected_result[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules, nodes_count, tplgy)
    print("test_clique done")


if __name__ == "__main__":
    test_is_isolated_uptime()
    test_star()
    test_chain()
    test_grid()
    test_ring()
    test_clique()
