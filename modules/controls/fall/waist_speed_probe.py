"""T&R 3eacd56 ask: waist-pitch speed in D99 fall set (contract TUCK mode, 68 kg). Logs peak |waist pitch qvel|,
waist pitch range hit (MJCF range = stop proxy), and torso pitch at first non-foot floor contact. Light CPU MuJoCo."""
import os, sys, json, math
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
L = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'limits'); sys.path.insert(0, L)
import prone_data as P, knee_stop_impact as K
from drive_thermal_derate import friction_hold
from fall_mode import knee_fall_torque  # waist drive is off here (tau=0), so the D102 zero (1ed4d73) is a no-op
out = []
for case in K.CASES:
  for lean in [l for l in (0.1, 0.3, 0.5) ]:
    s = P.Sim(68.0); m, d = s.m, s.d
    wj = [i for i in range(m.njnt) if 'waist' in m.joint(i).name and 'pitch' in m.joint(i).name]
    if not wj: print('no waist pitch joint'); sys.exit(1)
    wj = wj[0]; wq, wv = m.jnt_qposadr[wj], m.jnt_dofadr[wj]; rng = m.jnt_range[wj].copy()
    pose, _ = K.CASES[case]; s.place(pose, lean); q = s.target(pose)
    for _ in range(30): d.ctrl[:] = s.pd(q); mujoco.mj_step(m, d)
    for i, n in enumerate(s.names): m.dof_frictionloss[s.vadr[i]] = friction_hold(n)
    ki = [s.names.index(n) for n in ('l_knee', 'r_knee')]; lim = 0.5 * s.lim
    kv = [m.jnt_dofadr[m.joint(n).id] for n in ('l_knee', 'r_knee')]; kq = [m.jnt_qposadr[m.joint(n).id] for n in ('l_knee','r_knee')]
    vmax = 0.0; atstop = None; qw = [1e9, -1e9]
    for _ in range(int(2.0 / m.opt.timestep)):
        tau = np.zeros(m.nu)
        for k in range(2): tau[ki[k]] = knee_fall_torque(float(d.qpos[kq[k]]), float(d.qvel[kv[k]]), float(lim[ki[k]]))
        d.ctrl[:] = tau; mujoco.mj_step(m, d)
        v = float(d.qvel[wv]); x = float(d.qpos[wq]); vmax = max(vmax, abs(v)); qw = [min(qw[0], x), max(qw[1], x)]
        if atstop is None and (x <= rng[0] + 1e-3 or x >= rng[1] - 1e-3): atstop = round(v, 3)
    out.append(dict(case=case, lean=lean, waist_range_deg=[round(math.degrees(r),1) for r in rng],
                    waist_q_span_deg=[round(math.degrees(r),1) for r in qw], peak_abs_waist_qvel=round(vmax,3), v_at_range_end=atstop))
    print(out[-1], flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'waist_speed_probe.json'), 'w'), indent=1)
