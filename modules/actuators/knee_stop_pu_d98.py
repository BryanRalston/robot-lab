"""D98: r75 PU knee stop - sizing for 66 J x >=1.4, placement in model_v4 (Legs L78 sweep method), STEP of pads + seats.
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
w=6.37; Ib=2.71; C=133.0   # contact moved 135->133 so 66 J lands at ~830 N.m with 25 % top-out <=143.6 (135 shown as alt)
QMAX=143.6; R=75.0
Jc=Jref(C); E_phys=0.5*(Ib+Jc)*w**2; E_des=66.0; E_req=1.4*E_des
NL,tl,ts=6,9.25,1.5; T=NL*tl                                   # 6 x 9.25 mm PU, 5 x 1.5 mm shims, ø6 guide pin, 3 mm end plates
AY,AR=28.0,21.0; A=2*(AY*AR-math.pi*9)                                    
V=A*T/1000; E25=cum[-1]*V
def at(E):
    e=float(np.interp(E/V,cum,eps)); s=float(np.interp(e,eps,sig)); return dict(E_J=E,strain=round(e,3),knee_deg=round(C+math.degrees(e*T/R),2),
        pad_force_kN=round(s*A/1000,2),torque_Nm=round(s*A*R/1000))
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
mass=(V*1.13+2*(NL-1)*(AY*AR-math.pi*9)*ts*7.85e-3+2*2*32*25*3*2.8e-3+2*(32*22*10+24*12*45)*2.8e-3+2*36*30*8*2.8e-3+80)/1000   # PU, steel shims, 7075 end plates, strikers+arms, seats, femur collar bar 80 g [EST]
res=dict(J_reflected_kgm2={q:round(Jref(q),3) for q in (0,30,60,75,90,120,135,143.6)},arm_mm_135=round(arm(C),1),N_135=round(N(C),1),
 E_physical_J=round(E_phys,1),E_rotor_J=round(0.5*Jc*w**2,1),E_design_J=E_des,E_required_25pct_J=round(E_req,1),
 pad=f'2 stacks {AY:.0f}(y) x {AR:.0f}(radial) face, {NL} x {tl} mm PUR90A + {NL-1} x {ts} mm steel shims + 2 x 3 mm end plates, centroid r {R:.0f}',
 shape_factor=round((AY*AR-math.pi*9)/(2*(AY+AR)*tl),2),V_cm3=round(V,1),E_bottom_25pct_J=round(E25,1),energy_SF_vs_66=round(E25/E_des,2),
 at_physical=at(E_phys),at_62p7=at(62.7),at_66=pk,at_bottom=at(E25*0.9999),top_out_25pct_deg=curve[-1]['knee_deg'],
 alt_contact_for_830=alts,
 rotor=dict(alpha_rad_s2=round(alpha),tau_rotor_on_shank_Nm=round(tau_rot_knee,1),sign='+flexion (same sense as the impact; the pad reacts it)',
  F_rotor_pair_N=round(F_rot_pair),F_rotor_per_screw_N=round(F_rot_screw),screw_dL_dq_mm_per_deg=round(dLdq,3),
  screw_rotor_load='tension (screw shortens with flexion; rotor keeps driving shortening)' if dLdq<0 else 'compression',F_motor_peak_pair_N=round(F_mot_pair),
  per_screw_worst_N=round(F_mot_pair/2),C0a_frac=round(max(F_mot_pair/2,F_rot_screw)/27300,3)),
 mass_kg_per_knee=round(mass,3),mass_kg_robot=round(2*mass,3),curve=curve)
json.dump(res,open(f'{HERE}/results/knee_stop_pu_d98.json','w'),indent=1)
print(json.dumps({k:v for k,v in res.items() if k!='curve'},indent=0))
# STEP: one stack (6 x 9.25 PU + 5 x 1.5 shims + 2 x 3 end plates, ø6 guide hole), its seat plate and the tibia striker lug, stack-local frame
st=cq.Workplane('XY'); z=0
for i in range(NL):
    st=st.union(cq.Workplane('XY').box(AY,AR,tl,centered=(True,True,False)).translate((0,0,z+3))); z+=tl
    if i<NL-1: st=st.union(cq.Workplane('XY').box(AY,AR,ts,centered=(True,True,False)).translate((0,0,z+3))); z+=ts
st=st.union(cq.Workplane('XY').box(AY+4,AR+4,3,centered=(True,True,False))).union(cq.Workplane('XY').box(AY+4,AR+4,3,centered=(True,True,False)).translate((0,0,z+3)))
st=st.cut(cq.Workplane('XY').circle(3).extrude(z+6))
seat=cq.Workplane('XY').box(36,30,8,centered=(True,True,False)).translate((0,0,z+6))
strk=cq.Workplane('XY').box(32,22,10,centered=(True,True,False)).translate((0,0,-10))
asm=st.union(seat).union(strk)
cq.exporters.export(asm,f'{HERE}/cad/knee_stop_pu_r75_d98.step'); print('stack length mm',z+6)
