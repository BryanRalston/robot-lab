"""Tables for CARRY_LIMIT.md: full P-042 profile sim (dt 0.01, copper + iron) at h 8/10/12, eta 0.7, x1.0/x1.1.
Hot start = steady 64.4 N·m hold. Duty: carry D / rest R at 64.4 (and idle 0 N·m) cycles, 3 h -> max peak <= 120.
-> carry_limit_table.json"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'thermal'))
import winding_model as W
d = np.load(os.path.join(W.ROOT, 'modules/legs/results/p042/carry_20kg_1p0.npz')); va = d['va']; dt0 = float(d['t'][1] - d['t'][0])
c = max((3, 9), key=lambda c: np.mean(d['TAU'][:, va[c]] ** 2)); DT = 0.02
idx = np.arange(0, len(d['t']), int(round(DT / dt0))); TQ = np.abs(d['TAU'][idx, va[c]]); OM = d['V'][idx, va[c]]
p8 = W.load_params(knee='revB')['knee']; PFE = W.p_fe(p8, OM)
prof = {'rms_x1.0': round(float(np.sqrt(np.mean(TQ ** 2))), 2), 'pfe_mean_W': round(float(PFE.mean()), 3), 'knee_col': int(c), 'cycle_s': round(len(TQ) * DT, 2)}
def run(p, Tw, Th, s, T, rest_tau=None, stop=True):
    """carry (rest_tau None) or rest; returns Tw, Th, peak, t120 (first time >= 120 or None)."""
    n = int(T / DT); pk = Tw; t120 = None; Rwh, Rha, Cw, Ch = p['Rwh'], p['Rha'], p['Cw'], p['Ch']
    for k in range(n):
        if rest_tau is None: q = W.p_cu(p, TQ[k % len(TQ)] * s, Tw) + PFE[k % len(TQ)] * s
        else: q = W.p_cu(p, rest_tau, Tw)
        qwh = (Tw - Th) / Rwh; Tw += DT * (q - qwh) / Cw; Th += DT * (qwh - (Th - W.T_AMB) / Rha) / Ch
        if Tw > pk: pk = Tw
        if t120 is None and Tw >= 120:
            t120 = (k + 1) * DT
            if stop: break
    return Tw, Th, pk, t120
def steady(p, tau):
    Ts = W.T_AMB
    for _ in range(200): Ts = W.T_AMB + W.p_cu(p, tau, Ts) * (p['Rwh'] + p['Rha'])
    Th = W.T_AMB + W.p_cu(p, tau, Ts) * p['Rha']; return Ts, Th
def duty_ok(p, s, D, R, rest_tau, start, T=3 * 3600):
    Tw, Th = start; t = 0
    while t < T:
        Tw, Th, pk, t1 = run(p, Tw, Th, s, D)
        if t1: return False
        Tw, Th, _, _ = run(p, Tw, Th, s, R, rest_tau); t += D + R
    return True
def rest_req(p, s, D, rest_tau, start):
    if not duty_ok(p, s, D, 3600, rest_tau, start, T=4 * 3600): return None
    lo, hi = 0.0, 3600.0
    while hi - lo > 10: m = (lo + hi) / 2; (lo, hi) = (lo, m) if duty_ok(p, s, D, m, rest_tau, start) else (m, hi)
    return round(hi)
def main(HS):
    out = dict(profile=prof, basis='rev B as built 0.0703 m2, eta_f 0.7, 35 C, drives off, target 120 C', rows=[])
    for h in HS:
        p = W.load_params(knee='revB', h=h)['knee']; hot = steady(p, 64.4)
        for s in (1.0, 1.1):
            r = dict(h=h, scale=s, hot_Tw=round(hot[0], 1))
            r['t_hot_s'] = run(p, *hot, s, 4 * 3600)[3]; r['t_cold_s'] = run(p, W.T_AMB, W.T_AMB, s, 4 * 3600)[3]
            r['tau_cont120'] = round(float(W.tau_cont(p, t_w=120)), 1)
            if r['t_hot_s']:
                for D in (60, 120, 300):
                    if D < r['t_hot_s']:
                        for rn, rt in (('hold64', 64.4), ('idle0', 0.0)):
                            R = rest_req(p, s, D, rt, hot); r[f'rest_{rn}_D{D}'] = R
                            r[f'duty_{rn}_D{D}'] = None if R is None else round(D / (D + R), 3)
            out['rows'].append(r); print(r, flush=True)
    json.dump(out, open(os.path.join(HERE, 'carry_limit_table.json'), 'w'), indent=1)
if __name__ == '__main__':
    import sys as _s; main([float(x) for x in _s.argv[1:]] or [8.0, 10.0, 12.0])
