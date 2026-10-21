"""R-146(b) G4 safe-stop, kneel part, on a toe-supported task-space WBC (same contact-set approach as
chest_lower_wbc.py). sim/v3 + pads [EST], 68 kg, legs + arms x0.5, ankle soft limit P-157/D96 applied at runtime
(-0.955 rad, roll held 0; sim/v3 XML unchanged per the job-10 pin).

Phases (contact set in brackets):
  A  crouch + CoM shift to the toe line         [feet flat: 4 sole corners each]
  B  toe support, controlled knee drop to pads  [toe edge of each foot: the feet roll on the toe contact]
     knee-pad descent speed governed like ProneLowerGuard (0.4 -> 0.1 m/s at <= 50 mm); contact speed + peak force
  C  hands to the floor                         [toes + knee pads]; hand descent governed the same way
  D  chest-supported lower                      chest_lower_wbc.run(sim=...) from the reached hands-and-knees state
"""
import os, sys, json
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import prone_data as P
import chest_lower_wbc as CL
from drive_thermal_derate import ProneLowerGuard, ankle_pitch_min

IKJ = ('wrist_yaw', 'hip_pitch', 'knee', 'ankle_pitch', 'shoulder_pitch', 'elbow', 'wrist_pitch', 'waist_pitch')
STAND = dict(hip_pitch=-0.54, knee=1.17, ankle_pitch=-0.63, shoulder_pitch=-0.3, elbow=-0.3)
T_A = 1.0                 # s, crouch + CoM shift
COMZ_A = 0.62             # CoM height at the end of A [EST from the IK]
COM_BACK = 0.03           # CoM x behind the toe line in A
W_SUP, W_COM, W_PITCH, W_TASK, LAM = 30.0, 20.0, 2.0, 10.0, 0.05
KC = 20.0
PITCH_A, PITCH_C = 0.35, 1.1     # trunk pitch targets (rad, forward) at the end of A and C
HAND_X_AHEAD = 0.50       # hand floor target ahead of the knee pads (m)
MARGIN = 0.9
ORDER = 'hands_first'   # 'knees_first' (ruling order; falls onto the pads) or 'hands_first' (pending Arbiter)
COM_K0 = 0.05
K_MODE = 'joint'      # 'joint': knee drop as a guard-throttled joint path to the hands-and-knees posture; 'task': IK
K_ARMS = {}           # arm override of the K target posture
SETTLE_S = 0.4         # hold the hands-and-knees posture before the chest lower
K_RATE = 1.0 / 1.2     # path rate (1/s) before throttling
PITCH_K0, PITCH_K = 0.6, 1.25   # trunk pitch ramp during the knee drop (frees the hip from its -105 deg limit)
COM_K = 0.25          # hands_first knee drop: CoM held this far ahead of the toe line
HAND_X_TOE = 0.30      # hands_first: hand target ahead of the toe line (m)
DEBUG = False
COM_OVER_KNEES = False
COM_KNEE_OFF = 0.05
K_ELBOW = None
H_ELBOW = None
H_WRIST = None
H_PITCH_RATE = 0.8   # rad/s trunk pitch ramp while reaching for the floor
W_ELB = 50.0
KNEE_MAX_RAD = None   # soft upper knee limit for the whole kneel (Robot Lab: <= 125 deg, no exemption)
H_SPEED_SCALE = 1.0  # hand descent speed scale vs ProneLowerGuard
KNEE_CAP = True      # 513a7d5/D99 cap: <= 50 N.m at >= 120 deg


def corners(m, d, g, toe_only):
    sz = m.geom_size[g]; R = d.geom_xmat[g].reshape(3, 3); c = d.geom_xpos[g]
    xs = (sz[0],) if toe_only else (sz[0], -sz[0])
    return [c + R @ np.array([x, y, -sz[2]]) for x in xs for y in (sz[1], -sz[1])]


def point_jac(m, d, body, p):
    jp = np.zeros((3, m.nv)); mujoco.mj_jac(m, d, jp, None, p, body); return jp


