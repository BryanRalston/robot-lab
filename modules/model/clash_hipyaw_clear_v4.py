"""Hip yaw/roll clearance check (model_v4, r116b knee housing) on the FINAL L90 surface (Legs 8569e3a + yaw_min update
2026-10-21): L roll -10..15 (yaw -12..+28 for r>=-3; coupled to +10/-5 at r=-12, checked to -10 controlled limit and -12
crush corner), R mirrored. Arms hang at default pose, so the hanging hand is among the non-moved parts checked.
Reports every pose where a moved part comes within 3 mm of a non-moved part (non-mates). Writes out/clash_hipyaw_clear_v4.json."""
import json, os, itertools, sys
import model_v4 as M
from clash_v4 import bb, ov, mate
THR = 3.0
def band(r):
    a = max(-3 - r, 0); return -12 + 7 / 9 * a, 28 - 2 * a
POSES = []
for r in (15, 0, -3, -6, -10, -12):
    lo, hi = band(r); POSES += [(r, round(lo, 2)), (r, round(hi, 2))]
POSES += [(0, 0), (-10, 0)]
out = {}
for S, sg in (('L', 1), ('R', -1)):
    rows = []
    for r, y in POSES:
        if S == 'R' and r == 15: r_ = -15
        pose = {f'{S}_hip_roll': sg * r, f'{S}_hip_yaw': sg * y}
        parts = M.build(pose); mv = [any(j in p['deps'] for j in pose) for p in parts]
        B = [bb(p, THR) for p in parts]; near = []
        for i, j in itertools.combinations(range(len(parts)), 2):
            if mv[i] == mv[j] or not ov(B[i], B[j]) or mate(parts[i], parts[j]): continue
            try: dist = parts[i]['solid'].distance(parts[j]['solid'])
            except Exception: continue
            if dist < THR: near.append((parts[i]['name'], parts[j]['name'], round(dist, 2)))
        rows.append(dict(roll=sg * r, yaw=sg * y, under_3mm=sorted(near, key=lambda x: x[2])[:6]))
        print(S, sg * r, sg * y, len(near), near[:3], flush=True)
    out[S] = dict(poses=rows, min_clear_poses=[x for x in rows if x['under_3mm']])
json.dump(out, open(os.path.join(M.HERE, 'out', 'clash_hipyaw_clear_v4.json'), 'w'), indent=1)
