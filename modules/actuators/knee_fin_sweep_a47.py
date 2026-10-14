"""A47 first-pass fin clash sweep for D69 rev (R-043): knee twin housing + axial fins (12 x 20 mm tall [EST] for +0.05 m2:
2*n*L*h = 0.05 with L 101 mm). Builds model_v4 at L_knee 0..135 (screw stroke follows the pose) and measures the OCC distance
from the knee twin housing to every other left-leg part except its own mates (screws/rods, trunnions, knee lever, rod ends).
Fin clash where distance < 20 + 1 mm. -> results/knee_fin_sweep_a47.json"""
import sys, os, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '../model'))
import model_v4 as M
SKIP = ('knee twin housing', 'knee trunnion cheek', 'knee trunnion pin', 'L_knee screw')   # own mates only
rows = []
POSES = [dict(L_knee=float(a)) for a in range(0, 136, 15)] + [dict(L_knee=k, L_hip_pitch=hp) for k in (0.0, 135.0) for hp in (-105.0, 40.0)]
for a in POSES:
    P = M.build(a)
    hs = [p for p in P if p['name'].startswith('L_') and 'knee twin housing' in p['name']]
    if not hs: hs = [p for p in P if 'knee twin housing' in p['name'] and p['solid'].Center().y > 0]
    h = hs[0]['solid']; bb = h.BoundingBox()
    near = []
    for p in P:
        if p is hs[0] or any(s in p['name'] for s in SKIP): continue
        b = p['solid'].BoundingBox()
        if b.xmax < bb.xmin-25 or b.xmin > bb.xmax+25 or b.ymax < bb.ymin-25 or b.ymin > bb.ymax+25 or b.zmax < bb.zmin-25 or b.zmin > bb.zmax+25: continue
        near.append((round(float(h.distance(p['solid'])), 1), p['name']))
    near.sort(); rows.append(dict(knee=a, closest=near[:4])); print(a, near[:4], flush=True)
worst = min((r['closest'][0][0], str(r['knee']), r['closest'][0][1]) for r in rows if r['closest'])
json.dump(dict(fin_h_mm=20, rows=rows, worst=worst, fin_clash=worst[0] < 21), open(os.path.join(H, 'results/knee_fin_sweep_a47.json'), 'w'), indent=1)
print('worst', worst)
