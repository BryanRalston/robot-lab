"""Sim data for T&R's R-146 prone check (fef9348). sim/v3 4115f6e, knee pads [EST] (safe_sit_wbc._xml_with_pads),
CPU MuJoCo at 1 kHz. Writes prone_data_results.json, summarised in PRONE_DATA_TR.md.

1. kneel_cog: CoM height in an upright kneel (knee pads + toes on the floor). Kinematic placement [EST].
2. controlled_lower: start hands+knees (PD-held quadruped, settled), interpolate the joints to prone. The progress
   rate is throttled by ProneLowerGuard so the chest-pad descent speed stays <= its speed_limit(gap). Contact speed,
   peak chest-pad force, then MO=0 (D94 friction) and the static load split by contact group. Run nominally and over
   a small DR sweep (mass 65 / 68.5 kg, floor friction 0.6 / 1.0, chest-pad contact stiffness timeconst 0.005 / 0.02 s).
3. tip_over: upright kneel held by PD, then MO=0 with a 0.15 rad forward lean, arms passive: peak chest-pad force and
   torso acceleration (g; finite difference of the torso COM velocity, 1 kHz, unfiltered and 60 Hz moving-average).
"""
import os, sys, json, itertools
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np
import mujoco
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kneel_hold as KH
from drive_thermal_derate import ProneLowerGuard, friction_hold
from gait_lib import LEG

G0 = 9.80665
POSE_QUAD = {'hip_pitch': -1.45, 'knee': 1.57, 'ankle_pitch': 0.70, 'shoulder_pitch': -1.45}
POSE_KNEES = {'hip_pitch': -1.2, 'knee': 2.1, 'ankle_pitch': 0.70, 'shoulder_pitch': -1.45, 'elbow': 0.0}
POSE_CHEST = {'hip_pitch': -0.6, 'knee': 1.8, 'ankle_pitch': 0.70, 'shoulder_pitch': -1.2, 'elbow': -1.6}
POSE_PRONE = {'hip_pitch': 0.0, 'knee': 0.2, 'ankle_pitch': 0.6, 'shoulder_pitch': -0.5, 'elbow': -1.9, 'waist_pitch': 0.0}
POSE_ARMS_OUT = dict(POSE_PRONE, shoulder_pitch=-2.9, elbow=-0.3, shoulder_roll=0.4)
SLOW_EXP = 0.0   # anticipatory slow-down exponent (0 = off; 1-2 tried, no better)
LOWER_PATH = (POSE_KNEES, POSE_CHEST, POSE_PRONE, POSE_ARMS_OUT)   # last: arms slide forward, chest settles onto the pad   # elbow flexion is negative in sim/v3
POSE_KNEEL = {'hip_pitch': 0.0, 'knee': 1.57, 'ankle_pitch': 0.70}


