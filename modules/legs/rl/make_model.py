"""Build the MJX training model and the 1 s reference cycles.

Reads sim/v3/humanoid_v3.xml and writes modules/legs/rl/humanoid_mjx.xml.
Does not modify sim/v3. Mass is scaled the same way as gait_lib LEGS_MASS=65
(uniform, payload excluded). Leg ctrlranges are CONTRACTS R1.2 (LIM_R1).
"""
import os
import numpy as np
import mujoco

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
XML_V3 = os.path.join(ROOT, 'sim', 'v3', 'humanoid_v3.xml')
REF_DIR = os.path.join(ROOT, 'modules', 'legs', 'results', 'r7', 'ref_ds25')
OUT_XML = os.path.join(HERE, 'humanoid_mjx.xml')
OUT_ROUGH = os.path.join(HERE, 'humanoid_mjx_rough.xml')
OUT_REF = os.path.join(HERE, 'ref_cycle.npz')
OUT_GAINS = os.path.join(HERE, 'gains.npz')

MASS_TARGET = 67.1  # Arbiter R-118: sim nominal (robustness setting; T2 limit 66.5 stands)
LIM_R1 = {
    'hip_yaw': 70.0, 'hip_roll': 204.0, 'hip_pitch': 350.0,
    'knee': 258.0, 'ankle_pitch': 311.0, 'ankle_roll': 177.0,
}
W_LIM = {
    'hip_yaw': 6.13, 'hip_roll': 3.64, 'hip_pitch': 12.16,
    'knee': 16.03, 'ankle_pitch': 13.7, 'ankle_roll': 13.7,
}
# Carry pose from scenarios.sc_walk (carry_20kg_r2): waist -0.25, arms in front of the chest.
CARRY_OFFSET = {
    'waist_pitch': -0.25,
    'l_shoulder_pitch': -0.60, 'r_shoulder_pitch': -0.60,
    'l_elbow': -1.20, 'r_elbow': -1.20,
}
# Flat-foot crouch with the COM over the ankle. PD at tau/0.25 holds this for 5 s.
HOME_JOINT = {
    'hip_pitch': -0.20,
    'knee': 0.35,
    'ankle_pitch': -0.15,
    'elbow': -0.30,
}


def _xml_text():
    xml = open(XML_V3, encoding='utf-8').read()
    xml = xml.replace(
        '<option timestep="0.002" integrator="implicitfast"/>',
        '<option timestep="0.002" integrator="implicitfast" iterations="4" ls_iterations="8"/>',
    )
    xml = xml.replace(
        '<geom name="l_foot" type="box" pos="0.060 0 -0.074" size="0.120 0.05 0.012" friction="1.0"/>',
        '<site name="l_sole" pos="0.060 0 -0.086" size="0.20"/>'
        '<geom name="l_foot" type="box" pos="0.060 0 -0.074" size="0.120 0.05 0.012" condim="3" friction="1.0 0.005 0.0001"/>',
    )
    xml = xml.replace(
        '<geom name="r_foot" type="box" pos="0.060 0 -0.074" size="0.120 0.05 0.012" friction="1.0"/>',
        '<site name="r_sole" pos="0.060 0 -0.086" size="0.20"/>'
        '<geom name="r_foot" type="box" pos="0.060 0 -0.074" size="0.120 0.05 0.012" condim="3" friction="1.0 0.005 0.0001"/>',
    )
    xml = xml.replace(
        '<geom name="torso" type="box" pos="0 0 0.180" size="0.11 0.17 0.130"/>',
        '<body name="payload" pos="0.25 0 0.10">'
        '<inertial pos="0 0 0" mass="0.001" diaginertia="0.00001 0.0000075 0.00001"/>'
        '</body>'
        '<geom name="torso" type="box" pos="0 0 0.180" size="0.11 0.17 0.130"/>',
    )
    sensors = """
  <sensor>
    <gyro site="imu" name="gyro"/>
    <velocimeter site="imu" name="local_linvel"/>
    <accelerometer site="imu" name="accelerometer"/>
    <framezaxis objtype="site" objname="imu" name="upvector"/>
    <touch site="l_sole" name="l_foot_touch"/>
    <touch site="r_sole" name="r_foot_touch"/>
    <subtreecom body="pelvis" name="pelvis_com"/>
    <subtreelinvel body="pelvis" name="pelvis_linvel"/>
  </sensor>
  <keyframe>
    <key name="home" qpos="0 0 1.02 1 0 0 0 0 0 -0.3 0.6 -0.3 0 0 0 -0.3 0.6 -0.3 0 0 0 0 0 0 0 -0.3 0 0 0 0 0 0 0 -0.3 0 0 0"/>
  </keyframe>
"""
    xml = xml.replace('</mujoco>', sensors + '</mujoco>')
    return xml


