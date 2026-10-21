"""Does the D100 14 N.m hip roll/yaw cap (gap <= warn) break walk, kneel or the side-fall tuck? Runs Controls side_fall.py
(tuck controller, S1/S2b/S2c x L/R x 68 kg x 250/550 N) with and without the cap, patching mj_step in-process (limits/ not edited)."""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '../limits'))
import mujoco, numpy as np
import hip_pinch as H, hip_pinch_cap as C
import side_fall as SF
_step = mujoco.mj_step; STATE = {}
def capped_step(m, d, *a):
    c = STATE.get('cap')
    if c is not None:
        if 'ids' not in STATE:
            STATE['ids'] = {n: (m.jnt_qposadr[m.joint(n).id], m.actuator(n).id) for n in C.CAPPED + [f'{s}_hip_pitch' for s in 'lr']}
        ids = STATE['ids']; q = {n: float(d.qpos[a_]) for n, (a_, _) in ids.items()}
        if c.update(q, d.time):
            for n in C.CAPPED:
                i = ids[n][1]; d.ctrl[i] = float(np.clip(d.ctrl[i], -C.TAU_CAP, C.TAU_CAP))
        g = c.gap; STATE['gmin'] = min(STATE.get('gmin', 1e9), g)
    return _step(m, d, *a)
mujoco.mj_step = capped_step
rows = []
for sc in ('S1', 'S2b', 'S2c'):
    for sd in 'lr':
        for pu in (250.0, 550.0):
            r = {}
            for cap in (False, True):
                STATE.clear(); STATE['cap'] = C.HipPinchTorqueCap() if cap else None
                if not cap: STATE['cap'] = None
                o = SF.run(sc, sd, 68.0, pu, 'tuck')
                if cap: r['cap_active_samples'] = STATE['cap'].n_active; r['gap_min_mm'] = round(STATE.get('gmin', 1e9), 1)
                r['cap' if cap else 'nocap'] = dict(fell=o['fell'], E_max_J=o['E_max_J'], pass_bumper=o['pass_bumper'], z_min=o['torso_z_min_m'])
            r.update(scn=sc, side=sd, push=pu); rows.append(r); print(r, flush=True)
json.dump(rows, open(os.path.join(HERE, 'hip_pinch_cap_check.json'), 'w'), indent=1)