class Sim:
    def __init__(s, mass=68.0, friction=1.0, pad_tc=0.02):
        m = KH.model()
        base = sum(m.body_mass[i] for i in range(m.nbody)); k = mass / base
        m.body_mass[:] *= k; m.body_inertia[:] *= k
        for i in range(m.ngeom):
            if m.geom_type[i] == mujoco.mjtGeom.mjGEOM_PLANE:
                m.geom_friction[i][0] = friction
        cp = m.geom('chest_pad').id
        m.geom_solref[cp] = [pad_tc, 1.0]
        mujoco.mj_setConst(m, mujoco.MjData(m))
        s.m = m; s.d = mujoco.MjData(m)
        s.names = [m.actuator(i).name for i in range(m.nu)]
        s.qadr = np.array([m.jnt_qposadr[m.actuator_trnid[i, 0]] for i in range(m.nu)])
        s.vadr = np.array([m.jnt_dofadr[m.actuator_trnid[i, 0]] for i in range(m.nu)])
        g = np.load(os.path.join(KH.S.LEGS, 'rl', 'gains.npz')); gn = [str(x) for x in g['joint_names'].tolist()]
        s.kp = np.array([g['kp'][gn.index(n)] for n in s.names]); s.kd = np.array([g['kd'][gn.index(n)] for n in s.names])
        leg = np.array([any(n.endswith(j) for j in LEG) for n in s.names])
        s.lim = m.actuator_ctrlrange[:, 1] * np.where(leg, KH.S.DERATE, 1.0)
        s.floor = {i for i in range(m.ngeom) if m.geom_type[i] == mujoco.mjtGeom.mjGEOM_PLANE}
        s.cp = cp; s.torso = m.body('torso').id
        s.groups = {'chest_pad': {cp},
                    'knee_pads': {m.geom('l_knee_pad').id, m.geom('r_knee_pad').id},
                    'hands_arms': {i for i in range(m.ngeom) if any(w in m.geom(i).name for w in ('hand', 'forearm', 'upper_arm'))},
                    'feet': {m.geom('l_foot').id, m.geom('r_foot').id}}

    def target(s, spec):
        q = np.zeros(s.m.nu)
        for i, n in enumerate(s.names):
            for k, v in spec.items():
                if n.endswith(k): q[i] = v
        jid = s.m.actuator_trnid[:, 0]
        return np.clip(q, s.m.jnt_range[jid, 0], s.m.jnt_range[jid, 1])

    def place(s, spec, pitch, lift=0.002):
        m, d = s.m, s.d
        d.qpos[:] = 0; d.qvel[:] = 0; d.qpos[3:7] = [np.cos(pitch / 2), 0, np.sin(pitch / 2), 0]
        d.qpos[s.qadr] = s.target(spec); d.qpos[2] = 1.0
        mujoco.mj_forward(m, d)
        zmin = 9.0
        for i in range(m.ngeom):
            if i in s.floor or m.geom_bodyid[i] == 0: continue
            # lowest point of the geom AABB in world (boxes/capsules via corners of the local aabb)
            c = m.geom_aabb[i][:3]; h = m.geom_aabb[i][3:]
            R = d.geom_xmat[i].reshape(3, 3)
            for sg in itertools.product((-1, 1), repeat=3):
                zmin = min(zmin, (d.geom_xpos[i] + R @ (c + np.array(sg) * h))[2])
        d.qpos[2] -= zmin - lift
        mujoco.mj_forward(m, d)

    def pd(s, qt, vt=None, gain=1.0):
        d = s.d
        vt = np.zeros(s.m.nu) if vt is None else vt
        return np.clip(gain * s.kp * (qt - d.qpos[s.qadr]) + np.sqrt(gain) * s.kd * (vt - d.qvel[s.vadr]), -s.lim, s.lim)

    def contacts(s):
        m, d = s.m, s.d; f6 = np.zeros(6); out = {k: 0.0 for k in s.groups}; out['other'] = 0.0
        for i in range(d.ncon):
            c = d.contact[i]; gg = {c.geom1, c.geom2}
            if not gg & s.floor: continue
            o = (gg - s.floor).pop(); mujoco.mj_contactForce(m, d, i, f6)
            for k, ids in s.groups.items():
                if o in ids: out[k] += f6[0]; break
            else:
                out['other'] += f6[0]
        return out

    def chest_gap_vz(s):
        m, d = s.m, s.d; i = s.cp
        R = d.geom_xmat[i].reshape(3, 3); h = m.geom_size[i]
        z = min((d.geom_xpos[i] + R @ (np.array(sg) * h))[2] for sg in itertools.product((-1, 1), repeat=3))
        v6 = np.zeros(6); mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_GEOM, i, v6, 0)
        return float(z), float(-v6[5])

    def mo_off_settle(s, T=1.5):
        m, d = s.m, s.d
        for i, n in enumerate(s.names):
            m.dof_frictionloss[s.vadr[i]] = friction_hold(n)
        d.ctrl[:] = 0
        for _ in range(int(T / m.opt.timestep)):
            mujoco.mj_step(m, d)
        return s.contacts()


def kneel_cog():
    s = Sim(); s.place(POSE_KNEEL, 0.0)
    mujoco.mj_forward(s.m, s.d)
    c = s.contacts()
    return dict(kneel_cog_height_m=round(float(s.d.subtree_com[1][2]), 3), basis='kinematic placement on knee pads + toes, trunk upright [EST]',
                pose=POSE_KNEEL)


