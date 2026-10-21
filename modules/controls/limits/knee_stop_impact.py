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
# D97 (Actuators 770da54): PU 90A pad pair at r 60, torque vs penetration past 135 deg (2 pads), 25 % strain at 8.6 deg
PU_DEG = np.array([0.0, 0.7, 1.7, 3.4, 5.2, 6.9, 8.6])
PU_NM = np.array([0.0, 119, 242, 525, 782, 1028, 1258])
PU_RES = 0.34          # resilience: unloading path = 0.34 x loading curve -> rebound energy 34 %
PU_LIMIT_DEG, PU_LIMIT_NM = 8.6, 1258.0
KNEE_ARMATURE = 0.553  # kg m^2 per knee, D97 rotors (2 x Jm x 59.7^2); sim/v3 carries 0.2018
MODE = 'pu_d97'        # 'pu_d97' (joint-space spring + hysteresis) or 'solref' (old rigid-limit study)


def pu_torque(delta_rad, ddelta):
    if delta_rad <= 0: return 0.0
    dg = np.degrees(delta_rad)
    k = float(np.interp(dg, PU_DEG, PU_NM)) if dg <= PU_DEG[-1] else PU_NM[-1] + (dg - PU_DEG[-1]) * (PU_NM[-1] - PU_NM[-2]) / (PU_DEG[-1] - PU_DEG[-2])
    return k if ddelta > 0 else PU_RES * k
CASES = {
    'crouch_collapse': (dict(hip_pitch=-0.9, knee=1.6, ankle_pitch=-0.7), (0.0, 0.05, -0.05)),
    'forward_fall': (dict(hip_pitch=-0.54, knee=1.17, ankle_pitch=-0.63), (0.10, 0.20, 0.30)),
    'kneel_tip': (P.POSE_KNEEL, (-0.30, -0.15, 0.15, 0.30)),
}


def run(case, lean, mass=68.0, pu_tc=0.01, T=2.0):
    s = P.Sim(mass); m, d = s.m, s.d
    kn = [m.joint(j).id for j in ('l_knee', 'r_knee')]
    for j in kn:
        if MODE == 'solref':
            m.jnt_range[j, 1] = STOP_RAD
            m.jnt_solref[j] = [pu_tc, 1.0]
        else:
            m.jnt_range[j, 1] = np.radians(170.0)   # no rigid limit: the PU torque is the stop
            if KNEE_ARMATURE is not None:
                m.dof_armature[m.jnt_dofadr[j]] = KNEE_ARMATURE
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
        if MODE != 'solref':
            for k in range(2):
                tq = pu_torque(float(d.qpos[kq[k]]) - STOP_RAD, float(d.qvel[kv[k]]))
                d.qfrc_applied[kv[k]] = -tq
                if tq > 0:
                    if hit_v[k] is None: hit_v[k] = v_prev[k]
                    peak_tau[k] = max(peak_tau[k], tq)
        mujoco.mj_step(m, d)
        for k in range(2):
            qk = float(d.qpos[kq[k]]); qmax = max(qmax, qk); vmax = max(vmax, v_prev[k])
            for r in range(d.nefc):
                if MODE == 'solref' and d.efc_type[r] == mujoco.mjtConstraint.mjCNSTR_LIMIT_JOINT and d.efc_id[r] == kn[k] and qk > STOP_RAD - 0.2:   # upper (135 deg) stop only
                    if hit_v[k] is None: hit_v[k] = v_prev[k]
                    peak_tau[k] = max(peak_tau[k], abs(float(d.efc_force[r])))
    hv = [v for v in hit_v if v is not None]
    return dict(case=case, lean=lean, mass=mass, pu_tc=pu_tc, stop_hit=bool(hv),
                knee_speed_at_stop_rad_s=round(max(hv), 2) if hv else None,
                knee_peak_flex_speed_rad_s=round(vmax, 2), knee_max_deg=round(float(np.degrees(qmax)), 1),
                stop_peak_torque_Nm=round(max(peak_tau), 1) if hv else None,
                peak_penetration_deg=round(max(0.0, float(np.degrees(qmax - STOP_RAD))), 2))


if __name__ == '__main__':
    rows = []
    for case, (_, leans) in CASES.items():
        third = (0.005, 0.01, 0.02) if MODE == 'solref' else (0.553, 0.2018, 0.0)   # pu mode: DR over knee armature
        for lean, mass, x in itertools.product(leans, (65.0, 68.0, 68.5), third):
            if MODE != 'solref':
                globals()['KNEE_ARMATURE'] = x; rows.append(dict(run(case, lean, mass), knee_armature=x))
            else:
                rows.append(run(case, lean, mass, x))
    summ = {}
    for case in CASES:
        r = [x for x in rows if x['case'] == case]
        nom = [x for x in r if x['mass'] == 68.0 and (x['pu_tc'] == 0.01 if MODE == 'solref' else x['knee_armature'] == 0.553)]
        hits = [x for x in r if x['stop_hit']]
        summ[case] = dict(n=len(r), n_stop_hit=len(hits),
                          nominal=[{k: x[k] for k in ('lean', 'knee_speed_at_stop_rad_s', 'stop_peak_torque_Nm', 'knee_max_deg', 'peak_penetration_deg')} for x in nom],
                          dr_max_speed_at_stop_rad_s=max((x['knee_speed_at_stop_rad_s'] for x in hits), default=None),
                          dr_max_stop_torque_Nm=max((x['stop_peak_torque_Nm'] for x in hits), default=None),
                          dr_max_penetration_deg=max((x['peak_penetration_deg'] for x in r), default=None),
                          dr_max_knee_deg=max(x['knee_max_deg'] for x in r),
                          flagged=[{k: x[k] for k in ('lean', 'mass', 'knee_armature', 'peak_penetration_deg', 'stop_peak_torque_Nm')} for x in r
                                   if MODE != 'solref' and (x['peak_penetration_deg'] > PU_LIMIT_DEG or (x['stop_peak_torque_Nm'] or 0) > PU_LIMIT_NM)])
    allhit = [x for x in rows if x['stop_hit']]
    summ['all_cases'] = dict(peak_speed_at_stop_rad_s=max(x['knee_speed_at_stop_rad_s'] for x in allhit), peak_stop_torque_Nm_EST=max(x['stop_peak_torque_Nm'] for x in allhit))
    out = dict(stop_deg=135.0, model=('sim/v3 + pads [EST]; PU stop = joint-limit constraint, solref timeconst [EST]' if MODE == 'solref' else 'sim/v3 + pads [EST]; D97 PU pair as joint-space torque past 135 deg (table, hysteretic unload x0.34); DR: mass x knee armature 0.553/0.2018/0'), summary=summ, rows=rows)
    json.dump(out, open(os.path.join(HERE, 'knee_stop_impact_results.json' if MODE == 'solref' else 'knee_stop_pu_d97_results.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))
