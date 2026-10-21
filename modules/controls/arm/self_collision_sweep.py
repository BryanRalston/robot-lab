"""Closed-loop kinematic re-sweep of the arm self-collision supervisor (T&R 925d72e thresholds). Light CPU:
forward kinematics only, 1 kHz, joint positions integrated from supervised velocities. Usage: python self_collision_sweep.py [y_out]"""
import json, sys, numpy as np, mujoco
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import self_collision as S
D = np.pi / 180

def setup(y_out):
    cfg = S.load_cfg(); cfg['knee_shroud']['y_out'] = y_out
    m, d = S.build_model(cfg); return m, d, cfg

def jadr(m, n): return m.jnt_qposadr[m.joint(n).id]
def dadr(m, n): return m.jnt_dofadr[m.joint(n).id]

def run(m, d, cfg, mode, arm_tgt, leg_tgt, side='l', T=1.6, v_arm=3.0, v_leg=2.0, walk_osc=None, arm0=None, sup_on=True):
    """Command arm joints toward arm_tgt (deg) and legs toward leg_tgt (deg) (or a walk hip oscillation)."""
    sup = S.Supervisor(m, d, cfg); dt = 1e-3
    d.qpos[:] = 0; d.qpos[2] = 1.16; d.qpos[3] = 1
    for k, v in (arm0 or {}).items(): d.qpos[jadr(m, k)] = v * D
    mins = {}; plume_in = {'l': 0.0, 'r': 0.0}; maxcur = 0.0; maxwin = 0.0
    rng_lo, rng_hi = m.jnt_range[:, 0], m.jnt_range[:, 1]
    for i in range(int(T / dt)):
        t = i * dt; qd = np.zeros(m.nv)
        for k, v in arm_tgt.items():
            e = v * D - d.qpos[jadr(m, k)]; qd[dadr(m, k)] = np.clip(e / 0.05, -v_arm, v_arm)
        if walk_osc:
            a, b, f = walk_osc; hp = (a + b) / 2 + (b - a) / 2 * np.sin(2 * np.pi * f * t)
            for sd in 'lr':
                ph = 0 if sd == 'l' else np.pi
                hp = (a + b) / 2 + (b - a) / 2 * np.sin(2 * np.pi * f * t + ph)
                qd[dadr(m, f'{sd}_hip_pitch')] = (hp * D - d.qpos[jadr(m, f'{sd}_hip_pitch')]) / dt
        else:
            for k, v in leg_tgt.items():
                e = v * D - d.qpos[jadr(m, k)]; qd[dadr(m, k)] = np.clip(e / 0.05, -v_leg, v_leg)
        qs = sup.filter(qd, mode, bypass=not sup_on)
        for p, dist, _ in sup.last:
            mins[p.kind] = min(mins.get(p.kind, 9), dist)
            if 'plate' in p.name or 'straps' in p.name: mins['plate'] = min(mins.get('plate', 9), dist)
            if p.kind == 'shroud': mins['shroud_' + p.name] = min(mins.get('shroud_' + p.name, 9), dist)
        for sd in 'lr':
            tm = sup.timers[sd]
            if tm.cur > 0: plume_in[sd] += dt
            maxcur = max(maxcur, tm.cur); maxwin = max(maxwin, tm.window_used)
        # integrate (hinge joints only; base fixed), clip to joint ranges
        for j in range(1, m.njnt):
            a = m.jnt_qposadr[j]; dv = m.jnt_dofadr[j]
            d.qpos[a] = np.clip(d.qpos[a] + qs[dv] * dt, m.jnt_range[j, 0], m.jnt_range[j, 1])  # jnt_range is rad
    trips = [e for e in sup.events if e[1] == 'trip']
    return dict(min_shroud_mm=round(1000 * mins.get('shroud', 9), 1), min_chest_mm=round(1000 * mins.get('chest', 9), 1),
                min_plume_mm=round(1000 * mins.get('plume', 9), 1), min_plate_mm=round(1000 * mins.get('plate', 9), 1), plume_s=round(sum(plume_in.values()), 3),
                max_transit_s=round(maxcur, 3), max_window_frac=round(maxwin, 3), trip_cycles=len(trips))

def arm_dict(side, a): return {f'{side}_{j}': v for j, v in zip(S.ARM_J, a)}

