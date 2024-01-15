import time

import numpy as np

random_generator = np.random.default_rng(int(time.time()))

agg_degree = 1
nb_msrmt = 4
B = [[1]*agg_degree + [0]*(nb_msrmt-agg_degree)]  # Aggregator
chance_bw = 0.5
for msrmt_num in range(1, nb_msrmt+1):
    bw_msrmt = [1*bool(random_generator.random(1) < chance_bw) for _ in range(nb_msrmt-msrmt_num)]
    B.append(bw_msrmt)

print(*B,sep="\n")
