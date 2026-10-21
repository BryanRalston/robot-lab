"""Hip-pinch keep-out (T&R R_HIP_PINCH.md ca68f3a) on ID P-023 rev 8b (acb9bd5): L<->R thigh panels and pelvis hem <-> each panel, ISO 13854 finger 25 mm
+ 2 tol + 1 model = 28 mm. Thresholds warn 35 / limit 30 / trip 28 mm. All motors-on modes (walk, carry, crouch, kneel, sit,
R-146 lowering). Geometry = ID rev 8b: hip_skirt_r8.py chain/retained skirt with the hem cut to R 144 about C1 (hip_skirt_r8b.py), and the
rev 8b panel (inboard edge y 86 + 40 mm inboard-rear chamfer from phi 45, hip_skirt_r8_asym.panel(y0=86, c=40, phi0=45)).
No rev 8b STL exists in the repo (acb9bd5 ships scripts only), so the point clouds are rebuilt from ID's scripts.
Motors-off / limp cases are out of scope (ID PE foam edges <= 140 N). ID/T&R (p, r, y) = sim/v3 LEFT hip (pitch, roll, yaw) in deg
(same axes and signs: + roll = abduction, + yaw = left toe-out); the right leg is the y-mirror: (p_R, -r_R, -y_R).
Speed: KD-tree queries on ~1000 panel points; Python ~1 ms/eval (reference; C++ port for 1 kHz)."""
from __future__ import annotations
import math, numpy as np
from pathlib import Path
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[3]
ID_SCRIPT = ROOT / 'modules/design/cad/covers/hip_skirt_r8.py'
ASYM = ROOT / 'modules/design/cad/covers/hip_skirt_r8_asym.py'
HEM_R = 144.0  # rev 8b (fallback REV='8b')
REV = "8f"
COV = ROOT / 'modules/design/cad/covers'
JCH = 3.0  # rev 8c rigid PC J-channel lip on the hem (foam excluded)
WARN, LIMIT, TRIP = 40.0, 35.0, 33.0  # T&R 76de66a/42c4e50 stopgap; return to 35/30/28 only on T&R re-verification
HIP = ['hip_pitch', 'hip_roll', 'hip_yaw']
_G = {}

def geometry():
    """Exec ID's script up to the gap evaluation (same cut as T&R), fixed hem R 152.8."""
    if _G: return _G
    src = ID_SCRIPT.read_text().split('hem=[(float')[0].replace('R1=dmin[0]-25', f'R1={HEM_R}')
    src = src.replace("dmin=min((float(np.linalg.norm(T(P,*q)-C1,axis=1).min()),q) for q in POSES); ", '')
    ns = {'__file__': str(ID_SCRIPT)}; exec(compile(src, 'hip_skirt_r8', 'exec'), ns)
    asym = {'__file__': str(ASYM)}; a = ASYM.read_text().split('rng=np.random')[0]
    exec(compile(a, 'hip_skirt_r8_asym', 'exec'), asym)
    if REV == '8b':
        _G.update(P=asym['panel'](y0=86, c=40, phi0=45), T=ns['T'], KT=ns['KT'], mir=ns['mir'], off=0.0); return _G
    import trimesh  # rev 8f (ID 76cc34d): rigid panel STL (R152 relief, y86 + chamfer) and notched hem STL (R141.5)
    pm = trimesh.load(COV / 'hip_skirt_r8f_thigh_panel.stl', force='mesh')
    hm = trimesh.load(COV / 'hip_skirt_r8f_pelvis_notched.stl', force='mesh')
    P = np.vstack([pm.vertices, trimesh.sample.sample_surface_even(pm, 4000, seed=0)[0]])
    P = P[P[:, 0] <= P[:, 0].max() - 1.0]  # inboard skin of the 1.5 mm hull only (drop the offset copy)
    _, ix = np.unique(np.round(P / 2.0), axis=0, return_index=True); P = P[np.sort(ix)]  # 2 mm voxel thin-out (<=~1 mm error)
    KH = np.vstack([hm.vertices, hm.triangles_center])
    _, ix = np.unique(np.round(KH / 2.0), axis=0, return_index=True); KH = KH[ix]
    _G.update(P=P, T=ns['T'], KT=cKDTree(KH), mir=ns['mir'], off=JCH)
    return _G

