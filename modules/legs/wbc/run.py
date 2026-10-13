"""Forward-sim the whole-body walking controller and write acceptance metrics.

Usage (from anywhere):
  python modules/legs/wbc/run.py --mode stand --seconds 2
  python modules/legs/wbc/run.py --mode walk --seconds 20 --gif
  python modules/legs/wbc/run.py --mode push --seconds 20
  python modules/legs/wbc/run.py --mode carry --seconds 20 --gif
"""
import os, sys, json, time, argparse
import numpy as np
import mujoco

HERE = os.path.dirname(os.path.abspath(__file__))
LEGS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(LEGS))
os.environ.setdefault('LEGS_MASS', '65')
os.environ.setdefault('LEGS_LIMITS', 'r1')
if LEGS not in sys.path:
    sys.path.insert(0, LEGS)

from gait_lib import load, LEG, LIM_R1, SOLE, HEEL, TOE, HALFW
from controller import WalkController, measured_cop, cop_margin_mm

OUT = os.path.join(LEGS, 'grokbuild', 'results')
GIF = os.path.join(ROOT, 'media', 'progress', '2026-10-13_legs_wbc_walk1p2.gif')


def run(mode='walk', seconds=20.0, cruise=1.20, dt=0.001, push=False, carry=False,
        gif=False, seed_note=''):
    m = load(20.0, (0.25, 0.0, 0.10)) if carry else load()
    m.opt.timestep = dt
    d = mujoco.MjData(m)
    ctrl = WalkController(m, carry=carry, cruise=cruise)
    if mode == 'stand':
        ctrl.stand_only = True
    info = ctrl.initialize(d)
    if mode != 'stand':
        plan = os.path.join(LEGS, 'results', 'r2',
                            'carry_20kg_r2.npz' if carry else 'walk_1p2_r2.npz')
        extra = ctrl.use_plan(plan, d)
        info.update(extra)
    print('init', {k: round(v, 4) if isinstance(v, float) else v for k, v in info.items()},
          'nv', m.nv, 'nu', m.nu, flush=True)
    n = int(seconds / dt)
    leg_idx = [ctrl.act_name.index(f'{s}_{j}') for s in 'lr' for j in LEG]
    leg_names = [ctrl.act_name[i] for i in leg_idx]
    tau_log = np.zeros((n, 12))
    cop_log = np.full(n, np.nan)
    cop_local = np.full((n, 2), np.nan)  # worst-foot local cop x,y of the tighter foot
    fz_log = np.zeros((n, 2))
    state = np.zeros((n, 8))  # t x y z vx vy roll pitch  (yaw separate)
    yaw_log = np.zeros(n)
    q_keep = []
    t_keep = []
    push_impulse = 0.0
    push_t = None
    push_side = None
    push_vy0 = None
    push_vy1 = None
    fell = None
    fall_why = None
    t_push_end = None
    torso = ctrl.torso
    k_end = 0
    air_t = 0.0
    ms_sum = 0.0
    t0 = time.perf_counter()
    for k in range(n):
        ctrl.step(d)
        ms_sum += ctrl.last_ms
        # +Y push during left-foot swing (the +Y foot), so the landing can catch it.
        # Left swing occupies the first ~0.23 s of the 1 s cruise cycle.
        local = float(ctrl.phase_t % ctrl.period) if getattr(ctrl, 'plan_on', False) else ctrl.s
        if (push and push_t is None and d.time > 3.5 and ctrl.phase == 'ss'
                and ctrl.swing == 'l' and 0.06 <= local <= 0.18):
            push_t = float(d.time)
            push_side = ctrl.swing
            push_vy0 = float(d.qvel[1])
            t_push_end = push_t + 0.20
            print(f'PUSH at t={push_t:.3f}s swing={push_side} s={ctrl.s:.2f} vy={push_vy0:.3f}',
                  flush=True)
        if push_t is not None and d.time <= t_push_end:
            d.xfrc_applied[torso, :] = 0
            d.xfrc_applied[torso, 1] = 300.0
            push_impulse += 300.0 * dt
        else:
            if push_t is not None and push_vy1 is None:
                push_vy1 = float(d.qvel[1])
            d.xfrc_applied[torso, :] = 0
        mujoco.mj_step(m, d)
        k_end = k + 1
        tau_log[k] = ctrl.last_tau[leg_idx]
        # measured CoP margin on each loaded foot; keep the tighter one
        margins = []
        for si, s in enumerate('lr'):
            cop, fz = measured_cop(m, d, ctrl.foot_geom[s])
            fz_log[k, si] = fz
            if cop is not None and fz > 40:
                p = d.xpos[ctrl.foot[s]]
                R = d.xmat[ctrl.foot[s]].reshape(3, 3)
                margin, local = cop_margin_mm(cop, p, R)
                margins.append((margin, local))
        if margins:
            margins.sort(key=lambda z: z[0])
            cop_log[k] = margins[0][0]
            cop_local[k] = margins[0][1]
        Rm = d.xmat[ctrl.pelvis].reshape(3, 3)
        roll = np.arctan2(Rm[2, 1], Rm[2, 2])
        pitch = np.arctan2(-Rm[2, 0], np.hypot(Rm[2, 1], Rm[2, 2]))
        yaw = np.arctan2(Rm[1, 0], Rm[0, 0])
        mujoco.mj_subtreeVel(m, d)
        vx, vy = d.subtree_linvel[1][:2]
        state[k] = [d.time, d.qpos[0], d.qpos[1], d.qpos[2], vx, vy, roll, pitch]
        yaw_log[k] = yaw
        if k % int(0.05 / dt) == 0:
            q_keep.append(d.qpos.copy())
            t_keep.append(float(d.time))
        if d.ncon == 0:
            air_t += dt
        else:
            air_t = 0.0
        if d.qpos[2] < ctrl.z0 - 0.28 or Rm[2, 2] < 0.72:
            fell = float(d.time)
            fall_why = 'pelvis'
            print(f'FELL t={fell:.3f} z={d.qpos[2]:.3f} up={Rm[2, 2]:.2f}', flush=True)
            break
        if air_t > 0.15 or d.qpos[2] > ctrl.z0 + 0.22:
            fell = float(d.time)
            fall_why = 'airborne' if air_t > 0.15 else 'jumped'
            print(f'FELL t={fell:.3f} why={fall_why} z={d.qpos[2]:.3f} ncon={d.ncon}', flush=True)
            break
        if k % int(0.5 / dt) == 0:
            print(f't={d.time:5.2f} x={d.qpos[0]:5.2f} vx={vx:5.2f} y={d.qpos[1]:5.2f} '
                  f'z={d.qpos[2]:5.3f} rpy=({np.degrees(roll):4.1f},{np.degrees(pitch):4.1f},{np.degrees(yaw):4.1f}) '
                  f'{ctrl.phase:7} s={ctrl.s:4.2f} ncon={d.ncon:2d} cop={cop_log[k]:6.1f} '
                  f'qp={ctrl.last_ms:5.1f}ms base={ctrl.last_base_res:5.1f} {ctrl.last_status}',
                  flush=True)
    elapsed = time.perf_counter() - t0
    sl = slice(0, k_end)
    tau = tau_log[sl]
    st = state[sl]
    t_end = float(st[-1, 0]) if k_end else 0.0
    # touchdowns from vertical force: airborne > 0.08 s then loaded
    td = 0
    air = np.zeros(2)
    for k in range(k_end):
        for i in range(2):
            if fz_log[k, i] < 20:
                air[i] += dt
            else:
                if air[i] > 0.08 and st[k, 0] > 0.4:
                    td += 1
                air[i] = 0.0
    joints = []
    for i, name in enumerate(leg_names):
        jkey = name.split('_', 1)[1]
        # name is l_hip_yaw -> joint hip_yaw. split once: 'l', 'hip_yaw' only if we split on first _
        jkey = name[2:]  # hip_yaw / ankle_pitch / ...
        avail = float(LIM_R1[jkey])
        series = tau[:, i]
        peak = float(np.max(np.abs(series))) if k_end else 0.0
        rms = float(np.sqrt(np.mean(series ** 2))) if k_end else 0.0
        sat = float(np.mean(np.abs(series) >= 0.99 * avail)) if k_end else 0.0
        joints.append(dict(joint=name, peak_Nm=round(peak, 2), rms_Nm=round(rms, 2),
                           avail_Nm=avail, peak_over_avail=round(peak / avail, 3),
                           saturated_pct=round(100.0 * sat, 2)))
    cop_ok = cop_log[sl]
    cop_ok = cop_ok[np.isfinite(cop_ok)]
    cop_min = float(np.min(cop_ok)) if len(cop_ok) else None
    # peak distance of CoP from the sole center (0.06, 0), mm
    loc = cop_local[sl]
    good = np.isfinite(loc[:, 0])
    if np.any(good):
        exc = np.hypot(loc[good, 0] - 0.06, loc[good, 1])
        cop_exc_peak = float(np.max(exc) * 1000.0)
    else:
        cop_exc_peak = None
    mean_speed = float(st[-1, 1] / t_end) if t_end > 0 else 0.0
    # steady window: last half, if long enough
    if t_end > 4:
        mask = st[:, 0] > t_end * 0.5
        steady = float(np.mean(st[mask, 4])) if np.any(mask) else mean_speed
    else:
        steady = float(np.mean(st[:, 4])) if k_end else 0.0
    res = dict(
        mode=mode, carry_kg=20.0 if carry else 0.0, cruise_cmd_mps=cruise,
        timestep_s=dt, wbc_hz=round(1.0 / dt), mpc_hz=round(1.0 / (10 * dt)),
        seconds_commanded=seconds, sim_time_s=round(t_end, 4),
        fell_at_s=None if fell is None else round(fell, 4),
        fall_trigger=fall_why,
        completed=fell is None and t_end >= seconds - 2 * dt,
        mean_speed_pelvis_mps=round(mean_speed, 4),
        mean_speed_com_vx_mps=round(steady, 4),
        pelvis_x_m=round(float(st[-1, 1]), 4) if k_end else 0.0,
        touchdowns=int(td),
        cop_margin_min_mm=None if cop_min is None else round(cop_min, 2),
        cop_offset_from_sole_center_peak_mm=None if cop_exc_peak is None else round(cop_exc_peak, 2),
        joints=joints,
        qp_ok=ctrl.qp_ok, qp_fail=ctrl.qp_fail,
        mean_wbc_ms=round(ms_sum / max(k_end, 1), 3),
        wall_s=round(elapsed, 2),
        push_applied=bool(push),
        push_time_s=None if push_t is None else round(push_t, 4),
        push_swing_foot=push_side,
        push_impulse_Ns=round(push_impulse, 3),
        push_vy_before=None if push_vy0 is None else round(push_vy0, 4),
        push_vy_after=None if push_vy1 is None else round(push_vy1, 4),
        push_dvy=None if push_vy0 is None or push_vy1 is None else round(push_vy1 - push_vy0, 4),
        landings=ctrl.landings[-12:],
        note=seed_note,
        mass_kg=round(ctrl.mass, 3),
        com_z_m=round(ctrl.com_z_ref, 4),
    )
    # proper mean solve time is tracked as last_ms only at the end; recompute from a running
    # value stored on the controller if present
    print('RESULT', json.dumps({k: res[k] for k in
          ('sim_time_s', 'fell_at_s', 'mean_speed_pelvis_mps', 'mean_speed_com_vx_mps',
           'touchdowns', 'cop_margin_min_mm', 'qp_ok', 'qp_fail', 'wall_s', 'push_impulse_Ns')}),
          flush=True)
    os.makedirs(OUT, exist_ok=True)
    tag = mode
    np.savez_compressed(os.path.join(OUT, f'{tag}_trace.npz'),
                        state=st, yaw=yaw_log[:k_end], tau=tau, cop_margin_mm=cop_log[sl],
                        cop_local=loc if k_end else cop_local[:1], fz=fz_log[sl],
                        t_q=np.array(t_keep), q=np.array(q_keep) if q_keep else np.zeros((0, m.nq)))
    if gif and q_keep:
        write_gif(GIF if mode == 'walk' else os.path.join(OUT, f'{tag}.gif'),
                  np.array(q_keep), np.array(t_keep), m, fell)
        res['gif'] = GIF if mode == 'walk' else os.path.join(OUT, f'{tag}.gif')
    json.dump(res, open(os.path.join(OUT, f'{tag}.json'), 'w'), indent=1)
    return res


