"""R-127: r15 roll sweep vs Torso real cover (modules/torso/cad/torso_cover.json params, b697350; robot frame = torso body,
origin waist centre). Analytic: rounded box (|Z edges R25) x -110..110, y +-170, z 0..470 + sternum bulge (110 sq, to x 147),
shoulder openings dia D on the side walls at z 380. Clearance = distance to shell material (rim distance inside the opening).
Bodies: Arms r15 carrier_w2 + pad_envelope_w2 + housing_7013_coaxX (Arms FK as r15_cover_clash.py)."""
import trimesh, numpy as np, mujoco, json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, '../../../arms/cad/r15')
P = json.load(open(os.path.join(H, '../../../torso/cad/torso_cover.json')))["params"]
m = mujoco.MjModel.from_xml_path(os.path.join(H, '../../../../sim/v3/humanoid_v3.xml')); d = mujoco.MjData(m)
J = lambda n: m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)]
B = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
pts = {f: trimesh.load(os.path.join(A, f+'.stl')).sample(4000) for f in ('carrier_w2', 'pad_envelope_w2', 'housing_7013_coaxX')}
Rx = lambda a: np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
def sd_rbox(L, lo, hi, r):
    c = (lo+hi)/2; h = (hi-lo)/2; q = np.abs(L-c)-h
    qx, qy = q[:, 0]+r, q[:, 1]+r   # vertical-edge fillet r
    dxy = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
    return np.maximum(dxy, q[:, 2]) if True else None
def gap(L, D):
    s = sd_rbox(L, np.array([P["x_back"], -P["half_w"], P["z_bot"]]), np.array([P["x_front"], P["half_w"], P["z_top"]]), P["fillet"])
    zc, sz = P["sternum_c"][0], P["sternum_size"]
    sb = sd_rbox(L, np.array([P["x_front"]-1, -sz/2, zc-sz/2]), np.array([P["x_front"]+P["sternum_proud"], sz/2, zc+sz/2]), 0)
    s = np.minimum(s, sb)
    r = np.hypot(L[:, 0], L[:, 2]-P["shoulder_z"]); R = D/2
    rim = np.hypot(np.maximum(R-r, 0), np.maximum(np.abs(L[:, 1])-P["half_w"], 0))  # dist to rim circle edge when within hole
    near_wall = np.abs(L[:, 1]) > P["half_w"]-40
    return np.where((r < R) & near_wall, np.where(s < 0, R-r, rim), s)
def ev(sp, sr, D):
    mujoco.mj_resetData(m, d); d.qpos[2] = 1.16; d.qpos[J('l_shoulder_pitch')] = np.radians(sp); d.qpos[J('l_shoulder_roll')] = np.radians(sr); mujoco.mj_forward(m, d)
    Rs = d.xmat[B('L_shoulderP')].reshape(3, 3); o = (d.xpos[B('L_shoulderP')] + Rs@np.array([0, .112, -.04]))*1000
    Rt, ot = d.xmat[B('torso')].reshape(3, 3), d.xpos[B('torso')]*1000
    return {f: float(gap(((Rs@Rx(np.radians(sr))@p.T).T+o-ot)@Rt, D).min()) for f, p in pts.items()}
def sweep(D):
    res = {}
    for sp in (-150, -90, -30, 0, 5, 30):
        f0 = f3 = None; wmin = {}
        for sr in range(0, 181):
            r = ev(sp, sr, D); g = min(r.values())
            for k, v in r.items(): wmin[k] = min(wmin.get(k, 1e9), v)
            if f3 is None and g < 3: f3 = (sr, min(r, key=r.get))
            if f0 is None and g < 0: f0 = (sr, min(r, key=r.get))
        res[str(sp)] = dict(first_lt3mm=f3, first_contact=f0, min_gap_by_body=dict((k, round(v, 1)) for k, v in wmin.items()))
    return res
# shoulder centre in torso frame at rest
mujoco.mj_resetData(m, d); d.qpos[2] = 1.16; mujoco.mj_forward(m, d)
Rt, ot = d.xmat[B('torso')].reshape(3, 3), d.xpos[B('torso')]*1000
sc = ((d.xpos[B('L_shoulderP')]*1000 + d.xmat[B('L_shoulderP')].reshape(3, 3)@np.array([0, 112, -40]))-ot)@Rt
out = {"torso_params": P, "roll_axis_centre_torso_frame_mm": np.round(sc, 1).tolist(), "sweeps": {}}
out["sweeps"]["torso_as_given_D130"] = sweep(130)
P.update(z_bot=50, z_top=310, shoulder_z=220)   # ID-corrected: sim/site torso height, opening on the pitch axis (z 220)
out["sweeps"]["ID_corrected_z50_310_open_z220_D110"] = sweep(110)
out["ID_corrected_params"] = dict(z_bot=50, z_top=310, shoulder_z=220, shoulder_open_dia=110)
json.dump(out, open(os.path.join(H, 'r127_roll_sweep.json'), 'w'), indent=1); print(json.dumps({k: v["0"] for k, v in out["sweeps"].items()}))
