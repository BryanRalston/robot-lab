"""R-069: Controls check of Actuators knee fin rev C (r069_knee_fins_revc.py, cad/knee_twin_housing_finned_revc.step, 6b86723)
vs as-built rev B (0.0703 m2). Model: A40 2-node (winding_model knee='revB'/'revC' convention G = h*(A_bare + eta_f*A_fin)),
drives OFF housing, 35 C. (0) geometry: re-measure added area from the STEP files (net of fin root footprint), fin thickness,
analytic straight-fin efficiency. (1) P-042 carry_20kg_1p0 x1.1 looped 60 min (h 12 added for comparison with knee_revB_cad h12 rows) (knee_size_r1 method: worse knee by RMS, copper +
iron loss), h 8/10, eta_f 0.7/1.0. (2) standing hold 64.4 / 70.8 N·m (knee_hold_r1 method), h 8, eta 0.7/1.0.
(3) tau_cont at 120 C and pick-limit dwell at 150/180 N·m (pick_limit_gen method, hot start = 64.4 steady). -> knee_revC_check.json"""
import os, sys, json, copy, math, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import winding_model as W
ACT = os.path.join(W.ROOT, 'modules/actuators')
out = {}
# (0) geometry
try:
    import cadquery as cq
    A = {k: cq.importers.importStep(os.path.join(ACT, 'cad', f)).val().Area() * 1e-6 for k, f in
         (('bare', 'knee_twin_housing.step'), ('revB', 'knee_twin_housing_finned_revb.step'), ('revC', 'knee_twin_housing_finned_revc.step'))
         if os.path.exists(os.path.join(ACT, 'cad', f))}
    out['geom_step_area_m2'] = {k: round(v, 4) for k, v in A.items()}
    out['geom_added_m2'] = {k: round(v - A['bare'], 4) for k, v in A.items() if k != 'bare'}
except Exception as e:
    out['geom_error'] = repr(e)
def fin_eff(t_mm, L_mm, h, k=167.0):   # straight rectangular fin, corrected length, 6061-T6 k 167 W/mK
    m = math.sqrt(2 * h / (k * t_mm * 1e-3)); Lc = (L_mm + t_mm / 2) * 1e-3; return math.tanh(m * Lc) / (m * Lc)
out['fin_eff_analytic'] = {f't{t} L{L} h{h}': round(fin_eff(t, L, h), 3) for t in (1.0, 1.5) for L in (9.0, 17.0) for h in (8.0, 10.0)}
p0 = W.load_params(knee='07613D')['knee']; A_BARE = 1.0 / (p0['Rha'] * W.H_AIR * W.FINS)
AF = {'revB': W.REVB_A_FIN, 'revC': W.REVC_A_FIN}
def par(rev, h, eta):
    p = copy.deepcopy(p0); p['Rha'] = 1.0 / (h * (A_BARE + eta * AF[rev])); return p
out['A_bare'] = round(A_BARE, 4)
# (1) P-042 carry x1.1
d = np.load(os.path.join(W.ROOT, 'modules/legs/results/p042/carry_20kg_1p0.npz')); va = d['va']; dt = float(d['t'][1] - d['t'][0])
c = max((3, 9), key=lambda c: np.mean(d['TAU'][:, va[c]] ** 2)); tau = np.abs(d['TAU'][:, va[c]]) * 1.1; om = d['V'][:, va[c]]
DT = 0.01; idx = np.arange(0, len(tau), max(1, int(round(DT / dt)))); tq = tau[idx]; pfe = W.p_fe(p0, om[idx])
keys = [(r, h, e) for r in AF for h in (8.0, 10.0, 12.0) for e in (0.7, 1.0)]; ps = [par(*k) for k in keys]
Rha = np.array([p['Rha'] for p in ps]); n, ratio, eta, Km = p0['nmot'], p0['ratio'], p0['eta'], p0['Km25']
Tw = np.full(len(ps), W.T_AMB); Th = Tw.copy(); mx = Tw.copy()
for k in range(int(3600 / DT)):
    i = k % len(tq); q = n * (tq[i] / (ratio * eta * n) / (Km / np.sqrt(1 + W.ALPHA_CU * (Tw - 25)))) ** 2 + pfe[i]
    qwh = (Tw - Th) / p0['Rwh']; Tw = Tw + DT * (q - qwh) / p0['Cw']; Th = Th + DT * (qwh - (Th - W.T_AMB) / Rha) / p0['Ch']; mx = np.maximum(mx, Tw)
out['carry_p042_x1.1'] = dict(knee_col=int(c), rms=round(float(np.sqrt(np.mean(tq ** 2))), 1),
    cases={f'{r} h{h} eta{e}': dict(Tw60=round(float(t), 1), peak=round(float(m), 1), vs120=round(float(m) - 120, 1)) for (r, h, e), t, m in zip(keys, Tw, mx)})
# (2) standing hold
def hold(p, tau, T=3600.0, DT=0.05):
    Tw = Th = W.T_AMB
    for _ in range(int(T / DT)):
        q = W.p_cu(p, tau, Tw); qwh = (Tw - Th) / p['Rwh']; Tw += DT * (q - qwh) / p['Cw']; Th += DT * (qwh - (Th - W.T_AMB) / p['Rha']) / p['Ch']
    Ts = W.T_AMB
    for _ in range(200): Ts = W.T_AMB + W.p_cu(p, tau, Ts) * (p['Rwh'] + p['Rha'])
    return dict(Tw60=round(Tw, 1), Tss=round(float(Ts), 1), vs120=round(float(Ts) - 120, 1), vs130=round(float(Ts) - 130, 1))
out['hold'] = {f'{r} tau{t} h8 eta{e}': hold(par(r, 8.0, e), t) for r in AF for t in (64.4, 70.8) for e in (0.7, 1.0)}
# (3) ratings + pick dwell (pick_limit_gen method)
out['ratings_h8'] = {f'{r} eta{e}': dict(Rha=round(par(r, 8, e)['Rha'], 3), tau_cont120=round(float(W.tau_cont(par(r, 8, e), t_w=120)), 1),
                     tau_cont130=round(float(W.tau_cont(par(r, 8, e))), 1)) for r in AF for e in (0.7, 1.0)}
def pick(p, DTp=0.1):
    def step(Tw, Th, t):
        q = W.p_cu(p, t, Tw); qwh = (Tw - Th) / p['Rwh']; return Tw + DTp * (q - qwh) / p['Cw'], Th + DTp * (qwh - (Th - W.T_AMB) / p['Rha']) / p['Ch']
    Tw = Th = W.T_AMB
    for _ in range(int(4 * 3600 / DTp)): Tw, Th = step(Tw, Th, 64.4)
    hot = (Tw, Th); res = dict(hot_Tw=round(Tw, 1), hot_Th=round(Th, 1))
    for tau in (150, 180):
        for nm, s in (('hot', hot), ('cold', (W.T_AMB, W.T_AMB))):
            a, b = s; t = 0.0
            while a < W.T_TARGET and t < 3600: a, b = step(a, b, tau); t += DTp
            res[f'dwell_{nm}_{tau}_s'] = round(t, 1) if t < 3600 else None
    return res
out['pick_h8_eta0.7'] = {r: pick(par(r, 8.0, 0.7)) for r in AF}
json.dump(out, open(os.path.join(HERE, 'knee_revC_check.json'), 'w'), indent=1); print(json.dumps(out, indent=1))
