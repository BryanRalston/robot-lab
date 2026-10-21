"""D99 rev r75b (Legs L84 r2 6a3d84c: striker arm 24x18 x 63 mm cantilever, tibia ring ø51x3x24 bonded + 2x ø6 pins). D99 (from D98; T&R 8c7ac56 L60 rev C pass limits): bottoming energy >=92.5 J at 25 %, design 44.1 J, rate factor, speed cap, mass.
D98: r75 PU knee stop - sizing for 66 J x >=1.4, placement in model_v4 (Legs L78 sweep method), STEP of pads + seats.
Basis: Controls b5890e1 worst 6.37 rad/s at stop contact (135 deg); I_body 2.71 kg m^2/knee (D97 fit);
reflected rotor J_r(q) = 2 x (0.576 [TBM2G-07613D, tbm2g p.284] + 0.2 [EST hub]) e-4 x N(q)^2, N(q)=2*pi*arm(q)/5 (RV12x5),
arm(q) from model_v4 knee linkage (lever r47.5 clock 0, trunnion x-130 z+270). Flex sign: model_v4 knee joint axis +y, q>0
moves the shank to -x (q=90: shank x -420..28), +x forward (foot toe +130) -> arm(135)=18.4 mm.
PU: Freelin-Wade PUR90A ASTM D575 160/325/705/1050/1380/1690 psi @2..25 %; 25 % dynamic limit (Gallagher); SF>=0.5 (laminated, steel shims).
Quasi-static energy method; PU rate stiffening not included [EST]."""
import os,sys,json,math,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq
eps=np.array([0,.02,.05,.10,.15,.20,.25]); sig=np.array([0,160,325,705,1050,1380,1690])*0.0068948
cum=np.concatenate([[0],np.cumsum(np.diff(eps)*(sig[1:]+sig[:-1])/2)])          # J/cm^3
def arm(q):
    t=math.radians(q); p=(-47.5*math.sin(t),-47.5*math.cos(t)); u=(p[0]+130,p[1]-270); n=math.hypot(*u)
    return abs(p[0]*u[1]/n-p[1]*u[0]/n)
def L(q):
    t=math.radians(q); return math.hypot(-47.5*math.sin(t)+130,-47.5*math.cos(t)-270)
Jr1=2*(0.576e-4+0.2e-4); N=lambda q:2*math.pi*arm(q)/5.0; Jref=lambda q:Jr1*N(q)**2
w=6.37; Ib=2.71; C=130.0   # D99: contact 130 so the 92.5 J fault stays inside 25 % with bottoming moment x rate within T&R C2
QMAX=143.6; R=75.0
Jc=Jref(C); E_phys=0.5*(Ib+Jc)*w**2; E_des=44.1; E_req=92.5; E_fault=92.5   # rev B: Controls 3d1da26 powered fall set max 40.1 J x 1.1; motors-off fault 92.5 J
NL,tl,ts=7,10.17,1.0; T=NL*tl                                   # 6 x 9.25 mm PU, 5 x 1.5 mm shims, ø6 guide pin, 3 mm end plates
AY,AR=24.0,20.0; A=2*(AY*AR-math.pi*9)                                    
V=A*T/1000; E25=cum[-1]*V
def at(E):
    e=float(np.interp(E/V,cum,eps)); s=float(np.interp(e,eps,sig)); return dict(E_J=E,strain=round(e,3),knee_deg=round(C+math.degrees(e*T/R),2),
        pad_force_kN=round(s*A/1000,2),torque_Nm=round(s*A*R/1000))
k25=(sig[-1]-sig[-2])/(eps[-1]-eps[-2])
def fault(E):
    x=0.0; dE=E/V-cum[-1]
    if dE>0: x=(-sig[-1]+math.sqrt(sig[-1]**2+2*k25*dE))/k25
    e=0.25+x; s_=sig[-1]+k25*x; return dict(E_J=E,strain=round(e,3),knee_deg=round(C+math.degrees(e*T/R),2),pad_force_kN=round(s_*A/1000,2),torque_Nm=round(s_*A*R/1000),note='beyond 25 %: tangent-slope continuation of the D575 curve [EST]; inspect/replace pads after')
