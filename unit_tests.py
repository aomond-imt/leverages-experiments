from shared_methods import is_isolated_uptime, BANDWIDTH
from topologies import star, chain, clique, ring, grid, tree, starchain


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
            res_zero.append(is_isolated_uptime(node_num, hour_num, uptime_schedules, len(uptime_schedules), zero_topology, -1))
            res_full.append(is_isolated_uptime(node_num, hour_num, uptime_schedules, len(uptime_schedules), full_topology, -1))
            res_central.append(is_isolated_uptime(node_num, hour_num, uptime_schedules, len(uptime_schedules), central_topology, -1))
            res_no_ovlp.append(is_isolated_uptime(node_num, hour_num, uptime_schedules_no_ovlp, len(uptime_schedules), full_topology, -1))
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
        assert expected_result[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules, nodes_count, tplgy, -1)
    print("test_star done")


def test_chain():
    uptime_schedules = [[0], [30], [75], [15]]
    nodes_count = 4
    tplgy, _ = chain(nodes_count, BANDWIDTH)
    expected_result = [False, False, False, True]
    for node_num in range(nodes_count):
        assert expected_result[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules, nodes_count, tplgy, -1)
    print("test_chain done")


def test_grid():
    uptime_schedules = [[0], [200], [0], [60], [200], [60], [0], [60], [0]]
    nodes_count = 9
    tplgy, _ = grid(nodes_count, BANDWIDTH)
    expected_result = [True, False, True, True, False, True, True, True, True]
    for node_num in range(nodes_count):
        assert expected_result[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules, nodes_count, tplgy, -1)
    print("test_grid done")


def test_ring():
    uptime_schedules = [[50], [80], [125], [65], [0]]
    nodes_count = 5
    tplgy, _ = ring(nodes_count, BANDWIDTH)
    expected_result = [False, False, False, True, False]
    for node_num in range(nodes_count):
        assert expected_result[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules, nodes_count, tplgy, -1)
    print("test_ring done")


def test_clique():
    uptime_schedules = [[50], [80], [125], [65], [0]]
    nodes_count = 5
    tplgy, _ = clique(nodes_count, BANDWIDTH)
    expected_result = [False, False, False, False, False]
    for node_num in range(nodes_count):
        assert expected_result[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules, nodes_count, tplgy, -1)
    print("test_clique done")


def test_tree_9():
    uptime_schedules_true = [
        [400], [200], [200], [300], [300], [300], [300], [400], [400]
    ]
    nodes_count = 9
    tplgy, _ = tree(nodes_count, BANDWIDTH)
    expected_result_true = [True]*9
    for node_num in range(nodes_count):
        assert expected_result_true[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules_true, nodes_count, tplgy, -1)

    uptime_schedules_false = [
        [400], [400], [200], [800], [800], [200], [100], [800], [100]
    ]
    expected_result_false = [False]*4+[True]+[False]*4
    for node_num in range(nodes_count):
        assert expected_result_false[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules_false, nodes_count, tplgy, -1)
    print("test_tree_9 done")


def test_tree_16():
    uptime_schedules_true = [
        [400], [200], [200], [300], [300], [300], [300], [400], [400], [400], [400], [400], [400], [400], [450], [500]
    ]
    nodes_count = 16
    tplgy, _ = tree(nodes_count, BANDWIDTH)
    expected_result_true = [True]*16
    for node_num in range(nodes_count):
        assert expected_result_true[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules_true, nodes_count, tplgy, -1)

    uptime_schedules_false = [
        [100], [50], [150], [50], [0], [200], [150], [50], [200], [0], [0], [200], [200], [200], [150], [50]
    ]
    expected_result_false = [False]*8 + [True] + [False]*7
    for node_num in range(nodes_count):
        assert expected_result_false[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules_false, nodes_count, tplgy, -1)
    print("test_tree_16 done")


def test_tree_25():
    uptime_schedules_true = [
        [400], [200], [200], [300], [300], [300], [300], [400], [400], [400], [400], [400], [450], [450], [450], [500], [500], [500], [500], [500], [500], [500], [500], [500], [500]
    ]
    nodes_count = 25
    tplgy, _ = tree(nodes_count, BANDWIDTH)
    expected_result_true = [True]*25
    for node_num in range(nodes_count):
        assert expected_result_true[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules_true, nodes_count, tplgy, -1)

    print("test_tree_25 done")


def test_starchain():
    uptime_schedules_true = [
        [200], [400], [100], [0], [100], [0], [100], [0], [400]
    ]
    uptime_schedules_false_1 = [
        [0], [100], [100], [100], [100], [100], [100], [100], [100]
    ]
    uptime_schedules_false_2 = [
        [100], [150], [50], [150], [50], [150], [50], [150], [50]
    ]
    nodes_count = 9
    tplgy, _ = starchain(nodes_count, BANDWIDTH)
    expected_result_true = [True]*9
    expected_result_false_1 = [True] + [False]*8
    expected_result_false_2 = [False]*9
    for node_num in range(nodes_count):
        assert expected_result_true[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules_true, nodes_count, tplgy, -1)
        assert expected_result_false_1[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules_false_1, nodes_count, tplgy, -1)
        assert expected_result_false_2[node_num] == is_isolated_uptime(node_num, 0, uptime_schedules_false_2, nodes_count, tplgy, -1)

    print("test_starchain done")


if __name__ == "__main__":
    test_is_isolated_uptime()
    test_star()
    test_chain()
    test_grid()
    test_ring()
    test_clique()
    test_tree_9()
    test_tree_16()
    test_tree_25()
    test_starchain()
