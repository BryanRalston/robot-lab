"""Hip-pinch keep-out check (T&R ca68f3a spec on ID rev 8b acb9bd5): controller poses, assumed walk/carry ranges and the
job-10 policy action space (ref_cycle +/- 0.25 rad residual per hip joint) vs warn 35 / limit 30 / trip 28 mm. FK only."""
import json, sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import hip_pinch as H
ROOT = Path(__file__).resolve().parents[3]; R = np.pi / 180
def both(sp):
    return {f'{sd}_{k}': v for k, v in sp.items() for sd in 'lr'}
poses = {
    'stand': {}, 'safe-sit crouch [approx hip -0.6]': {'hip_pitch': -0.6},
    'KNEEL_W1': {'hip_pitch': -1.45}, 'KNEEL_POSE': {'hip_pitch': -0.6}, 'POSE_KNEEL': {'hip_pitch': -0.3},
    'chest-lower start POSE_HANDS': {'hip_pitch': -0.9}, 'chest-lower end POSE_PRONE': {'hip_pitch': 0.0},
    'kneel_hold A': {'hip_pitch': 0.0}, 'kneel_hold B sit-back': {'hip_pitch': -0.9}, 'kneel_hold C': {'hip_pitch': -1.45},
    'kneel_hold D': {'hip_pitch': -1.4}, 'sit 0.45 m [approx hip -1.57]': {'hip_pitch': -1.57},
    'fall tuck B knee drop [approx hip -1.0]': {'hip_pitch': -1.0}, 'deep crouch hip -105 (limit)': {'hip_pitch': -105 * R},
    'hip extension +40 (limit)': {'hip_pitch': 40 * R},
}
out = dict(thresholds_mm=[H.WARN, H.LIMIT, H.TRIP], poses=[], sweeps={})
for nm, sp in poses.items():
    G = H.gaps(both(sp)); g = min(G.values())
    out['poses'].append(dict(pose=nm, min_mm=round(g, 1), pair=min(G, key=G.get), status=H.status(g)))
rng = np.random.default_rng(0)
def sweep(tag, n, gen):
    worst = (1e9, None, None); cnt = dict(ok=0, warn=0, limit=0, trip=0)
    for _ in range(n):
        q = gen(); G = H.gaps(q); g = min(G.values()); cnt[H.status(g)] += 1
        if g < worst[0]: worst = (g, {k: round(float(np.degrees(v)), 1) for k, v in q.items()}, min(G, key=G.get))
    out['sweeps'][tag] = dict(n=n, min_mm=round(worst[0], 1), pair=worst[2], worst=worst[1], counts=cnt)
U = lambda a, b: rng.uniform(a, b) * R
sweep('walk_carry_assumed (hip -60..+20, roll +/-5, yaw +/-10 per leg)', 600,
      lambda: {f'{sd}_hip_pitch': U(-60, 20) for sd in 'lr'} | {f'{sd}_hip_roll': U(-5, 5) for sd in 'lr'} |
              {f'{sd}_hip_yaw': U(-10, 10) for sd in 'lr'})
ref = np.load(ROOT / 'modules/legs/rl/ref_cycle.npz')['q']  # (3 speeds, 200, 30) hinge order; l 0 yaw 1 roll 2 pitch, r 6/7/8
IDX = {'l_hip_yaw': 0, 'l_hip_roll': 1, 'l_hip_pitch': 2, 'r_hip_yaw': 6, 'r_hip_roll': 7, 'r_hip_pitch': 8}
lim = {'l_hip_yaw': (-35, 45), 'r_hip_yaw': (-45, 35), 'l_hip_roll': (-12, 15), 'r_hip_roll': (-15, 12),
       'l_hip_pitch': (-105, 40), 'r_hip_pitch': (-105, 40)}
def gen_policy(corner=False):
    sp, k = rng.integers(3), rng.integers(200); q = {}
    for n, i in IDX.items():
        res = (rng.choice([-0.25, 0.25]) if corner else rng.uniform(-0.25, 0.25))
        q[n] = float(np.clip(ref[sp, k, i] + res, lim[n][0] * R, lim[n][1] * R))
    return q
sweep('job10 action space: ref_cycle + uniform +/-0.25 rad (hips, clipped to mirrored ROM)', 600, gen_policy)
sweep('job10 action space: ref_cycle + corner +/-0.25 rad', 600, lambda: gen_policy(True))
def gen_stand(corner=False):
    return {n: float(np.clip((rng.choice([-0.25, 0.25]) if corner else rng.uniform(-0.25, 0.25)), lim[n][0] * R, lim[n][1] * R)) for n in IDX}
sweep('stand mode: home + corner +/-0.25 rad', 400, lambda: gen_stand(True))
out['ref_cycle_hip_ranges_deg'] = {n: [round(float(np.degrees(ref[:, :, i].min())), 1), round(float(np.degrees(ref[:, :, i].max())), 1)] for n, i in IDX.items()}
Path(__file__).with_name('bilateral_panel_check.json').write_text(json.dumps(out, indent=1))
for p in out['poses']: print(p)
for k, v in out['sweeps'].items(): print(k, v['min_mm'], v['pair'], v['counts'], v['worst'])
print(out['ref_cycle_hip_ranges_deg'])