curve=[dict(strain=float(e),knee_deg=round(C+math.degrees(e*T/R),2),torque_Nm=round(s*A*R/1000),pad_force_kN=round(s*A/1000,2),energy_J=round(c*V,1)) for e,s,c in zip(eps,sig,cum)]
# alt: contact earlier so 830 N.m at 66 J with E25>=92.4 and 25 % at <=143.6
def alt(c):
    Tt=R*math.radians(QMAX-c)/0.25; Aa=E_req/(cum[-1]*Tt/1000); Va=Aa*Tt/1000
    e=float(np.interp(E_des/Va,cum,eps)); return dict(contact_deg=c,T_mm=round(Tt,1),A_mm2=round(Aa),torque_66J_Nm=round(float(np.interp(e,eps,sig))*Aa*R/1000))
alts=[alt(c) for c in (135,133,132,131,130)]
# rotor reaction on the stop: knee decel alpha = tau_pad/(Ib+Jc); rotor needs J_r1*N*alpha at the rotor -> from screw nut.
pk=at(E_des); alpha=pk['torque_Nm']/(Ib+Jc); tau_rot_knee=Jc*alpha                   # N.m about knee, +flexion on the shank
F_rot_pair=tau_rot_knee/(arm(C)/1000); F_rot_screw=F_rot_pair/2
F_mot_pair=7267.0   # D96 K_PEAK pair motor peak
dLdq=(L(C+0.5)-L(C-0.5))/1.0                                                          # mm/deg: screw shortens with flexion at 135
mass=(V*1.13+(NL-1)*2*(AY*AR-math.pi*9)*ts*2.8e-3+2*2*(AY+2)*(AR+2)*2*2.8e-3+2*(AY*20*8+18*24*63)*2.8e-3+2*30*26*6*2.8e-3+40)/1000   # own-estimate cross-check: PU, 7075 shims, end plates, strikers (lug + 24x18x63 arm), seats, bar 40 g [EST]
MASS_LINE_ROBOT=0.344+0.143   # P-159 line per Legs L84 r2 (6a3d84c): D99 0.344 + Legs leg-side growth 0.143 (ring 28.7 + arm deepening 38 + tie boss 5 g/knee)
res=dict(J_reflected_kgm2={q:round(Jref(q),3) for q in (0,30,60,75,90,120,135,143.6)},arm_mm_135=round(arm(C),1),N_135=round(N(C),1),
 E_physical_J=round(E_phys,1),E_rotor_J=round(0.5*Jc*w**2,1),E_design_J=E_des,E_required_25pct_J=round(E_req,1),
 pad=f'2 stacks {AY:.0f}(y) x {AR:.0f}(radial) face, {NL} x {tl} mm PUR90A + {NL-1} x {ts} mm 7075 shims + 2 x 3 mm end plates + ø6 guide pin, centroid r {R:.0f}',
 shape_factor=round((AY*AR-math.pi*9)/(2*(AY+AR)*tl),2),V_cm3=round(V,1),E_bottom_25pct_J=round(E25,1),energy_SF_vs_66=round(E25/E_des,2),
 at_physical=at(E_phys),at_powered_40p1=at(40.1),at_design_44p1=pk,at_62p7=at(62.7),at_66=at(66.0),at_25pct=at(E25*0.9999),fault_92p5=fault(E_fault),top_out_25pct_deg=curve[-1]['knee_deg'],
 alt_contact_for_830=alts,
 rotor=dict(alpha_rad_s2=round(alpha),tau_rotor_on_shank_Nm=round(tau_rot_knee,1),sign='+flexion (same sense as the impact; the pad reacts it)',
  F_rotor_pair_N=round(F_rot_pair),F_rotor_per_screw_N=round(F_rot_screw),screw_dL_dq_mm_per_deg=round(dLdq,3),
  screw_rotor_load='tension (screw shortens with flexion; rotor keeps driving shortening)' if dLdq<0 else 'compression',F_motor_peak_pair_N=round(F_mot_pair),
  per_screw_worst_N=round(F_mot_pair/2),C0a_frac=round(max(F_mot_pair/2,F_rot_screw)/27300,3)),
 mass_kg_per_knee=round(mass,3),mass_kg_robot=round(2*mass,3),curve=curve)
