"""Quasi-static transition to pose (b) (RL Controls decision 10:44): task-space IK (kneel_toe_wbc style) + derated PD +
contact-consistent static ff, knee hard-limited 120 deg in the IK and the 50 N.m cap >= 120 deg on the torque.
  P1 crouch : feet anchored (toe edge only once heels unload), CoM z -> Z1, CoM x held over the feet (toe line - COM_BACK),
              trunk pitch -> PITCH1.
  P2 reach  : CoM held over the feet, hands lowered under a speed governor (<= V_H, <= V_C within 50 mm), trunk pitch ramps;
              hands unloaded (not in the ff support set). Ends at hand contact.
  P3 shift  : CoM x moved toward the hands slowly; ff support set feet + hands with hand share ramped 0 -> F_TGT/hand.
  P4 hold   : 1 s.
68 kg first. Writes qs_transition.json."""
import os, sys, json, math, itertools
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chest_lower_wbc as CL
import kneel_toe_wbc as KT
from soft_limits import apply_knee_stop_cap
from drive_thermal_derate import ankle_pitch_min

KNEE_MAX = math.radians(120.0) - 0.01
TOE_SWITCH = True
P = dict(Z1=0.62, COM_BACK=0.04, PITCH1=0.6, PITCH2=1.25, T1=2.5, V_H=0.20, V_C=0.08, T3=2.5, SHIFT=0.10, F_TGT=150.0, HAND_X=0.30, WIDTH=0.0)
W_SUP, W_COM, W_PITCH, W_TASK, LAM, KC = 30.0, 20.0, 2.0, 10.0, 0.05, 20.0


def ff_split(m, d, feet, hands, f_hand):
    """Static ff with the vertical hand force pinned to f_hand per hand (rest on the feet, min-norm)."""
    jp = np.zeros((3, m.nv)); Jf = []; Jh = []
    for g in feet:
        mujoco.mj_jacGeom(m, d, jp, None, g); Jf.append(jp.copy())
    for g in hands:
        mujoco.mj_jacGeom(m, d, jp, None, g); Jh.append(jp.copy())
    Jf = np.vstack(Jf); b = d.qfrc_bias[:6].copy(); tau_h = np.zeros(m.nv)
    if hands and f_hand > 0:
        Jh = np.vstack(Jh); fh = np.tile([0.0, 0.0, f_hand], len(hands)); tau_h = Jh.T @ fh; b = b - tau_h[:6]
    A = Jf[:, :6].T; f = A.T @ np.linalg.solve(A @ A.T + 1e-6 * np.eye(6), b)
    return d.qfrc_bias - Jf.T @ f - tau_h


