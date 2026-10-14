"""Shoulder impact pad R2 (R-042, Materials 5f8f149 R042_EPP_SHOULDER.md). RL Industrial Design.
Requirement: absorb E = 220 J (A44 strategy cap) with peak lateral force F <= 550 N·m / 0.060 m = 9.17 kN.
EPP: ARPRO 5170 curve 0.50/0.70/1.60 MPa @ 25/50/75 %, rate x1.45, hot (40 C pad face) x0.70 (-30 %), densification 60-70 %.
Force is checked cold/RT x rate; stroke/bottoming is checked hot x rate (softer foam must still stop 220 J by 65 % strain).
Honeycomb: constant crush stress, stroke = 0.72 t, rate x1.10, temp ~0, pre-crushed (no initial peak); design force 8.3 kN (10 % margin).
Crush strengths are [EST] HexWeb/Plascore 5052 1/4" cell class values; Materials to cite."""
import json,os,numpy as np
H=os.path.dirname(os.path.abspath(__file__))
E=265.0; FMAX=550/0.060; RATE=1.45; HOT=0.70; EPS_LIM=0.65
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
for name,EJ in (('a_EPP80_265J',265),('c_EPP80_80J',80)):
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
A=FD/(0.90e6*1.10); t2=(245/FD)/0.72
per=A*t2*50+A*0.015*80+A*1e-3*2700*0.5+BACK+sleeve(A,t2+0.017)
opts['d_hybrid HC3.1 + 15 mm EPP']=dict(area_cm2=round(A*1e4),t_mm=round(t2*1e3)+15,kg_side=round(per,4),kg_pair=round(2*per,3),peak_kN=round(FD*1.1/1e3,2),M_Nm=round(FD*1.1*0.06),stack_mm=round(t2*1e3)+15+1+2+5,single_use='HC yes; EPP multi-hit')
# b2 R3 (Controls 03fc980: 265 J; contact at/above centre, 10-15 mm below when hip-first): 3.1 pcf, 84 cm2 as 80 w x 105 h, centre 5 mm low; EPP face 6 mm
A=FD/(0.90e6*1.10)
per=A*t*50+A*0.006*80+A*1e-3*2700*0.5+BACK+sleeve(A,t+0.008)
opts['b2_R3 HC 3.1 pcf 80x105, 6 mm EPP face']=dict(area_cm2=round(A*1e4),footprint_mm='80 w x 105 h, centre 5 mm below shoulder axis',t_mm=round(t*1e3),kg_side=round(per,4),kg_pair=round(2*per,3),peak_kN=round(FD*1.1/1e3,2),M_Nm=round(FD*1.1*0.06),stack_mm=round(t*1e3)+6+1+2+5,coverage='contact band +15/-15 mm about centre stays >= 37 mm inside top/bottom edges (52.5 mm half-height)',single_use='yes')
# R4 (Materials 8a3cc66, R-049): HexWeb CR III 5052 4.5 pcf crush 1.79 MPa (cited), dynamic factor up to 1.30; EPP face in series (no energy, no peak credit)
SC=1.79e6; DYN=1.30; a=0.062; tc=0.057; EFF=0.72
A4=a*a; Fpk=SC*DYN*A4; Est=SC*A4*EFF*tc
items4=dict(core_HC_4p5pcf=A4*tc*72, spreader_Al_0p5mm_80x100_ribbed=0.080*0.100*0.5e-3*2700,
 side_guides_4_PC_corner_posts=0.004, backing_PC_1p5_62x62_with_M4_inserts=A4*1.5e-3*1200,
 EPP80_face_6mm_80x100=0.080*0.100*0.006*80, sleeve_TPU_nylon_face_only=0.005, low_e_foil_and_4_standoffs=0.001)
per4=sum(items4.values())
opts['R4 HC 4.5 pcf 62x62x57 cartridge']=dict(area_cm2=round(A4*1e4,1),core_mm='62 x 62 x 57 (pre-crushed)',peak_kN_x1p3=round(Fpk/1e3,2),M_Nm_x1p3=round(Fpk*0.06),pass_peak=Fpk<=FMAX,
 E_J_x1p0=round(Est),pass_energy=Est>=E,face_plate_mm='80 w x 100 h, centre 5 mm below shoulder axis',
 coverage='contact band +-15 mm: >= 35 mm inside plate top/bottom edges; contact centre stays <= 15 mm off core centre (16 mm inside core edge)',
 thermal='>= 5 mm air gap vented top + bottom, low-e foil on bulkhead (pad face ~47-50 C, Thermal)',
 mass_items_kg_side={k:round(v,4) for k,v in items4.items()},kg_side=round(per4,4),kg_pair=round(2*per4,3),stack_mm=1.5+57+0.5+6+5,single_use='yes')
out=dict(P='P-051 (proposed)',E_J=E,F_allow_kN=round(FMAX/1e3,2),cap_pair_kg=0.10,options=opts,
 r1_40mm_EPP='FAIL: ~19.5 kN, ~1.17 kN·m (Materials)',pick='R4 HC 4.5 pcf 62x62x57 cartridge',measured=False)
json.dump(out,open(os.path.join(H,'shoulder_pad.json'),'w'),indent=1)
for k,v in opts.items(): print(k,v)
