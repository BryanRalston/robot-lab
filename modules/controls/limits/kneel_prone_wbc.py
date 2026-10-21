"""R-146(b) G4 safe-stop path in sim: WBC toe-pivot kneel -> knee pads -> hands -> chest pad (prone) -> MO=0 under the
D94 interlocks. sim/v3 4115f6e, 68 kg, legs at the 0.5 derate, CPU MuJoCo, knee pads [EST] as in safe_sit_wbc.py.

Phases (times from the latch, which is t=0):
  P1 TOE_PIVOT (WBC): CoM moves forward over the toe line. The support polygon switches to the toe band (heel_line,
     toe_xy hooks), the feet pitch heel-up to FOOT_PITCH, and the CoM drops. The posture tracks a limit-checked IK pose
     with knees as low as the toe-supported CoM allows. The ankle is kept >= ANKLE_MIN (config; -0.79 rad stop).
  P2 KNEE_DROP (joint PD, fall-mode stand-in): the knees go forward to the pads (the last ~0.2 m is a short drop) and
     the arms reach forward.
  P3 HANDS: hands/forearms to the floor, hips extend.
  P4 PRONE: lower onto the chest pad, then soft gains (KP_SOFT) so the commanded torques settle.
  MO=0 only via DriveDerateSupervisor (kneel_enabled=True): contact (knee pad or chest pad), CoM inside the contact
  hull, CoM speed < 0.1 m/s, and torque_ok (|tau| < D94 friction hold at every joint), all held for 50 ms.
"""
import os, sys, json
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np
import mujoco
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import safe_sit_wbc as S
from safe_sit_wbc import mj, mj_d, PEL_PITCH, WalkController, FC, HALF_W, load, LEG
from controller import ankle_from_toe
from gait_lib import quat_pitch, TOE, HEEL
import gait_lib as GL
from drive_thermal_derate import (DerateConfig, DriveDerateSupervisor, MO_OFF, KNEEL, CONTACT_CONFIRMED,
                                  friction_hold, static_hold_ok)

ANKLE_MIN = -0.79          # rad, ankle dorsiflexion stop (Legs may extend it; config value)
FOOT_PITCH = 0.5           # rad heel-up at the end of P1
P1_PZ, P1_PITCH, P1_CX = 0.74, 0.0, TOE - 0.04   # IK search result: knee origin 0.29 m, CoM 0.68 m over the toes
T1A = 0.8                  # P1a: flat-foot CoM shift to the toe line (before the heel lifts)
T1, T2, T3, T4 = 1.0, 0.5, 0.5, 0.6   # T1: P1b pivot + lower
KP_SOFT = 0.05
XK = 0.0
ZMP_K = (12.0, 7.0)          # fallback only; kneel/safe-stop mode uses controller_config safe_stop_zmp_k
def _safe_stop_zmp_k():
    import json
    try:
        c = json.load(open(os.path.join(HERE, '..', 'controller_config.json')))['drive_thermal_derate']
        return tuple(c['safe_stop_zmp_k'])
    except (OSError, KeyError):
        return ZMP_K
POSE_KNEEL = {'hip_pitch': -0.3, 'knee': 1.6, 'ankle_pitch': 0.6, 'waist_pitch': 0.2, 'shoulder_pitch': -1.3}
POSE_HANDS = {'hip_pitch': -0.9, 'knee': 1.5, 'ankle_pitch': 0.6, 'waist_pitch': 0.4, 'shoulder_pitch': -1.4, 'elbow': 0.3}
POSE_PRONE = {'hip_pitch': 0.0, 'knee': 0.3, 'ankle_pitch': 0.5, 'waist_pitch': 0.0, 'shoulder_pitch': -0.3, 'elbow': 1.8}


def _model():
    orig = GL.XML; p = S._xml_with_pads()
    try:
        GL.XML = p; os.environ['LEGS_CHAIR'] = ''
        m = load()
    finally:
        GL.XML = orig; os.unlink(p)
    m.opt.timestep = 0.001
    return m


def _pose(names, base, spec):
    q = base.copy()
    for i, n in enumerate(names):
        for k, v in spec.items():
            if n.endswith(k): q[i] = v
    return q


