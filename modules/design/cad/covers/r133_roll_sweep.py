"""R-133 sweep: same method as r127 vs Torso cover 35eebd2 (z 50-310, taper 250@z50 -> 340@z220, 45 mm top-shoulder
chamfer, dia110 openings on the pitch axis z 220). Convex YZ profile extruded x -110..110 (corner fillets R20 ignored: conservative)."""
import trimesh, numpy as np, mujoco, json, os
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, '../../../arms/cad/r15')
P = json.load(open(os.path.join(H, '../../../torso/cad/torso_cover.json')))["params"]
m = mujoco.MjModel.from_xml_path(os.path.join(H, '../../../../sim/v3/humanoid_v3.xml')); d = mujoco.MjData(m)
J = lambda n: m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)]; B = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
pts = {f: trimesh.load(os.path.join(A, f+'.stl')).sample(4000) for f in ('carrier_w2', 'pad_envelope_w2', 'housing_7013_coaxX')}
Rx = lambda a: np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
hb, hs, c, zb, zs, zt = P["w_bot"]/2, P["w_shoulder"]/2, P["shoulder_chamfer"], P["z_bot"], P["z_shoulder"], P["z_top"]
poly = [(-hb, zb), (hb, zb), (hs, zs), (hs, zt-c), (hs-c, zt), (-hs+c, zt), (-hs, zt-c), (-hs, zs)]
E = []
for i in range(len(poly)):
    (y0, z0), (y1, z1) = poly[i], poly[(i+1) % len(poly)]; n = np.array([z1-z0, -(y1-y0)]); n /= np.linalg.norm(n); E.append((n, n@[y0, z0]))
CH = E[3][0]  # chamfer edge index 3 (hs,zt-c)->(hs-c,zt)
def sd(L):
    s = np.max([L[:, 1:]@n - k for n, k in E], 0); return np.maximum(s, np.abs(L[:, 0]) - 110)
def gap(L):
    s = sd(L); r = np.hypot(L[:, 0], L[:, 2]-zs); R = P["shoulder_open_dia"]/2
    near = (np.abs(L[:, 1]) > hs-40) & (np.abs(L[:, 2]-zs) < R)
    rim = np.hypot(np.maximum(R-r, 0), np.maximum(np.abs(L[:, 1])-hs, 0))
    g = np.where((r < R) & near, np.where(s < 0, R-r, rim), s)
    chamf = (L[:, 2] > zt-c-5) & (L[:, 1] > hs-c-5)
    return g, chamf
def ev(sp, sr):
    mujoco.mj_resetData(m, d); d.qpos[2] = 1.16; d.qpos[J('l_shoulder_pitch')] = np.radians(sp); d.qpos[J('l_shoulder_roll')] = np.radians(sr); mujoco.mj_forward(m, d)
    Rs = d.xmat[B('L_shoulderP')].reshape(3, 3); o = (d.xpos[B('L_shoulderP')] + Rs@np.array([0, .112, -.04]))*1000
    Rt, ot = d.xmat[B('torso')].reshape(3, 3), d.xpos[B('torso')]*1000; r, ch = {}, {}
    for f, p in pts.items():
        g, cm = gap(((Rs@Rx(np.radians(sr))@p.T).T + o - ot)@Rt); r[f] = float(g.min()); ch[f] = float(g[cm].min()) if cm.any() else None
    return r, ch
out = {"torso_params": P, "pitch_actuator_radial_clearance_mm": P["shoulder_open_dia"]/2 - 96/2, "sweeps": {}}
for sp in (-150, -90, -30, 0, 5, 30):
    f0 = f3 = None; wb = {}; wc = {}
    for sr in range(0, 181):
        r, ch = ev(sp, sr); g = min(r.values())
        for k in r:
            wb[k] = min(wb.get(k, 1e9), r[k])
            if ch[k] is not None and sr <= 127: wc[k] = min(wc.get(k, 1e9), ch[k])
        if f3 is None and g < 3: f3 = (sr, min(r, key=r.get))
        if f0 is None and g < 0: f0 = (sr, min(r, key=r.get))
    out["sweeps"][str(sp)] = dict(first_lt3mm=f3, first_contact=f0, min_gap_full_ROM={k: round(v, 1) for k, v in wb.items()},
                                  min_gap_to_chamfer_roll_le127={k: round(v, 1) for k, v in wc.items()})
json.dump(out, open(os.path.join(H, 'r133_roll_sweep.json'), 'w'), indent=1)
print(json.dumps({k: (v["first_lt3mm"], v["first_contact"], v["min_gap_to_chamfer_roll_le127"]) for k, v in out["sweeps"].items()}))
