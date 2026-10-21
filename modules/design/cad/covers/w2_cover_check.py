"""R-125 W2 cover clearance check: head shell + torso cover (site v4 frame, mm) vs W2 shoulder pad on the roll axis
(36.5 mm standout beyond the OD108 housing flange) + R14 housing. r15 carrier not committed -> R14 housing + R10 core envelope.
Site frame: X fore-aft, Y up, Z lateral (L shoulder_roll at (0,1500,-260), joints_v4.json). Arms frame (left side):
x = X, y_out = -(Z+260), z = Y-1500. Right side mirrors. Triangles sampled (barycentric grid) for distances."""
import json, numpy as np, re
def load_stl(f):
    v = np.array([list(map(float, l.split()[1:])) for l in open(f) if l.strip().startswith("vertex")]); return v.reshape(-1, 3, 3)
def sample(T, n=6):
    P = []
    for i in range(n+1):
        for j in range(n+1-i):
            a, b = i/n, j/n; P.append(T[:, 0]*(1-a-b) + T[:, 1]*a + T[:, 2]*b)
    return np.concatenate(P)
def to_arms(P): return np.c_[P[:, 0], -(P[:, 2]+260.0), P[:, 1]-1500.0]
R_FL, STAND = 54.0, 36.5
pad = dict(x=(-31, 31), y=(R_FL+STAND-82.3, R_FL+STAND), z=(-31, 31))   # tray+core+EPP 82.3 deep, outer face y 90.5
def d_box(P, b):
    q = np.stack([np.maximum(np.maximum(b[k][0]-P[:, i], P[:, i]-b[k][1]), 0) for i, k in enumerate("xyz")], 1)
    inside = np.all([(P[:, i] > b[k][0]) & (P[:, i] < b[k][1]) for i, k in enumerate("xyz")], 0)
    return np.linalg.norm(q, axis=1), inside
def d_cyl(P, r=R_FL, x=(-7.5, 7.5)):
    rr = np.hypot(P[:, 1], P[:, 2]); dr = np.maximum(rr-r, 0); dx = np.maximum(np.maximum(x[0]-P[:, 0], P[:, 0]-x[1]), 0)
    return np.hypot(dr, dx), (dr == 0) & (dx == 0)
out = {}
for nm in ("head_shell", "torso_cover"):
    P = to_arms(sample(load_stl(nm+".stl")))
    dp, ip = d_box(P, pad); dh, ih = d_cyl(P)
    out[nm] = {"min_clear_pad_mm": round(float(dp.min()), 1), "pts_inside_pad": int(ip.sum()),
               "min_clear_housing_mm": round(float(dh.min()), 1), "pts_inside_housing": int(ih.sum()),
               "closest_pt_to_pad_armsframe": np.round(P[dp.argmin()], 1).tolist()}
out["pad_envelope_armsframe"] = pad; out["note"] = "torso mesh = 28-tri coarse envelope; R14 housing (r15 carrier not in repo)"
json.dump(out, open("w2_cover_check.json", "w"), indent=1); print(json.dumps(out))
