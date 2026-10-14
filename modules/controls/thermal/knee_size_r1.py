"""R-043 blocking: minimum knee continuous rating for Tw <= 120 °C at 60 min (35 °C, drives off housing, Thermal limits)
on Legs ID plans; candidate TBM2G frames x heat paths. Vectorized over candidates (numpy, light). -> knee_size_r1.json
Heat paths (joint Rha): bare 1/(12*2*A) = 1.44 K/W; fins (R-044 adopted, 1.05 K/W req., +0.05 kg/knee); shank (D69 0.72)."""
import os, sys, json, copy, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winding_model as W
L = os.path.join(W.ROOT, 'modules/legs/results')
TR = {'carry r2 plan': 'r2/carry_20kg_r2.npz', 'carry r4 1.0': 'r4/carry_20kg_1p0.npz', 'walk r7 1.2': 'r7/ref_ds25/walk_1p2_r7.npz'}
mot = json.load(open(os.path.join(W.ROOT, 'v3/analysis/tbm2g.json'))); W.MOT_CACHE.update(mot)
base = W.load_params(knee='07613D')['knee']
PATHS = {'bare': (base['Rha'], 0.0), 'fins': (1.05, 0.05), 'shank': (base['Rha'] * 0.5, 0.12)}   # (Rha, kg/knee [EST]); shank per Thermal 26412c7
FRAMES = ['TBM2G-07613', 'TBM2G-06826', 'TBM2G-08513', 'TBM2G-07626', 'TBM2G-08526']
def cand(fr, n, path):
    M = mot[fr]; p = copy.deepcopy(base); ratio_k = 2.0 / n   # keep joint ratio; single motor carries all torque
    p.update(motor=fr + 'D', nmot=n, Km25=M['Km'][2], Kt=M['Kt_hot'][2], Rwh=0.6 * M['Rth'] / n, Rha=PATHS[path][0],
             Cw=W.F_CU * n * M['mass'] * W.C_CU, Ch=base['Ch'] + (1 - W.F_CU) * (n * M['mass'] - 2 * mot['TBM2G-07613']['mass']) * W.C_FE)
    a, b = W.IRON['TBM2G-07613']; k = M['mass'] / mot['TBM2G-07613']['mass']; p['iron_a'], p['iron_b'] = a * k, b * k   # [EST] mass-scaled
    peak = n * M['Tp'][2] / (2 * mot['TBM2G-07613']['Tp'][2]) * base['T_out']
    return p, dict(frame=fr + 'D', n=n, path=path, tau_cont130=round(float(W.tau_cont(p)), 1), peak_Nm=round(peak, 0),
                   d_motor_kg_robot=round(2 * (n * M['mass'] - 2 * mot['TBM2G-08513']['mass']), 3), path_kg_knee=PATHS[path][1])
C = [cand(f, n, pa) for f in FRAMES for n in (2, 1) for pa in PATHS if not (n == 1 and f in ('TBM2G-07613', 'TBM2G-06826'))]
def sim(ps, tau, om, dt_src, T=3600.0, DT=0.01):
    idx = np.arange(0, len(tau), max(1, int(round(DT / dt_src)))); tq, w = np.abs(tau[idx]), np.abs(om[idx])
    g = lambda k: np.array([p[k] for p in ps])
    n, ratio, eta, Km, Rwh, Rha, Cw, Ch, ia, ib = map(g, ('nmot', 'ratio', 'eta', 'Km25', 'Rwh', 'Rha', 'Cw', 'Ch', 'iron_a', 'iron_b'))
    Tw = np.full(len(ps), W.T_AMB); Th = Tw.copy(); mx = Tw.copy()
    for k in range(int(T / DT)):
        i = k % len(tq); Tm = tq[i] / (ratio * eta * n); nk = w[i] * ratio * 60 / (2 * np.pi) / 1000
        q = n * (Tm / (Km / np.sqrt(1 + W.ALPHA_CU * (Tw - 25)))) ** 2 + n * (ia * nk + ib * nk ** 2)
        qwh = (Tw - Th) / Rwh; Tw = Tw + DT * (q - qwh) / Cw; Th = Th + DT * (qwh - (Th - W.T_AMB) / Rha) / Ch
        mx = np.maximum(mx, Tw)
    return Tw, mx
out = {'candidates': [c[1] for c in C]}
for name, f in TR.items():
    d = np.load(os.path.join(L, f)); va = d['va']; dt = float(d['t'][1] - d['t'][0])
    worst = max((3, 9), key=lambda c: np.mean(d['TAU'][:, va[c]] ** 2))
    Tw, mx = sim([c[0] for c in C], d['TAU'][:, va[worst]], d['V'][:, va[worst]], dt)
    for c, t, m in zip(out['candidates'], Tw, mx): c[name] = round(float(m), 1)
    # minimum tau_cont: scale Km of 2x07613D on each path until max Tw = 120
    for pa in PATHS:
        s = np.linspace(0.8, 2.0, 25); ps = []
        for x in s:
            p, _ = cand('TBM2G-07613', 2, pa); p['Km25'] *= x; ps.append(p)
        _, mx2 = sim(ps, d['TAU'][:, va[worst]], d['V'][:, va[worst]], dt)
        j = int(np.argmax(mx2 <= 120.0)) if (mx2 <= 120.0).any() else None
        out.setdefault('min_tau_cont130', {})[f'{name} | {pa}'] = None if j is None else round(float(W.tau_cont(ps[j])), 1)
for c in out['candidates']: c['pass_5K'] = all(c[n] <= 115.0 for n in TR)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knee_size_r1.json'), 'w'), indent=1)
for c in sorted(out['candidates'], key=lambda c: (c['d_motor_kg_robot'] + 2 * c['path_kg_knee'])): print(c)
print(out['min_tau_cont130'])
