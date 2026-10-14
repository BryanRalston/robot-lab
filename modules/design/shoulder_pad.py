"""Shoulder impact pad R2 (R-042, Materials 5f8f149 R042_EPP_SHOULDER.md). RL Industrial Design.
Requirement: absorb E = 220 J (A44 strategy cap) with peak lateral force F <= 550 N·m / 0.060 m = 9.17 kN.
EPP: ARPRO 5170 curve 0.50/0.70/1.60 MPa @ 25/50/75 %, rate x1.45, hot (40 C pad face) x0.70 (-30 %), densification 60-70 %.
Force is checked cold/RT x rate; stroke/bottoming is checked hot x rate (softer foam must still stop 220 J by 65 % strain).
Honeycomb: constant crush stress, stroke = 0.72 t, rate x1.10, temp ~0, pre-crushed (no initial peak); design force 8.3 kN (10 % margin).
Crush strengths are [EST] HexWeb/Plascore 5052 1/4" cell class values; Materials to cite."""
import json,os,numpy as np
H=os.path.dirname(os.path.abspath(__file__))
E=220.0; FMAX=550/0.060; RATE=1.45; HOT=0.70; EPS_LIM=0.65
eps=np.array([0,0.25,0.50,0.75]); sig=np.array([0,0.50,0.70,1.60])*1e6
def s(e): return np.interp(e,eps,sig)
def w(e):  # J/m3 to strain e
    x=np.linspace(0,e,400); return np.trapezoid(s(x),x)
def epp(E_J,rho=80,F=FMAX):
    A=F/(s(EPS_LIM)*RATE)                     # area so RT peak at 65 % = F
    t=E_J/(w(EPS_LIM)*RATE*HOT*A)             # hot foam must absorb E by 65 %
    return dict(area_cm2=round(A*1e4),t_mm=round(t*1e3),foam_kg=round(A*t*rho,4))
BACK=0.008; SLEEVE=0.30  # kg PC backing (Materials); sleeve kg/m2
def sleeve(A,t): return SLEEVE*(A+4*np.sqrt(A)*t)
opts={}
for name,EJ in (('a_EPP80_220J',220),('c_EPP80_80J',80)):
    r=epp(EJ); A=r['area_cm2']/1e4; t=r['t_mm']/1e3
    per=r['foam_kg']+BACK+sleeve(A,t)
    opts[name]=dict(r,E_J=EJ,peak_kN=round(FMAX/1e3,2),M_Nm=550,kg_side=round(per,4),kg_pair=round(2*per,3),stack_mm=r['t_mm']+5+2,single_use='>50 % strain')
HC={'5052 1.6 pcf (26 kg/m3)':(26,0.31),'5052 2.3 pcf (37)':(37,0.62),'5052 3.1 pcf (50)':(50,0.90),'5052 4.5 pcf (72)':(72,1.65),'3003 3.1 pcf (50)':(50,0.83)}
FD=8.3e3; stroke=E/FD; t=stroke/0.72
for k,(rho,sc) in HC.items():
    A=FD/(sc*1e6*1.10); hc=A*t*rho
    skin=A*0.010*80          # 10 mm EPP 80 cosmetic/comfort layer
    spread=A*1.0e-3*2700*0.5 # 0.5 mm Al load spreader
    per=hc+skin+spread+BACK*min(1,A/0.0109)+sleeve(A,t+0.012)
    opts['b_HC '+k]=dict(area_cm2=round(A*1e4),t_mm=round(t*1e3),hc_kg=round(hc,4),kg_side=round(per,4),kg_pair=round(2*per,3),peak_kN=round(FD*1.10/1e3,2),M_Nm=round(FD*1.10*0.06),stack_mm=round(t*1e3)+10+1+2+5,single_use='yes (replaceable cartridge)')
# d hybrid: honeycomb 3.1 pcf core sized for 200 J + 15 mm EPP outer taking first ~20 J below FD
A=FD/(0.90e6*1.10); t2=(200/FD)/0.72
per=A*t2*50+A*0.015*80+A*1e-3*2700*0.5+BACK+sleeve(A,t2+0.017)
opts['d_hybrid HC3.1 + 15 mm EPP']=dict(area_cm2=round(A*1e4),t_mm=round(t2*1e3)+15,kg_side=round(per,4),kg_pair=round(2*per,3),peak_kN=round(FD*1.1/1e3,2),M_Nm=round(FD*1.1*0.06),stack_mm=round(t2*1e3)+15+1+2+5,single_use='HC yes; EPP multi-hit')
out=dict(P='P-051 (proposed)',E_J=E,F_allow_kN=round(FMAX/1e3,2),cap_pair_kg=0.10,options=opts,
 r1_40mm_EPP='FAIL: ~19.5 kN, ~1.17 kN·m (Materials)',pick='b_HC 5052 3.1 pcf (50)',measured=False)
json.dump(out,open(os.path.join(H,'shoulder_pad.json'),'w'),indent=1)
for k,v in opts.items(): print(k,v)
