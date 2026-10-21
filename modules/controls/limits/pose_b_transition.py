"""Pose study (b) dynamic transition: stand -> hands-and-toes pose (static-feasible from pose_study_b) by a joint-space
minimum-jerk path (T s), derated PD + contact-consistent static ff (support: feet; feet + hands once a hand touches),
knee cap from 120 deg, ankle soft limit; then hold 1 s. 68 kg. Reports fall, hand contact speed / peak force per hand,
knee max, timing."""
import os, sys, json, math, itertools
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chest_lower_wbc as CL
from soft_limits import apply_knee_stop_cap
from drive_thermal_derate import ankle_pitch_min
STAND = dict(hip_pitch=-0.54, knee=1.17, ankle_pitch=-0.63, shoulder_pitch=-0.3, elbow=-0.3)


def run(target, T=3.0, mass=68.0, elbow_cap=38.0, width=0.0, hold=1.0):
    s = CL.make_sim(mass); m, d = s.m, s.d
    for n in ('l_ankle_pitch', 'r_ankle_pitch'): m.jnt_range[m.joint(n).id, 0] = ankle_pitch_min(0.0)
    for i, n in enumerate(s.names):
        if n.endswith('elbow'): s.lim[i] = elbow_cap
    s.place(STAND, 0.0); q0 = s.target(STAND)
    for _ in range(300):
        d.ctrl[:] = s.pd(q0); mujoco.mj_step(m, d)
    q0 = d.qpos[s.qadr].copy(); q1 = s.target(target)
    rl = math.asin(width / 0.8)
    for side, sg in (('l', 1), ('r', -1)):
        q1[s.names.index(f'{side}_hip_roll')] = sg * rl; q1[s.names.index(f'{side}_ankle_roll')] = -sg * rl
    feet = [m.geom('l_foot').id, m.geom('r_foot').id]; hands = [m.geom('l_hand').id, m.geom('r_hand').id]
    hpk = [0.0, 0.0]; hv = [None, None]; f6 = np.zeros(6); kmax = 0.0; t_touch = None; fell = None
    for k in range(int((T + hold) / m.opt.timestep)):
        t = k * m.opt.timestep; u = min(1.0, t / T); a = 10 * u**3 - 15 * u**4 + 6 * u**5
        ad = (30 * u**2 - 60 * u**3 + 30 * u**4) / T if u < 1 else 0.0
        qt = q0 + (q1 - q0) * a; vt = (q1 - q0) * ad
        sup = feet + (hands if t_touch is not None else [])
        tau = np.clip(s.pd(qt, vt) + CL.static_ff(m, d, sup, s.vadr), -s.lim, s.lim)
        apply_knee_stop_cap(s.names, lambda n: float(d.qpos[s.qadr[s.names.index(n)]]), tau, 'KNEEL')
        d.ctrl[:] = tau; mujoco.mj_step(m, d)
        for ci in range(d.ncon):
            c = d.contact[ci]
            for j, g in enumerate(hands):
                if g in (c.geom1, c.geom2) and (c.geom1 in s.floor or c.geom2 in s.floor):
                    mujoco.mj_contactForce(m, d, ci, f6); hpk[j] = max(hpk[j], float(f6[0]))
                    if hv[j] is None:
                        v6 = np.zeros(6); mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_GEOM, g, v6, 0); hv[j] = round(float(np.linalg.norm(v6[3:])), 3)
                        if t_touch is None: t_touch = round(t, 3)
        kmax = max(kmax, max(float(d.qpos[s.qadr[i]]) for i, n in enumerate(s.names) if n.endswith('knee')))
        cc = s.contacts()
        if fell is None and (cc['chest_pad'] > 1 or cc['other'] > 50 or cc['knee_pads'] > 50): fell = round(t, 3)
    return dict(T=T, mass=mass, elbow_cap=elbow_cap, width=width, fell=fell, t_hand_touch=t_touch, hand_speed_mps=hv,
                hand_peak_N=[round(x, 1) for x in hpk], knee_max_deg=round(math.degrees(kmax), 1),
                pass_=bool(fell is None and t_touch is not None and max(hpk) <= 875 and kmax <= math.radians(120.5)))


if __name__ == '__main__':
    rows = []
    for (kn, hp, wa), T, wid, ec in itertools.product(((1.95, -1.83, 0.4), (2.09, -1.83, 0.4), (1.75, -1.83, 0.0)), (2.0, 3.5), (0.0, 0.05, 0.10), (38.0, 49.0)):
        tg = dict(hip_pitch=hp, knee=kn, ankle_pitch=-0.9, shoulder_pitch=-1.4, elbow=-0.13, wrist_pitch=-0.96, waist_pitch=wa)
        r = dict(knee_t=round(math.degrees(kn), 1), hip_t=round(math.degrees(hp), 1), waist=wa, **run(tg, T, elbow_cap=ec, width=wid)); rows.append(r); print(json.dumps(r), flush=True)
    json.dump(rows, open(os.path.join(HERE, 'pose_b_transition.json'), 'w'), indent=1)
