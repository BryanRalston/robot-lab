"""R-021 / A3: size M3 covers and M4 brain from cited parts. Run from repo root."""
import json, trimesh, collections
S = trimesh.load('v3/cad/export/bhl_v3.glb')
P = {p['id']: p for p in json.load(open('v3/cad/export/parts.json'))}
seg = collections.defaultdict(list)
for n in S.graph.nodes_geometry:
    T, g = S.graph[n]; m = S.geometry[g].copy(); m.apply_transform(T)
    seg[P.get(n, P.get(g, {})).get('seg', '?')].append(m)
hull = {k: trimesh.util.concatenate(v).convex_hull.area for k, v in seg.items()}
LIMBS = [f'{s}_{p}' for s in 'LR' for p in ('thigh', 'shank', 'upper_arm', 'forearm')]
A_limb = sum(hull[k] for k in LIMBS)
RHO_PA12 = 1010      # HP 3D HR PA 12 datasheet, ASTM D792, 1.01 g/cm3 (cited)
T_SHELL = 1.5e-3     # [EST] = Shapeways MJF PA12 min unsupported wall (smooth) 1.5 mm, used as design wall
COVERAGE = 0.50      # [EST] front/lateral panels only
covers = dict(
    limb_panels=A_limb * COVERAGE * T_SHELL * RHO_PA12,          # calc: CAD area x cited density x [EST] t, coverage
    clips_fasteners=0.050,                                      # [EST]
    epp_pads=0.36,                                              # v3 v3.py formula 0.06/10mm x2 at 30 mm, carried unchanged [EST]
)
brain_cited = dict(
    jetson_t5000=0.280,      # NVIDIA product sheet 900-13834-0080-000, w/o packaging ~0.28 kg
    gauntlet_agx301=0.266,   # Connect Tech CTIM-00140 manual, board only + PHY heat spreader
    vicor_dcm3623=0.024,     # Vicor DCM3623x75H26C2 datasheet 24.0 g
)
brain_est = dict(
    cold_plate=0.100 * 0.087 * 0.006 * 2700,                     # 6061 plate on module TTP footprint, 6 mm [EST]
    tray=0.130 * 0.200 * 0.002 * 2810,                           # 7075 2 mm base, v3 compute bay 130x200
    lid=(0.130 * 0.200 + 2 * (0.130 + 0.200) * 0.040) * 1.5e-3 * RHO_PA12,
    rt_safety_mcu=0.040, nvme_2280=0.008, dcm_filter_heatsink=0.030, standoffs_fasteners=0.030,
)
def credit(base, cited, est):
    paper = cited + est; save = base - paper
    return paper, base - (save * cited / paper + 0.5 * save * est / paper) if save > 0 else paper
bc, be = sum(brain_cited.values()), sum(brain_est.values())
b_paper, b_cred = credit(1.80, bc, be)
c_paper = sum(covers.values()); c_cred = 1.86 - 0.5 * (1.86 - c_paper)   # all saving rests on [EST] t/coverage
out = dict(hull_m2={k: round(hull[k], 3) for k in LIMBS}, A_limb_m2=round(A_limb, 3),
           covers={k: round(v, 3) for k, v in covers.items()}, covers_paper=round(c_paper, 3), covers_credited=round(c_cred, 3),
           brain_cited={k: round(v, 3) for k, v in brain_cited.items()}, brain_est={k: round(v, 3) for k, v in brain_est.items()},
           brain_paper=round(b_paper, 3), brain_credited=round(b_cred, 3),
           credible=round(66.891 - (1.80 - b_cred) - (1.86 - c_cred), 3),
           paper=round(65.75 - (1.80 - b_paper) - (1.86 - c_paper), 3),
           full_coverage_covers=round(A_limb * T_SHELL * RHO_PA12 + 0.41, 3))
print(json.dumps(out, indent=1)); json.dump(out, open('modules/arbiter/a3_size.json', 'w'), indent=1)
