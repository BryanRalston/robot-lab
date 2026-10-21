"""Exact (grid) boundary of the 28 mm hip-pinch keep-out in sim/v3 joint space (mirrored ROM: left yaw -35..45, roll -12..15,
right mirrored; pitch -105..40). Writes hip_pinch_boundary.json. ~4 min, one core."""
import json, sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import hip_pinch as H
from scipy.spatial import cKDTree
R = np.radians; g = H.geometry(); T, P, mir, KT = g['T'], g['P'], g['mir'], g['KT']
PS = np.arange(-105, 40.1, 5); RS = np.r_[np.arange(-12, 15.1, 2), 15.0]; YS = np.arange(-35, 45.1, 2.5)
hem = np.zeros((len(PS), len(RS), len(YS))); lr = np.zeros_like(hem)
for i, p in enumerate(PS):
    for j, r in enumerate(RS):
        for k, y in enumerate(YS):
            PL = T(P, p, r, y); hem[i, j, k] = KT.query(PL)[0].min()
            lr[i, j, k] = cKDTree(PL).query(mir(PL))[0].min()  # symmetric both-leg (right = mirror of left)
out = dict(grid=dict(pitch=PS.tolist(), roll=RS.tolist(), yaw=YS.tolist()), trip_mm=H.TRIP)
def bound(A, name):
    bad = A < H.TRIP
    # per roll: smallest yaw that violates at any pitch (and the pitch span), and per yaw the roll boundary
    per_roll = {}
    for j, r in enumerate(RS):
        ks = [k for k in range(len(YS)) if bad[:, j, k].any()]
        per_roll[float(r)] = None if not ks else dict(
            yaw_violating=[float(YS[k]) for k in ks],
            pitch_span={float(YS[k]): [float(PS[bad[:, j, k]].min()), float(PS[bad[:, j, k]].max())] for k in ks})
    i, j, k = np.unravel_index(np.argmin(A), A.shape)
    out[name] = dict(min_mm=round(float(A.min()), 1), at=dict(pitch=float(PS[i]), roll=float(RS[j]), yaw=float(YS[k])),
                     n_bad=int(bad.sum()), n=int(bad.size), per_roll=per_roll)
bound(hem, 'hem_single_leg'); bound(lr, 'lr_symmetric')
# asymmetric both-leg random sample (independent legs, mirrored ROM)
rng = np.random.default_rng(0); worst = (1e9, None); nb = 0; N = 1000
for _ in range(N):
    q = {}
    for sd, s in (('l', 1), ('r', -1)):
        q[f'{sd}_hip_pitch'] = R(rng.uniform(-105, 40))
        q[f'{sd}_hip_roll'] = R(s * rng.uniform(-12, 15)); q[f'{sd}_hip_yaw'] = R(s * rng.uniform(-35, 45))
    G = H.gaps(q); gm = min(G.values()); nb += gm < H.TRIP
    if gm < worst[0]: worst = (gm, {k: round(float(np.degrees(v)), 1) for k, v in q.items()}, min(G, key=G.get))
out['asymmetric_random'] = dict(n=N, frac_below_trip=round(nb / N, 4), min_mm=round(worst[0], 1), worst=worst[1], pair=worst[2])
Path(__file__).with_name('hip_pinch_boundary.json').write_text(json.dumps(out, indent=1))
print({k: (v['min_mm'], v.get('at'), v.get('n_bad')) for k, v in out.items() if isinstance(v, dict) and 'min_mm' in v})
