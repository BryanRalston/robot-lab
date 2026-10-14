"""D68 knee thermal fix check (light, numpy). Reuses RL Controls A40 2-node model (controls/thermal/winding_model.py,
same Cw/Ch/Rwh/Rha conventions) on the WBC 1.2 m/s cruise trace looped 60 min at 35 C, and adds TBM2G iron loss
(iron_loss.json fit, motor speed from legs walk_1p2 knee velocity). Options: base, (a) 2x TBM2G-08513D,
(b) conductive shank path Rha x0.5 [EST], (d) forced air h 12->40 W/m2K [EST], (a)+(d).  -> results/knee_thermal.json"""
import os, sys, json, math, copy, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f'{H}/../..')
sys.path.insert(0, f'{R}/modules/controls/thermal'); import winding_model as W
P0 = W.load_params(); mot = json.load(open(f'{R}/v3/analysis/tbm2g.json'))
fe = json.load(open(f'{H}/results/iron_loss.json'))['TBM2G-07613D']
lg = np.load(f'{R}/modules/legs/results/walk_1p2.npz'); va = lg['va']
def iron_W(p, a, b):   # mean iron loss per joint (both motors), from knee joint speed trace
    n = np.abs(np.r_[lg['V'][:, va[3]], lg['V'][:, va[9]]]) * p['ratio'] * 60 / (2*math.pi) / 1000
    return p['nmot'] * float(np.mean(a*n + b*n**2))
d = np.load(f'{R}/modules/legs/grokbuild/results/walk_trace.npz'); tau = d['tau']
dt = float(d['state'][1, 0]-d['state'][0, 0]); seg = tau[int(1.0/dt):int(4.5/dt)]
DT = 0.01; sub = seg[::int(DT/dt)]; KN = {'l': 3, 'r': 9}
def run(p, pfe, t_end=3600):
    out = {}
    for s, c in KN.items():
        Tw = Th = W.T_AMB; t120 = None; tq = sub[:, c]
        for k in range(int(t_end/DT)):
            q = W.p_cu(p, tq[k % len(tq)], Tw) + pfe          # iron loss lumped into winding node (conservative)
            qwh = (Tw-Th)/p['Rwh']; Tw += DT*(q-qwh)/p['Cw']; Th += DT*(qwh-(Th-W.T_AMB)/p['Rha'])/p['Ch']
            if t120 is None and Tw >= 120: t120 = k*DT/60
        Pm = float(np.mean(W.p_cu(p, tq, 120.0)))+pfe
        out[s] = dict(rms_Nm=float(np.sqrt(np.mean(tq**2))), t120_min=t120, Tw60=Tw, Tss_est=W.T_AMB+Pm*(p['Rwh']+p['Rha']))
    out['tau_cont130'] = float(W.tau_cont(p)); return out
base = P0['knee']; res = {}
def opt(name, p, a=fe['a_W_per_krpm'], b=fe['b_W_per_krpm2']):
    pfe = iron_W(p, a, b); r = run(p, pfe); r['iron_W'] = pfe; res[name] = r
    print(f"{name:22s} iron {pfe:4.1f} W  tau_cont {r['tau_cont130']:5.0f}  " + '  '.join(
        f"{s}: rms {r[s]['rms_Nm']:.0f} t120 {r[s]['t120_min']} min Tw60 {r[s]['Tw60']:.0f} Tss {r[s]['Tss_est']:.0f}" for s in KN))
opt('base 07613D', base)
pa = copy.deepcopy(base); M = mot['TBM2G-08513']
pa.update(Km25=M['Km'][2], Kt=M['Kt_hot'][2], Rwh=0.6*M['Rth']/2)
pa['Cw'] = W.F_CU*2*M['mass']*W.C_CU; pa['Ch'] += (1-W.F_CU)*2*(M['mass']-mot['TBM2G-07613']['mass'])*W.C_FE
opt('(a) 2x 08513D', pa)       # iron loss: 07613D fit used ([EST], 085 frame not fitted D winding)
pb = copy.deepcopy(base); pb['Rha'] *= 0.5; opt('(b) shank path Rha/2', pb)
pd = copy.deepcopy(base); pd['Rha'] *= 12/40; opt('(d) fan h40', pd)
pad = copy.deepcopy(pa); pad['Rha'] *= 12/40; opt('(a)+(d)', pad)
pab = copy.deepcopy(pa); pab['Rha'] *= 0.5; opt('(a)+(b)', pab)
json.dump(res, open(f'{H}/results/knee_thermal.json', 'w'), indent=1, default=float)
