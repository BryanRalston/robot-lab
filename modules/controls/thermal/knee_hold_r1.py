"""R-062 condition (3): worst STANDING P-042 carry hold on the D69 rev B knee (2x 07613D + 0.0703 m2 CAD fins,
Actuators fbd762b on act-work), drives off housing, 35 °C. Own model (winding_model params), constant torque, no motion
(no iron loss). Housing-air: G = h*(A_bare + eta_f*A_fin); the size.py x2 'fins' factor stood in for fins, so it is DROPPED.
Hold torque: worst stance knee torque in the 20 kg carry ID plans at standing (t=0, double support, plan crouch):
r2 carry_20kg_r2 L knee 64.4 N·m (knee 66.6°); p042 regen 58.5; r4 59.8. Also x1.10. -> knee_hold_r1.json"""
import os, sys, json, copy, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winding_model as W
p0 = W.load_params(knee='07613D')['knee']
A_BARE = 1.0 / (p0['Rha'] * W.H_AIR * W.FINS)   # = sizing area_cad
A_FIN = 0.0703
def run(tau, h, eta, fan=False, T=3600.0, DT=0.05):
    p = copy.deepcopy(p0); p['Rha'] = 1.0 / (h * (A_BARE + eta * A_FIN))
    Tw = Th = W.T_AMB
    for _ in range(int(T / DT)):
        q = W.p_cu(p, tau, Tw); qwh = (Tw - Th) / p['Rwh']
        Tw += DT * (q - qwh) / p['Cw']; Th += DT * (qwh - (Th - W.T_AMB) / p['Rha']) / p['Ch']
    Ts = W.T_AMB   # steady state, fixed point with T-dependent copper
    for _ in range(200): Ts = W.T_AMB + W.p_cu(p, tau, Ts) * (p['Rwh'] + p['Rha'])
    return dict(Rha=round(p['Rha'], 3), tau_cont130=round(float(W.tau_cont(p)), 1), Tw60=round(Tw, 1), Tss=round(float(Ts), 1),
                vs120=round(float(Ts) - 120, 1), vs130=round(float(Ts) - 130, 1))
out = dict(A_bare=round(A_BARE, 4), A_fin=A_FIN, cases={})
for tau in (64.4, 70.8):
    for h in (8.0, 10.0):
        for eta in (1.0, 0.7):
            k = f'tau {tau} h {h} eta {eta}'; out['cases'][k] = run(tau, h, eta); print(k, out['cases'][k])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knee_hold_r1.json'), 'w'), indent=1)
