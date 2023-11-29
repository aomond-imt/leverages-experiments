import json

for u in range(200):
    with open(f"uptimes_schedules/{u}-60.json") as f:
        r = json.load(f)

    for i in range(30):
        for j in range(30):
            if i != j:
                t = 0
                nb_o = 0
                for upt_0, upt_1 in zip(r[i], r[j]):
                    if min(upt_0 + 60, upt_1 + 60) - max(upt_0, upt_1) > 0:
                        nb_o += 1
                    t += 1
                res = round(nb_o/t, 3)
                if res > 0.04 or res < 0.03:
                    print(t, nb_o, res)