def controlled_lower(mass=68.0, friction=1.0, pad_tc=0.02, rate=1.0 / 3.0):
    s = Sim(mass, friction, pad_tc); m, d = s.m, s.d
    s.place(POSE_QUAD, 1.45)
    qq = s.target(POSE_QUAD)
    for _ in range(1500):
        d.ctrl[:] = s.pd(qq); mujoco.mj_step(m, d)
    q0 = d.qpos[s.qadr].copy(); way = [q0] + [s.target(w) for w in LOWER_PATH]; nseg = len(way) - 1
    guard = ProneLowerGuard()
    p = 0.0; t = 0.0; contact_t = None; hold = 0
    while t < 6.0:
        gap, vz = s.chest_gap_vz()
        # progress-rate throttle: scale so the measured chest descent speed stays under the guard limit
        lim = guard.speed_limit(max(gap, 0.0))
        sc = 1.0 if vz <= 0.5 * lim else max(0.05, min(1.0, lim / max(vz, 1e-6)))
        sc *= (lim / guard.v_far) ** SLOW_EXP   # anticipatory: slow the path as the chest nears the floor
        p = min(1.0, p + rate * sc * m.opt.timestep)
        x = min(p * nseg, nseg - 1e-9); i = int(x); u = x - i
        a = 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5
        d.ctrl[:] = s.pd(way[i] + (way[i + 1] - way[i]) * a)
        mujoco.mj_step(m, d); t += m.opt.timestep
        f = s.contacts()['chest_pad']
        guard.observe(t, f > 1.0, vz, f)
        if f > 1.0 and contact_t is None:
            contact_t = t
        if p >= 1.0:
            hold += 1
            if hold > 300: break
    loads = s.mo_off_settle()
    tot = sum(loads.values())
    return dict(mass=mass, friction=friction, pad_tc=pad_tc, t_lower_s=round(t, 3), t_chest_contact_s=None if contact_t is None else round(contact_t, 3),
                chest_contact_speed_mps=None if guard.contact_speed is None else round(guard.contact_speed, 3),
                peak_chest_N=round(guard.peak_force, 1), guard_ok=guard.ok,
                prone_static_N={k: round(v, 1) for k, v in loads.items()},
                prone_static_pct={k: round(100 * v / max(tot, 1e-9), 1) for k, v in loads.items()},
                total_N=round(tot, 1), weight_N=round(float(m.body_subtreemass[1] * G0), 1))


def tip_over(lean=0.15, T=1.5):
    s = Sim(); m, d = s.m, s.d
    s.place(POSE_KNEEL, lean)
    qk = s.target(POSE_KNEEL)
    for _ in range(30):
        d.ctrl[:] = s.pd(qk); mujoco.mj_step(m, d)
    for i, n in enumerate(s.names):
        m.dof_frictionloss[s.vadr[i]] = friction_hold(n)
    d.ctrl[:] = 0
    v6 = np.zeros(6); prev = None; acc = []; peakF = 0.0; t_hit = None; first = None
    for k in range(int(T / m.opt.timestep)):
        mujoco.mj_step(m, d)
        mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_BODY, s.torso, v6, 0)
        v = v6[3:].copy()
        if prev is not None:
            acc.append(np.linalg.norm(v - prev) / m.opt.timestep / G0)
        prev = v
        f = s.contacts()
        peakF = max(peakF, f['chest_pad'])
        if f['chest_pad'] > 1 and t_hit is None:
            t_hit = k * m.opt.timestep
        if first is None:
            hit = [g for g, val in f.items() if val > 1 and g != 'knee_pads' and g != 'feet']
            if hit: first = hit[0]
    acc = np.array(acc)
    w = 17   # ~60 Hz moving average at 1 kHz
    sm = np.convolve(acc, np.ones(w) / w, mode='same') if len(acc) > w else acc
    return dict(lean=lean, first_upper_contact=first, t_chest_hit_s=t_hit, peak_chest_N=round(peakF, 1),
                torso_peak_g_raw=round(float(acc.max()), 1), torso_peak_g_ma60Hz=round(float(sm.max()), 1))


if __name__ == '__main__':
    out = dict(kneel=kneel_cog())
    out['lower_nominal'] = controlled_lower()
    dr = []
    for mass, fr, tc in itertools.product((65.0, 68.5), (0.6, 1.0), (0.005, 0.02)):
        dr.append(controlled_lower(mass, fr, tc))
    out['lower_dr'] = dr
    sp = [r['chest_contact_speed_mps'] for r in dr if r['chest_contact_speed_mps'] is not None]
    pk = [r['peak_chest_N'] for r in dr]
    out['lower_dr_summary'] = dict(n=len(dr), contacts=len(sp), speed_mean=round(float(np.mean(sp)), 3) if sp else None,
                                   speed_max=round(float(np.max(sp)), 3) if sp else None,
                                   peak_force_mean=round(float(np.mean(pk)), 1), peak_force_max=round(float(np.max(pk)), 1))
    out['tip_over'] = [tip_over(l) for l in (0.15, 0.3)]
    json.dump(out, open(os.path.join(HERE, 'prone_data_results.json'), 'w'), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))
