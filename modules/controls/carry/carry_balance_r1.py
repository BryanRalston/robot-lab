"""P-042 carry balance re-check (RL Controls, static). Light: MuJoCo kinematics only.
Model: sim/v3/humanoid_v3.xml (arm_inertials_r3 applied), non-payload mass scaled to 65 kg as gait_lib LEGS_MASS=65.
Payload 20 kg rigid in the torso frame (origin = waist_pitch axis), as gait_lib._load. Feet flat, legs straight.
Cases: Legs' assumption (0.25, 0, 0.10) vs P-042 hand position (0.32, 0, 0.415), with waist_pitch 0 / -0.25 rad."""
import os, json, numpy as np, mujoco
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
XML = os.path.join(R, 'sim/v3/humanoid_v3.xml'); G = 9.81
HEEL, TOE = -0.060, 0.180   # gait_lib sole extents from the ankle axis
ANK_PEAK = 323.8            # ankle_pitch T_out per leg (sizing.json)
def model(pos):
    x = open(XML).read(); tag = '<geom name="torso" type="box"'
    x = x.replace(tag, f'<body name="payload" pos="{pos[0]} {pos[1]} {pos[2]}"><inertial pos="0 0 0" mass="20" diaginertia="0.2 0.15 0.2"/></body>' + tag, 1)
    m = mujoco.MjModel.from_xml_string(x)
    base = sum(m.body_mass[i] for i in range(m.nbody) if m.body(i).name != 'payload'); k = 65.0 / base
    for i in range(m.nbody):
        if m.body(i).name != 'payload': m.body_mass[i] *= k; m.body_inertia[i] *= k
    return m, base
def check(pos, waist, arms):
    m, base = model(pos); d = mujoco.MjData(m)
    for j, v in dict(waist_pitch=waist, **arms).items():
        for pre in ('', 'l_', 'r_'):
            try: d.qpos[m.jnt_qposadr[m.joint(pre + j).id]] = v
            except KeyError: pass
    mujoco.mj_forward(m, d)
    com = d.subtree_com[0].copy(); ank = 0.5 * (d.xpos[m.body('L_foot').id] + d.xpos[m.body('R_foot').id])
    dx = float(com[0] - ank[0]); M = float(m.body_mass.sum())
    return dict(payload_pos=list(pos), waist_pitch=waist, arms=arms, sim_mass_unscaled=round(base, 3), total_kg=round(M, 2),
                com_x_from_ankle_m=round(dx, 4), toe_margin_mm=round((TOE - dx) * 1000, 1), heel_margin_mm=round((dx - HEEL) * 1000, 1),
                ankle_static_Nm_per_leg=round(M * G * dx / 2, 1), ankle_peak_ratio=round(ANK_PEAK / max(1e-6, abs(M * G * dx / 2)), 2))
P042 = dict(shoulder_pitch=np.deg2rad(-60), elbow=np.deg2rad(-110))
LEGS = dict(shoulder_pitch=-0.60, elbow=-1.20)   # make_model CARRY_OFFSET
out = [check((0.25, 0, 0.10), w, LEGS) for w in (0.0, -0.25)] + [check((0.32, 0, 0.415), w, P042) for w in (0.0, -0.25)]
for o in out: print(o)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'carry_balance_r1.json'), 'w'), indent=1, default=float)
