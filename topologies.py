import json
import os

import numpy as np


def clique(nodes_count, bw):
    B = np.full((nodes_count, nodes_count), bw)
    L = np.full((nodes_count, nodes_count), 0)
    return B, L


def symmetricize(arr1D):
    ID = np.arange(arr1D.size)
    return arr1D[np.abs(ID - ID[:,None])]


def chain(nodes_count, bw):
    if nodes_count < 3:
        node_0 = np.array([bw]*nodes_count)
    else:
        node_0 = np.array([bw, bw] + [0]*(nodes_count-2))
    B = symmetricize(node_0)
    L = np.full((nodes_count, nodes_count), 0)
    return B, L


def ring(nodes_count, bw):
    if nodes_count < 4:
        node_0 = np.array([bw]*nodes_count)
    else:
        node_0 = np.array([bw, bw] + ([0]*(nodes_count-3)) + [bw])
    B = symmetricize(node_0)
    L = np.full((nodes_count, nodes_count), 0)
    return B, L


def star(nodes_count, bw):
    all_arrays = [np.array([bw]*nodes_count)]
    for dep_num in range(1, nodes_count):
        dep_t = [bw, *[0]*(nodes_count-1)]
        dep_t[dep_num] = bw
        all_arrays.append(np.array(dep_t))
    L = np.full((nodes_count, nodes_count), 0)
    B = np.asarray(all_arrays)
    return B, L


def grid(nodes_count, bw):
    if nodes_count == 4:
        return ring(4, bw)

    res = []
    line_length = int(nodes_count**.5)
    for node_num in range(nodes_count):
        node_x, node_y = node_num%line_length, node_num//line_length
        res_node = []
        for other_node_num in range(nodes_count):
            other_node_x, other_node_y = other_node_num % line_length, other_node_num // line_length
            if abs(node_x - other_node_x) + abs(node_y - other_node_y) <= 1:
                res_node.append(bw)
            else:
                res_node.append(0)
        res.append(np.array(res_node))

    B = np.array(res)
    L = np.full((nodes_count, nodes_count), 0)

    return B, L


