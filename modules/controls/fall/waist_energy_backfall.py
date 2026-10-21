"""T&R 3eacd56 amended: (A) waist energy bound 0.5*I*w^2 on the D99 forward set; (B) backward-fall waist set (standing only).
I = upper-body (waistY subtree incl. arms/head) inertia about the waist-pitch axis at the impact instant, from the model.
w = waist pitch joint speed at range end (MJCF -30/+60 as stop proxy). Bound treats the lower body as fixed [EST upper bound
on relative KE only if lower body is much heavier; it is not - see md]. Light CPU MuJoCo."""
import os, sys, json, math, itertools
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'limits'))
import prone_data as P, knee_stop_impact as K
from drive_thermal_derate import friction_hold
from fall_mode import knee_fall_torque, waist_fall_torque
from soft_limits import waist_stop_zone_tau

def setup(mass, pose, lean):
    s = P.Sim(mass); m, d = s.m, s.d
    wj = [i for i in range(m.njnt) if 'waist' in m.joint(i).name and 'pitch' in m.joint(i).name][0]
    s.place(pose, lean); q = s.target(pose); return s, m, d, wj, q

def I_axis(m, d, wj):
    root = m.jnt_bodyid[wj]; ax = d.xaxis[wj]; an = d.xanchor[wj]; I = 0.0
    for b in range(m.nbody):
        p = b
        while p and p != root: p = m.body_parentid[p]
        if p != root: continue
        R = d.ximat[b].reshape(3, 3); a = R.T @ ax
        r = d.xipos[b] - an; rp = r - ax * (r @ ax)
        I += float(a @ (m.body_inertia[b] * a)) + m.body_mass[b] * float(rp @ rp)
    return I

def run(mass, pose, lean, waist0=None, push=0.0, held=False, T=2.0, waist_B=None, ramp_deg=20.0):
    s, m, d, wj, q = setup(mass, pose, lean)
    wq, wv = m.jnt_qposadr[wj], m.jnt_dofadr[wj]; rng = m.jnt_range[wj].copy()
    wi = [i for i, n in enumerate(s.names) if 'waist' in n and 'pitch' in n]
    if waist0 is not None:
        d.qpos[wq] = math.radians(waist0); mujoco.mj_forward(m, d); q = q.copy()
        if wi: q[wi[0]] = math.radians(waist0)
    for _ in range(30): d.ctrl[:] = s.pd(q); mujoco.mj_step(m, d)
    for i, n in enumerate(s.names): m.dof_frictionloss[s.vadr[i]] = friction_hold(n)
    ki = [s.names.index(n) for n in ('l_knee', 'r_knee')]; lim = 0.5 * s.lim
    kv = [m.jnt_dofadr[m.joint(n).id] for n in ('l_knee', 'r_knee')]; kq = [m.jnt_qposadr[m.joint(n).id] for n in ('l_knee', 'r_knee')]
    pel = m.body('pelvis').id; head = m.body('head').id; tor = m.body('torso').id
    feet = {m.body('L_foot').id, m.body('R_foot').id}
    ends = {'lo': None, 'hi': None}; first = None; hv = None; tv = None; pF = 0.0; vmax = 0.0
    nst = int(T / m.opt.timestep); f6 = np.zeros(6)
    for k in range(nst):
        tau = np.clip(s.pd(q), -lim, lim) if held else np.zeros(m.nu)
        if not held: pass
        else:
            keep = np.zeros(m.nu); 
            if wi: keep[wi[0]] = tau[wi[0]]
            tau = keep
        for j in range(2): tau[ki[j]] = knee_fall_torque(float(d.qpos[kq[j]]), float(d.qvel[kv[j]]), float(lim[ki[j]]))
        if wi:
            xw, vw = float(d.qpos[wq]), float(d.qvel[wv])
            if waist_B is not None:   # TUCK waist damping (fall_mode.waist_fall_torque), replaces the hold
                tau[wi[0]] = waist_fall_torque(xw, vw, waist_B, float(lim[wi[0]]), ramp_deg)
            tau[wi[0]] = waist_stop_zone_tau(xw, tau[wi[0]])   # D102 zero (1ed4d73)
        d.ctrl[:] = tau
        d.xfrc_applied[pel, 0] = -push / 0.1 if k * m.opt.timestep < 0.1 else 0.0
        mujoco.mj_step(m, d)
        x, v = float(d.qpos[wq]), float(d.qvel[wv]); vmax = max(vmax, abs(v))
        for key, hit in (('lo', x <= rng[0] + 1e-3), ('hi', x >= rng[1] - 1e-3)):
            if hit and ends[key] is None:
                I = I_axis(m, d, wj); ends[key] = dict(w=round(v, 3), I=round(I, 3), E_J=round(0.5 * I * v * v, 1), t=round(k * m.opt.timestep, 3))
        for c in range(d.ncon):
            g = d.contact[c]; b = {m.geom_bodyid[g.geom1], m.geom_bodyid[g.geom2]}
            if 0 not in b: continue
            bb = (b - {0}).pop()
            if bb in feet: continue
            if first is None: first = m.body(bb).name
            if bb == head and hv is None: hv = round(float(np.linalg.norm(d.cvel[head][3:])), 2)
            if bb == tor and tv is None: tv = round(float(np.linalg.norm(d.cvel[tor][3:])), 2)
            if bb == pel: mujoco.mj_contactForce(m, d, c, f6); pF = max(pF, abs(f6[0]))
    return dict(mass=mass, lean=lean, waist_B=waist_B, waist0=waist0, push=push, held=held, range_deg=[round(math.degrees(r)) for r in rng],
                peak_w=round(vmax, 2), lo_end=ends['lo'], hi_end=ends['hi'], first_contact=first,
                head_contact_speed=hv, torso_pack_contact_speed=tv, pelvis_peak_normal_N=round(pF))

if __name__ == '__main__':
    A = [dict(case=c, **run(68.0, K.CASES[c][0], l)) for c in K.CASES for l in (0.1, 0.3, 0.5)]
    for r in A: print('A', r, flush=True)
    B = []
    for mass, w0, pu, held in itertools.product((68.0, 72.1), (0, 20, 60), (60, 90, 120), (False, True)):
        r = run(mass, dict(), 0.0, waist0=w0, push=pu, held=held); B.append(r); print('B', r, flush=True)
    json.dump(dict(A=A, B=B), open(os.path.join(H, 'waist_energy_backfall.json'), 'w'), indent=1)
