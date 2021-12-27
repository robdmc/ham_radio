#! /usr/bin/env python

import os
import sys
import re
import math

in_file_name, n_radials = sys.argv[1], sys.argv[2]
n_radials = int(n_radials)



def get_radial(template, angle):
    out = template
    # return out
    out =  re.sub(r"cos\(.*?\)", f"cos({angle})", out)
    out =  re.sub(r"sin\(.*?\)", f"sin({angle})", out)
    return out

def replace_tag(line, tag):
    out = line
    if (line.startswith('GW') or line.startswith('LD')) and not line.endswith('radiator'):
        if line.startswith('LD'):
            out = re.sub(r"(?P<pref>(GW|LD).*?\d+.*?)\d+", r"\g<pref>" + f"{tag[0]}", line)
        else:
            out = re.sub(r"(?P<pref>(GW|LD).*?)\d+", r"\g<pref>" + f"{tag[0]}", line)
        tag[0] += 1
    return out


radials_unprinted = True
loads_unprinted = True

rex_radial = re.compile(r"^GW.*'radial$")
tag = [1]

for line in open(in_file_name).readlines():
    line = line.strip()
    # print(line)
    # continue
    # if line.endswith('radiator'):
    #     print('****', line)
    #     continue

    if rex_radial.match(line):
        if radials_unprinted:
            dtheta = 360 / n_radials
            for nn in range(n_radials):
                angle = dtheta * nn
                out_line = get_radial(line, angle)
                out_line = replace_tag(out_line, tag)
                print(out_line)

            radials_unprinted = False

    elif line.startswith('LD') and (not line.endswith('radiator')) and loads_unprinted:
        for nn in range(1, n_radials + 1):
            outline = replace_tag(line, [nn])
            print(outline)
        loads_unprinted = False

    else:
        out_line = replace_tag(line, tag)
        print(out_line)
