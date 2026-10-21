"""Fallback (c) [Robot Lab]: crouch -> sit back onto the pelvis -> recline (no kneel). Joint-space min-jerk segments,
derated PD (legs/arms x0.5) + knee cap (>= 120 deg 50 N.m), sim/v3 + pads [EST]; no back/seat pad exists in the model
(pelvis/torso box contact with the floor, default MuJoCo contact = rigid-ish [EST]). Interpretation of 'sit-back chest lower'
as crouch -> sit -> lie back is ours (flagged). DR: mass 65/68/68.5 x pad tc 0.005/0.02/0.04 (pads only affect knees/chest).
Writes sitback_lower.json."""
import os, sys, json, math, itertools
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chest_lower_wbc as CL
from soft_limits import apply_knee_stop_cap
from drive_thermal_derate import ankle_pitch_min
STAND = dict(hip_pitch=-0.54, knee=1.17, ankle_pitch=-0.63, shoulder_pitch=-0.3, elbow=-0.3)
CROUCH = dict(hip_pitch=-1.35, knee=2.05, ankle_pitch=-0.8, shoulder_pitch=-1.4, elbow=-0.3, waist_pitch=0.0)   # best of an 8-variant probe
SIT = dict(hip_pitch=-1.4, knee=1.9, ankle_pitch=-0.3, shoulder_pitch=-1.0, elbow=-0.3)
LIE = dict(hip_pitch=-0.3, knee=0.6, ankle_pitch=0.0, shoulder_pitch=0.0, elbow=-0.3, waist_pitch=0.0, neck_pitch=0.5)
SEG = ((CROUCH, 2.5), (SIT, 2.0), (LIE, 3.0))


def run(mass=68.0, pad_tc=0.02, seg=SEG, hold=1.0):
    s = CL.make_sim(mass, pad_tc); m, d = s.m, s.d
    for n in ('l_ankle_pitch', 'r_ankle_pitch'): m.jnt_range[m.joint(n).id, 0] = ankle_pitch_min(0.0)
    s.place(STAND, 0.0); q = s.target(STAND)
    for _ in range(300):
        d.ctrl[:] = s.pd(q); mujoco.mj_step(m, d)
    lim = 0.5 * m.actuator_ctrlrange[:, 1]
    pel = m.geom('pelvis').id; tor = m.geom('torso').id; head = m.geom('head').id
    first = {}; pk = {}; kmax = 0.0; f6 = np.zeros(6); t = 0.0; seq = []
    qa = d.qpos[s.qadr].copy()
    for pose, T in seg:
        qb = s.target(pose); seq.append((t, T))
        for k in range(int(T / m.opt.timestep)):
            u = (k + 1) * m.opt.timestep / T; a = 10 * u**3 - 15 * u**4 + 6 * u**5; ad = (30 * u**2 - 60 * u**3 + 30 * u**4) / T
            tau = np.clip(s.pd(qa + (qb - qa) * a, (qb - qa) * ad), -lim, lim)
            apply_knee_stop_cap(s.names, lambda n: float(d.qpos[s.qadr[s.names.index(n)]]), tau, 'KNEEL')
            d.ctrl[:] = tau; mujoco.mj_step(m, d); t += m.opt.timestep
            for ci in range(d.ncon):
                c = d.contact[ci]
                for nm, g in (('pelvis', pel), ('torso', tor), ('head', head)):
                    if g in (c.geom1, c.geom2) and (c.geom1 in s.floor or c.geom2 in s.floor):
                        mujoco.mj_contactForce(m, d, ci, f6); pk[nm] = max(pk.get(nm, 0.0), float(f6[0]))
                        if nm not in first:
                            v6 = np.zeros(6); mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_GEOM, g, v6, 0)
                            first[nm] = dict(t=round(t, 3), speed_mps=round(float(np.linalg.norm(v6[3:])), 3))
            kmax = max(kmax, max(float(d.qpos[s.qadr[i]]) for i, n in enumerate(s.names) if n.endswith('knee')))
        qa = qb
    for _ in range(int(hold / m.opt.timestep)):
        d.ctrl[:] = np.clip(s.pd(qa), -lim, lim); mujoco.mj_step(m, d); t += m.opt.timestep
    return dict(mass=mass, pad_tc=pad_tc, first_contact=first, peak_N={k: round(v, 1) for k, v in pk.items()},
                knee_max_deg=round(math.degrees(kmax), 1), T_total_s=round(t, 2), segments=[(round(a, 2), b) for a, b in seq],
                pelvis_z_final=round(float(d.xpos[m.body('pelvis').id][2]), 3) if 'pelvis' in [m.body(i).name for i in range(m.nbody)] else None)


if __name__ == '__main__':
    rows = [run(ms, tc) for ms, tc in itertools.product((65.0, 68.0, 68.5), (0.005, 0.02, 0.04))]
    json.dump(rows, open(os.path.join(HERE, 'sitback_lower.json'), 'w'), indent=1)
    for r in rows: print(json.dumps(r))
