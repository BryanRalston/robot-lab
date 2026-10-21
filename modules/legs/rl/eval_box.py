"""Replay the walk policy on the unmodified v3 box. Numpy and MuJoCo only.

Loads sim/v3/humanoid_v3.xml, scales mass to 65 kg the way gait_lib does, and
clips leg torques to the R1.2 limits. Does not write sim/v3. The policy is the
tanh of the first 30 MLP outputs, after the training obs normalizer.
"""
import argparse
import json
import os

os.environ.setdefault('MUJOCO_GL', 'egl')

import numpy as np
import mujoco

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
XML_V3 = os.path.join(ROOT, 'sim', 'v3', 'humanoid_v3.xml')
OUT_DIR = os.path.join(HERE, 'results')

LIM_R1 = {
    'hip_yaw': 70.0, 'hip_roll': 204.0, 'hip_pitch': 350.0,
    'knee': 258.0, 'ankle_pitch': 311.0, 'ankle_roll': 177.0,
}
DT = 0.002
CTRL_DT = 0.02
SUB = 10


def _quat_R(q):
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def load_policy(path):
    z = np.load(path)
    weights = []
    i = 0
    while f'pi__params__hidden_{i}__kernel' in z.files:
        weights.append((
            np.asarray(z[f'pi__params__hidden_{i}__kernel'], dtype=np.float64),
            np.asarray(z[f'pi__params__hidden_{i}__bias'], dtype=np.float64),
        ))
        i += 1
    if len(weights) < 2:
        raise SystemExit(f'no MLP weights in {path}: {z.files[:12]}')
    mean = std = None
    for key in z.files:
        if key.endswith('mean__state') or key.endswith('mean/state'):
            mean = np.asarray(z[key], dtype=np.float64).reshape(-1)
        if key.endswith('std__state') or key.endswith('std/state'):
            std = np.asarray(z[key], dtype=np.float64).reshape(-1)
    if mean is None or std is None:
        raise SystemExit('normalizer mean/std not in ' + path + ' keys ' + ','.join(z.files[:40]))
    meta = load_meta(path)
    dim = int(meta.get('policy_obs_dim') or (109 if meta.get('heading_obs') else 107))
    if mean.shape != (dim,) or std.shape != (dim,):
        raise SystemExit(f'normalizer shape {mean.shape} {std.shape}, expected {dim}')
    return weights, mean, std, meta


def load_meta(path):
    """Sidecar written by train.py (J10). Job-4 policies have none: infer the legacy layout."""
    side = path[:-4] + '.meta.json'
    if os.path.isfile(side):
        with open(side, encoding='utf-8') as f:
            return json.load(f)
    return {'policy_obs_dim': 107, 'heading_obs': False, 'leg_action_mult': 1.0, 'payload_empty_frac': None}


def empty_payload_frac(policy):
    """payload_frac the policy saw with no payload in training.

    Job 4 trained walk_a/walk_b with a 0.001 kg placeholder, so payload_frac was 5e-5 and the
    normalizer std was its 1e-6 floor. Feeding 0.0 gave a -50 sigma input and the falls in <1 s
    (RETRAIN_PLAN_J10.md section 2.1). J10 policies train with exactly 0.
    """
    weights, mean, std, meta = policy
    if meta.get('payload_empty_frac') is not None:
        return float(meta['payload_empty_frac'])
    if std[12] < 1e-3:
        return float(mean[12])
    return 0.0


OBS_Z_MAX = 8.0


def obs_z_check(obs, mean, std, names=None):
    """Largest |normalized obs| and its index. A replay mismatch shows up here first."""
    z = np.abs((obs - mean) / std)
    i = int(np.argmax(z))
    return float(z[i]), i


def policy_action(obs, weights, mean, std):
    h = (obs - mean) / std
    for i, (w, b) in enumerate(weights):
        h = h @ w + b
        if i < len(weights) - 1:
            h = h / (1.0 + np.exp(-np.clip(h, -40.0, 40.0)))
    return np.tanh(h[:30])