def run(mass=68.0, pad_tc=0.02, frames=None, fps=25, join_chest=True):
    s = CL.make_sim(mass, pad_tc); m, d = s.m, s.d
    for n in ('l_ankle_pitch', 'r_ankle_pitch'):
        m.jnt_range[m.joint(n).id, 0] = ankle_pitch_min(0.0)
    s.place(STAND, 0.0); qs = s.target(STAND)
    for _ in range(300):
        d.ctrl[:] = s.pd(qs); mujoco.mj_step(m, d)
    nv = m.nv; act = s.vadr
    lock = np.zeros(nv)
    for i, n in enumerate(s.names):
        if not any(n.endswith(j) for j in IKJ): lock[act[i]] = 1e6
    jid = m.actuator_trnid[:, 0]; lo = m.jnt_range[jid, 0] + 0.01; hi = m.jnt_range[jid, 1] - 0.01
    if KNEE_MAX_RAD is not None:
        for i, n in enumerate(s.names):
            if n.endswith('knee'): hi[i] = min(hi[i], KNEE_MAX_RAD)
    kmax = {}
    feet = [m.geom('l_foot').id, m.geom('r_foot').id]
    kp = [m.geom('l_knee_pad').id, m.geom('r_knee_pad').id]
    hands = [m.geom('l_hand').id, m.geom('r_hand').id]
    q_des = d.qpos[s.qadr].copy()
    toe_x = float(np.mean([p[0] for g in feet for p in corners(m, d, g, True)]))
    com0 = d.subtree_com[1].copy()
    anchors = {}
    def anchor(key, pts):
        if key not in anchors: anchors[key] = [p.copy() for p in pts]
        return anchors[key]
    kguard = ProneLowerGuard(); hguard = ProneLowerGuard()
    t = 0.0; ph = 'A'; tph = {'A': 0.0}; res = dict(fell=None)
    hpk = {'l': 0.0, 'r': 0.0}; hv = {'l': None, 'r': None}; hpost = {}
    qK0 = None; sK = 0.0; gap = 1.0; vz = 0.0
    peak_tau = np.zeros(m.nu); kref = None; href = None; hand_tgt = None
    while t < 8.0:
        f = s.contacts()
        rows, rhs, w = [], [], []
        def task(J, b, wt):
            rows.append(np.atleast_2d(J)); rhs.extend(np.atleast_1d(b)); w.extend([wt] * np.atleast_2d(J).shape[0])
        pitch = float(2 * np.arcsin(np.clip(d.qpos[5], -1, 1)))
        jr = np.zeros((3, nv)); mujoco.mj_jacBody(m, d, None, jr, s.torso)
        jc = np.zeros((3, nv)); mujoco.mj_jacSubtreeCom(m, d, jc, 1)
        com = d.subtree_com[1]
        # supports
        toe_only = ph in ('B', 'C', 'K')
        for g in feet:
            pts = corners(m, d, g, toe_only); a = anchor(('foot', g, toe_only), pts)
            for p, p0 in zip(pts, a):
                task(point_jac(m, d, m.geom_bodyid[g], p), -KC * (p - p0), W_SUP)
        if ph == 'K':
            for g in hands:
                a = anchor(('hand', g), [d.geom_xpos[g]])[0]
                mujoco.mj_jacGeom(m, d, (jp := np.zeros((3, nv))), None, g); task(jp, -KC * (d.geom_xpos[g] - a), W_SUP)
        if ph == 'C':
            for g in kp:
                a = anchor(('knee', g), [d.geom_xpos[g]])[0]
                mujoco.mj_jacGeom(m, d, (jp := np.zeros((3, nv))), None, g); task(jp, -KC * (d.geom_xpos[g] - a), W_SUP)
        if ph == 'A':
            u = min(1.0, t / T_A); a5 = 10 * u**3 - 15 * u**4 + 6 * u**5
            cx = com0[0] + (toe_x - COM_BACK - com0[0]) * a5; cz = com0[2] + (COMZ_A - com0[2]) * a5
            task(jc[0:1], KC * (cx - com[0]), W_COM); task(jc[1:2], KC * (0 - com[1]), W_COM); task(jc[2:3], KC * (cz - com[2]), W_COM)
            task(jr[1:2], 3.0 * (PITCH_A * a5 - pitch), W_PITCH)
            if u >= 1.0:
                ph = 'B' if ORDER == 'knees_first' else 'H'; tph[ph] = t
        elif ph == 'B':
            task(jc[0:1], KC * (toe_x - 0.005 - com[0]), W_COM); task(jc[1:2], KC * (0 - com[1]), W_COM)
            gaps = [float(min(p[2] for p in [d.geom_xpos[g] + d.geom_xmat[g].reshape(3, 3) @ np.array([sx, sy, sz_]) * m.geom_size[g]
                                              for sx in (-1, 1) for sy in (-1, 1) for sz_ in (-1, 1)])) for g in kp]
            gap = min(gaps)
            if kref is None: kref = gap; res['knee_gap0_m'] = round(gap, 3)
            v_ref = MARGIN * kguard.speed_limit(max(gap, 0.0))
            kref = max(kref - v_ref * m.opt.timestep, gap - 0.01)
            for g in kp:
                mujoco.mj_jacGeom(m, d, (jp := np.zeros((3, nv))), None, g)
                vz_k = -float((jp @ d.qvel)[2])
                task(jp[2:3], -float(np.clip(v_ref + 8.0 * (gap - kref), 0.0, v_ref / MARGIN * MARGIN)), W_TASK)
            task(jr[1:2], 0.0, W_PITCH * 0.5)
            vz = max(-float((point_jac(m, d, m.geom_bodyid[g], d.geom_xpos[g]) @ d.qvel)[2]) for g in kp)
            kguard.observe(t, f['knee_pads'] > 1.0, vz, f['knee_pads'])
            if f['knee_pads'] > 1.0 and 'C' not in tph:
                res['knee_contact_speed_mps'] = round(kguard.contact_speed, 4); ph = 'C'; tph['C'] = t
        elif ph == 'H':
            if hand_tgt is None:
                hand_tgt = [np.array([toe_x + HAND_X_TOE, d.geom_xpos[g][1], 0.0]) for g in hands]; pitch_c0 = pitch; tc0 = t
            task(jc[0:1], KC * (toe_x - COM_BACK - com[0]), W_COM); task(jc[1:2], KC * (0 - com[1]), W_COM)
            hz = min(float(d.geom_xpos[g][2] - m.geom_size[g][0]) for g in hands)
            if href is None: href = hz
            v_ref = H_SPEED_SCALE * MARGIN * hguard.speed_limit(max(hz, 0.0))
            href = max(href - v_ref * m.opt.timestep, hz - 0.01)
            for g, ht in zip(hands, hand_tgt):
                mujoco.mj_jacGeom(m, d, (jp := np.zeros((3, nv))), None, g)
                task(jp[0:2], KC * (ht[:2] - d.geom_xpos[g][:2]) * 0.3, W_TASK)
                task(jp[2:3], -float(np.clip(v_ref + 8.0 * (hz - href), 0.0, v_ref)), W_TASK)
            task(jr[1:2], 3.0 * (min(PITCH_C, pitch_c0 + H_PITCH_RATE * (t - tc0)) - pitch), W_PITCH)
            for i, n in enumerate(s.names):   # Arms R19 plant posture targets
                tgt = {k: v for k, v in {'elbow': H_ELBOW, 'wrist_pitch': H_WRIST, 'wrist_yaw': 0.0 if H_ELBOW is not None else None}.items() if v is not None}.get(n[2:])
                if tgt is not None:
                    jj = np.zeros((1, nv)); jj[0, act[i]] = 1.0; task(jj, 4.0 * (tgt - d.qpos[s.qadr[i]]), W_ELB)
            vzh = max(-float((point_jac(m, d, m.geom_bodyid[g], d.geom_xpos[g]) @ d.qvel)[2]) for g in hands)
            hguard.observe(t, f['hands_arms'] > 1.0, vzh, f['hands_arms'])
            if f['hands_arms'] > 5.0:
                res['hand_contact_speed_mps'] = round(hguard.contact_speed, 4); ph = 'K'; tph['K'] = t
        elif ph == 'K':
            gap = min(float(min(p[2] for p in [d.geom_xpos[g] + d.geom_xmat[g].reshape(3, 3) @ (np.array([sx, sy, sz_]) * m.geom_size[g])
                                                for sx in (-1, 1) for sy in (-1, 1) for sz_ in (-1, 1)])) for g in kp)
            if kref is None: kref = gap; res['knee_gap0_m'] = round(gap, 3)
            v_ref = MARGIN * kguard.speed_limit(max(gap, 0.0))
            kref = max(kref - v_ref * m.opt.timestep, gap - 0.01)
            for g in kp:
                mujoco.mj_jacGeom(m, d, (jp := np.zeros((3, nv))), None, g)
                task(jp[2:3], -float(np.clip(v_ref + 8.0 * (gap - kref), 0.0, v_ref)), W_TASK)
            ck = COM_K0 + (COM_K - COM_K0) * (1 - max(kref, 0.0) / res["knee_gap0_m"])
            task(jr[1:2], 3.0 * (PITCH_K0 + (PITCH_K - PITCH_K0) * (1 - max(kref, 0.0) / res["knee_gap0_m"]) - pitch), W_PITCH)
            if COM_OVER_KNEES:   # CoM x held over the knee pads (plus COM_KNEE_OFF), not ahead of the toes
                ck = float(np.mean([d.geom_xpos[g][0] for g in kp])) + COM_KNEE_OFF - toe_x
            task(jc[0:1], KC * (toe_x + ck - com[0]), W_COM); task(jc[1:2], KC * (0 - com[1]), W_COM)
            if K_ELBOW is not None:   # near-straight elbows: arm load through the bones, not elbow torque
                for i, n in enumerate(s.names):
                    if n.endswith('elbow'):
                        jj = np.zeros((1, nv)); jj[0, act[i]] = 1.0; task(jj, 4.0 * (K_ELBOW - d.qpos[s.qadr[i]]), W_ELB)
            vz = max(-float((point_jac(m, d, m.geom_bodyid[g], d.geom_xpos[g]) @ d.qvel)[2]) for g in kp)
            kguard.observe(t, f['knee_pads'] > 1.0, vz, f['knee_pads'])
            if f['knee_pads'] > 1.0 and 'S' not in tph:
                res['knee_contact_speed_mps'] = round(kguard.contact_speed, 4); tph['S'] = t
            if 'S' in tph and t - tph['S'] >= SETTLE_S:
                tph['D'] = t; break
        elif ph == 'C':
            if hand_tgt is None:
                xk = float(np.mean([d.geom_xpos[g][0] for g in kp]))
                hand_tgt = [np.array([xk + HAND_X_AHEAD, d.geom_xpos[g][1], 0.0]) for g in hands]; pitch_c0 = pitch; tc0 = t
            hz = min(float(d.geom_xpos[g][2] - m.geom_size[g][0]) for g in hands)
            if href is None: href = hz
            v_ref = MARGIN * hguard.speed_limit(max(hz, 0.0))
            href = max(href - v_ref * m.opt.timestep, hz - 0.01)
            for g, ht in zip(hands, hand_tgt):
                mujoco.mj_jacGeom(m, d, (jp := np.zeros((3, nv))), None, g)
                task(jp[0:2], KC * (ht[:2] - d.geom_xpos[g][:2]) * 0.3, W_TASK)
                task(jp[2:3], -float(np.clip(v_ref + 8.0 * (hz - href), 0.0, v_ref)), W_TASK)
            task(jr[1:2], 3.0 * (min(PITCH_C, pitch_c0 + H_PITCH_RATE * (t - tc0)) - pitch), W_PITCH)
            vzh = max(-float((point_jac(m, d, m.geom_bodyid[g], d.geom_xpos[g]) @ d.qvel)[2]) for g in hands)
            hguard.observe(t, f['hands_arms'] > 1.0, vzh, f['hands_arms'])
            if f['hands_arms'] > 5.0:
                res['hand_contact_speed_mps'] = round(hguard.contact_speed, 4); tph['D'] = t; break
        J = np.vstack(rows); b = np.array(rhs); W = np.diag(w)
        A = J.T @ W @ J + LAM * np.eye(nv) + np.diag(lock)
        qd = np.linalg.solve(A, J.T @ W @ b)
        qa = qd[act]
        at = ((d.qpos[s.qadr] <= lo + 0.005) & (qa < 0)) | ((d.qpos[s.qadr] >= hi - 0.005) & (qa > 0))
        if at.any():   # active-set: freeze joints at their limits, re-solve
            l2 = lock.copy(); l2[act[at]] = 1e6
            qd = np.linalg.solve(J.T @ W @ J + LAM * np.eye(nv) + np.diag(l2), J.T @ W @ b); qa = qd[act]
        q_des = np.clip(q_des + qa * m.opt.timestep, lo, hi)
        if ph == 'K' and K_MODE == 'joint':
            if qK0 is None:
                qK0 = d.qpos[s.qadr].copy(); qK1 = s.target(dict(CL.SPAWN, **{k: v for k, v in K_ARMS.items() if v is not None})); sK = 0.0
                for i, n in enumerate(s.names):   # None in K_ARMS: hold that joint where K started
                    if any(n.endswith(k) for k, v in K_ARMS.items() if v is None): qK1[i] = qK0[i]
            vlim = kguard.speed_limit(max(gap, 0.0))
            sc = 1.0 if vz <= 0.5 * vlim else max(0.02, min(1.0, vlim / max(vz, 1e-6)))
            if 'S' not in tph: sK = min(1.0, sK + K_RATE * sc * m.opt.timestep)   # freeze at knee contact, settle
            a5 = 10 * sK**3 - 15 * sK**4 + 6 * sK**5
            q_des = qK0 + (qK1 - qK0) * a5; qa = np.zeros(m.nu)
        sup_g = feet + (kp if ph == 'C' else []) + (hands if ph == 'K' else [])
        tau = np.clip(s.pd(q_des, qa) + CL.static_ff(m, d, sup_g, act), -s.lim, s.lim)
        if KNEE_CAP:
            CL.apply_knee_stop_cap(s.names, lambda n: float(d.qpos[s.qadr[s.names.index(n)]]), tau, 'KNEEL')
        kq_ = max(float(d.qpos[s.qadr[i]]) for i, n in enumerate(s.names) if n.endswith('knee')); kmax[ph] = max(kmax.get(ph, 0.0), kq_)
        d.ctrl[:] = tau; peak_tau = np.maximum(peak_tau, np.abs(tau))
        if DEBUG and int(round(t * 1000)) % 100 == 0:
            r_ = np.abs(tau) / s.lim; i_ = int(np.argmax(r_))
            heel = min(p[2] for p in corners(m, d, feet[0], False)[2:])
            print(f'{t:.2f} {ph} comx-toe {com[0]-toe_x:+.3f} comz {com[2]:.3f} pitch {pitch:.2f} heel {heel:.3f} knee_z {d.geom_xpos[kp[0]][2]:.3f} sat {r_[i_]:.2f} {s.names[i_]} q {[round(float(d.qpos[s.qadr[i]]),2) for i,n in enumerate(s.names) if n.startswith("l_") and n[2:] in ("hip_pitch","knee","ankle_pitch")]} fz {f["feet"]:.0f} kp {f["knee_pads"]:.0f}')
        mujoco.mj_step(m, d); t += m.opt.timestep
        if ph in ('H', 'K'):
            f6 = np.zeros(6)
            for ci in range(d.ncon):
                c = d.contact[ci]
                for side, g in zip('lr', hands):
                    if g in (c.geom1, c.geom2) and (c.geom1 in s.floor or c.geom2 in s.floor):
                        mujoco.mj_contactForce(m, d, ci, f6); hpk[side] = max(hpk[side], float(f6[0]))
                        if hv[side] is None:
                            q_ = lambda j: float(d.qpos[m.jnt_qposadr[m.joint(f'{side}_{j}').id]])
                            hp_ = d.contact[ci].pos
                            def line_mm(body):   # horizontal distance of the vertical force line through the contact to a joint
                                jid_ = m.joint(f'{side}_{body}').id; return round(1000 * float(np.hypot(*(d.xanchor[jid_][:2] - hp_[:2]))), 1)
                            hpost[side] = dict(elbow_deg=round(np.degrees(q_('elbow')), 1), wrist_pitch_deg=round(np.degrees(q_('wrist_pitch')), 1),
                                               wrist_yaw_deg=round(np.degrees(q_('wrist_yaw')), 1), line_to_elbow_mm=line_mm('elbow'), line_to_shoulder_mm=line_mm('shoulder_pitch'))
                            v6 = np.zeros(6); mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_GEOM, g, v6, 0); hv[side] = round(-float(v6[5]), 4)
        if frames is not None and int(round(t * 1000)) % int(1000 / fps) == 0: frames.append(d.qpos.copy())
        if f['chest_pad'] > 1 or f['other'] > 1 or d.qpos[2] < 0.12:
            res['fell'] = dict(t=round(t, 3), phase=ph, chest=round(f['chest_pad'], 1), other=round(f['other'], 1)); break
    res['hand_plant_posture'] = hpost; res['hand_contact_speed_per_hand_mps'] = hv; res['hand_peak_force_per_hand_N'] = {k: round(v, 1) for k, v in hpk.items()}
    res['knee_peak_force_N'] = round(kguard.peak_force, 1); res['hand_peak_force_N'] = round(hguard.peak_force, 1)
    keys = ['A', 'B', 'C', 'D'] if ORDER == 'knees_first' else ['A', 'H', 'K', 'S', 'D']
    res['phase_times_s'] = {k: round(tph[keys[i + 1]] - tph[k], 3) for i, k in enumerate(keys[:-1]) if keys[i + 1] in tph}
    res['t_kneel_s'] = round(t, 3)
    res['knee_max_deg_by_phase'] = {k: round(float(np.degrees(v)), 1) for k, v in kmax.items()}
    res['peak_tau_Nm'] = {j: round(float(max(peak_tau[i] for i, n in enumerate(s.names) if n.endswith(j))), 1) for j in ('hip_pitch', 'knee', 'ankle_pitch', 'elbow', 'shoulder_pitch')}
    res['ankle_min_rad'] = round(float(min(d.qpos[m.jnt_qposadr[m.joint(n).id]] for n in ('l_ankle_pitch', 'r_ankle_pitch'))), 3)
    if join_chest and res['fell'] is None and 'D' in tph:
        _cap = CL.apply_knee_stop_cap; kd_ = {'q': 0.0}
        def _w(names, qf, tau, st):
            kd_['q'] = max(kd_['q'], max(qf(n) for n in names if n.endswith('knee'))); return _cap(names, qf, tau, st)
        CL.apply_knee_stop_cap = _w
        try:
            r2 = CL.run(sim=s, frames=frames, fps=fps)
        finally:
            CL.apply_knee_stop_cap = _cap
        res['knee_max_deg_by_phase']['D_chest'] = round(float(np.degrees(kd_['q'])), 1)
        res['chest'] = {k: r2[k] for k in ('chest_contact_speed_mps', 'peak_chest_N', 't_lower_s', 't_d94_flag_mo0_s', 'max_descent_speed_minus_guard_limit_mps', 'peak_tau_Nm', 'prone_static_N', 'other_contact_geoms')}
    global LAST_SIM; LAST_SIM = s
    return res


if __name__ == '__main__':
    import itertools
    out = dict(order='hands_first (Arbiter R-150 a39a2a4)', nominal=run())
    out['dr'] = [dict(run(ms, tc), mass=ms, pad_tc=tc) for ms, tc in itertools.product((65.0, 68.0, 68.5), (0.005, 0.02, 0.04))]
    json.dump(out, open(os.path.join(HERE, 'kneel_toe_wbc_results.json'), 'w'), indent=1, default=float)
    print(json.dumps(out['nominal'], indent=1, default=float))
