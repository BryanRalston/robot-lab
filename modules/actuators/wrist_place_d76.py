"""D76 (R-076 / R-080) wrist pitch/yaw pair, side by side, both TBM2G-05008C + CSG-14-100 + CRBH 258 A + AksIM-2 MB022 (yaw back to CSG-14).
Frame as D73 (pivot origin, z toward elbow, y = pitch axis). Units axial along z at y = +-29 (Ø56 frame, 2 mm between cans), cited stack
58.8 + 2x2 walls [EST] = 62.8 mm, bottom at Z0. R-080: Z0 = +26.5 (was +28). Things below the units (wrist_clash_r4 / D73):
 - fork/cross: every fork/cross part inside the r 24.5 sphere about the pivot (wrist_clash_r4 fix); fork cheeks 20x6x20 at |y| 14..20, z -10..10
 - palm (palm_7075, top z -27, x+-16, y+-43, 90 deep) swept over P-026 pitch +-60 / yaw +-30
 - wrist roll: at the elbow end (D76 / Arms proposal, D74 dropped), so no roll output or roll bearing below the units
 - forearm shell, hand board, wrist leads (0.244 kg/side bundle): all at z > unit bottom (forearm side), so lowering the units only increases those gaps.
Gap rule: 2.0 mm (wrist_clash_r4 GAP). -> cad/wrist_place_d76.step, results/wrist_place_d76.json"""
import cadquery as cq, numpy as np, json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); D, L, YC = 56.0, 62.8, 29.0
def build(Z0):
    u = [cq.Workplane('XY').workplane(offset=Z0).center(0, s * YC).circle(D / 2).extrude(L) for s in (1, -1)]
    return u[0].union(u[1])
Rf = float(np.sqrt(10**2 + 20**2 + 10**2))   # 24.49
def clear(Z0):
    U = build(Z0).val()
    sph = cq.Solid.makeSphere(Rf); cheeks = [cq.Solid.makeBox(20, 6, 20, cq.Vector(-10, y0, -10)) for y0 in (14, -20)]
    d_sph = U.distance(sph); d_ch = min(U.distance(c) for c in cheeks)
    # palm swept: sample palm top skin (12 mm) and rotate as wrist_clash_r4 (Ry(pitch) Rx(yaw))
    P = np.array([(x, y, z) for x in np.arange(-16, 16.1, 2) for y in np.arange(-43, 43.1, 2) for z in np.arange(-27, -105.1, -6)])
    zmax = -1e9; dmin = 1e9
    for p in np.radians(np.arange(-60, 60.1, 10)):
        for yw in np.radians(np.arange(-30, 30.1, 10)):
            c, s = np.cos(p), np.sin(p); Ry = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]); c2, s2 = np.cos(yw), np.sin(yw); Rx = np.array([[1, 0, 0], [0, c2, -s2], [0, s2, c2]])
            Q = (Ry @ Rx @ P.T).T; zmax = max(zmax, Q[:, 2].max())
            r = np.hypot(np.abs(Q[:, 1]) - YC, Q[:, 0]); dz = np.maximum(Z0 - Q[:, 2], 0); dr = np.maximum(r - D / 2, 0)
            dmin = min(dmin, float(np.sqrt(dz**2 + dr**2).min()))
    return dict(Z0=Z0, top_z=Z0 + L, gap_to_fork_cross_sphere_mm=round(d_sph, 2), gap_to_fork_cheeks_mm=round(d_ch, 2), palm_swept_max_z=round(float(zmax), 1),
                gap_to_palm_swept_mm=round(dmin, 1), width_y_mm=2 * (YC + D / 2), width_with_2mm_walls_mm=2 * (YC + D / 2) + 4)
out = dict(before=clear(28.0), after=clear(26.5))
out['after']['pass_2mm'] = min(out['after']['gap_to_fork_cross_sphere_mm'], out['after']['gap_to_fork_cheeks_mm'], out['after']['gap_to_palm_swept_mm']) >= 2.0 - 1e-3
cq.exporters.export(build(26.5), f'{H}/cad/wrist_place_d76.step')
out['yaw_gear'] = dict(was='CSF-11-100 set 0.05 kg', now='CSG-14-100 set 0.09 kg', d_kg_per_side=0.04, d_kg_pair=0.08, src='HD CSF/CSG catalog weight table (datasheets/hd_csf_csg_catalog.txt l.1101: 11 -> 0.05, 14 -> 0.09)',
                       length='CSG-14 H1 18.5 vs CSF-11 16.0: +2.5 mm (yaw unit now = pitch unit, 62.8)', torque='CSG-14-100 rep peak 36 vs need 12.9 (2.79x); CSF-11 11 (0.85x) fails')
json.dump(out, open(f'{H}/results/wrist_place_d76.json', 'w'), indent=1); print(json.dumps(out, indent=1))
