"""R-143 rev 4b: fairing grille web temperature [EST hand model]. Thermal 389f91b basis: fins 48-53 mm deep,
~30 mm from grille, view F 0.5, grille inner eps 0.1, outer eps 0.9, Q 7.2 W/plate at duty, standing UA ~0.135, walking 0.15-0.24.
Grille web balance: h_i (T_air - T) + rad_in = h_o (T - Ta) + rad_out. T_air = Ta + f*dT_out
(f 0.5 mixed pocket air at the face, f 1.0 = web in the exhaust stream, worst)."""
import json, math
s=5.67e-8; cp=1005; rho=1.15
def chimney_dT(Q, H=0.12, A=1.2e-3, Cd=0.4):
    dT=20.0
    for _ in range(100):
        v=Cd*math.sqrt(2*9.81*H*dT/300); m=rho*v*A; dT=0.5*dT+0.5*Q/(m*cp)
    return dT, v
def web(Ta, Tfin, dTout, f, hi, ho):
    eps_in=1/(1/0.85+1/0.1-1); T=Ta+5
    for _ in range(400):
        K=lambda c:c+273.15
        qin=hi*(Ta+f*dTout-T)+eps_in*0.5*s*(K(Tfin)**4-K(T)**4)
        qout=ho*(T-Ta)+0.9*s*(K(T)**4-K(Ta)**4)
        T+=(qin-qout)/80
    return round(T,1)
cases={}
for Ta in (25.,35.):
  for mode in ('standing','walking'):
    for load in ('duty','carry'):
      UA=0.135 if mode=='standing' else 0.20
      Tcap=87.5   # derate: 75 start, 50 % at 85, off at 90 heat-sink -> base held ~85-90
      Tb=min(Ta+ (7.2/UA if load=='duty' else 1e9), Tcap) if load=='carry' else min(Ta+7.2/UA, Tcap)
      Q=UA*(Tb-Ta)
      if mode=='standing': dT,v=chimney_dT(Q)
      else: m=rho*0.3*3.2e-3; dT=Q/(m*cp); v=0.3
      hi,ho=(6,5) if mode=='standing' else (12,15)
      cases[f"{mode}_{load}_Ta{int(Ta)}"]=dict(T_base=round(Tb,1),Q_W=round(Q,1),dT_air_out=round(dT,1),v=round(v,2),
        grille_mixed=web(Ta,Tb,dT,0.5,hi,ho),grille_exhaust=web(Ta,Tb,dT,1.0,hi,ho))
json.dump(cases,open('r143_grille.json','w'),indent=1)
for k,v in cases.items(): print(k,v)
