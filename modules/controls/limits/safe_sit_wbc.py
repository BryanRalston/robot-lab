"""R-141/R-142 safe-sit timing in sim: the legs WBC (modules/legs/wbc, QP + ZMP balance) holds the CoM over the
feet while it lowers the CoM on a minimum-jerk profile into a deep sit/squat pose over a 0.45 m chair box.
Leg drive torque limits are the 0.5 derate (the stop latches at >= 83 C, R-142, where f(T) = 0.5).
Light CPU MuJoCo only. Model: sim/v3 at 68 kg (LEGS_MASS=68, R-123).

Pass per duration: no fall (pelvis tilt < pitch ref + 0.6 rad, pelvis z > 0.3 m), ZMP (measured CoP of the feet) inside the support polygon
(margin >= 0), |tau| <= derated limit for all leg actuators, QP failures 0, final CoM within 3 cm of target height.
Usage: python safe_sit_wbc.py [--gif]
"""
import os, sys, json, argparse
os.environ.setdefault('LEGS_MASS', '68')
os.environ.setdefault('LEGS_LIMITS', 'r1')
os.environ.setdefault('LEGS_CHAIR', '-0.02,0.45')   # chair seat front edge at x -0.02, seat 0.45 m (visual, no contact)
os.environ.setdefault('MUJOCO_GL', 'glfw')   # egl/osmesa unavailable on the box
import numpy as np
import mujoco
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
LEGS = os.path.join(ROOT, 'modules', 'legs')
sys.path[:0] = [LEGS, os.path.join(LEGS, 'wbc')]
from gait_lib import load, LEG, SOLE
import controller as _wbcmod
from controller import WalkController, HALF_W, FC, measured_cop
from gait_lib import quat_pitch

# Pelvis pitch reference. controller._wbc holds the pelvis at rpy_R(0, 0, yaw_ref) (line ~841), and that is its
# only rpy_R call. This script wraps rpy_R for calls from _wbc only, so the pelvis attitude task tracks
# PEL_PITCH['now']. The legs module itself is not edited.
PEL_PITCH = {'now': 0.0}
_rpy = _wbcmod.rpy_R
def _rpy_hook(roll, pitch, yaw):
    if sys._getframe(1).f_code.co_name == '_wbc' and roll == 0.0 and pitch == 0.0:
        return _rpy(0.0, PEL_PITCH['now'], yaw)
    return _rpy(roll, pitch, yaw)
_wbcmod.rpy_R = _rpy_hook

# Leg posture gain. In stand mode the WBC weights leg posture at kp 16, kd 3, w 0.12, so during a descent the
# hips lag and the shank runs into the ankle dorsiflexion stop (-0.79 rad), then it diverges. This rebuilds
# _wbc at runtime from its own source, with those three literals read from LEG_POSTURE. controller.py is unchanged.
import inspect, textwrap
LEG_POSTURE = {'kp': 16.0, 'kd': 3.0, 'w': 0.12}
_src = textwrap.dedent(inspect.getsource(_wbcmod.WalkController._wbc))
_lit = 'kp, kd, w = 16.0, 3.0, 0.12'
assert _src.count(_lit) == 1, 'controller._wbc leg posture literal changed'
_src = _src.replace(_lit, "kp, kd, w = LEG_POSTURE['kp'], LEG_POSTURE['kd'], LEG_POSTURE['w']")
_ns = dict(vars(_wbcmod)); _ns['LEG_POSTURE'] = LEG_POSTURE
exec(compile(_src, _wbcmod.__file__ + ':_wbc[patched]', 'exec'), _ns)
_wbcmod.WalkController._wbc = _ns['_wbc']

DERATE = 0.5
SETTLE = 0.5
HOLD = 1.5
WAIST = 0.0
SHOULDER = 0.0
XK = 0.0          # 5.0 used for the pitched-crouch case
LEAD = 1.0
PITCH = 0.0       # rad pelvis forward pitch at the bottom (hip flexion; keeps ankle inside its -0.79 rad stop)