def _deg(q, sd, j): return float(np.degrees(q.get(f'{sd}_{j}', 0.0)))

def gaps(q: dict):
    """q: sim joint name -> rad. Returns dict(lr, hem_l, hem_r) in mm."""
    g = geometry(); T, P, mir = g['T'], g['P'], g['mir']
    PL = T(P, _deg(q, 'l', 'hip_pitch'), _deg(q, 'l', 'hip_roll'), _deg(q, 'l', 'hip_yaw'))
    PR = mir(T(P, _deg(q, 'r', 'hip_pitch'), -_deg(q, 'r', 'hip_roll'), -_deg(q, 'r', 'hip_yaw')))
    lr = float(cKDTree(PL).query(PR)[0].min()) - g['off']  # rev 8c: L/R inboard edges also in the rigid J-channel
    o = g['off']
    return dict(lr=lr, hem_l=float(g['KT'].query(PL)[0].min()) - o, hem_r=float(g['KT'].query(mir(PR))[0].min()) - o)

def min_gap(q): return min(gaps(q).values())

def status(gmin):
    return 'trip' if gmin < TRIP else 'limit' if gmin < LIMIT else 'warn' if gmin < WARN else 'ok'

class HipPinchGuard:
    """Velocity filter on the 6 hip dofs. Below LIMIT+band the closing rate is damped to zero at LIMIT (same law as the
    arm supervisor); at/below TRIP the closing joint PAIR (same joint on both legs) is stopped (its closing component zeroed).
    Gradient by central finite differences (0.2 deg) of the governing gap."""
    def __init__(s, band=10.0, xi_deg_s=60.0, h=0.2):
        s.band, s.xi, s.h = band, xi_deg_s, h; s.events = []
    def grad(s, q, key):
        gr = {}
        for sd in 'lr':
            for j in HIP:
                n = f'{sd}_{j}'; qp = dict(q); qm = dict(q); d = np.radians(s.h)
                qp[n] = q.get(n, 0.0) + d; qm[n] = q.get(n, 0.0) - d
                gr[n] = (gaps(qp)[key] - gaps(qm)[key]) / (2 * s.h)  # mm/deg
        return gr
    def filter(s, q: dict, qdot: dict, t=0.0):
        """q rad, qdot rad/s (hip joints). Returns supervised qdot and the governing gap/status."""
        G = gaps(q); key = min(G, key=G.get); g = G[key]; st = status(g); out = dict(qdot)
        if g >= LIMIT + s.band: return out, g, st
        gr = s.grad(q, key)
        rate = sum(gr[n] * np.degrees(out.get(n, 0.0)) for n in gr)  # mm/s
        if g <= TRIP:
            s.events.append((t, 'trip', key, g))
            for j in HIP:  # stop each closing joint pair
                pair = [f'l_{j}', f'r_{j}']
                if sum(gr[n] * out.get(n, 0.0) for n in pair) < 0:
                    for n in pair: out[n] = 0.0 if gr[n] * out.get(n, 0.0) < 0 else out.get(n, 0.0)
            return out, g, st
        lb = -s.xi * (g - LIMIT) / s.band  # mm/s allowed closing
        if rate < lb:
            a = np.array([gr[n] for n in gr]); e = lb - rate
            if a @ a > 1e-12:
                for n, ai in zip(gr, a): out[n] = out.get(n, 0.0) + np.radians(ai * e / (a @ a))
        if st != 'ok': s.events.append((t, st, key, g))
        return out, g, st
