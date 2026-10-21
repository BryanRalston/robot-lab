"""Arm envelope vs knee rear-outlet shroud (T&R 2e9b25c R-143 B2 condition). RL Controls.
Light: MuJoCo forward kinematics + mj_geomDistance only (no dynamics).
Shroud: ID HANDLING_MAP N1 (P-156 rev 6 / Option B): x -76..-20, y 89..171, z 860..882 mm in the standing
frame, taken rigidly on L_thigh. Envelope case widens the outboard edge to the T&R limit y=176.
Hand = sim/v3 hand box geom. Distance = min surface-to-surface (mm). Right side by mirror symmetry;
the right hand reaching across to the left shroud is also checked."""
import json, re, sys, numpy as np, mujoco
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
XML = (ROOT / 'sim/v3/humanoid_v3.xml').read_text()
D2R = np.pi / 180
THIGH0 = np.array([0.0, 0.130, 0.920])  # L_thigh origin, standing, joints zero

def model(y_out):
    lo = np.array([-0.076, 0.089, 0.860]); hi = np.array([-0.020, y_out, 0.882])
    c = (lo + hi) / 2 - THIGH0; h = (hi - lo) / 2
    g = (f'<geom name="kshroud" type="box" pos="{c[0]:.4f} {c[1]:.4f} {c[2]:.4f}" '
         f'size="{h[0]:.4f} {h[1]:.4f} {h[2]:.4f}" contype="0" conaffinity="0"/>')
    x = re.sub(r'(<body name="L_thigh"[^>]*>)', r'\1' + g, XML, count=1)
    m = mujoco.MjModel.from_xml_string(x)
    return m, mujoco.MjData(m)

ARM = ['shoulder_pitch', 'shoulder_roll', 'shoulder_yaw', 'elbow', 'wrist_roll', 'wrist_pitch', 'wrist_yaw']
LEG = ['l_hip_yaw', 'l_hip_roll', 'l_hip_pitch', 'l_knee', 'waist_yaw', 'waist_pitch']

def ranges(m, side):
    r = {}
    for j in ARM:
        lo, hi = m.jnt_range[m.joint(f'{side}_{j}').id] / D2R
        if j == 'shoulder_roll':  # R-133 soft limit 127 deg abduction (left +, right -)
            lo, hi = (lo, 127.0) if side == 'l' else (-127.0, hi)
        r[j] = (lo, hi)
    return r

def dist(m, d, q, hand):
    d.qpos[:] = 0; d.qpos[2] = 1.16; d.qpos[3] = 1
    for n, v in q.items(): d.qpos[m.jnt_qposadr[m.joint(n).id]] = v * D2R
    mujoco.mj_kinematics(m, d)
    ft = np.zeros(6)
    return 1000 * mujoco.mj_geomDistance(m, d, m.geom(hand).id, m.geom('kshroud').id, 1.0, ft)

def armq(side, v):
    return {f'{side}_{j}': v[i] for i, j in enumerate(ARM)}

def sweep(m, d, side, arm_rng, leg_rng, n, rng, label):
    best = (1e9, None)
    def ev(a, l):
        q = armq(side, a); q.update(dict(zip(LEG, l)))
        return dist(m, d, q, f'{side}_hand'), q
    A = [np.array(arm_rng[j]) for j in ARM]; L = [np.array(leg_rng[j]) for j in LEG]
    for _ in range(n):
        a = [rng.uniform(*x) for x in A]; l = [rng.uniform(*x) for x in L]
        dd, q = ev(a, l)
        if dd < best[0]: best = (dd, q, a, l)
    # local refinement around the worst sample (clipped to range)
    _, _, a, l = best; step = 0.1
    for it in range(1500):
        a2 = [float(np.clip(v + rng.normal(0, step * (x[1] - x[0])), *x)) for v, x in zip(a, A)]
        l2 = [float(np.clip(v + rng.normal(0, step * (x[1] - x[0])), *x)) for v, x in zip(l, L)]
        dd, q = ev(a2, l2)
        if dd < best[0]: best = (dd, q, a2, l2); a, l = a2, l2
        if it % 300 == 299: step *= 0.5
    return {'case': label, 'hand': f'{side}_hand', 'min_mm': round(best[0], 1),
            'worst_pose_deg': {k: round(v, 1) for k, v in best[1].items()}}

