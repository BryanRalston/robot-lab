"""Hip-yaw clearance check (model_v4, r116b knee housing): per side, mirrored ranges L -35..+40, R -40..+35
(Legs ruling 2026-10-21). Reports every pose where a moved part comes within 3 mm of a non-moved part (non-mates).
Writes out/clash_hipyaw_clear_v4.json."""
import json, os, itertools
import model_v4 as M
from clash_v4 import bb, ov, mate
THR = 3.0
RANGES = {'L_hip_yaw': (-35, 40), 'R_hip_yaw': (-40, 35)}
out = {}
for jn, (lo, hi) in RANGES.items():
    rows = []
    for a in sorted(set(list(range(lo, hi + 1, 5)) + [lo, hi])):
        if a == 0: continue
        parts = M.build({jn: a}); mv = [jn in p['deps'] for p in parts]
        B = [bb(p, THR) for p in parts]; near = []
        for i, j in itertools.combinations(range(len(parts)), 2):
            if mv[i] == mv[j] or not ov(B[i], B[j]) or mate(parts[i], parts[j]): continue
            try: dist = parts[i]['solid'].distance(parts[j]['solid'])
            except Exception: continue
            if dist < THR: near.append((parts[i]['name'], parts[j]['name'], round(dist, 2)))
        rows.append(dict(angle=a, under_3mm=sorted(near, key=lambda x: x[2])[:6]))
        print(jn, a, len(near), near[:2], flush=True)
    out[jn] = dict(range=[lo, hi], poses=rows, min_clear_poses=[r for r in rows if r['under_3mm']])
json.dump(out, open(os.path.join(M.HERE, 'out', 'clash_hipyaw_clear_v4.json'), 'w'), indent=1)
