"""Demo + checks: python3 modules/controls/thermal/test_winding.py (numpy only, < 5 s)."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winding_model as W

P = W.load_params()
# 1) steady state vs actuators/sizing.json dT_cad (same R network, cold Km) -> sanity
for j in W.LEG:
    p = P[j]; print(f"{j:12s} Rwh {p['Rwh']:.3f} Rha {p['Rha']:.2f} K/W  Cw {p['Cw']:.0f} Ch {p['Ch']:.0f} J/K  "
                    f"tau_w {p['Cw']*p['Rwh']:.0f} s tau_h {p['Ch']*p['Rha']:.0f} s  tau_cont@130 {W.tau_cont(p):.0f} Nm (peak {p['T_out']:.0f})")
# 2) derate shape
p = P['knee']; tc = W.tau_cont(p)
for T in (100, 120, 125, 130, 135, 140):
    print('derate knee', T, round(W.derate(T, p['T_out'], tc), 1))
assert W.derate(119, 300, 100) == 300 and abs(W.derate(130, 300, 100) - 100) < 1e-9 and W.derate(140, 300, 100) == 0
# 3) WBC 1.2 m/s trace (legs/grokbuild/results/walk_trace.npz, cols l_* then r_*), cruise 1.0-4.5 s looped
d = np.load(os.path.join(W.ROOT, 'modules/legs/grokbuild/results/walk_trace.npz'))
tau = d['tau']; dt = float(d['state'][1, 0] - d['state'][0, 0]); seg = tau[int(1.0/dt):int(4.5/dt)]
names = ['l_' + j for j in W.LEG] + ['r_' + j for j in W.LEG]
m = W.WindingModel(names); DT = 0.01; sub = seg[::int(DT/dt)]
hist = []
for k in range(int(3600/DT)):
    Tw = m.step(sub[k % len(sub)], DT)
    if k % int(60/DT) == 0: hist.append(Tw)
hist = np.array(hist)
t120 = {n: (np.argmax(hist[:, i] >= 120) if (hist[:, i] >= 120).any() else None) for i, n in enumerate(names)}
print('\nWBC walk_1p2 cruise looped 60 min at 35 °C ambient (open housing):')
for i, n in enumerate(names):
    print(f"  {n:14s} Tw10min {hist[10, i]:6.1f}  Tw60min {Tw[i]:6.1f} °C  reaches 120 at {t120[n]} min")
lim = m.torque_limits(np.array([P[W._base(n)]['T_out'] for n in names]))
print('  torque limits at 60 min:', dict(zip(names, np.round(lim, 0))))
assert np.all(np.isfinite(Tw)) and Tw.min() > W.T_AMB
print('OK')
