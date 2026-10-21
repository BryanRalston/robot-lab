"""R-146(b) ruling: WBC chest-supported lower, tested on its own (independent of the kneel).
sim/v3 (prone_data.Sim: knee pads [EST], chest pad), 68 kg, CPU MuJoCo 1 kHz.

Spawn: supported hands-and-knees, elbows bent (knee pads + hands loaded, chest pad ~0.29 m off the floor), settled
under PD. Lower: a task-space WBC (damped weighted least squares on the full floating-base Jacobian, every step):
  - hands and knee pads: hold their world positions (support constraints, high weight)
  - chest pad lowest point: track a descent velocity v_ref = MARGIN * ProneLowerGuard.speed_limit(gap_ref)
    (0.4 m/s at >=200 mm ramping to 0.1 m/s at <=50 mm) + position feedback on gap_ref
  - posture regulariser, low weight (hips extend and elbows/shoulders flex eccentrically as the IK needs)
Joint targets are integrated from the IK rates and tracked by joint PD + gravity/Coriolis feed-forward (qfrc_bias
of the actuated dofs, weighted 0.5). Torques are clipped to the caps: legs AND arms x0.5 (derate),
elbow also <= 69 N·m hard cap (soft_limits.json R-080/R-085); elbow thermal 40 N·m (180 s) and 28 N·m continuous
are reported, not enforced.
Contact (chest force > 1 N) -> hold the targets until settled (|vz| < 5 mm/s for 0.2 s) -> relax the torque scale
1 -> 0 over RELAX_S while watching for motion -> D94 flag (every applied |tau| < friction hold, chest still) -> MO=0
(friction only) for 1 s, then the residual drop is measured.
"""
import os, sys, json, itertools
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import prone_data as P
from drive_thermal_derate import ProneLowerGuard, friction_hold
from soft_limits import apply_knee_stop_cap

SPAWN = {'hip_pitch': -1.1, 'knee': 1.6, 'ankle_pitch': 0.6, 'shoulder_pitch': -0.85, 'elbow': -1.0, 'neck_pitch': -0.3}   # hands-and-knees: hands + knee pads
SPAWN_PITCH = 1.35
MARGIN = 0.9          # track 90 % of the guard speed limit
GAP_END = -0.004      # reference ends just into the pad (preload)
REF_LEAD = 0.01      # reference may lead the measured gap by at most 10 mm
K_POST = 0.0         # posture pull toward the spawn pose (rad/s per rad)
KV = 0.5            # measured-speed feedback
KZ = 8.0              # chest gap position feedback (1/s)
KC = 20.0             # support point drift feedback (1/s)
W_SUP, W_CHEST, W_PITCH, LAM = 30.0, 10.0, 5.0, 0.05
W_FA = 10.0
W_KNEE_ROT = 0.0    # 30: knee pads stay loaded but the elbows hit the 38 N·m derated cap and the lower stalls at ~50 mm
ARM_SHARE_END = 0.35
W_COM, ARM_SHARE = 0.0, 0.35   # off: worse (pushes the hips to the torque cap)
W_HAND = 0.0   # off: palm-flat hold moves the load to the elbow (wrist range 70 deg)
KFA = 4.0
PITCH_END, KP_PITCH = 1.52, 3.0   # trunk pitch is slaved to the chest gap: spawn pitch -> PITCH_END (slightly head-up) at gap 0
RELAX_S = 0.8
ELBOW_HARD, ELBOW_SHORT, ELBOW_CONT = 69.0, 40.0, 28.0
ARM = ('shoulder_pitch', 'shoulder_roll', 'shoulder_yaw', 'elbow', 'wrist_roll', 'wrist_pitch', 'wrist_yaw')


FF = 1.0
SUPPORT = ('l_hand', 'r_hand', 'l_knee_pad', 'r_knee_pad')


def static_ff(m, d, sup, act):
    """Contact-consistent gravity/Coriolis feed-forward: pick support forces f (hands + knee pads, 3D each,
    min-norm, damped) so the floating-base rows of qfrc_bias are balanced, then tau = bias_act - Jc_act^T f."""
    jp = np.zeros((3, m.nv)); Js = []
    for g in sup:
        mujoco.mj_jacGeom(m, d, jp, None, g); Js.append(jp.copy())
    Jc = np.vstack(Js)                        # (3k, nv)
    A = Jc[:, :6].T                           # (6, 3k)
    b = d.qfrc_bias[:6]
    f = A.T @ np.linalg.solve(A @ A.T + 1e-6 * np.eye(6), b)
    return d.qfrc_bias[act] - (Jc[:, act].T @ f)