def load_box(carry_kg=0.0):
    xml = open(XML_V3, encoding='utf-8').read()
    if carry_kg > 0:
        needle = '<geom name="torso" type="box" pos="0 0 0.180" size="0.11 0.17 0.130"/>'
        payload = (
            f'<body name="payload" pos="0.25 0 0.10">'
            f'<inertial pos="0 0 0" mass="{carry_kg}" diaginertia="0.2 0.15 0.2"/>'
            f'</body>'
        )
        if needle not in xml:
            raise SystemExit('torso geom not found in v3 xml')
        xml = xml.replace(needle, payload + needle, 1)
    m = mujoco.MjModel.from_xml_string(xml)
    base = 0.0
    for i in range(m.nbody):
        if m.body(i).name != 'payload':
            base += float(m.body_mass[i])
    k = 65.0 / base
    for i in range(m.nbody):
        if m.body(i).name == 'payload':
            continue
        m.body_mass[i] *= k
        m.body_inertia[i] *= k
    for i in range(m.nu):
        name = m.actuator(i).name
        for jn, lim in LIM_R1.items():
            if name.endswith(jn) and name[:2] in ('l_', 'r_'):
                m.actuator_ctrlrange[i] = [-lim, lim]
    mujoco.mj_setConst(m, mujoco.MjData(m))
    return m, k


def _blend(table, phase, vx):
    n = table.shape[1]
    pos = float(phase) * n
    i0 = int(np.floor(pos)) % n
    i1 = (i0 + 1) % n
    a = pos - np.floor(pos)
    speeds = (1.0 - a) * table[:, i0] + a * table[:, i1]
    u = float(np.clip((vx - 0.8) / 0.2, 0.0, 2.0))
    w = float(np.clip(u, 0.0, 1.0))
    low = (1.0 - w) * speeds[0] + w * speeds[1]
    w2 = float(np.clip(u - 1.0, 0.0, 1.0))
    high = (1.0 - w2) * speeds[1] + w2 * speeds[2]
    return low if u < 1.0 else high


def _is_stand(cmd):
    return abs(cmd[0]) < 0.12 and abs(cmd[1]) < 0.12 and abs(cmd[2]) < 0.2


def _yaw(q):
    w, x, y, z = q
    return float(np.arctan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z)))


def _obs(d, cmd, phase, last, payload_frac, home_q, heading_ref=None):
    R = _quat_R(d.qpos[3:7])
    lin = R.T @ d.qvel[0:3]
    gyro = d.qvel[3:6].copy()
    grav = R.T @ np.array([0.0, 0.0, -1.0])
    ang = phase * 2.0 * np.pi
    phase_obs = np.array([
        np.sin(ang), np.cos(ang), np.sin(ang + np.pi), np.cos(ang + np.pi),
    ])
    return np.concatenate([
        lin, gyro, grav, np.asarray(cmd, dtype=np.float64),
        np.array([payload_frac]),
        d.qpos[7:] - home_q, d.qvel[6:], last, phase_obs,
    ] + ([] if heading_ref is None else [_heading_obs(d, heading_ref)]))


def _heading_obs(d, heading_ref):
    e = _yaw(d.qpos[3:7]) - heading_ref
    e = np.arctan2(np.sin(e), np.cos(e))
    return np.array([np.sin(e), np.cos(e)])


def _foot_fz(m, d):
    out = []
    for name in ('l_foot', 'r_foot'):
        gid = m.geom(name).id
        total = 0.0
        for i in range(d.ncon):
            c = d.contact[i]
            if c.geom1 == gid or c.geom2 == gid:
                f = np.zeros(6)
                mujoco.mj_contactForce(m, d, i, f)
                total += float(f[0])
        out.append(total)
    return out


