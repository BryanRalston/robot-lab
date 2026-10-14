"""Hand estimate: shoulder pad force vs energy with RL Materials' ARPRO 5170 curve (R042_EPP_SHOULDER.md, 5f8f149):
0.50/0.70/1.60 MPa at 25/50/75 % strain (ISO 844 quasi-static), x1.45 rate factor. Linear interpolation between points,
0 at 0 %; beyond 75 % extrapolated with the 50-75 % slope (3.6 MPa/strain) [EST, densification not sourced].
Bearing: IKO CRBH 7013 A C0 27.7 kN, Dpw 85 mm [EST], M = F x 0.06 m (v3.py)."""
import numpy as np, json
EPS=np.array([0,.25,.5,.75,.95]); SIG=np.array([0,.5,.7,1.6,1.6+3.6*.2])*1e6; RATE=1.45
C0=27700; DPW=0.085; ARM=0.06; GATE_F=9170.
def curve(A,t,n=2000):
    e=np.linspace(0,.95,n); s=np.interp(e,EPS,SIG)*RATE; F=s*A; E=np.concatenate([[0],np.cumsum(.5*(F[1:]+F[:-1])*np.diff(e)*t)]); return e,F,E
def at_energy(A,t,Ej):
    e,F,E=curve(A,t); i=np.searchsorted(E,Ej); return dict(E_J=Ej,strain=round(float(e[i]),3),F_N=round(float(F[i])),M_Nm=round(float(F[i])*ARM),fs_radial=round(C0/(F[i]+2*F[i]*ARM/DPW),2),fs_axial=round(C0/(2*F[i]*ARM/DPW+.44*F[i]),2))
def energy_at_force(A,t,Fmax):
    e,F,E=curve(A,t); i=np.searchsorted(F,Fmax)-1; return round(float(E[max(i,0)]),1), round(float(e[max(i,0)]),3)
A40=109e-4; t40=0.040
out=dict(pad40_109cm2={str(Ej):at_energy(A40,t40,Ej) for Ej in (80,150,215.6,220)},
 pad40_E_at_7p10kN=energy_at_force(A40,t40,7100), pad40_E_at_gate_9p17kN=energy_at_force(A40,t40,GATE_F))
# sizing: for E=220 J at peak F<=9.17 kN, thickness needed vs area (strain limited where 1.45*sigma*A = F)
siz={}
for Acm2 in (60,80,109,150,200):
    A=Acm2*1e-4; t=np.arange(0.02,0.25,0.001)
    ok=[tt for tt in t if energy_at_force(A,tt,GATE_F)[0]>=220]; siz[Acm2]=round(float(ok[0])*1e3) if ok else None
out['t_mm_for_220J_at_9p17kN_by_area_cm2']=siz
siz2={}
for Acm2 in (60,80,109,150):
    A=Acm2*1e-4; t=np.arange(0.02,0.25,0.001); ok=[tt for tt in t if energy_at_force(A,tt,7100)[0]>=220]; siz2[Acm2]=round(float(ok[0])*1e3) if ok else None
out['t_mm_for_220J_at_7p10kN_by_area_cm2']=siz2
# bearing needed if 40 mm pad kept and 220 J: required C0 for fs_radial 1.25
F=at_energy(A40,t40,220)['F_N']; out['C0_needed_fs1p25_radial_at_220J_N']=round(1.25*(F+2*F*ARM/DPW))
json.dump(out,open('epp_pad_estimate.json','w'),indent=1); print(json.dumps(out,indent=1))
