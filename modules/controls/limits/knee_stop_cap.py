"""Robot Lab ruling per T&R 513a7d5: knee |tau| <= 50 N.m at knee >= 125 deg in fall/TUCK/R-146 states.
Re-runs the D97 PU knee-stop fall set (knee_stop_impact.py, b5890e1: 3 cases x leans x mass 65/68/68.5 x knee
armature 0.553/0.2018/0 = 99 runs) and adds per-knee stop ENERGY (loading work of the PU pair past 135 deg,
integral tau_pu * d(delta) while compressing; gate <= 62.7 J, bottoming ~97 J).
Modes:
  mo0     : D97 baseline, MO=0 (drive tripped / TUCK, D94 friction only). The cap has nothing to clip (tau=0).
  cap     : motors ON, fall-mode knee hold (derated PD to the start pose, x0.5 derate) + 50 N.m cap >= 125 deg.
  ramp_knee_only : as ramp but every other joint MO=0 (only the knee drives brake) - closest to a real fall.
  ramp    : motors ON, pre-stop deceleration: knee damping tau = -B(q)*qdot (flexion resisted), B ramps 0->B_MAX
            over [RAMP_START, 125) deg, clipped to the derated limit; >= 125 deg clipped to the 50 N.m cap.
Light MuJoCo, CPU. Writes knee_stop_cap_results.json."""
import os, sys, json, itertools
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import prone_data as P
import knee_stop_impact as K
from drive_thermal_derate import friction_hold
from soft_limits import knee_torque_limit, KNEE_CAP_NM, KNEE_CAP_START_RAD

E_GATE, E_BOTTOM = 62.7, 97.0
DERATE = 0.5
RAMP_START_DEG, B_MAX = 95.0, 60.0   # N.m.s/rad [design choice, see results]


def run(case, lean, mass, arm, mode, T=2.0, b_max=B_MAX, ramp_start_deg=RAMP_START_DEG):
    s = P.Sim(mass); m, d = s.m, s.d
    kn = [m.joint(j).id for j in ('l_knee', 'r_knee')]
    for j in kn:
        m.jnt_range[j, 1] = np.radians(170.0)
        m.dof_armature[m.jnt_dofadr[j]] = arm
    pose, _ = K.CASES[case]
    s.place(pose, lean); q = s.target(pose)
    for _ in range(30):
        d.ctrl[:] = s.pd(q); mujoco.mj_step(m, d)
    for i, n in enumerate(s.names):
        m.dof_frictionloss[s.vadr[i]] = friction_hold(n)
    kq = [m.jnt_qposadr[j] for j in kn]; kv = [m.jnt_dofadr[j] for j in kn]
    ki = [s.names.index(n) for n in ('l_knee', 'r_knee')]
    lim = DERATE * s.lim
    E = [0.0, 0.0]; peak = [0.0, 0.0]; qmax = [0.0, 0.0]; hitv = [None, None]; tau_knee_zone = 0.0; tau_knee_max = 0.0
    r0, r1 = np.radians(ramp_start_deg), KNEE_CAP_START_RAD
    for _ in range(int(T / m.opt.timestep)):
        if mode == 'mo0':
            tau = np.zeros(m.nu)
        elif mode == 'cap':
            tau = np.clip(s.pd(q), -lim, lim)
        else:   # ramp: others hold pose derated (ramp_knee_only: others MO=0), knees replaced by damping ramp
            tau = np.clip(s.pd(q), -lim, lim) if mode == 'ramp' else np.zeros(m.nu)
            for k in range(2):
                qk, vk = float(d.qpos[kq[k]]), float(d.qvel[kv[k]])
                B = b_max * float(np.clip((qk - r0) / (r1 - r0), 0.0, 1.0)) if qk < r1 else b_max
                tau[ki[k]] = float(np.clip(-B * max(vk, 0.0), -lim[ki[k]], lim[ki[k]]))
        if mode != 'mo0':
            for k in range(2):   # 513a7d5 cap on top of the derate
                L = knee_torque_limit(float(d.qpos[kq[k]]), 'FALL', float(lim[ki[k]]))
                tau[ki[k]] = float(np.clip(tau[ki[k]], -L, L))
                if float(d.qpos[kq[k]]) >= KNEE_CAP_START_RAD:
                    tau_knee_zone = max(tau_knee_zone, abs(tau[ki[k]]))
                tau_knee_max = max(tau_knee_max, abs(tau[ki[k]]))
        d.ctrl[:] = tau
        for k in range(2):
            dl = float(d.qpos[kq[k]]) - K.STOP_RAD; v = float(d.qvel[kv[k]])
            tq = K.pu_torque(dl, v)
            d.qfrc_applied[kv[k]] = -tq
            if tq > 0:
                if hitv[k] is None: hitv[k] = v
                peak[k] = max(peak[k], tq)
                if v > 0: E[k] += tq * v * m.opt.timestep
        mujoco.mj_step(m, d)
        for k in range(2):
            qmax[k] = max(qmax[k], float(d.qpos[kq[k]]))
    pen = [max(0.0, float(np.degrees(x - K.STOP_RAD))) for x in qmax]
    return dict(case=case, lean=lean, mass=mass, knee_armature=arm, mode=mode,
                E_J=[round(e, 1) for e in E], E_max_J=round(max(E), 1),
                speed_at_stop_rad_s=[None if v is None else round(v, 2) for v in hitv],
                peak_stop_torque_Nm=round(max(peak), 1), peak_penetration_deg=round(max(pen), 2),
                knee_max_deg=round(float(np.degrees(max(qmax))), 1),
                knee_cmd_max_in_zone_Nm=round(tau_knee_zone, 1), knee_cmd_max_Nm=round(tau_knee_max, 1),
                passes=bool(max(E) <= E_GATE and max(pen) <= K.PU_LIMIT_DEG and max(peak) <= K.PU_LIMIT_NM))


