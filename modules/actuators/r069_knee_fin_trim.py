"""R-069: knee rev B fin trim now that the 2x Elmo drives are OFF the housing (R-062/R-066, thigh plate, no metal path).
Same 2-node loop as knee_resize_r043.py (Controls winding_model, 35 C, 60 min, worse of L/R knee), 07613D x2.
Cases: drives on/off housing node; h 12 (open) and h 10 (Controls R-052 standing-hold caveat), vented = h x15/12.
Traces: walk_1p2_r7, r4 carry x1.10, and regenerated P-042 carry (legs/results/p042/carry_20kg_1p0.npz) x1.0.
Fin area A (extra over bare housing) swept; criterion: every open/vented case <= 110 C (10 K under the 120 C design target).
-> results/r069_knee_fin_trim.json"""
import os, sys, json, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f'{H}/../..')
sys.path.insert(0, f'{R}/modules/controls/thermal'); import winding_model as W
W.load_params(knee='07613D'); mot = W.MOT_CACHE; sel = json.load(open(f'{R}/modules/actuators/results/sizing.json'))['sel']['knee']
TR = {'walk_1p2_r7': ('r7/ref_ds25/walk_1p2_r7.npz', 1.0), 'carry_r4_x1.10': ('r4/carry_20kg_1p0.npz', 1.10), 'carry_p042': ('p042/carry_20kg_1p0.npz', 1.0)}
D = {k: np.load(f'{R}/modules/legs/results/{f}') for k, (f, s) in TR.items()}
M = mot['TBM2G-07613']; p = W._p(M, 'TBM2G-07613D', 2, sel['ratio'], sel['eta'], sel['area_cad'], sel['housing_cad'], sel['T_out']); G0 = 1 / p['Rha']
def run(A, h, drv, tau, om, dt, T=3600.0, DT=0.01):
    Rha = 1 / (G0 * h / 12 + h * A)
    idx = np.arange(0, len(tau), max(1, int(round(DT / dt)))); tq, w = tau[idx], om[idx]
    pfe = W.p_fe(p, w); pdr = W.p_drv(p, tq) if drv else 0 * tq; Tw = Th = W.T_AMB
    for k in range(int(T / DT)):
        i = k % len(tq); q = W.p_cu(p, tq[i], Tw) + pfe[i]; qwh = (Tw - Th) / p['Rwh']
        Tw += DT * (q - qwh) / p['Cw']; Th += DT * (qwh + pdr[i] - (Th - W.T_AMB) / Rha) / p['Ch']
    return round(Tw, 1)
out = {}
for A in (0.0703, 0.06, 0.05, 0.045, 0.04, 0.035):
    for drv in (True, False):
        for h in (12, 10):
            key = f'A{A}_drv{"on" if drv else "off"}_h{h}'; r = {}
            for tn, (f, sc) in TR.items():
                d = D[tn]; va = d['va']; dt = float(d['t'][1] - d['t'][0])
                for case, hh in (('open', h), ('vented', h * 15 / 12)):
                    r[f'{tn}/{case}'] = max(run(A, hh, drv, sc * d['TAU'][:, va[c]], d['V'][:, va[c]], dt) for c in (3, 9))
            out[key] = dict(T=r, Tmax=max(r.values())); print(key, r, flush=True)
json.dump(out, open(f'{H}/results/r069_knee_fin_trim.json', 'w'), indent=1)