def _cycle(path):
    d = np.load(path)
    t = d['t']
    fz = d['FZ']
    lift = np.where((fz[:-1, 0] >= 20.0) & (fz[1:, 0] < 20.0))[0]
    # Steady cruise: left-foot lift nearest 4.2 s, then exactly one 1.0 s cycle.
    k = int(np.argmin(np.abs(t[lift] - 4.2)))
    i0 = int(lift[k])
    i1 = i0 + int(round(1.0 / np.median(np.diff(t))))
    if i1 > len(t):
        i0 = int(lift[k - 1])
        i1 = i0 + int(round(1.0 / np.median(np.diff(t))))
    sl = slice(i0, i1)
    return dict(
        t=t[sl] - t[i0],
        Q=d['Q'][sl],
        V=d['V'][sl],
        FZ=fz[sl],
        AL=d['AL'][sl],
    )


def _gains(m):
    nu = m.nu
    kp = np.zeros(nu)
    kd = np.zeros(nu)
    tau = np.zeros(nu)
    wlim = np.zeros(nu)
    names = []
    for i in range(nu):
        name = m.actuator(i).name
        names.append(name)
        jid = int(m.actuator_trnid[i, 0])
        dof = int(m.jnt_dofadr[jid])
        lim = float(m.actuator_ctrlrange[i, 1])
        tau[i] = lim
        # A static error of 0.25 rad commands stall torque. Below this the
        # zero-moment crouch sags through the knee and falls (checked at tau/0.35).
        kp_i = float(np.clip(lim / 0.25, 80.0, 2800.0))
        arm = float(max(m.dof_armature[dof], 0.05))
        kp[i] = kp_i
        kd[i] = 2.0 * np.sqrt(kp_i * arm) + 0.015 * kp_i
        for jn, w in W_LIM.items():
            if name.endswith(jn) and name[:2] in ('l_', 'r_'):
                wlim[i] = w
    # Matched to Kp: full action is one stall-torque of steady deflection, capped at 0.25 rad.
    action_scale = np.minimum(0.25, tau / np.maximum(kp, 1.0))
    return names, kp, kd, tau, wlim, action_scale


def _apply_limits_and_mass(m):
    for i in range(m.nu):
        name = m.actuator(i).name
        for jn, v in LIM_R1.items():
            if name.endswith(jn) and name[:2] in ('l_', 'r_'):
                m.actuator_ctrlrange[i] = [-v, v]
    payload = m.body('payload').id
    base = sum(float(m.body_mass[i]) for i in range(m.nbody) if i != payload)
    k = MASS_TARGET / base
    for i in range(m.nbody):
        if i == payload:
            continue
        m.body_mass[i] *= k
        m.body_inertia[i] *= k
    mujoco.mj_setConst(m, mujoco.MjData(m))
    return k, payload