def _drop_feet(m, d):
    mujoco.mj_forward(m, d)
    soles = []
    for name in ('l_foot', 'r_foot'):
        gid = m.geom(name).id
        soles.append(float(d.geom_xpos[gid, 2] - m.geom_size[gid, 2]))
    d.qpos[2] -= min(soles) - 0.001
    mujoco.mj_forward(m, d)


def run_episode(m, policy, gains, ref, cmd, seconds, mode, payload_frac,
                push=None, kick_vx=None, kick_after_s=0.0, record=None):
    """mode 'gait' starts in the reference at cmd vx. mode 'stand' uses the settled crouch.

    push: (t0, t1, fx, fy) world-frame force on the torso, or None.
    kick_vx: added to world vx at kick_after_s (the forward-push gate).
    """
    weights, mean, std, meta = policy
    use_heading = bool(meta.get('heading_obs'))
    dim = mean.shape[0]
    if payload_frac is None:
        payload_frac = empty_payload_frac(policy)
    home_q = np.asarray(gains['home_q'], dtype=np.float64)
    home_qpos = np.asarray(gains['home_qpos'], dtype=np.float64)
    kp = np.asarray(gains['kp'], dtype=np.float64)
    kd = np.asarray(gains['kd'], dtype=np.float64)
    tau_lim = np.asarray(gains['tau_lim'], dtype=np.float64)
    w_lim = np.asarray(gains['w_lim'], dtype=np.float64)
    scale = np.asarray(gains['action_scale'], dtype=np.float64).copy()
    legj = np.array([n[:2] in ('l_', 'r_') and any(n.endswith(j) for j in (
        'hip_roll', 'hip_pitch', 'knee', 'ankle_pitch', 'ankle_roll')) for n in [str(s) for s in gains['joint_names'].tolist()]])
    scale[legj] *= float(meta.get('leg_action_mult', 1.0))
    carry = np.asarray(gains['carry_offset'], dtype=np.float64)
    names = [str(s) for s in gains['joint_names'].tolist()]
    lo = m.actuator_ctrlrange[:, 0].copy()
    hi = m.actuator_ctrlrange[:, 1].copy()
    # Clip to the contract limit, which is what gains were built from.
    lo = np.maximum(lo, -tau_lim)
    hi = np.minimum(hi, tau_lim)

    d = mujoco.MjData(m)
    phase = 0.0
    if mode == 'gait':
        ref_q = _blend(ref['q'], phase, cmd[0])
        ref_qd = _blend(ref['qd'], phase, cmd[0])
        ref_z = float(_blend(ref['pelvis_z'], phase, cmd[0]))
        d.qpos[:] = 0
        d.qpos[2] = ref_z
        d.qpos[3] = 1.0
        d.qpos[7:] = ref_q
        d.qvel[:] = 0
        d.qvel[0] = cmd[0]
        d.qvel[1] = cmd[1]
        d.qvel[5] = cmd[2]
        d.qvel[6:] = ref_qd
    else:
        if home_qpos.shape[0] != m.nq:
            raise SystemExit(f'home qpos {home_qpos.shape} nq {m.nq}')
        d.qpos[:] = home_qpos
        d.qpos[0] = 0.0
        d.qpos[1] = 0.0
        d.qvel[:] = 0
    _drop_feet(m, d)
    z0 = float(d.qpos[2])
    last = np.zeros(m.nu)
    kicked = False
    torso = m.body('torso').id
    n_ctrl = int(round(seconds / CTRL_DT))
    speed = []
    forward = []
    vx_w = []
    vy_w = []
    z_log = []
    up_log = []
    tau_peak = np.zeros(m.nu)
    w_peak = np.zeros(m.nu)
    sat = np.zeros(m.nu)
    fz_log = []
    ankle = []
    fell = None
    fall_why = ''
    air_t = 0.0
    frames = []
    renderer = record
    aroll = [i for i, n in enumerate(names) if n.endswith('ankle_roll')]
    t_log = []
    heading_ref = _yaw(d.qpos[3:7])
    z_first = None
    knee_idx = [i for i, n in enumerate(names) if n.endswith('knee')]
    knee_sq = []

    for k in range(n_ctrl):
        t = k * CTRL_DT
        if kick_vx is not None and not kicked and t >= kick_after_s:
            d.qvel[0] += float(kick_vx)
            kicked = True
            mujoco.mj_forward(m, d)
        obs = _obs(d, cmd, phase, last, payload_frac, home_q, heading_ref if use_heading else None)
        if obs.shape != (dim,):
            raise SystemExit(f'obs {obs.shape} vs normalizer {dim}')
        if k == 0:
            z_first = obs_z_check(obs, mean, std)
            if z_first[0] > OBS_Z_MAX:
                raise SystemExit(f'obs index {z_first[1]} is {z_first[0]:.1f} sigma from the training '
                                 f'normalizer at t=0: replay does not match the training env')
        heading_ref += float(cmd[2]) * CTRL_DT
        action = policy_action(obs, weights, mean, std)
        stand = _is_stand(cmd)
        if stand:
            base = home_q
        else:
            base = _blend(ref['q'], phase, cmd[0])
        target = np.clip(base + payload_frac * carry + action * scale, m.jnt_range[1:, 0], m.jnt_range[1:, 1])
        fx = fy = 0.0
        if push is not None and push[0] <= t < push[1]:
            fx, fy = push[2], push[3]
        for _ in range(SUB):
            q = d.qpos[7:]
            qd = d.qvel[6:]
            tau = kp * (target - q) - kd * qd
            derate = np.ones(m.nu)
            mask = w_lim > 0
            derate[mask] = np.clip(1.0 - np.abs(qd[mask]) / (1.2 * w_lim[mask]), 0.0, 1.0)
            tmax = tau_lim * derate
            tau = np.clip(tau, -tmax, tmax)
            tau = np.clip(tau, lo, hi)
            d.ctrl[:] = tau
            d.xfrc_applied[:] = 0
            d.xfrc_applied[torso, 0] = fx
            d.xfrc_applied[torso, 1] = fy
            mujoco.mj_step(m, d)
        tau_peak = np.maximum(tau_peak, np.abs(tau))
        knee_sq.append([float(tau[i]) ** 2 for i in knee_idx])
        w_peak = np.maximum(w_peak, np.abs(d.qvel[6:]))
        sat += (np.abs(tau) > 0.95 * np.maximum(tmax, 1e-6)).astype(np.float64)
        R = _quat_R(d.qpos[3:7])
        lin = R.T @ d.qvel[0:3]
        up = float(R[2, 2])
        speed.append(float(np.hypot(d.qvel[0], d.qvel[1])))
        forward.append(float(lin[0]))
        vx_w.append(float(d.qvel[0]))
        vy_w.append(float(d.qvel[1]))
        z_log.append(float(d.qpos[2]))
        up_log.append(up)
        fz = _foot_fz(m, d)
        fz_log.append(fz)
        ankle.append([float(d.qpos[7 + i]) for i in aroll])
        t_log.append(t + CTRL_DT)
        if d.ncon == 0:
            air_t += CTRL_DT
        else:
            air_t = 0.0
        if fell is None:
            if d.qpos[2] < z0 - 0.28 or up < 0.72:
                fell, fall_why = float(d.time), 'pelvis'
            elif air_t > 0.15:
                fell, fall_why = float(d.time), 'airborne'
            elif d.qpos[2] > z0 + 0.22:
                fell, fall_why = float(d.time), 'jumped'
        # Walk clip: every 3rd control step from the start through 8 s, and
        # 0.5 s past a fall so an early fall still produces a GIF.
        if renderer is not None and t <= 8.0 and k % 3 == 0 and (fell is None or t <= fell + 0.5):
            renderer.update_scene(d, camera=record_cam(d))
            frames.append(renderer.render().copy())
        last = action
        if not stand:
            phase = (phase + CTRL_DT) % 1.0
        if fell is not None and t > fell + 0.5:
            break

    fz_a = np.asarray(fz_log) if fz_log else np.zeros((1, 2))
    both = (fz_a[:, 0] > 40.0) & (fz_a[:, 1] > 40.0)
    flight = (fz_a[:, 0] < 20.0) & (fz_a[:, 1] < 20.0)
    n = max(len(speed), 1)
    ankle_a = np.asarray(ankle) if ankle else np.zeros((1, len(aroll)))
    summary = {
        'seconds_ran': round(float(t_log[-1]) if t_log else 0.0, 3),
        'fell_at_s': None if fell is None else round(fell, 3),
        'fall_why': fall_why,
        'z0': round(z0, 4),
        'mean_horiz_speed': round(float(np.mean(speed)) if speed else 0.0, 4),
        'mean_forward': round(float(np.mean(forward)) if forward else 0.0, 4),
        'mean_vx_world': round(float(np.mean(vx_w)) if vx_w else 0.0, 4),
        'mean_vy_world': round(float(np.mean(vy_w)) if vy_w else 0.0, 4),
        'net_x_over_t': round(float(d.qpos[0] / max(d.time, 1e-6)), 4),
        'final_y': round(float(d.qpos[1]), 3),
        'final_heading_deg': round(float(np.degrees(_yaw(d.qpos[3:7]))), 2),
        'payload_frac_obs': payload_frac,
        'knee_rms_nm': [round(float(np.sqrt(np.mean(np.asarray(knee_sq)[:, j]))), 1) for j in range(len(knee_idx))] if knee_sq else None,
        'obs_z_max_t0': None if z_first is None else round(z_first[0], 2),
        'min_z': round(float(np.min(z_log)) if z_log else 0.0, 4),
        'min_up': round(float(np.min(up_log)) if up_log else 0.0, 4),
        'final_up': round(float(up_log[-1]) if up_log else 0.0, 4),
        'final_horiz_speed': round(float(speed[-1]) if speed else 0.0, 4),
        'ds_fraction': round(float(np.mean(both)), 4),
        'flight_fraction': round(float(np.mean(flight)), 4),
        'ankle_roll_peak_rad': [round(float(np.max(np.abs(ankle_a[:, i]))), 4) for i in range(ankle_a.shape[1])],
        'ankle_roll_peak_deg': [round(float(np.degrees(np.max(np.abs(ankle_a[:, i])))), 2) for i in range(ankle_a.shape[1])],
        'torque_peak': {names[i]: round(float(tau_peak[i]), 2) for i in range(m.nu)},
        'speed_peak': {names[i]: round(float(w_peak[i]), 3) for i in range(m.nu)},
        'sat_fraction': {names[i]: round(float(sat[i] / n), 4) for i in range(m.nu)},
        'tau_lim': {names[i]: round(float(tau_lim[i]), 2) for i in range(m.nu)},
        'w_lim': {names[i]: round(float(w_lim[i]), 3) for i in range(m.nu)},
    }
    return summary, frames