def fixed(m, d, side, a, label, legs):
    out = []
    for ln, l in legs.items():
        q = armq(side, a); q.update(l); out.append((dist(m, d, q, f'{side}_hand'), ln))
    dd, ln = min(out)
    return {'case': label, 'hand': f'{side}_hand', 'min_mm': round(dd, 1), 'worst_leg_pose': ln,
            'arm_deg': dict(zip(ARM, a))}

def main(n=int(sys.argv[1]) if len(sys.argv) > 1 else 20000):
    rng = np.random.default_rng(0); res = {}
    R = 180 / np.pi
    # leg/waist poses: standing, crouch/kneel/prone waypoints (modules/controls/limits, rad -> deg)
    wp = {'stand': {},
          'KNEEL_W1': {'l_hip_pitch': -1.45 * R, 'l_knee': 1.70 * R, 'waist_pitch': 0.8 * R},
          'KNEEL_POSE': {'l_hip_pitch': -0.6 * R, 'l_knee': 1.9 * R, 'waist_pitch': 0.4 * R},
          'POSE_KNEEL': {'l_hip_pitch': -0.3 * R, 'l_knee': 1.6 * R, 'waist_pitch': 0.2 * R},
          'POSE_HANDS': {'l_hip_pitch': -0.9 * R, 'l_knee': 1.5 * R, 'waist_pitch': 0.4 * R},
          'POSE_PRONE': {'l_hip_pitch': 0.0, 'l_knee': 0.3 * R, 'waist_pitch': 0.0},
          'carry_waist_lean': {'waist_pitch': -0.25 * R}}
    for y_out in (0.171, 0.176):
        m, d = model(y_out); key = f'shroud_y{int(round(y_out*1000))}'; rr = []
        legfull = {j: tuple(m.jnt_range[m.joint(j).id] / D2R) for j in LEG}
        for side in 'lr':
            ar = ranges(m, side)
            mir = -1 if side == 'r' else 1
            # fixed controller arm poses (shoulder roll/yaw mirrored for the right arm)
            P042 = [-60, 0, 0, -110, 0, 0, 0]
            TUCKB = [5, 0, 0, 0, 0, 0, 0]
            LB = [30, -15 * mir, 30 * mir, -75, 0, 0, 0]
            HOME = [0] * 7
            for nm, a in (('home/hanging', HOME), ('P-042 carry', P042), ('fall tuck B', TUCKB), ('LB fallback +30/-15/+30/-75', LB)):
                rr.append(fixed(m, d, side, a, nm, wp))
            # waypoint arm shoulder_pitch/elbow
            for nm, w in (('POSE_KNEEL', [-1.3*R,0,0,0,0,0,0]), ('POSE_HANDS', [-1.4*R,0,0,0.3*R,0,0,0]),
                          ('POSE_PRONE', [-0.3*R,0,0,1.8*R,0,0,0]), ('KNEEL_W1', [-1.2*R,0,0,0,0,0,0])):
                w = [w[0], w[1], w[2], float(np.clip(w[3], *ar['elbow'])), 0, 0, 0]
                rr.append(fixed(m, d, side, w, f'{nm} arms (elbow clipped to MJCF range)', {nm: wp[nm]}))
            # policy residual +/-0.25 rad (14.3 deg) about home and about P-042 [ASSUMED offsets]
            for nm, base in (('walk policy home +/-0.25 rad', HOME), ('carry policy P-042 +/-0.25 rad', P042)):
                pr = {j: (max(ar[j][0], b - 14.3), min(ar[j][1], b + 14.3)) for j, b in zip(ARM, base)}
                lr = dict(legfull); lr['l_knee'] = (0, 135)
                rr.append(sweep(m, d, side, pr, lr, n // 4, rng, nm + ' x full leg/waist range'))
            rr.append(sweep(m, d, side, ar, legfull, n, rng, 'full arm soft-limit range x full leg/waist range'))
        res[key] = rr
    out = Path(__file__).with_name('arm_knee_shroud_clearance.json')
    out.write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))

if __name__ == '__main__':
    main()
