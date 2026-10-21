"""Static IK check (RL Controls 10:47): can the hands reach the floor with the CoM over the FEET ONLY (hands unloaded)?
Variables: root pitch, hip_pitch, knee, ankle_pitch, waist_pitch, shoulder_pitch, elbow, wrist_pitch (symmetric L/R),
root height set so the lowest foot point is on the floor. Bounds: knee <= 120 deg, hip >= -105 deg, ankle >= -0.955,
others joint ranges; elbow either free or R-151 -5..-10 deg (sim sign negative = flexion).
Constraints: no geom other than feet/hands below the floor (+5 mm), CoM x inside the foot support:
  flat feet: foot tilt 0, CoM x in [heel, toe] - 10 mm;  toe support: CoM x in [toe - 20 mm, toe] [EST toe strip].
Objective: minimise the lowest hand point z. Multi-start SLSQP. Writes reach_ik_check.json."""
import os, sys, json, math, itertools
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chest_lower_wbc as CL
from pose_study_b import geom_zmin
import kneel_toe_wbc as KT

s = CL.make_sim(68.0); m, d = s.m, s.d
JN = ('hip_pitch', 'knee', 'ankle_pitch', 'waist_pitch', 'shoulder_pitch', 'elbow', 'wrist_pitch')
feet = [m.geom('l_foot').id, m.geom('r_foot').id]; hands = [m.geom('l_hand').id, m.geom('r_hand').id]
others = [g for g in range(m.ngeom) if g not in feet + hands and g not in s.floor and m.geom_bodyid[g] != 0]


def rng(n):
    j = m.joint(('l_' if n not in ('waist_pitch',) else '') + n).id; return m.jnt_range[j]


def setx(x):
    pitch = x[0]; spec = dict(zip(JN, x[1:]))
    d.qpos[:] = 0; d.qvel[:] = 0; d.qpos[3:7] = [math.cos(pitch / 2), 0, math.sin(pitch / 2), 0]
    for i, n in enumerate(s.names):
        for k, v in spec.items():
            if n.endswith(k): d.qpos[s.qadr[i]] = v
    d.qpos[2] = 1.0; mujoco.mj_forward(m, d)
    d.qpos[2] -= min(geom_zmin(m, d, g) for g in feet); mujoco.mj_forward(m, d)


def feet_geo():
    pts = [p for g in feet for p in KT.corners(m, d, g, False)]
    toe = max(p[0] for p in pts); heel = min(p[0] for p in pts)
    tilt = max(abs(math.asin(np.clip(d.geom_xmat[g].reshape(3, 3)[2, 0], -1, 1))) for g in feet)
    return toe, heel, tilt


def solve(mode, elbow_r151):
    lb = [0.0]; ub = [2.2]
    for n in JN:
        lo_, hi_ = rng(n)
        if n == 'knee': hi_ = min(hi_, math.radians(120))
        if n == 'hip_pitch': lo_ = max(lo_, math.radians(-105))
        if n == 'ankle_pitch': lo_ = max(lo_, -0.955)
        if n == 'elbow' and elbow_r151: lo_, hi_ = math.radians(-10), math.radians(-5)
        lb.append(lo_); ub.append(hi_)
    bnds = list(zip(lb, ub))
    def obj(x):
        setx(x); return min(geom_zmin(m, d, g) for g in hands)
    def cons(x):
        setx(x); toe, heel, tilt = feet_geo(); cx = d.subtree_com[1][0]
        c = [min(geom_zmin(m, d, g) for g in others) - 0.005]
        if mode == 'flat':
            c += [0.01 - tilt, toe - 0.01 - cx, cx - heel - 0.01]
        else:
            c += [toe - cx, cx - (toe - 0.02)]
        return np.array(c)
    best = None; rs = np.random.RandomState(0)
    for k in range(40):
        x0 = np.array([rs.uniform(a, b) for a, b in bnds])
        r = minimize(obj, x0, method='SLSQP', bounds=bnds, constraints=[dict(type='ineq', fun=cons)], options=dict(maxiter=200, ftol=1e-6))
        if r.success or np.all(cons(r.x) > -1e-3):
            if np.all(cons(r.x) > -1e-3) and (best is None or r.fun < best[0]): best = (float(r.fun), r.x.copy())
    if best is None: return dict(mode=mode, elbow_r151=elbow_r151, solution=None)
    setx(best[1]); toe, heel, tilt = feet_geo()
    return dict(mode=mode, elbow_r151=elbow_r151, hand_z_min_m=round(best[0], 4), root_pitch=round(float(best[1][0]), 3),
                joints_deg={n: round(math.degrees(v), 1) for n, v in zip(JN, best[1][1:])}, com_x_minus_toe_m=round(float(d.subtree_com[1][0] - toe), 4),
                foot_tilt_rad=round(tilt, 3), com_z=round(float(d.subtree_com[1][2]), 3), x=[float(v) for v in best[1]])


if __name__ == '__main__':
    out = [solve(md, e) for md in ('toe', 'flat') for e in (False, True)]
    json.dump(out, open(os.path.join(HERE, 'reach_ik_check.json'), 'w'), indent=1)
    for o in out: print(json.dumps({k: v for k, v in o.items() if k != 'x'}))


def solve_margin(elbow_r151=True, hand_z=0.0):
    """Max CoM margin behind the toe (flat feet) with the hands at the floor (lowest hand point <= hand_z + 2 mm)."""
    lb = [0.0]; ub = [2.2]
    for n in JN:
        lo_, hi_ = rng(n)
        if n == 'knee': hi_ = min(hi_, math.radians(120))
        if n == 'hip_pitch': lo_ = max(lo_, math.radians(-105))
        if n == 'ankle_pitch': lo_ = max(lo_, -0.955)
        if n == 'elbow' and elbow_r151: lo_, hi_ = math.radians(-10), math.radians(-5)
        lb.append(lo_); ub.append(hi_)
    bnds = list(zip(lb, ub))
    def obj(x):
        setx(x); toe, heel, tilt = feet_geo(); return -(toe - d.subtree_com[1][0])
    def cons(x):
        setx(x); toe, heel, tilt = feet_geo(); cx = d.subtree_com[1][0]; hz = min(geom_zmin(m, d, g) for g in hands)
        return np.array([min(geom_zmin(m, d, g) for g in others) - 0.005, 0.01 - tilt, cx - heel - 0.01, hand_z + 0.002 - hz, hz - hand_z + 0.002])
    best = None; rs = np.random.RandomState(1)
    for k in range(40):
        x0 = np.array([rs.uniform(a, b) for a, b in bnds])
        r = minimize(obj, x0, method='SLSQP', bounds=bnds, constraints=[dict(type='ineq', fun=cons)], options=dict(maxiter=300, ftol=1e-7))
        if np.all(cons(r.x) > -1e-3) and (best is None or r.fun < best[0]): best = (float(r.fun), r.x.copy())
    if best is None: return None
    setx(best[1]); toe, heel, tilt = feet_geo()
    return dict(com_margin_behind_toe_m=round(-best[0], 4), foot_len_m=round(toe - heel, 3), root_pitch=round(float(best[1][0]), 3),
                joints_deg={n: round(math.degrees(v), 1) for n, v in zip(JN, best[1][1:])}, x=[float(v) for v in best[1]])
