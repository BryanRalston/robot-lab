"""ID P-023 rev 8 (df1e9e3) L<->R thigh-panel keep-out: controller-pose check + sampled leg-range sweep. FK only.
Panels = ID's convex-hull STL per thigh (conservative vs ID's point cloud: the hull fills the arc chord)."""
import json, sys, numpy as np, mujoco
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import self_collision as S
m, d = S.build_model(); ft = np.zeros(6); cfg = S.load_cfg(); TG, WN, TR = (v / 1000 for v in cfg['thigh_panels']['mm'])
def gap(q):
    d.qpos[:] = 0; d.qpos[2] = 1.16; d.qpos[3] = 1
    for k, v in q.items(): d.qpos[m.jnt_qposadr[m.joint(k).id]] = v
    mujoco.mj_kinematics(m, d)
    return 1000 * mujoco.mj_geomDistance(m, d, m.geom('ko_panel_l').id, m.geom('ko_panel_r').id, 0.3, ft)
def both(spec):
    q = {}
    for k, v in spec.items():
        if k in ('waist_pitch', 'waist_yaw'): q[k] = v; continue
        for sd in 'lr': q[f'{sd}_{k}'] = v
    return q
R = np.pi / 180
poses = {
    'stand': {}, 'safe-sit crouch (pelvis 0.844, ~hip -0.6/knee 1.2 [approx])': {'hip_pitch': -0.6, 'knee': 1.2, 'ankle_pitch': -0.6},
    'KNEEL_W1': {'hip_pitch': -1.45, 'knee': 1.70, 'ankle_pitch': -0.75, 'waist_pitch': 0.8},
    'KNEEL_POSE': {'hip_pitch': -0.6, 'knee': 1.9, 'ankle_pitch': 0.3, 'waist_pitch': 0.4},
    'POSE_KNEEL': {'hip_pitch': -0.3, 'knee': 1.6, 'ankle_pitch': 0.6, 'waist_pitch': 0.2},
    'chest-lower start POSE_HANDS': {'hip_pitch': -0.9, 'knee': 1.5, 'ankle_pitch': 0.6, 'waist_pitch': 0.4},
    'chest-lower end POSE_PRONE': {'hip_pitch': 0.0, 'knee': 0.3, 'ankle_pitch': 0.5},
    'kneel_hold A upright': {'hip_pitch': 0.0, 'knee': 1.57, 'ankle_pitch': 0.70},
    'kneel_hold B sit-back': {'hip_pitch': -0.9, 'knee': 2.36, 'ankle_pitch': 0.70, 'waist_pitch': 0.3},
    'kneel_hold C hands-knees': {'hip_pitch': -1.45, 'knee': 1.57, 'ankle_pitch': 0.70},
    'kneel_hold D forearms-knees': {'hip_pitch': -1.4, 'knee': 1.8, 'ankle_pitch': 0.70, 'waist_pitch': 0.3},
    'sit 0.45 m seat (hip -1.57/knee 1.57 [approx])': {'hip_pitch': -1.57, 'knee': 1.57},
    'fall tuck B (knee drop, hip -1.0/knee 1.6 [approx])': {'hip_pitch': -1.0, 'knee': 1.6},
    'diagonal tuck B + waist yaw 45': {'hip_pitch': -1.0, 'knee': 1.6, 'waist_yaw': 45 * R},
    'diagonal tuck B + waist yaw -45': {'hip_pitch': -1.0, 'knee': 1.6, 'waist_yaw': -45 * R},
    'deep crouch hip -105 (sim limit)': {'hip_pitch': -105 * R, 'knee': 135 * R},
}
out = dict(thresholds_mm=[TG * 1000, WN * 1000, TR * 1000], poses=[], sweeps={})
for nm, sp in poses.items():
    q = both(sp); g = gap(q); ok, _, why = S.bilateral_soft_limit(q, cfg)
    out['poses'].append(dict(pose=nm, gap_mm=round(min(g, 300), 1), ge_target=bool(g >= TG * 1000), soft_limit_ok=ok))
rng = np.random.default_rng(0)
def sweep(tag, n, gen):
    worst = (1e9, None); below = 0; rule_miss = 0; rule_block_clear = 0
    for _ in range(n):
        q = gen(); g = gap(q); ok, _, _ = S.bilateral_soft_limit(q, cfg)
        below += g < TG * 1000; rule_miss += (g < TR * 1000) and ok; rule_block_clear += (not ok) and g >= TG * 1000
        if g < worst[0]: worst = (g, {k: round(np.degrees(v), 1) for k, v in q.items()})
    out['sweeps'][tag] = dict(n=n, min_mm=round(worst[0], 1), worst=worst[1], frac_below_target=round(below / n, 4),
                              trip_but_rule_ok=rule_miss, rule_blocks_but_clear=rule_block_clear)
U = lambda a, b: rng.uniform(a, b) * R
sim = lambda j, sd: tuple(m.jnt_range[m.joint(f'{sd}_{j}').id])
def gen_sim():
    return {f'{sd}_{j}': rng.uniform(*sim(j, sd)) for sd in 'lr' for j in ('hip_yaw', 'hip_roll', 'hip_pitch')} | \
           {f'{sd}_knee': U(0, 135) for sd in 'lr'}
def gen_walk():  # [ASSUMED] walk/carry: hip pitch -60..+20 per leg, roll +/-5, yaw +/-10, independent legs
    return {f'{sd}_hip_pitch': U(-60, 20) for sd in 'lr'} | {f'{sd}_hip_roll': U(-5, 5) for sd in 'lr'} | \
           {f'{sd}_hip_yaw': U(-10, 10) for sd in 'lr'} | {f'{sd}_knee': U(0, 90) for sd in 'lr'}
def gen_id():  # ID's Legs range, mirrored: roll inward to 20, toe-out to 45 both
    p, r, y = U(-107.3, 40), U(-20, 45), U(-35, 45)
    return {'l_hip_pitch': p, 'r_hip_pitch': p, 'l_hip_roll': r, 'r_hip_roll': -r, 'l_hip_yaw': y, 'r_hip_yaw': -y}
sweep('sim_v3_joint_ranges_independent', 20000, gen_sim)
sweep('walk_carry_assumed', 10000, gen_walk)
sweep('ID_legs_ranges_mirrored', 10000, gen_id)
out['note'] = ('sim/v3 limits: l_hip_roll -12..15, r_hip_roll -15..12 (inward 12 max each); hip yaw -35..45 on BOTH sides (not '
               'mirrored), so right toe-out is limited to 35 in sim. ID used mirrored Legs ranges (inward 20, toe-out 45).')
Path(__file__).with_name('bilateral_panel_check.json').write_text(json.dumps(out, indent=1))
for p in out['poses']: print(p)
for k, v in out['sweeps'].items(): print(k, v)