def mj(s):
    s = min(max(s, 0.0), 1.0)
    return 10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5


def mj_d(s):
    s = min(max(s, 0.0), 1.0)
    return 30 * s ** 2 - 60 * s ** 3 + 30 * s ** 4


def sit_pose(ctrl, d, pel_z):
    r = ctrl.robot
    m = ctrl.m
    d0 = d.qpos.copy()
    A = lambda n: m.jnt_qposadr[m.joint(n).id]
    # Trunk lean and arms forward put the CoM ahead so the shank stays inside the ankle dorsiflexion stop
    # (-0.79 rad); with an upright trunk the IK needs ankle -1.05 rad at this depth.
    d0[A('waist_pitch')] = WAIST
    d0[A('l_shoulder_pitch')] = d0[A('r_shoulder_pitch')] = SHOULDER
    feet = {'l': (np.array([0.0, HALF_W, SOLE]), 0.0, 0.0), 'r': (np.array([0.0, -HALF_W, SOLE]), 0.0, 0.0)}
    q = r.ik_com(d0, feet, np.array([FC, 0.0]), pel_z, quat_pitch(PITCH), iters=12)
    r.fk(q)
    return q, float(r.com()[2])


def run(T, pel_z_sit=0.85, frames=None, fps=25):
    m = load()
    m.opt.timestep = 0.001
    d = mujoco.MjData(m)
    ctrl = WalkController(m)
    ctrl.stand_only = True
    info = ctrl.initialize(d)
    leg = np.array([any(ctrl.act_name[i].endswith(j) for j in LEG) for i in range(m.nu)])
    nominal = ctrl.tau_max.copy()
    ctrl.tau_max = np.where(leg, DERATE * nominal, nominal)   # derate on every leg drive (whole-robot worst case)
    PEL_PITCH['now'] = 0.0
    q0 = d.qpos.copy(); z0 = ctrl.com_z_ref
    q1, z1 = sit_pose(ctrl, d, pel_z_sit)
    ctrl.v_ref = np.zeros(m.nv)
    res = dict(T=T, fell=None, cop_margin_min_mm=1e9, tau_ratio_max=0.0, qp_fail=0, com_z0=round(z0, 3), com_z_target=round(z1, 3))
    soles = [m.geom('l_foot').id, m.geom('r_foot').id]
    renderer = None
    if frames is not None:
        renderer = mujoco.Renderer(m, 360, 480)
        cam = mujoco.MjvCamera(); cam.azimuth = 120; cam.elevation = -12; cam.distance = 2.6; cam.lookat[:] = [0, 0, 0.6]
    n = int((SETTLE + T + HOLD) / 0.001)
    for k in range(n):
        t = k * 0.001
        s = (t - SETTLE) / T
        a = mj(s)
        ctrl.com_z_ref = z0 + (z1 - z0) * a
        PEL_PITCH['now'] = PITCH * mj(s * LEAD)   # hip hinge leads the descent (LEAD >= 1)
        ctrl.q_ref = q0 + (q1 - q0) * a
        v = np.zeros(m.nv)
        v[6:] = (q1 - q0)[7:] * mj_d(s) / T if 0 < s < 1 else 0.0
        ctrl.v_ref = v
        # CoM over the sole centres. The stand ZMP loop has x gain 2.5 s^-2 (controller._zmp_target), too soft
        # for a fast descent, so the reference is leaned against the error (XK) to stiffen it from outside.
        mujoco.mj_subtreeCom(m, d) if hasattr(mujoco, 'mj_subtreeCom') else None
        ex = float(d.subtree_com[1][0]) - FC
        ctrl.x_ref = FC - float(np.clip(XK * ex, -0.06, 0.06))
        tau = ctrl.step(d)
        mujoco.mj_step(m, d)
        if ctrl.last_status != 'ok':
            res['qp_fail'] += 1
        res['tau_ratio_max'] = max(res['tau_ratio_max'], float(np.max(np.abs(d.ctrl[leg]) / (DERATE * nominal[leg]))))
        up = d.xmat[ctrl.pelvis][8]
        if up < np.cos(min(PEL_PITCH['now'] + 0.6, 1.5)) or d.qpos[2] < 0.3:   # fall: >0.6 rad past the pitch ref
            res['fell'] = round(t, 3); break
        # support polygon: both feet flat, rectangle hull; margin from measured CoP of the total wrench
        num = np.zeros(3); fzt = 0.0
        for g in soles:
            c_, f_ = measured_cop(m, d, g)
            if c_ is not None:
                num += f_ * c_; fzt += f_
        cop = num / fzt if fzt > 1.0 else None
        if cop is not None:
            xs = []
            for g in soles:
                c = d.geom_xpos[g]; h = m.geom_size[g]
                xs.append((c[0] - h[0], c[0] + h[0], c[1] - h[1], c[1] + h[1]))
            x0, x1 = min(b[0] for b in xs), max(b[1] for b in xs)
            y0, y1 = min(b[2] for b in xs), max(b[3] for b in xs)
            mg = min(cop[0] - x0, x1 - cop[0], cop[1] - y0, y1 - cop[1]) * 1e3
            if mg < res['cop_margin_min_mm']:
                res['cop_margin_min_mm'] = float(mg); res['cop_min_t'] = round(t, 3)
            if t > SETTLE:
                res['_n'] = res.get('_n', 0) + 1
                res['_edge'] = res.get('_edge', 0) + (mg < 5.0)
                res['cop_margin_min_after_settle_mm'] = round(min(res.get('cop_margin_min_after_settle_mm', 1e9), float(mg)), 1)
        if renderer is not None and k % int(1000 / fps) == 0:
            renderer.update_scene(d, cam); frames.append(renderer.render().copy())
    mujoco.mj_subtreeVel(m, d)
    res['cop_lt5mm_frac'] = round(res.pop('_edge', 0) / max(res.pop('_n', 1), 1), 3)
    res['com_z_final'] = round(float(d.subtree_com[1][2]), 3)
    res['pelvis_z_final'] = round(float(d.qpos[2]), 3)
    res['tau_ratio_max'] = round(res['tau_ratio_max'], 3)
    res['cop_margin_min_mm'] = round(res['cop_margin_min_mm'], 1)
    res['ok'] = (res['fell'] is None and res['qp_fail'] == 0 and res['cop_margin_min_mm'] >= 0
                 and res['tau_ratio_max'] <= 1.0 + 1e-6 and abs(res['com_z_final'] - z1) < 0.03)
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--gif', action='store_true'); ap.add_argument('--pel', type=float, default=0.85)
    a = ap.parse_args()
    out = [run(T, a.pel) for T in (1.0, 1.5, 2.0, 2.5)]
    for r in out: print(json.dumps(r, default=float))
    ok = [r['T'] for r in out if r['ok']]
    clean = [r['T'] for r in out if r['ok'] and r['tau_ratio_max'] < 0.999]
    print('FASTEST_STABLE', min(ok) if ok else None, 'FASTEST_UNSATURATED', min(clean) if clean else None)
    if a.gif:
        import imageio.v2 as imageio
        T = min(clean) if clean else 2.5
        frames = []
        run(T, a.pel, frames=frames)
        gif = os.path.join(ROOT, 'media', 'progress', '2026-10-21_controls_r142_safe_sit_wbc.gif')
        imageio.mimsave(gif, frames, duration=0.04, loop=0)
        print('GIF', gif, len(frames))


