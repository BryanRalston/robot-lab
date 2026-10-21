"""D96 / Robot Lab: PU knee stop pair at 135 deg (sim/v3 knee range 0..135 deg = 2.356 rad), modelled as the MuJoCo
joint-limit contact with a PU-like soft constraint (solreflimit timeconst [EST]: 0.005 / 0.01 / 0.02 s).
Measures the knee angular speed at first stop contact and the peak stop torque (joint-limit constraint force) in
the fall/tuck cases, MO=0 (D94 friction holds only), sim/v3 + knee/chest pads [EST], 1 kHz CPU:
  crouch_collapse : derated crouch held by PD, then drive trip (MO=0)   [= R-146(a) HOLD_DERATED -> trip/TUCK]
  forward_fall    : standing stance, forward lean, MO=0
  kneel_tip       : upright kneel on the pads, lean back/forward, MO=0
DR: mass 65 / 68 / 68.5 kg x PU timeconst x lean. Writes knee_stop_impact_results.json.
"""
import os, sys, json, itertools
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import prone_data as P
from drive_thermal_derate import friction_hold

STOP_RAD = np.radians(135.0)
CASES = {
    'crouch_collapse': (dict(hip_pitch=-0.9, knee=1.6, ankle_pitch=-0.7), (0.0, 0.05, -0.05)),
    'forward_fall': (dict(hip_pitch=-0.54, knee=1.17, ankle_pitch=-0.63), (0.10, 0.20, 0.30)),
    'kneel_tip': (P.POSE_KNEEL, (-0.30, -0.15, 0.15, 0.30)),
}


def run(case, lean, mass=68.0, pu_tc=0.01, T=2.0):
    s = P.Sim(mass); m, d = s.m, s.d
    kn = [m.joint(j).id for j in ('l_knee', 'r_knee')]
    for j in kn:
        m.jnt_range[j, 1] = STOP_RAD
        m.jnt_solref[j] = [pu_tc, 1.0]
    pose, _ = CASES[case]
    s.place(pose, lean)
    q = s.target(pose)
    for _ in range(30):
        d.ctrl[:] = s.pd(q); mujoco.mj_step(m, d)
    for i, n in enumerate(s.names):
        m.dof_frictionloss[s.vadr[i]] = friction_hold(n)
    d.ctrl[:] = 0
    kq = [m.jnt_qposadr[j] for j in kn]; kv = [m.jnt_dofadr[j] for j in kn]
    hit_v = [None, None]; peak_tau = [0.0, 0.0]; vmax = 0.0; qmax = 0.0
    for _ in range(int(T / m.opt.timestep)):
        v_prev = [float(d.qvel[a]) for a in kv]
        mujoco.mj_step(m, d)
        for k in range(2):
            qk = float(d.qpos[kq[k]]); qmax = max(qmax, qk); vmax = max(vmax, v_prev[k])
            for r in range(d.nefc):
                if d.efc_type[r] == mujoco.mjtConstraint.mjCNSTR_LIMIT_JOINT and d.efc_id[r] == kn[k] and qk > STOP_RAD - 0.2:   # upper (135 deg) stop only
                    if hit_v[k] is None: hit_v[k] = v_prev[k]
                    peak_tau[k] = max(peak_tau[k], abs(float(d.efc_force[r])))
    hv = [v for v in hit_v if v is not None]
    return dict(case=case, lean=lean, mass=mass, pu_tc=pu_tc, stop_hit=bool(hv),
                knee_speed_at_stop_rad_s=round(max(hv), 2) if hv else None,
                knee_peak_flex_speed_rad_s=round(vmax, 2), knee_max_deg=round(float(np.degrees(qmax)), 1),
                stop_peak_torque_Nm=round(max(peak_tau), 1) if hv else None)


if __name__ == '__main__':
    rows = []
    for case, (_, leans) in CASES.items():
        for lean, mass, tc in itertools.product(leans, (65.0, 68.0, 68.5), (0.005, 0.01, 0.02)):
            rows.append(run(case, lean, mass, tc))
    summ = {}
    for case in CASES:
        r = [x for x in rows if x['case'] == case]
        nom = [x for x in r if x['mass'] == 68.0 and x['pu_tc'] == 0.01]
        hits = [x for x in r if x['stop_hit']]
        summ[case] = dict(n=len(r), n_stop_hit=len(hits),
                          nominal=[{k: x[k] for k in ('lean', 'knee_speed_at_stop_rad_s', 'stop_peak_torque_Nm', 'knee_max_deg')} for x in nom],
                          dr_max_speed_at_stop_rad_s=max((x['knee_speed_at_stop_rad_s'] for x in hits), default=None),
                          dr_max_stop_torque_Nm=max((x['stop_peak_torque_Nm'] for x in hits), default=None))
    allhit = [x for x in rows if x['stop_hit']]
    summ['all_cases'] = dict(peak_speed_at_stop_rad_s=max(x['knee_speed_at_stop_rad_s'] for x in allhit), peak_stop_torque_Nm_EST=max(x['stop_peak_torque_Nm'] for x in allhit))
    out = dict(stop_deg=135.0, model='sim/v3 + pads [EST]; PU stop = joint-limit constraint, solref timeconst [EST]', summary=summ, rows=rows)
    json.dump(out, open(os.path.join(HERE, 'knee_stop_impact_results.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))