def run(mass=68.0, pad_tc=0.02, p=P, join_chest=False, elbow_cap=38.0):
    s = CL.make_sim(mass, pad_tc); m, d = s.m, s.d
    for n in ('l_ankle_pitch', 'r_ankle_pitch'): m.jnt_range[m.joint(n).id, 0] = ankle_pitch_min(0.0)
    for i, n in enumerate(s.names):
        if n.endswith('elbow'): s.lim[i] = elbow_cap
    s.place(KT.STAND, 0.0); qs = s.target(KT.STAND)
    for _ in range(300):
        d.ctrl[:] = s.pd(qs); mujoco.mj_step(m, d)
    nv = m.nv; act = s.vadr
    IKJ = ('hip_pitch', 'knee', 'ankle_pitch', 'shoulder_pitch', 'elbow', 'wrist_pitch', 'waist_pitch')
    lock = np.zeros(nv)
    for i, n in enumerate(s.names):
        if not any(n.endswith(j) for j in IKJ): lock[act[i]] = 1e6
    jid = m.actuator_trnid[:, 0]; lo = m.jnt_range[jid, 0] + 0.01; hi = m.jnt_range[jid, 1] - 0.01
    for i, n in enumerate(s.names):
        if n.endswith('knee'): hi[i] = min(hi[i], KNEE_MAX)
    feet = [m.geom('l_foot').id, m.geom('r_foot').id]; hands = [m.geom('l_hand').id, m.geom('r_hand').id]
    q_des = d.qpos[s.qadr].copy(); com0 = d.subtree_com[1].copy()
    toe_x = float(np.mean([pt[0] for g in feet for pt in KT.corners(m, d, g, True)]))
    heel_x = float(np.mean([pt[0] for g in feet for pt in KT.corners(m, d, g, False)[2:]]))
    anchors = {}
    t = 0.0; ph = 'P1'; tph = {'P1': 0.0}; res = dict(fell=None)
    href = None; hand_tgt = None; hv = [None, None]; hpk = [0.0, 0.0]; kmax = 0.0; f6 = np.zeros(6); fh = 0.0; pitch2_0 = None
    toe_only = False; cx_shift0 = None
    while t < 14.0:
        f = s.contacts(); rows, rhs, w = [], [], []
        def task(J, b, wt):
            rows.append(np.atleast_2d(J)); rhs.extend(np.atleast_1d(b)); w.extend([wt] * np.atleast_2d(J).shape[0])
        pitch = float(2 * np.arcsin(np.clip(d.qpos[5], -1, 1)))
        jr = np.zeros((3, nv)); mujoco.mj_jacBody(m, d, None, jr, s.torso)
        jc = np.zeros((3, nv)); mujoco.mj_jacSubtreeCom(m, d, jc, 1); com = d.subtree_com[1]
        for g in feet:
            pts = KT.corners(m, d, g, toe_only); key = (g, toe_only)
            if key not in anchors: anchors[key] = [x.copy() for x in pts]
            for pt, p0 in zip(pts, anchors[key]): task(KT.point_jac(m, d, m.geom_bodyid[g], pt), -KC * (pt - p0), W_SUP)
        cx_feet = 0.5 * (toe_x + heel_x) if not toe_only else toe_x - p['COM_BACK']
        if ph == 'P1':
            u = min(1.0, t / p['T1']); a5 = 10 * u**3 - 15 * u**4 + 6 * u**5
            cx = com0[0] + (toe_x - p['COM_BACK'] - com0[0]) * a5; cz = com0[2] + (p['Z1'] - com0[2]) * a5
            task(jc[0:1], KC * (cx - com[0]), W_COM); task(jc[1:2], -KC * com[1], W_COM); task(jc[2:3], KC * (cz - com[2]), W_COM)
            task(jr[1:2], 3.0 * (p['PITCH1'] * a5 - pitch), W_PITCH)
            if u >= 1.0: ph = 'P2'; tph['P2'] = t
        elif ph in ('P2', 'P3', 'P4'):
            if hand_tgt is None:
                hand_tgt = [np.array([toe_x + p['HAND_X'], d.geom_xpos[g][1], 0.0]) for g in hands]; pitch2_0 = pitch; t2 = t
            cxt = toe_x - p['COM_BACK']
            if ph in ('P3', 'P4'):
                u3 = min(1.0, (t - tph['P3']) / p['T3']); cxt += p['SHIFT'] * (10 * u3**3 - 15 * u3**4 + 6 * u3**5); fh = p['F_TGT'] * u3
                if ph == 'P3' and u3 >= 1.0: ph = 'P4'; tph['P4'] = t
                if ph == 'P4' and t - tph['P4'] >= 1.0: break
            task(jc[0:1], KC * (cxt - com[0]), W_COM); task(jc[1:2], -KC * com[1], W_COM)
            hz = min(float(d.geom_xpos[g][2] - m.geom_size[g][0]) for g in hands)
            task(jr[1:2], 3.0 * (min(p['PITCH2'], pitch2_0 + p.get('PITCH_RATE', 0.5) * (t - t2)) - pitch), p.get('W_PITCH2', W_PITCH))
            if ph == 'P2':
                vlim = p['V_H'] if hz > 0.05 else p['V_C']
                if href is None: href = hz
                href = max(href - vlim * m.opt.timestep, hz - 0.01)
            for g, ht in zip(hands, hand_tgt):
                mujoco.mj_jacGeom(m, d, (jp := np.zeros((3, nv))), None, g)
                task(jp[0:2], KC * 0.3 * (ht[:2] - d.geom_xpos[g][:2]), W_TASK)
                if ph == 'P2': task(jp[2:3], -float(np.clip(vlim + 8.0 * (hz - href), 0.0, vlim)), W_TASK)
                else: task(jp[2:3], -KC * (d.geom_xpos[g][2] - anchors.setdefault(('h', g), d.geom_xpos[g].copy())[2]), W_SUP)
            if ph == 'P2' and f['hands_arms'] > 5.0: ph = 'P3'; tph['P3'] = t
        J = np.vstack(rows); b = np.array(rhs); Wd = np.diag(w)
        A = J.T @ Wd @ J + LAM * np.eye(nv) + np.diag(lock); qd = np.linalg.solve(A, J.T @ Wd @ b); qa = qd[act]
        at = ((q_des <= lo + 0.005) & (qa < 0)) | ((q_des >= hi - 0.005) & (qa > 0))
        if at.any():
            l2 = lock.copy(); l2[act[at]] = 1e6; qd = np.linalg.solve(J.T @ Wd @ J + LAM * np.eye(nv) + np.diag(l2), J.T @ Wd @ b); qa = qd[act]
        q_des = np.clip(q_des + qa * m.opt.timestep, lo, hi)
        ff = ff_split(m, d, feet, hands if ph in ('P3', 'P4') else [], fh)[act]
        tau = np.clip(s.pd(q_des, qa) + ff, -s.lim, s.lim)
        apply_knee_stop_cap(s.names, lambda n: float(d.qpos[s.qadr[s.names.index(n)]]), tau, 'KNEEL')
        d.ctrl[:] = tau; mujoco.mj_step(m, d); t += m.opt.timestep
        # heels unloaded -> switch the anchor to the toe edge
        if TOE_SWITCH and not toe_only and ph != 'P1' and min(pt[2] for g in feet for pt in KT.corners(m, d, g, False)[2:]) > 0.003:
            toe_only = True
        for ci in range(d.ncon):
            c = d.contact[ci]
            for j, g in enumerate(hands):
                if g in (c.geom1, c.geom2) and (c.geom1 in s.floor or c.geom2 in s.floor):
                    mujoco.mj_contactForce(m, d, ci, f6); hpk[j] = max(hpk[j], float(f6[0]))
                    if hv[j] is None:
                        v6 = np.zeros(6); mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_GEOM, g, v6, 0); hv[j] = round(float(abs(v6[5])), 4)
        kmax = max(kmax, max(float(d.qpos[s.qadr[i]]) for i, n in enumerate(s.names) if n.endswith('knee')))
        if f['chest_pad'] > 1 or f['knee_pads'] > 20 or f['other'] > 50:
            res['fell'] = dict(t=round(t, 3), phase=ph, knee_pads=round(f['knee_pads']), other=round(f['other'])); break
    res.update(phase_t={k: round(v, 3) for k, v in tph.items()}, T_s=round(t, 3), hand_contact_vz_mps=hv, hand_peak_N=[round(x, 1) for x in hpk],
               knee_max_deg=round(math.degrees(kmax), 1), hand_load_end_N=round(fh, 1))
    res['pass_'] = bool(res['fell'] is None and 'P4' in tph and all(v is not None and v <= 0.23 for v in hv) and max(hpk) <= 875 and kmax <= math.radians(120.5))
    if join_chest and res['pass_']:
        r2 = CL.run(sim=s); res['chest'] = {k: r2.get(k) for k in ('chest_contact_speed_mps', 'peak_chest_N', 'head_clear_before_chest_m', 'other_contact_geoms', 't_lower_s')}
    return res


if __name__ == '__main__':
    print(json.dumps(run()))