# ----------------------------------------------------------------------------------------------------------------
# R-145 (5f5bd1d): crouch (WBC, 2.0 s) then a controlled kneel to knee-pad contact, MO=0 only once supported.
# The repo has no fall-mode controller or config, so the kneel is a joint-space PD (gains.npz kp/kd, eval_box
# style) along a minimum-jerk path to KNEEL_POSE, with leg torque clipped to the 0.5 derate. Pose and gains are
# recorded in controller_config.json "fall_mode_kneel" [EST]. sim/v3 has no knee-contact geom, so a minimal pad
# box is added on the front of each shank at the knee [EST: 50 x 100 x 80 mm, not the PA12 cap CAD].
import tempfile
import gait_lib as _gl
from drive_thermal_derate import DerateConfig, DriveIO, DriveDerateSupervisor, MO_OFF, KNEEL, CONTACT_CONFIRMED

KNEE_PAD = '<geom name="{s}_knee_pad" type="box" pos="0.050 0 -0.060" size="0.025 0.05 0.04" rgba="0.9 0.5 0.1 1"/>'
# Two waypoints [EST]: W1 hinge forward so the CoM passes the toes and the heels lift (knees travel forward/down),
# W2 upright kneel on pads + toes. Fraction of T_kneel spent reaching W1: KNEEL_W1_FRAC.
KNEEL_W1 = {'hip_pitch': -1.45, 'knee': 1.70, 'ankle_pitch': -0.75, 'waist_pitch': 0.8, 'shoulder_pitch': -1.2}
KNEEL_POSE = {'hip_pitch': -0.6, 'knee': 1.9, 'ankle_pitch': 0.3, 'waist_pitch': 0.4}
KNEEL_W1_FRAC = 0.6
LEAN_S = 0.0        # WBC lean phase at the start of KNEEL: CoM forward to LEAN_X, pelvis pitch LEAN_PITCH
LEAN_X = 0.14
LEAN_PITCH = 0.3
KNEEL_GAIN = 1.0      # x gains.npz kp/kd