def write_gif(path, Q, times, m, fell):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.animation import PillowWriter
    d = mujoco.MjData(m)
    # downsample to ~10 fps
    if len(Q) > 2:
        dt = np.median(np.diff(times))
        step = max(1, int(round(0.10 / max(dt, 1e-3))))
    else:
        step = 1
    idx = list(range(0, len(Q), step))
    if idx[-1] != len(Q) - 1:
        idx.append(len(Q) - 1)
    chains = [
        ['pelvis', 'torso', 'head'],
        ['torso', 'L_shoulderP', 'L_upper_arm', 'L_forearm', 'L_hand'],
        ['torso', 'R_shoulderP', 'R_upper_arm', 'R_forearm', 'R_hand'],
        ['pelvis', 'L_hipY', 'L_thigh', 'L_shank', 'L_foot'],
        ['pelvis', 'R_hipY', 'R_thigh', 'R_shank', 'R_foot'],
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    writer = PillowWriter(fps=10)
    with writer.saving(fig, path, dpi=80):
        for i in idx:
            q = Q[i]
            d.qpos[:] = q
            mujoco.mj_forward(m, d)
            ax.clear()
            x0 = q[0]
            for c in chains:
                P = np.array([d.xpos[m.body(b).id] for b in c])
                col = 'C0' if 'L_' in c[-1] else ('C3' if 'R_' in c[-1] else 'k')
                ax.plot(P[:, 0] - x0, P[:, 2], '-o', color=col, ms=2.5, lw=1.6)
            for s, col in (('l', 'C0'), ('r', 'C3')):
                g = m.geom(f'{s}_foot').id
                cpos = d.geom_xpos[g]
                R = d.geom_xmat[g].reshape(3, 3)
                hx = m.geom_size[g][0]
                a = cpos - R[:, 0] * hx
                b = cpos + R[:, 0] * hx
                ax.plot([a[0] - x0, b[0] - x0], [a[2], b[2]], color=col, lw=3)
            ax.axhline(0, color='0.5', lw=0.8)
            ax.set_xlim(-0.7, 0.9)
            ax.set_ylim(-0.05, 1.85)
            ax.set_aspect('equal')
            ax.set_xlabel('x relative (m)')
            ax.set_ylabel('z (m)')
            mark = '  FELL' if fell is not None and times[i] >= fell - 1e-6 else ''
            ax.set_title(f't={times[i]:.2f}s   x={q[0]:.2f} m{mark}', fontsize=10)
            writer.grab_frame()
    plt.close(fig)
    print('gif', path, flush=True)


def write_report(path, runs):
    lines = []
    lines.append('# WBC walk 1.2 m/s — forward-sim results')
    lines.append('')
    lines.append('Controller: `modules/legs/wbc/`. Whole-body QP at 1 kHz. Decision variables are')
    lines.append('joint acceleration and a 6-D wrench on each foot. Hard constraints are the floating-base')
    lines.append('dynamics, R1.2 torque limits, the gait-library wrench cone (μ = 0.8, CoP inside the sole,')
    lines.append('|Mz| ≤ 0.05 Fz), and the avail-ω joint speed limits from `results/r2/requirements.md`.')
    lines.append('The cost tracks the planned inverse-dynamics torque plus joint PD on a looped 1 s cruise')
    lines.append('slice. A 100 Hz LIPM correction shifts swing-foot lateral position (step width) and yaw.')
    lines.append('Playback timing stays on the plan clock. Toe-roll timing is the plan CoP and ankle trajectory.')
    lines.append('')
    lines.append('CoP margin is the clearance from the measured contact CoP to the nearest sole edge.')
    lines.append('The minimum over the run is the number below (negative means the CoP left the sole).')
    lines.append('Speed is pelvis x divided by time, the same definition as `fsim.py`.')
    lines.append('')
    for r in runs:
        title = r['mode']
        lines.append(f'## {title}')
        lines.append('')
        fell = 'none (finished)' if r['fell_at_s'] is None else f"{r['fell_at_s']} s"
        lines.append(f"- Fall time: {fell}")
        lines.append(f"- Sim time: {r['sim_time_s']} s")
        lines.append(f"- Mean speed (pelvis x / t): {r['mean_speed_pelvis_mps']} m/s")
        lines.append(f"- Mean COM vx over the second half: {r['mean_speed_com_vx_mps']} m/s")
        lines.append(f"- Touchdowns: {r['touchdowns']}")
        lines.append(f"- Minimum CoP margin: {r['cop_margin_min_mm']} mm")
        lines.append(f"- Peak CoP distance from sole center: {r['cop_offset_from_sole_center_peak_mm']} mm")
        if r.get('push_applied'):
            lines.append(f"- Push: {r['push_impulse_Ns']} N·s at t={r['push_time_s']} s "
                         f"(swing foot {r['push_swing_foot']}, 300 N for 0.2 s along +Y on the torso)")
        lines.append(f"- QP solves ok/fail: {r['qp_ok']} / {r['qp_fail']}")
        lines.append(f"- Wall time: {r['wall_s']} s")
        lines.append('')
        lines.append('| joint | peak Nm | RMS Nm | R1.2 avail Nm | peak/avail | saturated % |')
        lines.append('|---|---:|---:|---:|---:|---:|')
        for j in r['joints']:
            lines.append(f"| {j['joint']} | {j['peak_Nm']} | {j['rms_Nm']} | {j['avail_Nm']} | "
                         f"{j['peak_over_avail']} | {j['saturated_pct']} |")
        lines.append('')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('report', path)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='walk', choices=['stand', 'walk', 'push', 'carry'])
    ap.add_argument('--seconds', type=float, default=20)
    ap.add_argument('--cruise', type=float, default=1.20)
    ap.add_argument('--gif', action='store_true')
    ap.add_argument('--dt', type=float, default=0.001)
    a = ap.parse_args()
    run(mode=a.mode, seconds=a.seconds, cruise=a.cruise, dt=a.dt,
        push=(a.mode == 'push'), carry=(a.mode == 'carry'), gif=a.gif)
