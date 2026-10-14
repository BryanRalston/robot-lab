"""Checks + 60-min demo: python3 modules/controls/thermal/test_winding.py (numpy only, ~10 s)."""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winding_model as W

P = W.load_params()
lg = np.load(os.path.join(W.ROOT, 'modules/legs/results/walk_1p2.npz')); va = lg['va']
FE = {j: float(np.mean([np.mean(W.p_fe(P[j], lg['V'][:, va[i + o]])) for o in (0, 6)])) for i, j in enumerate(W.LEG)}
print('joint          motor          n  Rwh   Rha  tau_w tau_h  iron@walk  tau_cont130 (Cu / Cu+Fe)  peak')
for j in W.LEG + W.UPPER:
    p = P[j]; fe = FE.get(j, 0.0)
    print(f"{j:14s} {p['motor']:14s} {p['nmot']}  {p['Rwh']:.3f} {p['Rha']:.2f}  {p['Cw']*p['Rwh']:4.0f}s {p['Ch']*p['Rha']:4.0f}s  "
          f"{fe:5.1f} W   {W.tau_cont(p):5.0f} / {W.tau_cont(p, p_fe_W=fe):5.0f} N·m   {p['T_out']}")
# derate shape (unchanged breakpoints; 155 hard limit above torque-off)
assert W.derate(119, 300, 100) == 300 and abs(W.derate(130, 300, 100) - 100) < 1e-9 and W.derate(140, 300, 100) == 0
assert W.T_TRIP < W.T_HARD == 155.0
# drive loss table
assert abs(W.p_drv(dict(ratio=1, eta=1, nmot=1, Kt=1.0), 20 / np.sqrt(2)) - 13) < 1e-9
# 60-min demo: WBC r6 walk_1p2 cruise (1.0-4.5 s) looped, 35 °C, open housing, iron = mean at walk_1p2 speeds, drive on
d = np.load(os.path.join(W.ROOT, 'modules/legs/grokbuild/results/walk_trace.npz'))
tau = d['tau']; dt = float(d['state'][1, 0] - d['state'][0, 0]); seg = tau[int(1.0/dt):int(4.5/dt)]
names = ['l_' + j for j in W.LEG] + ['r_' + j for j in W.LEG]
fe = np.array([FE[W._base(n)] for n in names])
out = {}
for case, kw in (('copper+iron+drive', dict(p_fe_W=fe, drive=True)), ('copper+iron (as knee_thermal.py)', dict(p_fe_W=fe, drive=False))):
    m = W.WindingModel(names, P); DT = 0.01; sub = seg[::int(DT/dt)]; t120 = [None] * len(names)
    for k in range(int(3600/DT)):
        Tw = m.step(sub[k % len(sub)], DT, **kw)
        for i in range(len(names)):
            if t120[i] is None and Tw[i] >= 120: t120[i] = round(k * DT / 60, 1)
    out[case] = {n: dict(Tw60=round(float(Tw[i]), 1), Th60=round(float(m.Th[i]), 1), t120_min=t120[i]) for i, n in enumerate(names)}
    print(f'\n60 min WBC 1.2 m/s cruise, {case}:')
    for n in names: print(f"  {n:14s} Tw {out[case][n]['Tw60']:6.1f}  Th {out[case][n]['Th60']:6.1f} °C  120 °C at {out[case][n]['t120_min']} min")
# arm hold (r1_budget hold torques: shoulder_pitch 61, elbow 40 N·m), 35 °C
for j, T in (('shoulder_pitch', 61.0), ('elbow', 40.0)):
    m = W.WindingModel([j], P); t = {}
    for k in range(int(1800/0.01)):
        Tw = m.step(np.array([T]), 0.01)[0]
        for lim in (120, 140, 155):
            if lim not in t and Tw >= lim: t[lim] = round(k * 0.01 / 60, 1)
    out[f'hold_{j}'] = dict(T=T, Tw30=round(float(Tw), 1), t_min=t)
    print(f'hold {j} {T} N·m: Tw30min {Tw:.0f} °C, minutes to 120/140/155: {t}')
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'demo_60min.json'), 'w'), indent=1)
print('OK')
