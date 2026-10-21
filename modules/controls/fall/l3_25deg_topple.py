"""T&R 3ab7dd6 L3 25-deg topple, Controls sim. 68 kg prone_data.Sim (sim/v3 + pads). chest_pad MuJoCo contact disabled and
replaced by T&R plateau: 9.21 kN constant normal (world +z) while crushing over 81.2 mm, then rigid wall 5.3 MN/m; crush state is
non-recovering (force only while at max crush). Model has NO shoulder pad geom -> shoulder pad not modelled. MO=0 + D94 friction."""
import os, sys, json, math
os.environ.setdefault('MUJOCO_GL', 'disable')
import numpy as np, mujoco
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'limits'))
import prone_data as P
from drive_thermal_derate import friction_hold
FP, ST, KB = 9210.0, 0.0812, 5.3e6
def run(seed):
    r = np.random.default_rng(seed); piv = 'knee' if seed % 2 else 'toe'
    fr = float(r.uniform(0.5, 1.0)); s = P.Sim(68.0, friction=fr); m, d = s.m, s.d
    pose = dict(P.POSE_KNEEL) if piv == 'knee' else dict(hip_pitch=0.0, knee=0.0, ankle_pitch=0.0)
    pose['shoulder_pitch'] = float(r.uniform(-0.8, 0.4)); lean = float(r.uniform(0.08, 0.3)); yaw = float(r.uniform(-0.3, 0.3))
    s.place(pose, lean); qw = d.qpos[3:7].copy(); qy = np.array([math.cos(yaw/2), 0, 0, math.sin(yaw/2)]); out = np.zeros(4)
    mujoco.mju_mulQuat(out, qy, qw); d.qpos[3:7] = out; mujoco.mj_forward(m, d); q = s.target(pose)
    for _ in range(30): d.ctrl[:] = s.pd(q); mujoco.mj_step(m, d)
    for i, n in enumerate(s.names): m.dof_frictionloss[s.vadr[i]] = friction_hold(n)
    cp = m.geom('chest_pad').id; m.geom_contype[cp] = 0; m.geom_conaffinity[cp] = 0; tb = m.geom_bodyid[cp]
    feet = {m.body('L_foot').id, m.body('R_foot').id}; kn = {m.body('L_shank').id, m.body('R_shank').id}
    p0 = {b: d.xpos[b][:2].copy() for b in feet | kn}
    cmax = 0.0; E = 0.0; first = None; tfirst = None; tchest = None; vn = None; att = None; hist = []; bott = False; F = 0.0; dt = m.opt.timestep
    for k in range(int(2.5 / dt)):
        d.ctrl[:] = 0; t = k * dt
        R = d.geom_xmat[cp].reshape(3, 3); hs = m.geom_size[cp]
        pts = [d.geom_xpos[cp] + R @ np.array([hs[0], sy*hs[1], sz*hs[2]]) for sy in (-1, 1) for sz in (-1, 1)]
        pf = min(pts, key=lambda p: p[2]); c = max(0.0, -pf[2])
        v6 = np.zeros(6); jac = np.zeros((3, m.nv)); mujoco.mj_jac(m, d, jac, None, pf, tb); v = jac @ d.qvel
        d.xfrc_applied[tb] = 0
        if c > 0:
            if tchest is None:
                tchest = t; vn = round(float(-v[2]), 2); z = R[:, 0]
                att = dict(pitch_deg=round(math.degrees(math.asin(np.clip(-z[2], -1, 1))), 1), roll_deg=round(math.degrees(math.asin(np.clip(z[1], -1, 1))), 1), com_z=round(float(d.subtree_com[1][2]), 3))
                if first is None: first, tfirst = 'chest_pad', t
            F = 0.0
            if c >= cmax - 1e-4 and v[2] < 0: F = FP
            if c > ST: F = FP + KB * (c - ST); bott = True
            cmax = max(cmax, c); E += F * max(0.0, -v[2]) * dt
            fv = np.array([0, 0, F]); tq = np.cross(pf - d.xipos[tb], fv); d.xfrc_applied[tb, :3] = fv; d.xfrc_applied[tb, 3:] = tq
        if first is None:
            for ci in range(d.ncon):
                g = d.contact[ci]; bb = {m.geom_bodyid[g.geom1], m.geom_bodyid[g.geom2]}
                if 0 in bb and len(bb) == 2:
                    b = (bb - {0}).pop()
                    if b not in feet and not (piv == 'knee' and b in kn): first, tfirst = m.body(b).name, t; break
        if k % 10 == 0 and tchest is not None and t - tchest < 0.3: hist.append([round(t - tchest, 3), round(c * 1000, 1)])
        mujoco.mj_step(m, d)
    slide = {m.body(b).name: round(float(np.linalg.norm(d.xpos[b][:2] - p0[b])) * 1000) for b in p0}
    gap = None if tchest is None else round((tchest - tfirst) * 1000, 1)
    E15 = round(1.5 * E, 1); vlim = 4.24 if piv == 'toe' else 4.67
    c1 = tchest is None or (first != 'chest_pad' and gap is not None and gap >= -10) or (gap is not None and gap > 10)
    c1 = bool((first != 'chest_pad' or (gap is not None and gap <= 10)) and E15 <= 680)
    return dict(seed=seed, pivot=piv, friction=round(fr, 2), lean=round(lean, 3), yaw=round(yaw, 3), shoulder_pitch=round(pose['shoulder_pitch'], 2),
                first_contact=first, gap_to_chest_ms=gap, chest_contact=tchest is not None, chest_E_J=round(E, 1), chest_E_x1p5=E15, pad_vn=vn, at_contact=att,
                max_crush_mm=round(cmax * 1000, 1), bottomed=bott, slide_mm=slide, crush_hist=hist,
                C1=c1, C2=(vn is not None and vn <= vlim), C3=any(v > 20 for v in slide.values()))
rows = [run(i) for i in range(24)]
for x in rows: print({k: x[k] for k in x if k != 'crush_hist'}, flush=True)
json.dump(rows, open(os.path.join(H, 'l3_25deg_topple.json'), 'w'), indent=1)
