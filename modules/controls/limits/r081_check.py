"""R-081 interim rule check (Thermal): P-042 carry x1.1, <=10 min carry then >=10 min unloaded, OR <=40 % duty over a
rolling 30 min. Worst-case compliance from hot start (64.4 N·m steady), rev B h 8 eta 0.7, 35 C, 3 h of cycles.
Worst 40 % arrangement = longest contiguous bout the rolling window allows: 12 min on / 18 min off.
Unloaded rest = idle 0 N·m; the 64.4 N·m loaded stand is shown as a conservative bound. Tighter numbers searched.
-> r081_check.json"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import carry_limit_gen as G, winding_model as W
p = W.load_params(knee='revB')['knee']; hot = G.steady(p, 64.4)
def peak(D, R, rest_tau, s=1.1, T=3 * 3600):
    Tw, Th = hot; pk = Tw; t = 0
    while t < T:
        Tw, Th, a, _ = G.run(p, Tw, Th, s, D, stop=False); pk = max(pk, a)
        Tw, Th, _, _ = G.run(p, Tw, Th, s, R, rest_tau, stop=False); t += D + R
    return round(float(pk), 1)
out = {'hot_start_Tw': round(hot[0], 1), 'rule_peaks_C': {}}
for nm, D, R in (('10on_10off', 600, 600), ('40pct_12on_18off', 720, 1080)):
    for rn, rt in (('idle0', 0.0), ('hold64', 64.4)):
        out['rule_peaks_C'][f'{nm} rest {rn}'] = peak(D, R, rt); print(nm, rn, out['rule_peaks_C'][f'{nm} rest {rn}'], flush=True)
# tighter: max bout D (s) with >=10 min idle rest, and with rest R for duty
out['tighter'] = {}
for R in (600,):
    for D in (480, 420, 360, 300, 240):
        pk = peak(D, R, 0.0); out['tighter'][f'D{D} R{R} idle'] = pk; print(D, R, pk, flush=True)
        if pk <= 120: break
for D, R in ((240, 360), (300, 450), (180, 270)):   # 40 % duty, shorter bouts
    out['tighter'][f'D{D} R{R} idle (40%)'] = peak(D, R, 0.0); print(D, R, out['tighter'][f'D{D} R{R} idle (40%)'], flush=True)
json.dump(out, open(os.path.join(HERE, 'r081_check.json'), 'w'), indent=1)
