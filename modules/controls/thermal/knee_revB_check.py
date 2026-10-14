"""R-052: independent check of Actuators D69 rev B (4366d32): knee = 2x TBM2G-07613D + housing fins.
Own model path: winding_model params + own vectorized 2-node loop (not knee_resize_r043.py). 35 °C, 60 min looped.
Sensitivities: fin area 0.025 vs 0.05 m2, fin efficiency 1.0 / 0.7, h 12 open vs 15 vented (A35), drive loss on/off housing."""
import os, sys, json, copy, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winding_model as W
L = os.path.join(W.ROOT, 'modules/legs/results')
base = W.load_params(knee='07613D')['knee']; G0 = 1 / base['Rha']; A_h = 1 / (base['Rha'] * W.H_AIR * W.FINS)   # housing area
TR = {'walk_1p2_r7': ('r7/ref_ds25/walk_1p2_r7.npz', 1.0), 'carry r4 1.0 x1.10': ('r4/carry_20kg_1p0.npz', 1.10),
      'carry P-042 x0.32 (Controls regen)': ('p042/carry_20kg_1p0.npz', 1.0)}
def variant(Af, eta_f, h, fan=False):
    p = copy.deepcopy(base)
    if fan: p['Rha'] = 1 / (40.0 * W.FINS * A_h)
    else: p['Rha'] = 1 / (G0 * h / 12.0 + h * eta_f * Af)      # base housing conductance scales with h too
    return p
V = {'bare h12': variant(0, 1, 12), 'fins 0.05 eta1 h12 (revB brief)': variant(0.05, 1, 12), 'fins 0.025 eta1 h12 (script)': variant(0.025, 1, 12),
     'fins 0.05 eta0.7 h12': variant(0.05, 0.7, 12), 'fins 0.05 eta1 h15 (vented)': variant(0.05, 1, 15),
     'fins 0.025 eta1 h15 (vented)': variant(0.025, 1, 15), 'fan h40 base': variant(0, 1, 40, fan=True)}
def sim(ps, tau, om, dt_src, drive, T=3600.0, DT=0.01):
    idx = np.arange(0, len(tau), max(1, int(round(DT / dt_src)))); tq, w = np.abs(tau[idx]), np.abs(om[idx])
    p0 = ps[0]; Rha = np.array([p['Rha'] for p in ps]); n, ratio, eta, Km = p0['nmot'], p0['ratio'], p0['eta'], p0['Km25']
    pfe = W.p_fe(p0, w); pdr = W.p_drv(p0, tq) if drive else np.zeros_like(tq)
    Tw = np.full(len(ps), W.T_AMB); Th = Tw.copy()
    for k in range(int(T / DT)):
        i = k % len(tq); Tm = tq[i] / (ratio * eta * n)
        q = n * (Tm / (Km / np.sqrt(1 + W.ALPHA_CU * (Tw - 25)))) ** 2 + pfe[i]
        qwh = (Tw - Th) / p0['Rwh']; Tw = Tw + DT * (q - qwh) / p0['Cw']; Th = Th + DT * (qwh + pdr[i] - (Th - W.T_AMB) / Rha) / p0['Ch']
    return Tw
out = {'tau_cont130': {k: round(float(W.tau_cont(p)), 1) for k, p in V.items()}, 'Rha': {k: round(p['Rha'], 3) for k, p in V.items()}}
for name, (f, sc) in TR.items():
    fp = os.path.join(L, f)
    if not os.path.exists(fp): continue
    d = np.load(fp); va = d['va']; dt = float(d['t'][1] - d['t'][0])
    c = max((3, 9), key=lambda c: np.mean(d['TAU'][:, va[c]] ** 2)); tau = d['TAU'][:, va[c]] * sc
    out[name] = {'rms': round(float(np.sqrt(np.mean(tau ** 2))), 1)}
    for drive in (False, True):
        Tw = sim(list(V.values()), tau, d['V'][:, va[c]], dt, drive)
        out[name]['drive_on_housing' if drive else 'drive_off'] = {k: round(float(t), 1) for k, t in zip(V, Tw)}
    print(name, json.dumps(out[name]))
print(out['tau_cont130']); print(out['Rha'])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knee_revB_check.json'), 'w'), indent=1)