def run(frames=None, fps=25, tail=1.0):
    m = _model(); d = mujoco.MjData(m)
    ctrl = WalkController(m); ctrl.stand_only = True
    ctrl.initialize(d)
    ctrl.zmp_k = _safe_stop_zmp_k()   # safe-stop mode only; set on this controller instance
    names = list(ctrl.act_name)
    leg = np.array([any(n.endswith(j) for j in LEG) for n in names])
    nominal = ctrl.tau_max.copy(); der = np.where(leg, S.DERATE * nominal, nominal); ctrl.tau_max = der.copy()
    qadr = np.array([m.jnt_qposadr[m.actuator_trnid[i, 0]] for i in range(m.nu)])
    vadr = np.array([m.jnt_dofadr[m.actuator_trnid[i, 0]] for i in range(m.nu)])
    for i, n in enumerate(names):          # ankle stop as a config value
        if n.endswith('ankle_pitch'):
            j = m.actuator_trnid[i, 0]; m.jnt_range[j, 0] = ANKLE_MIN
    g = np.load(os.path.join(S.LEGS, 'rl', 'gains.npz')); gn = [str(x) for x in g['joint_names'].tolist()]
    kp = np.array([g['kp'][gn.index(n)] for n in names]); kd = np.array([g['kd'][gn.index(n)] for n in names])
    # P1 target pose (feet pitched about the toes)
    q0 = d.qpos.copy(); z0 = ctrl.com_z_ref
    toe = {'l': np.array([TOE, HALF_W, 0.0]), 'r': np.array([TOE, -HALF_W, 0.0])}
    feet = {k: (ankle_from_toe(v, 0.0, FOOT_PITCH), 0.0, FOOT_PITCH) for k, v in toe.items()}
    q1 = ctrl.robot.ik_com(d.qpos.copy(), feet, np.array([P1_CX, 0.0]), P1_PZ, quat_pitch(P1_PITCH), iters=15)
    ctrl.robot.fk(q1); z1 = float(ctrl.robot.com()[2])
    plant0 = {s: dict(ctrl.plant[s]) for s in 'lr'}
    pads = {m.geom('l_knee_pad').id, m.geom('r_knee_pad').id}
    chest = {m.geom('chest_pad').id} if 'chest_pad' in [m.geom(i).name for i in range(m.ngeom)] else set()
    floor = {i for i in range(m.ngeom) if m.geom_type[i] == mujoco.mjtGeom.mjGEOM_PLANE}
    hands = {i for i in range(m.ngeom) if 'hand' in m.geom(i).name or 'forearm' in m.geom(i).name}
    feetg = {m.geom('l_foot').id, m.geom('r_foot').id}
    cfg = DerateConfig(kneel_enabled=True, t_stop=82.0, kneel_timeout_s=T1 + T2 + T3 + T4 + 1.5)
    class IO:
        mo = {n: True for n in names}
        def read_temp(s, n): return 82.0
        def write_limit(s, n, pm): pass
        def set_mo(s, n, on): s.mo[n] = on
        def read_fault(s, n): return 0, 0
    io = IO()
    sup = DriveDerateSupervisor(names, io, cfg)
    res = dict(phases={}, fell=None, peak_pad_N=0.0, peak_chest_N=0.0, peak_hand_N=0.0, tau_frac_wbc=0.0, tau_frac_pd=0.0,
               t_knee_contact=None, t_hand_contact=None, t_chest_contact=None, t_mo_off=None, ankle_min=1.0)
    ren = None
    if frames is not None:
        ren = mujoco.Renderer(m, 360, 480); cam = mujoco.MjvCamera()
        cam.azimuth = 120; cam.elevation = -12; cam.distance = 3.0; cam.lookat[:] = [0.4, 0, 0.45]
    f6 = np.zeros(6); qa = None; phase = 'P1'; tph = 0.0
    T_all = T1A + T1 + T2 + T3 + T4 + tail + 1.5
    for k in range(int(T_all / 0.001)):
        t = k * 0.001
        sup.step(0.001)
        if k == 0:
            sup.crouch_done()   # no separate crouch in the G4 path: the toe-pivot kneel starts at the latch
        if phase == 'P1':
            if t < T1A:                        # P1a: CoM forward over the toes, flat feet
                sa = mj(t / T1A)
                xr = FC + (P1_CX - FC) * sa
                mujoco.mj_subtreeVel(m, d) if k == 0 else None
                ex = float(d.subtree_com[1][0]) - xr
                ctrl.x_ref = xr - float(np.clip(XK * ex, -0.05, 0.05))
                ctrl.com_z_ref = z0; ctrl.q_ref = q0; ctrl.v_ref = np.zeros(m.nv)
                ctrl.step(d)
            else:                              # P1b: toe pivot (support -> toe band, heel lift) and lower
                s = (t - T1A) / T1; a = mj(s)
                th = FOOT_PITCH * a
                for sd in 'lr':
                    pl = ctrl.plant[sd]
                    pl['ankle'] = ankle_from_toe(toe[sd], 0.0, th)
                    pl['R'] = S._rpy(0.0, th, 0.0)
                ctrl.heel_line = TOE - 0.03
                ctrl.toe_xy = {sd: toe[sd][:2] for sd in 'lr'}
                ctrl.com_z_ref = z0 + (z1 - z0) * a
                ctrl.q_ref = q0 + (q1 - q0) * a
                v = np.zeros(m.nv); v[6:] = (q1 - q0)[7:] * mj_d(s) / T1 if s < 1 else 0.0
                ctrl.v_ref = v
                ex = float(d.subtree_com[1][0]) - P1_CX
                ctrl.x_ref = P1_CX - float(np.clip(XK * ex, -0.05, 0.05))
                PEL_PITCH['now'] = P1_PITCH * a
                ctrl.step(d)
                if s >= 1.0:
                    phase, tph, qa = 'P2', t, d.qpos[qadr].copy(); res['phases']['P1_toe_pivot'] = round(t, 3)
            if t >= T1A and 'P1a_com_shift' not in res['phases']:
                res['phases']['P1a_com_shift'] = round(t, 3)
            res['tau_frac_wbc'] = max(res['tau_frac_wbc'], float(np.max(np.abs(d.ctrl[leg]) / der[leg])))
        else:
            if phase == 'P2':
                tgt, T = _pose(names, qa, POSE_KNEEL), T2
            elif phase == 'P3':
                tgt, T = _pose(names, qa, POSE_HANDS), T3
            else:
                tgt, T = _pose(names, qa, POSE_PRONE), T4
            s = (t - tph) / T
            qt = qa + (tgt - qa) * mj(s); vt = (tgt - qa) * mj_d(s) / T if s < 1 else 0 * qa
            gain = KP_SOFT if (phase == 'P4' and s >= 1.0) else 1.0
            tau = np.clip(gain * kp * (qt - d.qpos[qadr]) + np.sqrt(gain) * kd * (vt - d.qvel[vadr]), -der, der)
            on = np.array([io.mo[n] for n in names], float)
            d.ctrl[:] = tau * on
            if on.all():
                res['tau_frac_pd'] = max(res['tau_frac_pd'], float(np.max(np.abs(tau[leg]) / der[leg])))
            if s >= 1.0 and phase in ('P2', 'P3'):
                key = {'P2': 'P2_knee_drop', 'P3': 'P3_hands'}[phase]
                res['phases'][key] = round(t, 3)
                phase = {'P2': 'P3', 'P3': 'P4'}[phase]; tph = t; qa = d.qpos[qadr].copy()
            if phase == 'P4' and s >= 1.0 and 'P4_prone' not in res['phases']:
                res['phases']['P4_prone'] = round(t, 3)
        mujoco.mj_step(m, d)
        res['ankle_min'] = min(res['ankle_min'], float(min(d.qpos[qadr][[i for i, n in enumerate(names) if n.endswith('ankle_pitch')]])))
        pts = []; pad = chestc = False; pf = cf = hf = 0.0
        for i in range(d.ncon):
            c = d.contact[i]; gg = {c.geom1, c.geom2}
            if not gg & floor: continue
            o = (gg - floor).pop()
            mujoco.mj_contactForce(m, d, i, f6)
            pts.append(c.pos[:2].copy())
            if o in pads: pad = True; pf += f6[0]
            elif o in chest: chestc = True; cf += f6[0]
            elif o in hands: hf += f6[0]
            elif o not in feetg and phase == 'P1':
                res['fell'] = res['fell'] or f'{t:.3f} {m.geom(o).name} on floor in P1'
        res['peak_pad_N'] = max(res['peak_pad_N'], pf); res['peak_chest_N'] = max(res['peak_chest_N'], cf); res['peak_hand_N'] = max(res['peak_hand_N'], hf)
        if pad and res['t_knee_contact'] is None: res['t_knee_contact'] = round(t, 3)
        if hf > 1 and res['t_hand_contact'] is None: res['t_hand_contact'] = round(t, 3)
        if chestc and res['t_chest_contact'] is None: res['t_chest_contact'] = round(t, 3)
        mujoco.mj_subtreeVel(m, d)
        com = d.subtree_com[1]; v = float(np.linalg.norm(d.subtree_linvel[1]))
        inside, _ = S._hull_contains(pts, com[:2]) if len(pts) >= 3 else (False, -1)
        tq = static_hold_ok({n: float(d.ctrl[i]) for i, n in enumerate(names)}) if phase == 'P4' else False
        sup.set_support(pad or chestc, inside, v, tq)
        if sup.state == MO_OFF and res['t_mo_off'] is None:
            res['t_mo_off'] = round(t, 3)
        if ren is not None and k % int(1000 / fps) == 0:
            ren.update_scene(d, cam); frames.append(ren.render().copy())
        if res['t_mo_off'] is not None and t > res['t_mo_off'] + tail:
            break
    res['state'] = sup.state; res['log'] = sup.log
    res['final_contacts'] = sorted({m.geom((({d.contact[i].geom1, d.contact[i].geom2} - floor) or {0}).pop()).name for i in range(d.ncon)})
    for kk in list(res):
        if isinstance(res[kk], float): res[kk] = round(res[kk], 3)
    res['gate_3p3s'] = res['t_mo_off'] is not None and res['t_mo_off'] <= 3.3
    return res


if __name__ == '__main__':
    gif = '--gif' in sys.argv
    fr = [] if gif else None
    r = run(frames=fr)
    print(json.dumps(r, default=str))
    if gif:
        import imageio.v2 as io
        io.mimsave(os.path.join(S.ROOT, 'media', 'progress', '2026-10-21_controls_r146b_kneel_prone.gif'), fr, duration=0.04, loop=0)