DRIFT_Y_MAX_M = 0.5
DRIFT_HEADING_MAX_DEG = 5.0


def drift_ok(s):
    """J10 no-drift gate for a straight command: |final y| <= 0.5 m and |heading| <= 5 deg."""
    return bool(abs(s['final_y']) <= DRIFT_Y_MAX_M and abs(s['final_heading_deg']) <= DRIFT_HEADING_MAX_DEG)


def record_cam(d):
    cam = mujoco.MjvCamera()
    cam.distance = 3.4
    cam.azimuth = 120
    cam.elevation = -18
    cam.lookat[:] = [d.qpos[0], d.qpos[1], 0.8]
    return cam


def _leg_rows(summary):
    rows = []
    for name, peak in summary['torque_peak'].items():
        if not (name[:2] in ('l_', 'r_') and any(name.endswith(j) for j in LIM_R1)):
            continue
        rows.append({
            'joint': name,
            'tau_peak': peak,
            'tau_lim': summary['tau_lim'][name],
            'tau_frac': round(peak / summary['tau_lim'][name], 3),
            'w_peak': summary['speed_peak'][name],
            'w_lim': summary['w_lim'][name],
            'w_frac': round(summary['speed_peak'][name] / summary['w_lim'][name], 3) if summary['w_lim'][name] else None,
            'sat_fraction': summary['sat_fraction'][name],
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--policy', required=True)
    ap.add_argument('--gif', action='store_true')
    ap.add_argument('--xml', default=None, help='MJCF to evaluate (default sim/v3/humanoid_v3.xml)')
    ap.add_argument('--tag', default='', help='prefix for results JSON and the GIF, so policies do not overwrite each other')
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    if args.xml:
        global XML_V3
        XML_V3 = os.path.abspath(args.xml)
    gains = np.load(os.path.join(HERE, 'gains.npz'))
    ref = np.load(os.path.join(HERE, 'ref_cycle.npz'))
    policy = load_policy(args.policy)
    m, k_mass = load_box(0.0)
    names = [m.actuator(i).name for i in range(m.nu)]
    gnames = [str(s) for s in gains['joint_names'].tolist()]
    if names != gnames:
        raise SystemExit(f'actuator order mismatch\nbox {names}\ngains {gnames}')
    print('mass_scale', round(k_mass, 6), 'mass', round(float(np.sum(m.body_mass)), 3), flush=True)

    renderer = None
    if args.gif:
        renderer = mujoco.Renderer(m, height=360, width=480)

    walk, frames = run_episode(
        m, policy, gains, ref, cmd=np.array([1.2, 0.0, 0.0]),
        seconds=20.0, mode='gait', payload_frac=None, record=renderer,
    )
    walk_pass = walk['fell_at_s'] is None and walk['seconds_ran'] >= 19.9 and walk['mean_horiz_speed'] >= 1.15
    walk['pass_legacy'] = bool(walk_pass)
    walk['drift_ok'] = drift_ok(walk)
    walk['pass'] = bool(walk_pass and walk['drift_ok'] and walk['net_x_over_t'] >= 1.15)
    walk['gate'] = 'walk 20s at 1.2 m/s, mean horizontal speed and net x/t >= 1.15, no fall, |y| <= 0.5 m, |heading| <= 5 deg'
    walk['legs'] = _leg_rows(walk)
    print('WALK', walk['pass'], 'speed', walk['mean_horiz_speed'], 'fwd', walk['mean_forward'],
          'x/t', walk['net_x_over_t'], 'fell', walk['fell_at_s'], walk['fall_why'], flush=True)

    # Lateral 60 N·s during the walk, applied at t=4.0 whether or not the walk is good.
    lat, _ = run_episode(
        m, policy, gains, ref, cmd=np.array([1.2, 0.0, 0.0]),
        seconds=8.0, mode='gait', payload_frac=None,
        push=(4.0, 4.2, 0.0, 300.0),
    )
    # Recovery window is (4 s, 6 s]. A fall before the push means the walk never got there.
    fell = lat['fell_at_s']
    if fell is None or fell > 6.0:
        lat['pass'] = True
        if fell is not None:
            lat['note'] = 'survived the 2 s after the push, then fell later'
    elif fell < 4.0:
        lat['pass'] = False
        lat['note'] = 'fell before the push, so recovery was not tested on a walking robot'
    else:
        lat['pass'] = False
        lat['note'] = 'fell during the 2 s recovery window'
    lat['gate'] = '300 N * 0.2 s = 60 N·s along +Y on the torso at t=4 during a 1.2 m/s walk; no fall through t=6'
    lat['push_Ns'] = 60.0
    print('LATERAL', lat['pass'], 'fell', lat['fell_at_s'], lat.get('note', ''), 'min_up', lat['min_up'], flush=True)

    fwd, _ = run_episode(
        m, policy, gains, ref, cmd=np.array([0.0, 0.0, 0.0]),
        seconds=3.0, mode='stand', payload_frac=None,
        kick_vx=0.6, kick_after_s=1.0,
    )
    # Kick at 1.0 s. Recover by 3.0 s: still up, and horizontal speed back under 0.5.
    fell_after = fwd['fell_at_s'] is not None and fwd['fell_at_s'] >= 1.0
    fell_before = fwd['fell_at_s'] is not None and fwd['fell_at_s'] < 1.0
    fwd['pass'] = bool((not fell_after) and (not fell_before) and fwd['final_up'] >= 0.72 and fwd['final_horiz_speed'] < 0.5 and fwd['seconds_ran'] >= 2.9)
    fwd['gate'] = 'forward push: +0.6 m/s COM velocity from the policy stand at t=1; upright and horizontal speed < 0.5 at t=3 (2 s later)'
    fwd['impulse_Ns'] = round(0.6 * float(np.sum(m.body_mass)), 3)
    print('FORWARD', fwd['pass'], 'fell', fwd['fell_at_s'], 'final_v', fwd['final_horiz_speed'], 'up', fwd['final_up'], flush=True)

    m20, k20 = load_box(20.0)
    print('carry mass', round(float(np.sum(m20.body_mass)), 3), 'scale', round(k20, 6), flush=True)
    try:
        carry, _ = run_episode(
            m20, policy, gains, ref, cmd=np.array([0.8, 0.0, 0.0]),
            seconds=20.0, mode='gait', payload_frac=1.0,
        )
    except SystemExit as exc:
        # A policy trained without payload has a ~1e-6 std on payload_frac: carry is out of scope.
        carry = {'fell_at_s': None, 'seconds_ran': 0.0, 'mean_horiz_speed': 0.0, 'final_y': 0.0,
                 'final_heading_deg': 0.0, 'net_x_over_t': 0.0, 'error': str(exc)}
    carry['pass_legacy'] = bool(carry['fell_at_s'] is None and carry['seconds_ran'] >= 19.9 and carry['mean_horiz_speed'] >= 0.8)
    carry['drift_ok'] = drift_ok(carry)
    carry['pass'] = bool(carry['pass_legacy'] and carry['drift_ok'] and carry['net_x_over_t'] >= 0.8)
    carry['gate'] = '20 kg torso payload at (0.25, 0, 0.10), command 0.8 m/s, 20 s, mean horizontal speed >= 0.8, no fall'
    carry['payload_kg'] = 20.0
    print('CARRY', carry['pass'], 'speed', carry['mean_horiz_speed'], 'fell', carry['fell_at_s'], flush=True)

    # Drop the bulky per-joint maps from the top level into legs for the walk file only.
    def slim(s, keep_legs=False):
        out = {k: v for k, v in s.items() if k not in ('torque_peak', 'speed_peak', 'sat_fraction', 'tau_lim', 'w_lim')}
        if keep_legs and 'legs' in s:
            out['legs'] = s['legs']
        return out

    prefix = (args.tag + '_') if args.tag else ''
    policy_name = os.path.basename(args.policy)
    walk_out = slim(walk, keep_legs=True)
    written = [
        ('walk.json', walk_out),
        ('push_lateral.json', slim(lat)),
        ('push_forward.json', slim(fwd)),
        ('carry.json', slim(carry)),
    ]
    for name, payload in written:
        payload['policy'] = policy_name
        with open(os.path.join(OUT_DIR, prefix + name), 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
    print('wrote', OUT_DIR, prefix or '(no tag)', flush=True)

    if frames:
        import imageio.v2 as imageio
        gif_path = os.path.join(HERE, prefix + 'walk.gif')
        imageio.mimsave(gif_path, frames, duration=3 * CTRL_DT, loop=0)
        print('gif', gif_path, 'frames', len(frames), flush=True)
    elif args.gif:
        print('GIF_FAILED no frames', flush=True)


if __name__ == '__main__':
    main()