ELBOW_KNEEL_NM = None   # None: 38 N.m derate (0.5 x 76). 49.0: Arms R19 proposal, kneel/lower only, NOT ruled


def make_sim(mass=68.0, pad_tc=0.02):
    s = P.Sim(mass, 1.0, pad_tc); m = s.m
    arm = np.array([any(n.endswith(a) for a in ARM) for n in s.names])
    s.lim = np.where(arm, 0.5 * m.actuator_ctrlrange[:, 1], s.lim)
    el = np.array([n.endswith('elbow') for n in s.names])
    s.lim = np.where(el, np.minimum(s.lim, ELBOW_HARD), s.lim)
    if ELBOW_KNEEL_NM is not None:   # kneel/lower states only (Arms R19 3de759b: ~49 N.m for 2 s at 82 C) [EST], Arbiter proposal
        s.lim = np.where(el, min(ELBOW_KNEEL_NM, ELBOW_HARD), s.lim)
    return s


def run(mass=68.0, pad_tc=0.02, frames=None, fps=25, sim=None):
    """sim=None: standalone (spawn hands-and-knees). sim given: continue from its current state (joined sequence)."""
    if sim is None:
        s = make_sim(mass, pad_tc); m, d = s.m, s.d
        s.place(SPAWN, SPAWN_PITCH); qs = s.target(SPAWN)
        for _ in range(1500):
            d.ctrl[:] = s.pd(qs); mujoco.mj_step(m, d)
    else:
        s = sim; m, d = s.m, s.d
    el = np.array([n.endswith('elbow') for n in s.names])
    sup = [m.geom(g).id for g in SUPPORT]
    p0 = {g: d.geom_xpos[g].copy() for g in sup}
    hand_ids = {m.geom('l_hand').id, m.geom('r_hand').id}
    knee_ids = {m.geom('l_knee_pad').id, m.geom('r_knee_pad').id}
    Rk0 = {g: d.geom_xmat[g].reshape(3, 3).copy() for g in knee_ids}
    Rh0 = {g: d.geom_xmat[g].reshape(3, 3).copy() for g in hand_ids}
    q_des = d.qpos[s.qadr].copy(); q_nom = q_des.copy()
    pitch0 = 2 * np.arcsin(d.qpos[5])
    dx0 = {sd: float(d.xpos[m.body(f'{sd}_forearm').id][0] - d.geom_xpos[m.geom(f'{sd.lower()}_hand').id][0]) for sd in 'LR'}
    guard = ProneLowerGuard(); gap0, _ = s.chest_gap_vz(); gap_ref = gap0
    nv = m.nv; act = s.vadr
    IKJ = ('hip_pitch', 'knee', 'ankle_pitch', 'shoulder_pitch', 'elbow', 'wrist_pitch')
    lock = np.zeros(nv)
    for i, n in enumerate(s.names):
        if not any(n.endswith(j) for j in IKJ): lock[act[i]] = 1e6
    jid = m.actuator_trnid[:, 0]; lo = m.jnt_range[jid, 0] + 0.02; hi = m.jnt_range[jid, 1] - 0.02
    jp = np.zeros((3, nv)); jr = np.zeros((3, nv))
    t = 0.0; st = 'LOWER'; t_contact = t_settled = t_flag = None; still = 0.0; scale = 1.0
    load_settled = q_settled = pitch_settled = None
    peak_tau = np.zeros(m.nu); hist = []; moved_in_relax = 0.0; t_relax0 = None
    while t < 8.0:
        gap, vz = s.chest_gap_vz()
        f = s.contacts()
        fc = f['chest_pad']
        guard.observe(t, fc > 1.0, vz, fc)
        if st == 'LOWER':
            v_ref = MARGIN * guard.speed_limit(max(gap_ref, 0.0))
            gap_ref = max(GAP_END, gap_ref - v_ref * m.opt.timestep, gap - REF_LEAD)   # reference governor
            if gap_ref <= GAP_END: v_ref = MARGIN * guard.v_contact   # keep approaching at the contact speed until touch
            rows = []; rhs = []; w = []
            for g in sup:
                mujoco.mj_jacGeom(m, d, jp, jr, g)
                rows.append(jp.copy()); rhs.extend(-KC * (d.geom_xpos[g] - p0[g])); w += [W_SUP] * 3
                if g in knee_ids and W_KNEE_ROT > 0:   # keep the shank on its pad (no rocking off the pad)
                    R = d.geom_xmat[g].reshape(3, 3); R0 = Rk0[g]
                    eo = 0.5 * (np.cross(R[:, 0], R0[:, 0]) + np.cross(R[:, 1], R0[:, 1]) + np.cross(R[:, 2], R0[:, 2]))
                    rows.append(jr.copy()); rhs.extend(KC * eo); w += [W_KNEE_ROT] * 3
                if g in hand_ids:   # keep the palm flat (no roll onto the hand box edge)
                    R = d.geom_xmat[g].reshape(3, 3); R0 = Rh0[g]
                    eo = 0.5 * (np.cross(R[:, 0], R0[:, 0]) + np.cross(R[:, 1], R0[:, 1]) + np.cross(R[:, 2], R0[:, 2]))
                    rows.append(jr.copy()); rhs.extend(KC * eo); w += [W_HAND] * 3
            # elbow over hand (forearm vertical): the hand force then passes through the elbow -> low elbow torque
            for side in 'LR':
                eb = m.body(f'{side}_forearm').id; hg = m.geom(f'{side.lower()}_hand').id
                jpe = np.zeros((3, nv)); mujoco.mj_jacBody(m, d, jpe, None, eb)
                jph = np.zeros((3, nv)); mujoco.mj_jacGeom(m, d, jph, None, hg)
                rows.append((jpe - jph)[0:1]); rhs.append(-KFA * (d.xpos[eb][0] - d.geom_xpos[hg][0] - dx0[side] * max(gap_ref, 0.0) / gap0)); w.append(W_FA)
            # CoM x: keep the arm share of the weight ~ARM_SHARE (CoM between knee pads and hands)
            if W_COM > 0:
                xk = 0.5 * (p0[sup[2]][0] + p0[sup[3]][0]); xh = 0.5 * (p0[sup[0]][0] + p0[sup[1]][0])
                jc = np.zeros((3, nv)); mujoco.mj_jacSubtreeCom(m, d, jc, 1)
                sh = ARM_SHARE_END + (ARM_SHARE - ARM_SHARE_END) * max(gap_ref, 0.0) / gap0
                rows.append(jc[0:1].copy()); rhs.append(KC * (xk + sh * (xh - xk) - d.subtree_com[1][0])); w.append(W_COM)
            # chest lowest point: use pad body jacobian at the pad centre (z row)
            mujoco.mj_jacGeom(m, d, jp, jr, s.cp)
            rows.append(jp[2:3].copy()); rhs.append(-float(np.clip(v_ref + KZ * (gap - gap_ref) + KV * (v_ref - vz), 0.0, MARGIN * guard.speed_limit(max(gap, 0.0))))); w.append(W_CHEST)
            # trunk pitch: keep (pitch rate 0)
            mujoco.mj_jacBody(m, d, jp, jr, s.torso)
            pitch = 2 * np.arcsin(np.clip(d.qpos[5] / max(np.linalg.norm(d.qpos[3:7]), 1e-9), -1, 1))
            pitch_ref = PITCH_END + (pitch0 - PITCH_END) * max(gap_ref, 0.0) / gap0
            rows.append(jr[1:2].copy()); rhs.append(KP_PITCH * (pitch_ref - pitch)); w.append(W_PITCH)
            J = np.vstack(rows); b = np.array(rhs); W = np.diag(w)
            A = J.T @ W @ J + LAM * np.eye(nv) + np.diag(lock)
            reg = np.zeros(nv); reg[act] = K_POST * (q_nom - d.qpos[s.qadr])
            qd = np.linalg.solve(A, J.T @ W @ b + LAM * reg)
            qd_act = qd[act]
            q_des = np.clip(q_des + qd_act * m.opt.timestep, lo, hi)
            if fc > 1.0:
                st = 'HOLD'; t_contact = t; qd_act[:] = 0
        else:
            qd_act = np.zeros(m.nu)
        if st == 'HOLD':
            still = still + m.opt.timestep if abs(vz) < 0.005 else 0.0
            if still >= 0.2:
                st = 'RELAX'; t_settled = t; t_relax0 = t
                load_settled = {k: round(float(v), 1) for k, v in f.items()}
                q_settled = {n: round(float(d.qpos[s.qadr[i]]), 2) for i, n in enumerate(s.names) if n.startswith('l_') and n[2:] in ('hip_pitch', 'knee', 'ankle_pitch', 'shoulder_pitch', 'elbow')}
                pitch_settled = round(float(2 * np.arcsin(d.qpos[5])), 3)
        if st == 'RELAX':
            scale = max(0.0, 1.0 - (t - t_relax0) / RELAX_S)
            moved_in_relax = max(moved_in_relax, abs(vz))
        tau = s.pd(q_des, qd_act) + FF * static_ff(m, d, sup, act)
        tau = np.clip(tau, -s.lim, s.lim) * scale
        apply_knee_stop_cap(s.names, lambda n: float(d.qpos[s.qadr[s.names.index(n)]]), tau, 'CHEST_LOWER')   # 513a7d5 cap
        if st == 'RELAX':
            flag = all(abs(tau[i]) < friction_hold(n) for i, n in enumerate(s.names)) and abs(vz) < 0.01
            if flag:
                st = 'MO_OFF'; t_flag = t; t_mo = t
                for i, n in enumerate(s.names):
                    m.dof_frictionloss[s.vadr[i]] = friction_hold(n)
        if st == 'MO_OFF':
            tau[:] = 0
            if t - t_mo > 1.0: break
        d.ctrl[:] = tau
        peak_tau = np.maximum(peak_tau, np.abs(tau))
        mujoco.mj_step(m, d); t += m.opt.timestep
        if frames is not None and int(t * 1000) % int(1000 / fps) == 0:
            frames.append(d.qpos.copy())
        hist.append((t, gap, vz, fc, gap_ref, 2 * np.arcsin(d.qpos[5]), float(np.abs(tau[el]).max()), float((np.abs(tau) / s.lim).max()), int(np.argmax(np.abs(tau) / s.lim))))
    H = np.array(hist); global LAST_H; LAST_H = H
    pre = H[:, 3] <= 1.0
    lim_tr = np.array([guard.speed_limit(max(g_, 0.0)) for g_ in H[pre, 1]])
    over = float(np.max(H[pre, 2] - lim_tr)) if pre.any() else None
    gap_final, _ = s.chest_gap_vz(); loads = s.contacts()
    other_geoms = sorted({m.geom(g).name for i in range(d.ncon) for g in (d.contact[i].geom1, d.contact[i].geom2)
                          if g not in s.floor and not any(g in ids for ids in s.groups.values())})
    global LAST_SIM; LAST_SIM = s
    tau_j = {n: round(float(peak_tau[i]), 1) for i, n in enumerate(s.names)}
    def pk(suf): return max(v for k, v in tau_j.items() if k.endswith(suf))
    return dict(mass=mass, pad_tc=pad_tc, gap0_m=round(gap0, 3),
                chest_contact_speed_mps=None if guard.contact_speed is None else round(guard.contact_speed, 4),
                peak_chest_N=round(guard.peak_force, 1), guard_ok=guard.ok,
                t_lower_s=None if t_contact is None else round(t_contact, 3),
                t_settled_s=None if t_settled is None else round(t_settled, 3),
                t_d94_flag_mo0_s=None if t_flag is None else round(t_flag, 3),
                max_chest_speed_in_relax_mps=round(moved_in_relax, 4),
                chest_gap_final_m=round(gap_final, 4),
                max_descent_speed_minus_guard_limit_mps=None if over is None else round(over, 4),
                other_contact_geoms=other_geoms,
                peak_tau_Nm=dict(elbow=pk('elbow'), shoulder_pitch=pk('shoulder_pitch'), hip_pitch=pk('hip_pitch'),
                                 knee=pk('knee'), ankle_pitch=pk('ankle_pitch')),
                caps_Nm=dict(elbow=float(s.lim[el].max()), elbow_hard=ELBOW_HARD, elbow_thermal_short_180s=ELBOW_SHORT,
                             elbow_thermal_cont=ELBOW_CONT,
                             shoulder_pitch=float(s.lim[[n.endswith('shoulder_pitch') for n in s.names]].max()),
                             hip_pitch=float(s.lim[[n.endswith('hip_pitch') for n in s.names]].max()),
                             knee=float(s.lim[[n.endswith('knee') for n in s.names]].max())),
                load_at_settle_N=load_settled, q_at_settle=q_settled, trunk_pitch_at_settle=pitch_settled,
                prone_static_N={k: round(float(v), 1) for k, v in loads.items()})


if __name__ == '__main__':
    out = dict(nominal=run())
    out['dr'] = [run(ms, tc) for ms, tc in itertools.product((65.0, 68.5), (0.005, 0.02, 0.04))]
    sp = [r['chest_contact_speed_mps'] for r in out['dr'] if r['chest_contact_speed_mps'] is not None]
    out['dr_summary'] = dict(n=len(out['dr']), contacts=len(sp), speed_max=max(sp) if sp else None,
                             peak_chest_N_max=max(r['peak_chest_N'] for r in out['dr']))
    json.dump(out, open(os.path.join(HERE, 'chest_lower_wbc_results.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))