def sweep(mode, **kw):
    rows = []
    for case, (_, leans) in K.CASES.items():
        for lean, mass, arm in itertools.product(leans, (65.0, 68.0, 68.5), (0.553, 0.2018, 0.0)):
            rows.append(run(case, lean, mass, arm, mode, **kw))
    return rows


def summ(rows):
    out = {}
    for case in K.CASES:
        r = [x for x in rows if x['case'] == case]
        out[case] = dict(n=len(r), E_max_J=max(x['E_max_J'] for x in r), E_min_J=min(x['E_max_J'] for x in r),
                         peak_torque_Nm=max(x['peak_stop_torque_Nm'] for x in r), pen_max_deg=max(x['peak_penetration_deg'] for x in r),
                         n_fail=sum(not x['passes'] for x in r))
    out['all'] = dict(n=len(rows), n_fail=sum(not x['passes'] for x in rows), E_max_J=max(x['E_max_J'] for x in rows),
                      zone_cmd_max_Nm=max(x['knee_cmd_max_in_zone_Nm'] for x in rows))
    return out


if __name__ == '__main__':
    modes = sys.argv[1:] or ['mo0', 'cap', 'ramp', 'ramp_knee_only']
    res = {}
    for md in modes:
        rows = sweep(md); res[md] = dict(summary=summ(rows), rows=rows)
        print(md, json.dumps(res[md]['summary']), flush=True)
    res['meta'] = dict(gate_J=E_GATE, bottom_J=E_BOTTOM, cap_Nm=KNEE_CAP_NM, cap_start_deg=125.0, derate=DERATE,
                       ramp=dict(start_deg=RAMP_START_DEG, B_max=B_MAX), basis='D97 PU (b5890e1) + 513a7d5 cap; sim/v3 + pads [EST]')
    json.dump(res, open(os.path.join(HERE, 'knee_stop_cap_results.json'), 'w'), indent=1)
