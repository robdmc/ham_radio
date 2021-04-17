#! /usr/bin/env python


def read_touchstone(file_name):
    import pandas as pd
    with open(file_name) as buff:
        rec_list = []
        for line in buff.readlines():
            line = line.strip()
            if line.startswith('!'):
                continue
            elif line.startswith('#'):
                words = line.split()
                z0 = float(words[-1])
            else:
                freq, r, x = [float(w) for w in line.split()]
                rec_list.append({
                    'f': freq,
                    'r': z0 * r,
                    'x': z0 * x,
                })
    return pd.DataFrame(rec_list)



