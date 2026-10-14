"""R-081 (Legs d81dcba) sole pad: CoP / ZMP margin re-check with a compliant contact. RL Controls. Light (numpy only).
Inputs: Legs ID plans (foot-frame CoP per loaded foot, FZ, com/zmp), static carry balance (carry_balance_r1.json).
Compliant edge model (Winkler layer, t 6 mm, rigid foot): CoP at an edge needs a triangular pressure block of length a
from the edge with peak p_max = E * eps_lim -> effective edge inset e = a/3 = 2F / (3 * w_edge * E * eps_lim).
eps_lim 0.39 (Legs spec edge strain at 1.31 BW) [EST]; w_edge = 0.100 m for toe/heel edges, 0.240 m for side edges.
E from Shore A (Gent): 47A ~1.9-2.2 MPa (spec 2.2), 67A ~4.4-4.8 (spec 4.8); bonded-pad shape factor stiffening ignored
(conservative). Height: +6 mm sole -> ZMP from LIPM shifts by (dz/zc)*(com - zmp); applied as an extra margin loss.
Margin per frame = min distance of the planned CoP to the sole edge (HEEL -60, TOE +180, |y| 50 mm) minus insets.
Bare 7075 = rigid (e = 0, dz = 0). -> sole_cop_r1.json"""
import os, json, numpy as np
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
L = os.path.join(R, 'modules/legs/results'); HEEL, TOE, HW = -0.060, 0.180, 0.050; T_PAD = 0.006; EPS = 0.39; DZ = 0.006
def gent(S): return 0.0981 * (56 + 7.62336 * S) / (0.137505 * (254 - 2.54 * S)) * 1e6
PADS = {'bare 7075': None, 'Gumlite 47A (E 2.2)': 2.2e6, 'Gumlite 44A low (Gent)': gent(44), 'SP 64A (Gent)': gent(64), 'SP 67A (E 4.8)': 4.8e6}
def inset(F, w, E): return 0.0 if E is None else 2 * np.maximum(F, 0) / (3 * w * E * EPS)
PLANS = {'walk 0.8 ref_m12': 'r7/ref_m12/walk_0p8_r7.npz', 'walk 1.0 ref_m12': 'r7/ref_m12/walk_1p0_r7.npz',
         'walk 1.2 ref_m12': 'r7/ref_m12/walk_1p2_r7.npz', 'walk 1.2 ref_ds25': 'r7/ref_ds25/walk_1p2_r7.npz',
         'carry P-042 1.0': 'p042/carry_20kg_1p0.npz', 'push_recover': 'push_recover.npz', 'stairs 18 cm': 'stairs_18cm.npz',
         'sit_to_stand': 'sit_to_stand.npz'}
out = dict(basis=__doc__.split('\n')[2], E_Pa={k: v for k, v in PADS.items()}, plans={}, static_carry={})
for name, f in PLANS.items():
    fp = os.path.join(L, f)
    if not os.path.exists(fp): continue
    d = np.load(fp); C, FZ = d['COP'], d['FZ']
    zc = 1.158; dzmp = DZ / zc * np.linalg.norm(d['com'] - d['zmp'], axis=1) if 'com' in d.files and d['com'].ndim == 2 and d['zmp'].ndim == 2 else np.zeros(len(FZ))
    res = {}
    for pad, E in PADS.items():
        ms = []
        for i in range(2):
            ok = (FZ[:, i] > 1) & np.isfinite(C[:, i, 0]); x, y, F = C[ok, i, 0], C[ok, i, 1], FZ[ok, i]
            mt = TOE - x - inset(F, 0.100, E); mh = x - HEEL - inset(F, 0.100, E); my = HW - np.abs(y) - inset(F, 0.240, E)
            m = np.minimum(np.minimum(mt, mh), my) - (0 if E is None else dzmp[ok]); ms.append(m)
        m = np.concatenate(ms) * 1000
        res[pad] = dict(min_mm=round(float(m.min()), 1), p5_mm=round(float(np.percentile(m, 5)), 1), median_mm=round(float(np.median(m)), 1),
                        frac_lt_12mm=round(float((m < 12 - 1e-6).mean()), 3), frac_lt_5mm=round(float((m < 5).mean()), 3), frac_le_0=round(float((m <= 0).mean()), 3))
    res['max_FZ_N'] = round(float(FZ.max()), 0); res['max_dzmp_mm'] = round(float(dzmp.max() * 1000), 2)
    out['plans'][name] = res; print(name, json.dumps(res))
# static carry (double support, feet flat): per-foot F = M g / 2, toe edge
for c in json.load(open(os.path.join(R, 'modules/controls/carry/carry_balance_r1.json'))):
    F = c['total_kg'] * 9.81 / 2; k = f"payload {c['payload_pos']} waist {c['waist_pitch']}"
    out['static_carry'][k] = {pad: round(c['toe_margin_mm'] - 1000 * inset(F, 0.100, E), 1) for pad, E in PADS.items()}
    print(k, out['static_carry'][k])
out['edge_inset_mm_at_1p31BW_single'] = {pad: dict(toe_heel=round(1000 * inset(85 * 9.81 * 1.31, 0.1, E), 1), side=round(1000 * inset(85 * 9.81 * 1.31, 0.24, E), 1)) for pad, E in PADS.items()}
print(out['edge_inset_mm_at_1p31BW_single'])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sole_cop_r1.json'), 'w'), indent=1)
