"""R-043 / A46: smallest knee motor + heat path keeping the winding <= 120 C at 35 C. Controls' model (winding_model.py,
same 2-node run loop as knee_id_r1.py) on Legs ID traces walk_1p2_r7 (ref_ds25) and r4 carry_20kg_1p0 (carry torque x1.10
[EST] margin for the P-042x0.32 regen). Drives (2x Elmo, p_drv chart) ON the housing node (Thermal 9b9e169 basis).
Heat paths: fins = +0.025 m2 wetted at h (Thermal option C, ~0.05 kg/knee [EST]); fan = h 40 on the base housing (option D,
0.02 kg + 1-2 W [EST]). Cases: open (h 12), vented (A35 h 15), closed cover (+35 K on the air side, Thermal R1 penalty).
Candidates: datasheet TBM2G (v3/analysis/tbm2g.json from manual sec. 9), Kt_hot <= 0.085 so the 7565 rpm envelope holds.
-> results/knee_resize_r043.json"""
import os, sys, json, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f'{H}/../..')
sys.path.insert(0, f'{R}/modules/controls/thermal'); import winding_model as W
base = W.load_params(knee='07613D')['knee']; mot = W.MOT_CACHE
sel = json.load(open(f'{R}/modules/actuators/results/sizing.json'))['sel']['knee']
TR = {'walk_1p2_r7': ('r7/ref_ds25/walk_1p2_r7.npz', 1.0), 'carry_20kg_1p0_r4 x1.10': ('r4/carry_20kg_1p0.npz', 1.10)}
def cand(mw, path):
    M = mot[mw[:11]]
    p = W._p(M, mw, 2, sel['ratio'], sel['eta'], sel['area_cad'], sel['housing_cad'] * (int(mw[6:9]) / 76), sel['T_out'])
    dm = 2 * (M['mass'] - mot['TBM2G-07613']['mass']) + sel['housing_cad'] * (int(mw[6:9]) / 76 - 1)
    G0 = 1 / p['Rha']; p['Rha_open'] = 1 / (G0 + 12 * 0.025) if path == 'fins' else (1 / (40 * W.FINS * sel['area_cad']) if path == 'fan' else p['Rha'])
    p['h_scale'] = 1.0; return p, dm + (0.05 if path == 'fins' else 0.02 if path == 'fan' else 0)
def run(p, tau, om, dt, case, T=3600.0, DT=0.01):
    Rha = p['Rha_open'] * (12 / 15 if case == 'vented' else 1); ta_air = W.T_AMB + (35 if case == 'closed' else 0)
    idx = np.arange(0, len(tau), max(1, int(round(DT / dt)))); tq, w = tau[idx], om[idx]
    pfe = W.p_fe(p, w); pdr = W.p_drv(p, tq); Tw = Th = W.T_AMB; t120 = None
    for k in range(int(T / DT)):
        i = k % len(tq); q = W.p_cu(p, tq[i], Tw) + pfe[i]; qwh = (Tw - Th) / p['Rwh']
        Tw += DT * (q - qwh) / p['Cw']; Th += DT * (qwh + pdr[i] - (Th - ta_air) / Rha) / p['Ch']
        if t120 is None and Tw >= 120: t120 = round(k * DT / 60, 1)
    return dict(rms=round(float(np.sqrt(np.mean(tq ** 2))), 1), Tw60=round(Tw, 1), t120=t120)
C = [('TBM2G-07613D', 'none'), ('TBM2G-07613D', 'fins'), ('TBM2G-07613D', 'fan'), ('TBM2G-09408D', 'fins'), ('TBM2G-08513D', 'fins')]
out = {}
for mw, path in C:
    p, dm = cand(mw, path); key = f'{mw} + {path}'
    pc = dict(p); pc['Rha'] = p['Rha_open']
    o = dict(dmass_per_knee=round(dm, 3), Kt_hot=p['Kt'], Km=p['Km25'], tau_cont130=round(float(W.tau_cont(pc)), 1), cases={})
    for tn, (f, sc) in TR.items():
        d = np.load(f'{R}/modules/legs/results/{f}'); va = d['va']; dt = float(d['t'][1] - d['t'][0])
        for case in ('open', 'vented', 'closed'):
            o['cases'][f'{tn}/{case}'] = max((run(p, sc * d['TAU'][:, va[c]], d['V'][:, va[c]], dt, case) for c in (3, 9)), key=lambda r: r['Tw60'])
    o['pass_open_vented'] = all(v['Tw60'] <= 120 for k, v in o['cases'].items() if not k.endswith('closed'))
    out[key] = o; print(key, o['dmass_per_knee'], o['tau_cont130'], {k: v['Tw60'] for k, v in o['cases'].items()}, o['pass_open_vented'])
json.dump(out, open(f'{H}/results/knee_resize_r043.json', 'w'), indent=1)