def _xml_with_pads():
    xml = open(_gl.XML).read()
    for s, S in (('l', 'L'), ('r', 'R')):
        tag = f'<geom name="{s}_shank" type="capsule"'
        assert tag in xml
        xml = xml.replace(tag, KNEE_PAD.format(s=s) + tag, 1)
    f = tempfile.NamedTemporaryFile('w', suffix='.xml', delete=False, dir=os.path.dirname(_gl.XML))
    f.write(xml); f.close()
    return f.name


class _SimIO(DriveIO):
    def __init__(s, names, t0): s.temp = {n: t0 for n in names}; s.mo = {n: True for n in names}; s.lim = {}
    def read_temp(s, n): return float(int(s.temp[n]))
    def write_limit(s, n, pm): s.lim[n] = pm
    def set_mo(s, n, on): s.mo[n] = on


def _hull_contains(pts, p):
    pts = np.unique(np.round(np.asarray(pts), 4), axis=0)
    if len(pts) < 3:
        return False, -1.0
    from scipy.spatial import ConvexHull
    try:
        h = ConvexHull(pts)
    except Exception:
        return False, -1.0
    # equations: n.x + c <= 0 inside
    dist = -(h.equations[:, :2] @ p + h.equations[:, 2])
    return bool(np.all(dist >= 0)), float(dist.min())


