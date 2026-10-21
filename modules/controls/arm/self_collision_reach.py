"""Open-loop full-range sweep (rev 6b geometry) + reach cost of the chest keep-out vs the R18 joint-coupled yaw band
+ effect of an inward shoulder-roll limit of 0 deg. FK only. Writes self_collision_reach.json."""
import json, sys, numpy as np, mujoco
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import self_collision as S
D = np.pi / 180
m, d = S.build_model(); ft = np.zeros(6)
G = {k: m.geom(k).id for k in ('l_hand', 'l_forearm', 'ko_shroud_l', 'ko_plume_l', 'ko_chest', 'torso')}
def setq(q):
    d.qpos[:] = 0; d.qpos[2] = 1.16; d.qpos[3] = 1
    for k, v in q.items(): d.qpos[m.jnt_qposadr[m.joint(k).id]] = v * D
    mujoco.mj_kinematics(m, d)
def dist(a, b): return mujoco.mj_geomDistance(m, d, G[a], G[b], 1.0, ft)
ARM = ['l_' + j for j in S.ARM_J]
LEG = ['l_hip_yaw', 'l_hip_roll', 'l_hip_pitch', 'l_knee', 'waist_yaw', 'waist_pitch']
rng = np.random.default_rng(0); out = {}
def sweep(arm_rng, leg_rng, n, tag):
    best = (9, None); below = 0
    for _ in range(n):
        q = {k: rng.uniform(*arm_rng[k]) for k in ARM}; q.update({k: rng.uniform(*leg_rng[k]) for k in LEG})
        setq(q); dd = min(dist('l_hand', 'ko_shroud_l'), dist('l_forearm', 'ko_shroud_l'))
        below += int(dd < 0.015)
        if dd < best[0]: best = (dd, {k: round(v, 1) for k, v in q.items()})
    out[tag] = dict(min_mm=round(1000 * best[0], 1), frac_below_15mm=round(below / n, 4), worst=best[1], n=n)
full_arm = {k: tuple(m.jnt_range[m.joint(k).id] / D) for k in ARM}; full_arm['l_shoulder_roll'] = (-15, 127)
full_leg = {k: tuple(m.jnt_range[m.joint(k).id] / D) for k in LEG}
walk_arm = {k: (max(full_arm[k][0], -14.3), min(full_arm[k][1], 14.3)) for k in ARM}
walk_leg = dict(l_hip_yaw=(-10, 10), l_hip_roll=(-5, 5), l_hip_pitch=(-60, 20), l_knee=(0, 90), waist_yaw=(-15, 15), waist_pitch=(-15, 15))
sweep(full_arm, full_leg, 20000, 'open_loop_full_range')
sweep(walk_arm, walk_leg, 10000, 'open_loop_walk_residual')
for tag, ar in (('walk_residual_roll_ge0', dict(walk_arm, l_shoulder_roll=(0, 14.3))),):
    sweep(ar, walk_leg, 10000, tag)
# reach cost: left arm grid, standing, wrists 0
cnt = dict(total=0, torso_self=0, cross=0, sup_block=0, sup_block_cross=0, r18_block=0, r18_block_cross=0, sup_only=0, r18_only=0)
for sp in range(-120, 61, 10):
    for sr in range(-15, 31, 5):
        for sy in range(-150, 151, 15):
            for el in range(-140, 1, 10):
                setq({'l_shoulder_pitch': sp, 'l_shoulder_roll': sr, 'l_shoulder_yaw': sy, 'l_elbow': el})
                if min(dist('l_hand', 'torso'), dist('l_forearm', 'torso')) < 0: cnt['torso_self'] += 1; continue
                cnt['total'] += 1
                cross = d.geom_xpos[G['l_hand']][1] < 0.0
                sup = min(dist('l_hand', 'ko_chest'), dist('l_forearm', 'ko_chest')) < 0
                band = {-140: -45, -130: -45, -120: -45, -110: -60, -100: -75, -90: -90}
                r18 = el <= -90 and -120 <= sp <= -10 and sy < band.get(el, -999) and sy >= -120
                cross=bool(cross); sup=bool(sup); r18=bool(r18); cnt['cross'] += cross; cnt['sup_block'] += sup; cnt['r18_block'] += r18
                cnt['sup_block_cross'] += sup and cross; cnt['r18_block_cross'] += r18 and cross
                cnt['sup_only'] += sup and not r18; cnt['r18_only'] += r18 and not sup
out['reach_cost'] = cnt
# roll >= 0 effect on named poses
out['roll_ge0_breaks'] = ['LB fallback +30/-15/+30/-75 (roll -15)', 'hands together at chest (-60,-15,-60,-100) R18',
                          'P-042 close carry (-25,-10,-40,-110) R18']
Path(__file__).with_name('self_collision_reach.json').write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
