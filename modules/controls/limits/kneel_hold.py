"""Actuators D94 (7d22c91): with MO=0 nothing holds (no brakes, roller screws backdrive, friction hold ~7-9 N·m).
The R-145 MO=0 end pose must need ~zero joint torque. This places candidate end poses on the floor (sim/v3 4115f6e,
68 kg, knee pads [EST] as in safe_sit_wbc.py), settles each under a PD hold at the 0.5 leg derate, and records the
static holding torque per joint (mean over the last 0.3 s). It then sets MO=0, with every joint's frictionloss at
its D94 hold (7 N·m; ankle 8), and checks whether the pose stays put for 1.5 s (CoM drop, max joint drift).
CPU only. Usage: python kneel_hold.py
"""
import os, sys, json
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np
import mujoco
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import safe_sit_wbc as S
from drive_thermal_derate import friction_hold, static_hold_ok
import gait_lib as GL
from gait_lib import LEG

# Candidate end poses (rad) [EST]. pitch = pelvis pitch (+ forward); z = pelvis drop height.
POSES = {
    'A_kneel_upright (knees+toes)': dict(pitch=0.0, z=0.62, q={'hip_pitch': 0.0, 'knee': 1.57, 'ankle_pitch': 0.70}),
    'B_kneel_sit_back (knee 135 deg stop)': dict(pitch=0.25, z=0.45, q={'hip_pitch': -0.9, 'knee': 2.36, 'ankle_pitch': 0.70, 'waist_pitch': 0.3}),
    'C_hands_knees': dict(pitch=1.45, z=0.62, q={'hip_pitch': -1.45, 'knee': 1.57, 'ankle_pitch': 0.70, 'shoulder_pitch': -1.45}),
    'D_forearms_knees': dict(pitch=1.2, z=0.55, q={'hip_pitch': -1.4, 'knee': 1.8, 'ankle_pitch': 0.70, 'shoulder_pitch': -0.6, 'elbow': 1.6, 'waist_pitch': 0.3}),
    'E_childs_pose (torso on thighs, arms forward)': dict(pitch=1.0, z=0.40, q={'hip_pitch': -1.80, 'knee': 2.36, 'ankle_pitch': 0.70, 'waist_pitch': 0.8, 'shoulder_pitch': -2.6}),
    'F_prone (lying face down)': dict(pitch=1.57, z=0.20, q={}),
}


def model():
    orig = GL.XML; p = S._xml_with_pads()
    try:
        GL.XML = p; os.environ['LEGS_CHAIR'] = ''
        m = S.load()
    finally:
        GL.XML = orig; os.unlink(p)
    m.opt.timestep = 0.001
    return m


def settle(name, spec, settle_s=3.0, off_s=1.5):
    m = model(); d = mujoco.MjData(m)
    names = [m.actuator(i).name for i in range(m.nu)]
    qadr = np.array([m.jnt_qposadr[m.actuator_trnid[i, 0]] for i in range(m.nu)])
    vadr = np.array([m.jnt_dofadr[m.actuator_trnid[i, 0]] for i in range(m.nu)])
    jid = m.actuator_trnid[:, 0]
    g = np.load(os.path.join(S.LEGS, 'rl', 'gains.npz')); gn = [str(x) for x in g['joint_names'].tolist()]
    kp = np.array([g['kp'][gn.index(n)] for n in names]); kd = np.array([g['kd'][gn.index(n)] for n in names])
    leg = np.array([any(n.endswith(j) for j in LEG) for n in names])
    lim = m.actuator_ctrlrange[:, 1] * np.where(leg, S.DERATE, 1.0)
    qt = np.zeros(m.nu)
    for i, n in enumerate(names):
        for k, v in spec['q'].items():
            if n.endswith(k): qt[i] = v
    qt = np.clip(qt, m.jnt_range[jid, 0], m.jnt_range[jid, 1])
    d.qpos[:] = 0; d.qpos[2] = spec['z']; th = spec['pitch']
    d.qpos[3:7] = [np.cos(th / 2), 0, np.sin(th / 2), 0]
    d.qpos[qadr] = qt
    mujoco.mj_forward(m, d)
    taus = []
    n1 = int(settle_s / 0.001)
    for k in range(n1):
        tau = np.clip(kp * (qt - d.qpos[qadr]) - kd * d.qvel[vadr], -lim, lim)
        d.ctrl[:] = tau
        mujoco.mj_step(m, d)
        if k >= n1 - 300:
            taus.append(tau.copy())
    tau_hold = np.mean(taus, 0)
    mujoco.mj_subtreeVel(m, d)
    com0 = d.subtree_com[1].copy(); v0 = float(np.linalg.norm(d.subtree_linvel[1])); q0 = d.qpos[qadr].copy()
    floor = [i for i in range(m.ngeom) if m.geom_type[i] == mujoco.mjtGeom.mjGEOM_PLANE]
    touch = sorted({m.geom(c.geom1 if c.geom2 in floor else c.geom2).name for c in d.contact[:d.ncon]
                    if c.geom1 in floor or c.geom2 in floor})
    for i, n in enumerate(names):
        m.dof_frictionloss[vadr[i]] = friction_hold(n)
    d.ctrl[:] = 0
    for k in range(int(off_s / 0.001)):
        mujoco.mj_step(m, d)
    mujoco.mj_subtreeVel(m, d)
    drift = np.abs(d.qpos[qadr] - q0)
    # static load carried by joint friction after MO=0 (efc friction rows, per dof): the torque the pose needs
    fr = np.zeros(m.nv)
    for r in range(d.nefc):
        if d.efc_type[r] == mujoco.mjtConstraint.mjCNSTR_FRICTION_DOF:
            fr[d.efc_id[r]] += d.efc_force[r]
    mo0_load = {n: round(float(fr[vadr[i]]), 1) for i, n in enumerate(names)}
    mo0_sat = [n for n in names if abs(mo0_load[n]) >= 0.95 * friction_hold(n)]
    per = {n: round(float(t), 1) for n, t in zip(names, tau_hold)}
    over = {n: (round(float(t), 1), friction_hold(n)) for n, t in zip(names, tau_hold) if abs(t) >= friction_hold(n)}
    return dict(pose=name, contacts=touch, com_z=round(float(com0[2]), 3), com_speed_settled=round(v0, 3),
                max_abs_hold_Nm=round(float(np.max(np.abs(tau_hold))), 1),
                static_hold_ok=static_hold_ok(per), joints_over_friction=over,
                mo0_com_drop_mm=round(float(com0[2] - d.subtree_com[1][2]) * 1e3, 1),
                mo0_max_joint_drift_deg=round(float(np.degrees(drift.max())), 1),
                mo0_worst_drift_joint=names[int(np.argmax(drift))], mo0_end_speed=round(float(np.linalg.norm(d.subtree_linvel[1])), 3),
                mo0_joints_at_friction_limit=mo0_sat, mo0_friction_load_Nm=mo0_load, hold_torque_Nm=per)


if __name__ == '__main__':
    out = [settle(k, v) for k, v in POSES.items()]
    json.dump(out, open(os.path.join(HERE, 'kneel_hold_results.json'), 'w'), indent=1)
    for r in out:
        print(json.dumps({k: v for k, v in r.items() if k not in ('hold_torque_Nm', 'mo0_friction_load_Nm')}))
