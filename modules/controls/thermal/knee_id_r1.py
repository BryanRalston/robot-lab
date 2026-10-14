"""A40 knee re-run on RL Legs inverse-dynamics plan trajectories (vs WBC r6 trace), 07613D baseline vs D69.
Thermal 26412c7 limits: target <=120, derate 130->145, off 150. 35 °C, open housing, drives off housing (P-027/D69).
Each ID plan is looped for 60 min; iron loss from the plan's own knee speed. Light (numpy). -> knee_id_r1.json"""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winding_model as W
L = os.path.join(W.ROOT, 'modules/legs/results')
TRACES = {   # name: (file, note)
    'walk 1.2 ID r7 ref_ds25 (RL reference)': ('r7/ref_ds25/walk_1p2_r7.npz', 'make_model REF_DIR; DS 25 %'),
    'walk 1.2 ID r4': ('r4/walk_1p2.npz', 'latest r4 sizing set'),
    'walk 1.2 ID r2 plan (WBC slice source)': ('r2/walk_1p2_r2.npz', 'plan tracked by WBC r6'),
    'carry 20 kg 1.0 ID r4': ('r4/carry_20kg_1p0.npz', 'payload 0.25 m, R-014'),
    'carry 20 kg ID r2 plan (WBC carry source)': ('r2/carry_20kg_r2.npz', 'plan tracked by WBC carry'),
}
def run(p, tau, om, dt_src, T=3600.0, DT=0.01):
    idx = np.arange(0, len(tau), max(1, int(round(DT / dt_src))))
    tq, w = tau[idx], om[idx]; pfe = W.p_fe(p, w)
    Tw = Th = W.T_AMB; t = {}
    for k in range(int(T / DT)):
        i = k % len(tq); q = W.p_cu(p, tq[i], Tw) + pfe[i]
        qwh = (Tw - Th) / p['Rwh']; Tw += DT * (q - qwh) / p['Cw']; Th += DT * (qwh - (Th - W.T_AMB) / p['Rha']) / p['Ch']
        for lim in (W.T_TARGET, W.T_DERATE, W.T_TRIP):
            if lim not in t and Tw >= lim: t[lim] = round(k * DT / 60, 1)
    return dict(rms=round(float(np.sqrt(np.mean(tq ** 2))), 1), iron_W=round(float(np.mean(pfe)), 2), Tw60=round(Tw, 1),
                t120=t.get(W.T_TARGET), t130=t.get(W.T_DERATE), t150=t.get(W.T_TRIP))
P = {'07613D': W.load_params(knee='07613D')['knee'], 'D69': W.load_params(knee='D69')['knee']}
out = {}
for name, (f, note) in TRACES.items():
    d = np.load(os.path.join(L, f)); va = d['va']; dt = float(d['t'][1] - d['t'][0])
    out[name] = dict(file=f, note=note)
    for opt, p in P.items():
        out[name][opt] = {s: run(p, d['TAU'][:, va[c]], d['V'][:, va[c]], dt) for s, c in (('L', 3), ('R', 9))}
    print(name, json.dumps({o: out[name][o] for o in P}))
for opt, p in P.items(): out[f'tau_cont_130_{opt}'] = round(float(W.tau_cont(p)), 1)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knee_id_r1.json'), 'w'), indent=1)
print({k: v for k, v in out.items() if k.startswith('tau_cont')})