def main():
    y_out = float(sys.argv[1]) if len(sys.argv) > 1 else 0.150
    m, d, cfg = setup(y_out); rng = np.random.default_rng(0); out = {'y_out': y_out, 'cases': []}
    # worst poses from ARM_KNEE_SHROUD_CLEARANCE.md (6d4c8fb) + adduction/wrist-yaw singles
    worst = [
        ('full-range worst', 'stand', [-30.6, -14.0, -119.6, -12.6, 2.5, -25.9, -16.9], {'l_hip_yaw': 6.2, 'l_hip_roll': -11.4, 'l_hip_pitch': -64.8, 'l_knee': 13.9, 'waist_yaw': 52.5, 'waist_pitch': 21.4}),
        ('walk-residual worst', 'walk', [12.3, -13.6, 9.6, -8.3, -9.6, 1.4, -9.0], {'l_hip_yaw': 24.0, 'l_hip_roll': -1.4, 'l_hip_pitch': -60.0, 'waist_yaw': -15}),
        ('adduction -14.3 stand', 'stand', [0, -14.3, 0, 0, 0, 0, 0], {}),
        ('adduction -15 + hip flex 50', 'walk', [9, -15, -14.3, -14.3, -14.3, -14.2, -14.3], {'l_hip_pitch': -50.3}),
        ('hanging + crouch hip -105', 'crouch', [0] * 7, {'l_hip_pitch': -105, 'l_knee': 135}),
        ('wrist-flexed chest fold', 'stand', [-60, -15, -100, -130, 0, 70, 0], {}),
        ('hands together at chest', 'carry', [-60, -15, -60, -100, 0, 0, 0], {}),
        ('roll 127 elbow fold (Arms 0a8a3cc)', 'stand', [30, 127, 60, -140, 0, 0, 0], {}),
        ('both-leg yaw -35 (Legs L77 knee plate)', 'stand', [0] * 7, {'l_hip_yaw': -35, 'r_hip_yaw': 35}),
        ('both-leg yaw -35 + adduction -15', 'walk', [0, -15, 0, 0, 0, 0, -14.3], {'l_hip_yaw': -35, 'r_hip_yaw': 35}),
    ]
    for nm, mode, a, l in worst:
        for on in (False, True):
            r = run(m, d, cfg, mode, arm_dict('l', a), l, sup_on=on); r.update(case=nm, mode=mode, supervisor=on); out['cases'].append(r)
    # random closed-loop targets
    ar = {j: tuple(m.jnt_range[m.joint('l_' + j).id] / D) for j in S.ARM_J}; ar['shoulder_roll'] = (-15, 127)
    groups = {'walk': (dict(l_hip_pitch=(-60, 20), l_hip_roll=(-5, 5), l_hip_yaw=(-10, 10), waist_yaw=(-15, 15), waist_pitch=(-15, 15)), 14.3, [0] * 7),
              'carry': (dict(l_hip_pitch=(-60, 20), waist_pitch=(-15, 0)), 14.3, [-60, 0, 0, -110, 0, 0, 0]),
              'stand': (dict(l_hip_pitch=(-20, 0), l_hip_roll=(-12, 15), l_hip_yaw=(-35, 45), waist_yaw=(-90, 90), waist_pitch=(-30, 60)), None, None),
              'crouch': (dict(l_hip_pitch=(-105, 0), l_knee=(0, 135), waist_pitch=(0, 60)), None, None)}
    for mode, (lr, res, base) in groups.items():
        for on in (False, True):
          rng = np.random.default_rng(7); agg = []
          for k in range(12):
            if res is None: a = [rng.uniform(*ar[j]) for j in S.ARM_J]
            else: a = [float(np.clip(b + rng.uniform(-res, res), *ar[j])) for b, j in zip(base, S.ARM_J)]
            l = {kk: rng.uniform(*v) for kk, v in lr.items()}
            agg.append(run(m, d, cfg, mode, arm_dict('l', a), l, T=1.0, arm0=arm_dict('l', base) if base else None, sup_on=on))
          out['cases'].append(dict(case=f'{mode} random x12', mode=mode, supervisor=on,
                                 min_shroud_mm=min(x['min_shroud_mm'] for x in agg), min_chest_mm=min(x['min_chest_mm'] for x in agg),
                                 min_plume_mm=min(x['min_plume_mm'] for x in agg), plume_s=round(sum(x['plume_s'] for x in agg), 3),
                                 trip_cycles=sum(x['trip_cycles'] for x in agg)))
    # walk swing 1 Hz hip -60..+20 for 12 s with the arm commanded inward/aft into the plume
    for on in (False, True):
        r = run(m, d, cfg, 'walk', arm_dict('l', [14.3, -14.3, 0, 0, 0, 0, -14.3]), {}, T=12.0, walk_osc=(-60, 20, 1.0), sup_on=on)
        r.update(case='walk swing 12 s (hip -60..+20 at 1 Hz), arm residual pushed aft/inward', mode='walk', supervisor=on); out['cases'].append(r)
    # fall mode poses
    sup = S.Supervisor(m, d, cfg); fall = []
    legs = {'stand': {}, 'crouch hip-105': {'l_hip_pitch': -105 * D, 'l_knee': 135 * D},
            'POSE_PRONE': {'l_hip_pitch': 0.0, 'l_knee': 0.3, 'waist_pitch': 0.0}, 'KNEEL_W1': {'l_hip_pitch': -1.45, 'l_knee': 1.7, 'waist_pitch': 0.8},
            'side-fall hip roll+15': {'l_hip_roll': 15 * D}}
    for pn, a in (('tuck B', [5, 0, 0, 0, 0, 0, 0]), ('LB fallback', [30, -15, 30, -75, 0, 0, 0])):
        for ln, lq in legs.items():
            d.qpos[:] = 0; d.qpos[2] = 1.16; d.qpos[3] = 1
            for k, v in lq.items(): d.qpos[jadr(m, k)] = v
            ok, (slack, nm) = sup.fall_pose_clear({k: v * D for k, v in arm_dict('l', a).items()}, 'crouch')
            fall.append(dict(pose=pn, legs=ln, clear=bool(ok), worst=nm, slack_vs_trip10_mm=round(1000 * slack, 1)))
    out['fall'] = fall
    Path(__file__).with_name(f'self_collision_sweep_y{int(round(y_out * 1000))}.json').write_text(json.dumps(out, indent=1))
    for c in out['cases']: print(c)
    for f in fall: print(f)

if __name__ == '__main__':
    main()
