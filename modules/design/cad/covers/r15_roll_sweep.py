"""ID r15 roll sweep (1 deg): Arms W2 carrier + pad envelope (modules/arms/cad/r15) vs torso cover.
Best real torso surface available = sim torso geom box 220x340x260 (humanoid_v3.xml) = site p009 (same dims; the glb
p009 is that box, open bottom). No finer torso cover CAD exists in design/, torso/ or site/. Analytic signed distance to the
geom box (outer CF skin). Same FK as Arms r15_cover_clash.py (L_shoulderP xform * Rx(roll), origin offset [0,.112,-.04])."""
import trimesh, numpy as np, mujoco, json, os
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, '../../../arms/cad/r15')
m = mujoco.MjModel.from_xml_path(os.path.join(H, '../../../../sim/v3/humanoid_v3.xml')); d = mujoco.MjData(m)
J = lambda n: m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)]
B = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n); G = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, 'torso')
src = {f: trimesh.load(os.path.join(A, f+'.stl')) for f in ('carrier_w2', 'pad_envelope_w2')}
pts = {f: s.sample(4000) for f, s in src.items()}
Rx = lambda a: np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
def ev(sp, sr):
    mujoco.mj_resetData(m, d); d.qpos[2] = 1.16; d.qpos[J('l_shoulder_pitch')] = np.radians(sp); d.qpos[J('l_shoulder_roll')] = np.radians(sr); mujoco.mj_forward(m, d)
    Rs = d.xmat[B('L_shoulderP')].reshape(3, 3); o = (d.xpos[B('L_shoulderP')] + Rs@np.array([0, .112, -.04]))*1000
    c, Rg, h = d.geom_xpos[G]*1000, d.geom_xmat[G].reshape(3, 3), m.geom_size[G]*1000
    r = {}
    for f, p in pts.items():
        P = (Rs@Rx(np.radians(sr))@p.T).T + o; L = (P-c)@Rg; q = np.abs(L)-h
        sd = np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(q.max(1), 0)   # <0 inside torso
        i = sd.argmin(); r[f] = dict(gap=round(float(sd.min()), 1), pt_torso_local=np.round(L[i], 1).tolist(), n_in=int((sd < 0).sum()),
                                    in_pts=L[sd < 3].tolist())
    return r
out = {"torso_box_mm": (m.geom_size[G]*2000).round(0).tolist(), "sweeps": {}}
for sp in (-150, -90, -30, 0, 5, 30):
    first0 = first3 = None; worst = 0; patch = []
    for sr in range(0, 181):
        r = ev(sp, sr); g = min(v['gap'] for v in r.values())
        if first3 is None and g < 3: first3 = sr
        if first0 is None and g < 0: first0 = sr
        worst = min(worst, g); patch += sum((v['in_pts'] for v in r.values()), [])
    P = np.array(patch) if patch else np.zeros((0, 3))
    out["sweeps"][str(sp)] = dict(first_contact_deg=first0, first_lt3mm_deg=first3, max_penetration_mm=round(-worst, 1),
        patch_bbox_torso_local_mm=[P.min(0).round(0).tolist(), P.max(0).round(0).tolist()] if len(P) else None)
json.dump(out, open(os.path.join(H, 'r15_roll_sweep.json'), 'w'), indent=1); print(json.dumps(out))