def run_kneel(T_crouch=2.0, T_kneel=0.8, pel_z=0.85, frames=None, fps=25, hold_after=1.0):
    orig_xml = _gl.XML
    path = _xml_with_pads()
    try:
        _gl.XML = path
        os.environ['LEGS_CHAIR'] = ''
        m = load()
    finally:
        _gl.XML = orig_xml
        os.unlink(path)
    m.opt.timestep = 0.001
    d = mujoco.MjData(m)
    ctrl = WalkController(m); ctrl.stand_only = True
    ctrl.initialize(d)
    names = list(ctrl.act_name)
    leg = np.array([any(n.endswith(j) for j in LEG) for n in names])
    nominal = ctrl.tau_max.copy()
    der = np.where(leg, DERATE * nominal, nominal)
    ctrl.tau_max = der.copy()
    PEL_PITCH['now'] = 0.0
    q0 = d.qpos.copy(); z0 = ctrl.com_z_ref
    q1, z1 = sit_pose(ctrl, d, pel_z)
    g = np.load(os.path.join(LEGS, 'rl', 'gains.npz'))
    gn = [str(x) for x in g['joint_names'].tolist()]
    kp = np.array([g['kp'][gn.index(n)] for n in names]) * KNEEL_GAIN
    kd = np.array([g['kd'][gn.index(n)] for n in names]) * KNEEL_GAIN
    qadr = np.array([m.jnt_qposadr[m.actuator_trnid[i, 0]] for i in range(m.nu)])
    vadr = np.array([m.jnt_dofadr[m.actuator_trnid[i, 0]] for i in range(m.nu)])
    qk = q1[qadr].copy(); qw = q1[qadr].copy()
    for i, n in enumerate(names):
        for k, v in KNEEL_POSE.items():
            if n.endswith(k): qk[i] = v
        for k, v in KNEEL_W1.items():
            if n.endswith(k): qw[i] = v
    pads = [m.geom('l_knee_pad').id, m.geom('r_knee_pad').id]
    shanks = [m.geom('l_shank').id, m.geom('r_shank').id]
    feet = [m.geom('l_foot').id, m.geom('r_foot').id]
    floor = [i for i in range(m.ngeom) if m.geom_type[i] == mujoco.mjtGeom.mjGEOM_PLANE]
    io = _SimIO(names, 83.0)
    ev = {}
    sup = DriveDerateSupervisor(names, io, DerateConfig(), request_safe_sit=lambda r: ev.setdefault('latch', d.time),
                                request_kneel=lambda: ev.setdefault('kneel', d.time))
    res = dict(T_crouch=T_crouch, T_kneel=T_kneel, fell=None, peak_pad_force_N=0.0, peak_shank_force_N=0.0,
               tau_frac_crouch=0.0, tau_frac_kneel=0.0, first_contact=None, t_supported=None, t_mo_off=None)
    renderer = None
    if frames is not None:
        renderer = mujoco.Renderer(m, 360, 480)
        cam = mujoco.MjvCamera(); cam.azimuth = 100; cam.elevation = -10; cam.distance = 2.6; cam.lookat[:] = [0.2, 0, 0.5]
    mode = 'settle'; qc = None; t_k0 = None
    f6 = np.zeros(6)
    n_steps = int((SETTLE + T_crouch + T_kneel + 1.5 + hold_after) / 0.001)
    for k in range(n_steps):
        t = k * 0.001
        if t >= SETTLE:
            sup.step(0.001)            # temperatures read 83 -> latches CROUCH at t = SETTLE
        st = sup.state
        if st == KNEEL and 'kneel' in ev and t - ev['kneel'] < LEAN_S and qc is None:
            s_ = (t - ev['kneel']) / LEAN_S
            ctrl.x_ref = FC + (LEAN_X - FC) * mj(s_)
            PEL_PITCH['now'] = LEAN_PITCH * mj(s_)
            ctrl.com_z_ref = z1; ctrl.q_ref = q1; ctrl.v_ref = np.zeros(m.nv)
            ctrl.step(d)
            t_lean_end = t
        elif st in ('CROUCH',) or mode == 'settle':
            mode = 'settle' if t < SETTLE else 'crouch'
            s = (t - SETTLE) / T_crouch
            a = mj(s)
            ctrl.com_z_ref = z0 + (z1 - z0) * a
            ctrl.q_ref = q0 + (q1 - q0) * a
            v = np.zeros(m.nv); v[6:] = (q1 - q0)[7:] * mj_d(s) / T_crouch if 0 < s < 1 else 0.0
            ctrl.v_ref = v; ctrl.x_ref = FC
            ctrl.step(d)
            if mode == 'crouch':
                res['tau_frac_crouch'] = max(res['tau_frac_crouch'], float(np.max(np.abs(d.ctrl[leg]) / der[leg])))
        else:
            if qc is None:
                qc = d.qpos[qadr].copy(); t_k0 = t
                res['lean_s'] = LEAN_S
            T1 = KNEEL_W1_FRAC * T_kneel; T2 = T_kneel - T1
            if t - t_k0 < T1:
                s = (t - t_k0) / T1; qa_, qb_, TT = qc, qw, T1
            else:
                s = (t - t_k0 - T1) / T2; qa_, qb_, TT = qw, qk, T2
            qt = qa_ + (qb_ - qa_) * mj(s)
            vt = (qb_ - qa_) * mj_d(s) / TT if s < 1 else 0 * qk
            tau = kp * (qt - d.qpos[qadr]) + kd * (vt - d.qvel[vadr])
            tau = np.clip(tau, -der, der)
            on = np.array([io.mo[n] for n in names], float)
            d.ctrl[:] = tau * on
            if on.all():
                res['tau_frac_kneel'] = max(res['tau_frac_kneel'], float(np.max(np.abs(tau[leg]) / der[leg])))
        mujoco.mj_step(m, d)
        # contacts
        knee_c, pts, padF, shF = False, [], 0.0, 0.0
        for i in range(d.ncon):
            c = d.contact[i]
            gg = {c.geom1, c.geom2}
            if not (gg & set(floor)):
                continue
            mujoco.mj_contactForce(m, d, i, f6)
            if gg & set(pads):
                knee_c = True; pts.append(c.pos[:2].copy()); padF += f6[0]
            elif gg & set(shanks):
                knee_c = True; pts.append(c.pos[:2].copy()); shF += f6[0]
            elif gg & set(feet):
                pts.append(c.pos[:2].copy())
            elif t > SETTLE:
                res['fell'] = res['fell'] or f'{t:.3f} {m.geom(list(gg - set(floor))[0]).name} on floor'
        res['peak_pad_force_N'] = max(res['peak_pad_force_N'], padF)
        res['peak_shank_force_N'] = max(res['peak_shank_force_N'], shF)
        if knee_c and res['first_contact'] is None:
            res['first_contact'] = round(t - SETTLE, 3)
        mujoco.mj_subtreeVel(m, d)
        com = d.subtree_com[1]; vcom = float(np.linalg.norm(d.subtree_linvel[1]))
        inside, margin = _hull_contains(pts, com[:2]) if knee_c else (False, -1.0)
        if sup.state in (KNEEL, CONTACT_CONFIRMED):
            sup.set_support(knee_c, inside, vcom)
        if sup.state == CONTACT_CONFIRMED and res['t_supported'] is None:
            res['t_supported'] = round(t - SETTLE, 3); res['support_margin_mm'] = round(margin * 1e3, 1)
        if sup.state != CONTACT_CONFIRMED and sup.state != MO_OFF:
            res['t_supported'] = None
        if sup.state == MO_OFF and res['t_mo_off'] is None:
            res['t_mo_off'] = round(t - SETTLE, 3)
        if renderer is not None and k % int(1000 / fps) == 0:
            renderer.update_scene(d, cam); frames.append(renderer.render().copy())
        if res['t_mo_off'] is not None and t - SETTLE > res['t_mo_off'] + hold_after:
            break
    mujoco.mj_subtreeVel(m, d)
    res['state'] = sup.state
    res['log'] = sup.log
    res['com_z_end'] = round(float(d.subtree_com[1][2]), 3)
    res['pelvis_up_end'] = round(float(d.xmat[ctrl.pelvis][8]), 3)
    for kk in ('peak_pad_force_N', 'peak_shank_force_N', 'tau_frac_crouch', 'tau_frac_kneel'):
        res[kk] = round(res[kk], 3 if 'frac' in kk else 1)
    res['ok'] = (res['fell'] is None and res['t_mo_off'] is not None and res['t_mo_off'] <= 2.8 + 0.05 + 1e-9
                 and res['tau_frac_kneel'] <= 1.0 + 1e-6)
    return res