def tree(nodes_count, bw):
    L = np.full((nodes_count, nodes_count), 0)
    B = None
    if nodes_count == 9:
        B = [
            [bw, bw, bw, 0, 0, 0, 0, 0, 0],
                [bw, 0, bw, bw, 0, 0, 0, 0],
                    [bw, 0, 0, bw, bw, 0, 0],
                        [bw, 0, 0, 0, bw, 0],
                            [bw, 0, 0, 0, 0],
                                [bw, 0, 0, 0],
                                    [bw, 0, bw],
                                        [bw, 0],
                                            [bw]
        ]
    elif nodes_count == 16:
        B = [
            [bw, bw, bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [bw, 0, bw, bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [bw, 0, 0, bw, bw, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [bw, 0, 0, 0, bw, bw, 0, 0, 0, 0, 0, 0, 0],
                            [bw, 0, 0, 0, 0, bw, bw, 0, 0, 0, 0, 0],
                                [bw, 0, 0, 0, 0, 0, bw, bw, 0, 0, 0],
                                    [bw, 0, 0, 0, 0, 0, 0, bw, bw, 0],
                                        [bw, 0, 0, 0, 0, 0, 0, 0, bw],
                                            [bw, 0, 0, 0, 0, 0, 0, 0],
                                                [bw, 0, 0, 0, 0, 0, 0],
                                                    [bw, 0, 0, 0, 0, 0],
                                                        [bw, 0, 0, 0, 0],
                                                            [bw, 0, 0, 0],
                                                                [bw, 0, 0],
                                                                    [bw, 0],
                                                                        [bw],
        ]
    elif nodes_count == 25:
        B = [
            [bw, bw, bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [bw, 0, bw, bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [bw, 0, 0, bw, bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [bw, 0, 0, 0, bw, bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [bw, 0, 0, 0, 0, bw, bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                [bw, 0, 0, 0, 0, 0, bw, bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    [bw, 0, 0, 0, 0, 0, 0, bw, bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                        [bw, 0, 0, 0, 0, 0, 0, 0, bw, bw, 0, 0, 0, 0, 0, 0, 0, 0],
                                            [bw, 0, 0, 0, 0, 0, 0, 0, 0, bw, bw, 0, 0, 0, 0, 0, 0],
                                                [bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, bw, bw, 0, 0, 0, 0],
                                                    [bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, bw, bw, 0, 0],
                                                        [bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, bw, bw],
                                                            [bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                                                [bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                                                    [bw, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                                                        [bw, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                                                            [bw, 0, 0, 0, 0, 0, 0, 0, 0],
                                                                                [bw, 0, 0, 0, 0, 0, 0, 0],
                                                                                    [bw, 0, 0, 0, 0, 0, 0],
                                                                                        [bw, 0, 0, 0, 0, 0],
                                                                                            [bw, 0, 0, 0, 0],
                                                                                                [bw, 0, 0, 0],
                                                                                                    [bw, 0, 0],
                                                                                                        [bw, 0],
                                                                                                            [bw],
        ]

    cpt = -1
    for m in range(len(B)-2, -1, -1):
        for i in range(m, -1, -1):
            B[m+1].insert(0, B[i][cpt])

        cpt -= 1

    return B, L


def deploy_tasks_list(nb_msrmt):
    # Aggregator
    t_sa = [["t_sa", 1.03, None]]
    t_sc = [[f"t_sc_{dep_num}", dep_time, f"t_di_{dep_num}"] for dep_num, dep_time in enumerate([
        6.35, 2.56, 5.94, 6.33, 7.2, 5.35, 4.86, 1.06, 3.46, 1.8, 1.82, 1.8, 3.63, 1.32, 1.14,
        1.46, 1.84, 2.2, 1.62, 12.99, 1.52, 1.16, 1.25, 5.19, 4.01, 6.36, 6.47, 5.75, 19.39, 3.12
    ][:nb_msrmt])]
    t_sr_deps = [[f"t_sr_{dep_num}", 0, f"t_dr_{dep_num}"] for dep_num in range(nb_msrmt)]
    t_sr = [["t_sr", 10.51, None]]
    aggtor = [t_sa, t_sc, t_sr_deps, t_sr]

    # Measurement
    msrmts = []
    for dep_num, dep_times in enumerate([
        (4.99, 16.69), (1.25, 1.52), (5.26, 2.29), (9.82, 2.41), (5.68, 1.40), (7.92, 3.8), (3.66, 2.8), (1.34, 9.21), (2.31, 1.46), (12.53, 12.82),  # 0-9
        (3.21, 1.81), (1.33, 2.62), (1.99, 3.88), (1.88, 22.04), (3.67, 7.29), (2.98, 1.09), (4.39, 3.01), (5.76, 8.07), (5.95, 2.97), (2.56, 1.99),  # 10-19
        (1.4, 4.37), (3.71, 2.1), (3.43, 3.86), (3.61, 5.8), (2.34, 4.46), (2.3, 3.93), (15.47, 3.52), (9.04, 6.97), (3.4, 1.05), (1.33, 3.0)         # 20-29
    ][:nb_msrmt]):
        t_di, t_dr = dep_times
        msrmts.append([[[f"t_di_{dep_num}", t_di, None]], [[f"t_dr_{dep_num}", t_dr, None]]])

    return aggtor, msrmts


def update_tasks_list(nb_msrmt):
    # Load transitions times
    with open(f"{os.environ['HOME']}/journal-pdc-experiments/transitions_duration.json") as f:
        tt = json.load(f)["transitions_times"]

    # Aggregator
    t_ss_sp_times = [t_ss + t_sp for t_ss, t_sp in zip(tt["server"]["t_ss"], tt["server"]["t_sp"])][:nb_msrmt]
    t_ss_sp = [[f"t_ss_sp_{dep_num}_provide", dep_time, None] for dep_num, dep_time in enumerate(t_ss_sp_times)]
    t_sr_deps = [[f"t_sr_{dep_num}", 0, f"t_dr_{dep_num}"] for dep_num in range(nb_msrmt)]
    t_sr = [["t_sr", tt["server"]["t_sr"], None]]
    aggtor = [t_ss_sp, t_sr_deps, t_sr]

    # Measurement
    t_du_dr = [(tt[f"dep{dep_num}"]["t_du"], tt[f"dep{dep_num}"]["t_dr"]) for dep_num in range(nb_msrmt)]
    msrmts = []
    for dep_num, dep_times in enumerate(t_du_dr):
        t_du, t_dr = dep_times
        msrmts.append([[[f"t_du_{dep_num}", t_du, f"t_ss_sp_{dep_num}_provide"]], [[f"t_dr_{dep_num}", t_dr, None]]])

    return aggtor, msrmts


def tasks_list_agg_0(nb_msrmt):
    aggtor, msrmts = update_tasks_list(nb_msrmt)
    agg_num = 0
    rn_num = nb_msrmt//2
    return agg_num, rn_num, [
        aggtor,
        *msrmts
    ]


def tasks_list_agg_middle(nb_msrmt):
    aggtor, msrmts = update_tasks_list(nb_msrmt)
    agg_num = nb_msrmt//2
    rn_num = 0
    return agg_num, rn_num, [
        *msrmts[:agg_num],
        aggtor,
        *msrmts[agg_num:]
    ]


def tasks_list_grid_fav(nb_msrmt):
    aggtor, msrmts = update_tasks_list(nb_msrmt)
    nodes_count = nb_msrmt + 1
    line_width = int(nodes_count**.5)
    agg_num = (line_width//2) + line_width * (line_width//2)
    rn_num = 0
    return agg_num, rn_num, [
        *msrmts[:agg_num],
        aggtor,
        *msrmts[agg_num:]
    ]


def tasks_list_grid_nonfav(nb_msrmt):
    aggtor, msrmts = update_tasks_list(nb_msrmt)
    agg_num = 0
    nodes_count = nb_msrmt + 1
    line_width = int(nodes_count ** .5)
    rn_num = (line_width // 2) + line_width * (line_width // 2)
    return agg_num, rn_num, [
        aggtor,
        *msrmts
    ]


if __name__ == "__main__":
    t_9 = tree(9, 50)
    t_16 = tree(16, 50)
    t_25 = tree(25, 50)

    s_9 = star(9, 50)
    s_16 = star(16, 50)
    s_25 = star(25, 50)

    r_9 = ring(9, 50)
    r_16 = ring(16, 50)
    r_25 = ring(25, 50)

    c_9 = clique(9, 50)
    c_16 = clique(16, 50)
    c_25 = clique(25, 50)

    chain_9 = chain(9, 50)
    chain_16 = chain(16, 50)
    chain_25 = chain(25, 50)

    g_9 = grid(9, 50)
    g_16 = grid(16, 50)
    g_25 = grid(25, 50)

    a = tasks_list_grid_nonfav(8)
    b = tasks_list_grid_nonfav(15)
    c = tasks_list_grid_nonfav(24)

    d = tasks_list_grid_fav(8)
    e = tasks_list_grid_fav(15)
    f = tasks_list_grid_fav(24)

    A = tasks_list_agg_0(8)
    B = tasks_list_agg_0(15)
    C = tasks_list_agg_0(24)

    D = tasks_list_agg_middle(8)
    E = tasks_list_agg_middle(15)
    F = tasks_list_agg_middle(24)
    print()
