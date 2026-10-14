"""Rev B as built (fbd762b, 0.0703 m2 CAD fins, x2 bare factor dropped): walk r7 and carry r4 x1.10 at h 12, eta 1/0.7,
drive off/on housing. Own loop (knee_revB_check.sim). -> knee_revB_cad.json"""
import os, sys, json, copy, types, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winding_model as W
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knee_revB_check.py')).read()
ns = {'__file__': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knee_revB_check.py')}; exec(src.split('out = {')[0], ns)   # reuse V-free helpers: base, sim, TR, L
base, sim, TR, L = ns['base'], ns['sim'], ns['TR'], ns['L']
A_B = 1.0 / (base['Rha'] * W.H_AIR * W.FINS)
def v(eta, h=12.0): p = copy.deepcopy(base); p['Rha'] = 1.0 / (h * (A_B + eta * 0.0703)); return p
V = {'cad eta1 h12': v(1.0), 'cad eta0.7 h12': v(0.7), 'cad eta1 h15 vented': v(1.0, 15.0)}
out = {'Rha': {k: round(p['Rha'], 3) for k, p in V.items()}, 'tau_cont130': {k: round(float(W.tau_cont(p)), 1) for k, p in V.items()}}
for name in ('walk_1p2_r7', 'carry r4 1.0 x1.10'):
    f, sc = TR[name]; d = np.load(os.path.join(L, f)); va = d['va']; dt = float(d['t'][1] - d['t'][0])
    c = max((3, 9), key=lambda c: np.mean(d['TAU'][:, va[c]] ** 2)); tau = d['TAU'][:, va[c]] * sc
    out[name] = {dr: {k: round(float(t), 1) for k, t in zip(V, sim(list(V.values()), tau, d['V'][:, va[c]], dt, dr == 'drive_on'))} for dr in ('drive_off', 'drive_on')}
    print(name, out[name], flush=True)
print(out['Rha'], out['tau_cont130'])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knee_revB_cad.json'), 'w'), indent=1)