RATE=1.3   # PU strain-rate factor on stress at ~10/s vs ASTM D575 quasi-static [EST]; Sarva, Deschanel, Boyce, Chen, Polymer 48 (2007) 2208 (PU stiffens with rate, rubbery->glassy over 1e-3..1e4/s); T&R used 1.2
ZT,ZF,FY,FTU,DLF,CAP=2781,2691,393,469,1.05,50
m44=at(E_des)['torque_Nm']; m25=at(E25*0.9999)['torque_Nm']
Mn=(m44*RATE+CAP)*DLF; Mf=(m25*RATE)*DLF
import functools
wcap=lambda E: math.sqrt(2*E/(Ib+Jref(C)))
chk=dict(rate_factor=RATE,strain_rate_per_s=round(w*R/T,1),
 C1_44J=dict(M_stop_qs=m44,M_tube=round(Mn),tibia_SF=round(FY*ZT/Mn/1000,2),femur_SF=round(FY*ZF/Mn/1000,2),limit='SF>=1.0 vs 393',
   pass_=FY*min(ZT,ZF)/1000>=Mn),
 bottoming=dict(E25_J=round(E25,1),limit='>=92.5 J',pass_=E25>=92.5-0.05),
 C2_fault=dict(M_stop_25pct_qs=m25,M_tube=round(Mf),tibia_MPa=round(Mf*1000/ZT),femur_MPa=round(Mf*1000/ZF),limit='no rupture: <=469 MPa (yield 393 accepted w/ inspect)',
   pass_=Mf*1000/min(ZT,ZF)<=FTU,elastic=Mf*1000/min(ZT,ZF)<=FY),
 top_out=dict(deg=curve[-1]['knee_deg'],limit='<=143.6',pass_=curve[-1]['knee_deg']<=143.61),
 speed_cap=dict(w_44J_rad_s=round(wcap(E_des),2),w_bottom_rad_s=round(wcap(E25),2),note='contact speed at 130 deg for 44.1 J / 25 % bottoming (I_body 2.71 + J_refl(130))'),
 mass=dict(robot_kg=MASS_LINE_ROBOT,own_estimate_robot_kg=round(2*mass,3),source='Legs L84 r2 6a3d84c',limit='<=0.35',pass_=MASS_LINE_ROBOT<=0.35,status='FAIL pending Robot Lab ruling'))
res['D99_checks']=chk
json.dump(res,open(f'{HERE}/results/knee_stop_pu_d99.json','w'),indent=1,default=lambda o:o.item())
print(json.dumps(chk,indent=0,default=lambda o:o.item()))
pass
# STEP: one stack (6 x 9.25 PU + 5 x 1.5 shims + 2 x 3 end plates, ø6 guide hole), its seat plate and the tibia striker lug, stack-local frame
st=cq.Workplane('XY'); z=0
for i in range(NL):
    st=st.union(cq.Workplane('XY').box(AY,AR,tl,centered=(True,True,False)).translate((0,0,z+3))); z+=tl
    if i<NL-1: st=st.union(cq.Workplane('XY').box(AY,AR,ts,centered=(True,True,False)).translate((0,0,z+3))); z+=ts
st=st.union(cq.Workplane('XY').box(AY+2,AR+2,3,centered=(True,True,False))).union(cq.Workplane('XY').box(AY+2,AR+2,3,centered=(True,True,False)).translate((0,0,z+3)))
st=st.cut(cq.Workplane('XY').circle(3).extrude(z+6))
seat=cq.Workplane('XY').box(36,30,8,centered=(True,True,False)).translate((0,0,z+6))
strk=cq.Workplane('XY').box(32,22,10,centered=(True,True,False)).translate((0,0,-10))
strk=strk.union(cq.Workplane('XY').box(63,24,18,centered=(False,True,False)).translate((16,0,-18)))   # L84 r2 arm 24 (radial) x 18 (tangential) x 63, flush with the striker face
ring=cq.Workplane('YZ').circle(25.5).circle(22.5).extrude(24).translate((79,0,-13))                  # tibia ring ø51 x 3 x 24 (Legs)
pins=cq.Workplane('XY').circle(3).extrude(51).translate((91,0,-38.5)).union(cq.Workplane('XZ').circle(3).extrude(51,both=True).translate((91,0,-13)))  # 2x ø6 cross pins [EST layout]
strk=strk.union(ring).union(pins)
asm=st.union(seat).union(strk)
cq.exporters.export(asm,f'{HERE}/cad/knee_stop_pu_r75b_d99.step'); print('stack length mm',z+6)
