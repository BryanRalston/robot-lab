"""R-070 pick-pose (deep squat) knee limit table from the A40 winding model, as-built D69 rev B default
(winding_model.load_params(): fbd762b 0.0703 m2 fins, x2 dropped, h 8 still air, eta_f 0.7, drives off housing, 35 C).
Constant knee torque per leg (both 07613D share it), no motion -> no iron loss. Winding target 120 C (derate at 130).
Start states: 'hot' = steady state at the worst standing P-042 carry hold 64.4 N·m (2e2d593), 'cold' = 35 C soak.
dwell = time from start until Tw = 120 C. Recovery: repeat cycles (dwell D at tau, rest R at the 64.4 N·m hold)
from the hot start for 2 h; R = shortest rest with peak Tw <= 120 C, for D = full and 50 % of the hot dwell.
Light (pure python, ~1 min). -> pick_limit_table.json"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'thermal'))
import winding_model as W
p = W.load_params()['knee']; DT = 0.1; TA = W.T_AMB; TGT = W.T_TARGET; HOLD = 64.4
def step(Tw, Th, tau):
    q = W.p_cu(p, tau, Tw); qwh = (Tw - Th) / p['Rwh']
    return Tw + DT * (q - qwh) / p['Cw'], Th + DT * (qwh - (Th - TA) / p['Rha']) / p['Ch']
def steady(tau):
    Tw = Th = TA
    for _ in range(int(4 * 3600 / DT)): Tw, Th = step(Tw, Th, tau)
    return Tw, Th
def dwell(tau, s, tmax=3600.0):
    Tw, Th = s; t = 0.0
    while t < tmax:
        Tw, Th = step(Tw, Th, tau); t += DT
        if Tw >= TGT: return round(t, 1)
    return None   # >1 h = unlimited
def cycles_ok(tau, D, R, s, T=7200.0):
    Tw, Th = s; t = 0.0; pk = Tw
    while t < T:
        for _ in range(int(D / DT)): Tw, Th = step(Tw, Th, tau); pk = max(pk, Tw)
        for _ in range(int(R / DT)): Tw, Th = step(Tw, Th, HOLD)
        t += D + R
    return pk <= TGT
def rest_needed(tau, D, s):
    lo, hi = 0.0, 3600.0
    if not cycles_ok(tau, D, hi, s): return None
    while hi - lo > 2.0:
        mid = 0.5 * (lo + hi); (hi, lo) = (mid, lo) if cycles_ok(tau, D, mid, s) else (hi, mid)
    return round(hi)
hot = steady(HOLD); cold = (TA, TA)
rows = []
for tau in (80, 100, 120, 150, 180, 220, 260, 300, 345):
    dh, dc = dwell(tau, hot), dwell(tau, cold)
    r = dict(tau_Nm=tau, dwell_hot_s=dh, dwell_cold_s=dc)
    if dh:
        r['rest_full_s'] = rest_needed(tau, dh, hot); r['rest_half_s'] = rest_needed(tau, round(0.5 * dh, 1), hot)
    rows.append(r); print(r)
out = dict(basis=__doc__.split('\n')[1], Rha=round(p['Rha'], 3), tau_cont120=round(float(W.tau_cont(p, t_w=120)), 1),
           hot_start_Tw=round(hot[0], 1), hot_start_Th=round(hot[1], 1), rows=rows)
json.dump(out, open(os.path.join(HERE, 'pick_limit_table.json'), 'w'), indent=1); print(out['tau_cont120'], hot)