def _home_from_cycle(Q, FZ):
    both = np.where((FZ[:, 0] > 80.0) & (FZ[:, 1] > 80.0))[0]
    k = int(both[len(both) // 2]) if len(both) else 0
    q = Q[k].copy()
    q[0] = 0.0
    q[1] = 0.0
    q[3:7] = [1.0, 0.0, 0.0, 0.0]
    return q


def _settle_stand(m, kp, kd):
    """Drop the flat-foot crouch onto the ground and PD-hold it.

    The keyframe stores the settled qpos. The PD target stays the kinematic
    crouch: retargeting to the sagged pose would command zero torque and sag again.
    """
    d = mujoco.MjData(m)
    names = [m.actuator(i).name for i in range(m.nu)]
    target = np.zeros(m.nu)
    for i, name in enumerate(names):
        for jn, val in HOME_JOINT.items():
            if name.endswith(jn):
                target[i] = val
    q = np.zeros(m.nq)
    q[3] = 1.0
    q[7:] = target
    q[2] = 1.05
    d.qpos[:] = q
    mujoco.mj_forward(m, d)
    soles = []
    for gname in ('l_foot', 'r_foot'):
        gid = m.geom(gname).id
        soles.append(float(d.geom_xpos[gid, 2] - m.geom_size[gid, 2]))
    d.qpos[2] -= min(soles) - 0.0005
    lo = m.actuator_ctrlrange[:, 0]
    hi = m.actuator_ctrlrange[:, 1]
    up_i = int(m.sensor_adr[m.sensor('upvector').id] + 2)
    for _ in range(2500):
        tau = kp * (target - d.qpos[7:]) - kd * d.qvel[6:]
        d.ctrl[:] = np.clip(tau, lo, hi)
        mujoco.mj_step(m, d)
    up = float(d.sensordata[up_i])
    print('stand settle z', round(float(d.qpos[2]), 4), 'up', round(up, 3),
          'ncon', d.ncon, 'vx', round(float(d.qvel[0]), 3))
    if up < 0.95 or d.qpos[2] < 0.9:
        raise SystemExit(f'stand did not hold: z={d.qpos[2]:.3f} up={up:.3f}')
    q = d.qpos.copy()
    q[0] = 0.0
    q[1] = 0.0
    q[3:7] = [1.0, 0.0, 0.0, 0.0]
    return q, target


def _write_rough(flat_xml_text_unused, m_flat_path):
    """Mild ±1 cm height field over the flat model. Training-only."""
    import re
    xml = open(m_flat_path, encoding='utf-8').read()
    # hfield elevation is 2 cm; data centered at 0.5 gives ±1 cm about a 1 cm mean.
    # Shift the field down by 1 cm so the mean ground stays at z=0.
    asset = '<hfield name="terrain" nrow="65" ncol="65" size="6 6 0.02 0.05"/>'
    if '<asset>' in xml and 'hfield name="terrain"' not in xml:
        xml = xml.replace('<asset>', '<asset>' + asset, 1)
    xml2, nsub = re.subn(
        r'<geom name="floor"[^/]*/>',
        '<geom name="floor" type="hfield" hfield="terrain" pos="0 0 -0.01" material="grid"/>',
        xml,
        count=1,
    )
    if nsub != 1:
        raise RuntimeError('floor geom not rewritten')
    xml = xml2
    rough_tmp = OUT_ROUGH + '.tmp.xml'
    open(rough_tmp, 'w', encoding='utf-8').write(xml)
    m = mujoco.MjModel.from_xml_path(rough_tmp)
    # Smooth low-frequency bumps, amplitude ±1 cm after the pos shift (data in [0, 1]).
    nrow = int(np.asarray(m.hfield_nrow).reshape(-1)[0])
    ncol = int(np.asarray(m.hfield_ncol).reshape(-1)[0])
    yy = np.linspace(0, 2 * np.pi, nrow)
    xx = np.linspace(0, 2 * np.pi, ncol)
    X, Y = np.meshgrid(xx, yy)
    h = 0.5 + 0.35 * np.sin(1.5 * X) * np.cos(1.2 * Y) + 0.15 * np.sin(3.0 * X + Y)
    h = np.clip(h, 0.0, 1.0).astype(np.float32)
    m.hfield_data[:] = h.ravel()
    mujoco.mj_saveLastXML(OUT_ROUGH, m)
    os.remove(rough_tmp)
    elev = float(np.asarray(m.hfield_size).reshape(-1, 4)[0, 2])
    print('rough', OUT_ROUGH, 'hfield', nrow, ncol, 'elev_m', elev)


def main():
    xml = _xml_text()
    m = mujoco.MjModel.from_xml_string(xml)
    k, payload = _apply_limits_and_mass(m)
    print('mass_scale', round(k, 6), 'nbody', m.nbody, 'nu', m.nu, 'nq', m.nq, 'nv', m.nv)
    print('total_mass_incl_payload', round(float(np.sum(m.body_mass)), 4))
    print('robot_mass', round(float(np.sum(m.body_mass) - m.body_mass[payload]), 4))
    print('opt', m.opt.timestep, int(m.opt.iterations), int(m.opt.ls_iterations), m.opt.integrator)
    for s in ('gyro', 'local_linvel', 'accelerometer', 'upvector', 'l_foot_touch', 'r_foot_touch', 'pelvis_linvel'):
        sid = m.sensor(s).id
        print(f'sensor {s} dim {int(m.sensor_dim[sid])} adr {int(m.sensor_adr[sid])}')

    cycles = []
    for speed, name in ((0.8, 'walk_0p8_r7'), (1.0, 'walk_1p0_r7'), (1.2, 'walk_1p2_r7')):
        c = _cycle(os.path.join(REF_DIR, name + '.npz'))
        dx = float(c['Q'][-1, 0] - c['Q'][0, 0])
        dur = float(c['t'][-1] - c['t'][0] + np.median(np.diff(c['t'])))
        fz = c['FZ']
        ds = float(np.mean((fz[:, 0] > 40) & (fz[:, 1] > 40)))
        flight = float(np.mean((fz[:, 0] < 20) & (fz[:, 1] < 20)))
        print(name, 'frames', len(c['t']), 'dx', round(dx, 3), 'dur', round(dur, 3),
              'speed', round(dx / dur, 3), 'ds', round(ds, 3), 'flight', round(flight, 3))
        cycles.append(c)

    names, kp, kd, tau, wlim, action_scale = _gains(m)
    stand_q, stand_target = _settle_stand(m, kp, kd)
    if stand_q.shape[0] != m.nq:
        raise SystemExit(f'stand qpos {stand_q.shape} != nq {m.nq}')
    m.key_qpos[0] = stand_q
    m.key_qvel[0] = 0
    mujoco.mj_saveLastXML(OUT_XML, m)
    # mj_saveLastXML omits the default timestep. Put it back so the file is explicit.
    saved = open(OUT_XML, encoding='utf-8').read()
    saved = saved.replace(
        '<option integrator="implicitfast" iterations="4" ls_iterations="8"/>',
        '<option timestep="0.002" integrator="implicitfast" iterations="4" ls_iterations="8"/>',
    )
    open(OUT_XML, 'w', encoding='utf-8').write(saved)
    m2 = mujoco.MjModel.from_xml_path(OUT_XML)
    print('saved', OUT_XML, 'bytes', os.path.getsize(OUT_XML),
          'mass', round(float(np.sum(m2.body_mass)), 3),
          'dt', m2.opt.timestep,
          'home_z', round(float(m2.key_qpos[0, 2]), 4))
    names, kp, kd, tau, wlim, action_scale = _gains(m2)
    stand_q = m2.key_qpos[0].copy()
    carry_offset = np.zeros(m2.nu)
    for i, name in enumerate(names):
        if name in CARRY_OFFSET:
            carry_offset[i] = CARRY_OFFSET[name]
    np.savez(
        OUT_GAINS,
        joint_names=np.array(names),
        kp=kp, kd=kd, tau_lim=tau, w_lim=wlim, action_scale=action_scale,
        carry_offset=carry_offset,
        home_qpos=m2.key_qpos[0].copy(),
        home_q=stand_target.astype(np.float64),
    )
    # Joint vectors: actuators follow the hinge order after the free joint.
    q = np.stack([c['Q'][:, 7:] for c in cycles], axis=0)
    v = np.stack([c['V'][:, 6:] for c in cycles], axis=0)
    fz = np.stack([c['FZ'] for c in cycles], axis=0)
    contact = (fz > 20.0).astype(np.float32)
    np.savez(
        OUT_REF,
        speeds=np.array([0.8, 1.0, 1.2]),
        q=q.astype(np.float32),
        qd=v.astype(np.float32),
        fz=fz.astype(np.float32),
        contact=contact,
        pelvis_z=np.stack([c['Q'][:, 2] for c in cycles]).astype(np.float32),
        period=np.array(1.0),
    )
    print('ref', q.shape, 'gains kp', np.round(kp, 1).tolist())
    print('action_scale', np.round(action_scale, 3).tolist())
    try:
        _write_rough(None, OUT_XML)
    except Exception as exc:
        print('ROUGH_FAILED', type(exc).__name__, exc)


if __name__ == '__main__':
    main()
