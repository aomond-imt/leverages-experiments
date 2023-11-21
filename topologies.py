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
    # Aggregator
    t_ss_sp = [[f"t_ss_sp_{dep_num}_provide", dep_time, None] for dep_num, dep_time in enumerate([
        7.04, 10.72, 6.27, 9.08, 3.51, 8.47, 3.21, 14.08, 5.14, 5.36,
        6.46, 5.02, 5.42, 6.41, 7.65, 6.71, 3.48, 3.15, 4.86, 7.31,
        14.78, 3.45, 5.44, 26.9, 4.08, 8.88, 6.72, 5.95, 26.26, 2.83,
    ][:nb_msrmt])]
    t_sr_deps = [[f"t_sr_{dep_num}", 0, f"t_dr_{dep_num}"] for dep_num in range(nb_msrmt)]
    t_sr = [["t_sr", 10.51, None]]
    aggtor = [t_ss_sp, t_sr_deps, t_sr]

    # Measurement
    msrmts = []
    for dep_num, dep_times in enumerate([
        (1.52, 16.69), (21.13, 1.52), (2.52, 2.29), (1.98, 2.41), (1.65, 1.4), (4.02, 3.8), (3.42, 2.8), (2.1, 9.21), (3.97, 1.46), (2.52, 12.82),
        (4.47, 1.81), (2.95, 2.62), (1.22, 3.88), (3.26, 22.04), (5.88, 7.29), (1.99, 1.09), (5.08, 3.01), (1.04, 8.07), (12.14, 2.97), (7.43, 1.99),
        (8.26, 4.37), (16.6, 2.1), (7.09, 3.86), (6.1, 5.8), (1.88, 4.46), (2.84, 3.93), (10.88, 3.52), (1.16, 6.97), (2.31, 1.05), (6.63, 3.0)
    ][:nb_msrmt]):
        t_du, t_dr = dep_times
        msrmts.append([[[f"t_di_{dep_num}", t_du, f"t_ss_sp_{dep_num}_provide"]], [[f"t_dr_{dep_num}", t_dr, None]]])

    return aggtor, msrmts


def tasks_list_coord(coord_name):
    tasks_list = {
        "deploy": deploy_tasks_list,
        "update": update_tasks_list
    }
    return tasks_list[coord_name]


def tasks_list_agg_0(coord_name, nb_msrmt):
    aggtor, msrmts = tasks_list_coord(coord_name)(nb_msrmt)
    return [
        aggtor,
        *msrmts
    ]


def tasks_list_agg_middle(coord_name, nb_msrmt):
    aggtor, msrmts = tasks_list_coord(coord_name)(nb_msrmt)
    return [
        *msrmts[:nb_msrmt//2],
        aggtor,
        *msrmts[nb_msrmt//2:]
    ]


def tasks_list_grid_fav(coord_name, nb_msrmt):
    aggtor, msrmts = tasks_list_coord(coord_name)(nb_msrmt)
    nodes_count = nb_msrmt + 1
    line_width = int(nodes_count**.5)
    agg_num = (line_width//2) + line_width * (line_width//2)
    return [
        *msrmts[:agg_num],
        aggtor,
        *msrmts[agg_num:]
    ]
