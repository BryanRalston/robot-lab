"""R5b: Actuators review of Legs' split-collar thigh clamp (L18, P-014): one axial ø12 spherical eye per hip_pitch screw body at y ±69,
collar on the femur tube ø50 x 1.2 (7075), collar height 30 mm, ring 6 mm (legs fea_r4.py clamp(), fea_clamp_h2.5_hz30.json).
Checks at max screw force 4542 N per body (454.2 N·m / 50 mm / 2), both bodies same sense: slip by friction, bolt preload, tube crush, eye (SKF GE 12 E), swing/tilt, fatigue."""
import json, os, math, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); L=json.load(open(f'{H}/../legs/results/r4/fea_clamp_h2.5_hz30.json'))
F=4542.0; D=50.0; t=1.2; Lc=30.0; R=(D-t)/2; Sy=503.0; E=71700.0; mu=0.15; SFs=1.5; scatter=1.25   # mu anodised Al/Al dry, VDI 2230 low band; torque-tightening scatter alpha_A 1.6 -> +-25 %
# body swing vs thigh over the hip range (hp_clearance geometry: lever r50, clock 60, trunnion (30,-300))
T=np.array([30,-300.]); ang=[]
for th in np.arange(-105,40.01,0.5):
    a=math.radians(60-th); Ep=np.array([-50*math.sin(a),-50*math.cos(a)]); u=Ep-T; ang.append(math.degrees(math.atan2(u[0],u[1])))
ang=np.array(ang); swing=ang.max()-ang.min(); off=np.abs(ang).max()
Fax=2*F*math.cos(math.radians(off)); Ftr=2*F*math.sin(math.radians(off))
N_req=SFs*Fax/mu; p=N_req/(math.pi*D*Lc); sig_hoop=p*R/t; SF_crush=Sy/(sig_hoop*scatter)
T_bolt=p*(D/2)*Lc   # hoop tension per split side to generate p
p_cr=E/(4*(1-0.33**2))*(t/R)**3
# bonded alternative (3M Scotch-Weld DP490: lap shear ~30 MPa Al/Al per 3M TDS [EST here]); fatigue allowable 20 % of static
tau=Fax/(math.pi*D*Lc); SF_bond=0.2*30/tau
# eye: SKF GE 12 E (datasheets/skf_ge12e.pdf): C 10.8 kN, C0 54 kN, alpha 10 deg, K 100 N/mm2
C,C0,K,alpha=10800,54000,100,10.0; s0=C0/F; Pw=0.52*F; p_eye=K*Pw/C
beta=swing/2; v=5.82e-7*18*beta*1.0   # m/s at 1 Hz gait, dk 18 mm
Gh=330/(p_eye**2.5*v)                 # SKF steel/steel basic rating life (h), b-factors 1, relubricated
pin_tau=F/(math.pi*12**2/4); pin_M=F*(6+3); pin_sig=pin_M/(math.pi*12**3/32)   # single shear, 6 mm half eye + 3 mm gap lever arm
# fatigue: Legs FEA max/p99.9 at 4542, walking amplitude 0.52x fully reversed, 7075-T6 Se ~ 159 MPa @5e8 (MMPDS-typical, [EST])
c=L['cases']['screw_max_push']; Se=159
fat=dict(SF_max=Se/(0.52*c['vm_max']),SF_p999=Se/(0.52*c['vm_p999']))
out=dict(inputs=dict(F_per_body=F,femur=f'ø{D}x{t}',collar_h=Lc,mu=mu,SF_slip=SFs,scatter=scatter),
 body_angle_deg=dict(min=float(ang.min()),max=float(ang.max()),swing=float(swing)),F_axial_both=Fax,F_transverse_both=Ftr,
 friction_only=dict(N_radial_req_N=N_req,p_contact_MPa=p,tube_hoop_MPa=sig_hoop,SF_tube_yield_with_scatter=SF_crush,p_collapse_long_tube_MPa=p_cr,
   hoop_tension_per_side_N=T_bolt,bolts='2x M6 10.9 per side (FM ~ 10.4 kN each at muG 0.12, VDI 2230 table) -> 20.8 kN >= %.1f kN'%(T_bolt/1e3),verdict='FAIL: tube hoop yield SF %.2f < 1.5 with preload scatter; friction alone not acceptable'%SF_crush),
 bonded_plus_light_clamp=dict(tau_MPa=tau,SF_fatigue=SF_bond,clamp_p_MPa=3.0,tube_hoop_MPa=3.0*R/t,verdict='PASS'),
 eye=dict(part='SKF GE 12 E',s0=s0,p_walk_Nmm2=p_eye,G_h_relubricated=Gh,tilt_needed_deg=swing/2,tilt_allow_deg=alpha,
   note='if the eye pin is parallel to the hip axis the swing is plain rotation; if truly axial the ±%.1f° swing uses tilt (≤ 10° OK)'%(swing/2)),
 pin=dict(tau_MPa=pin_tau,bend_MPa=pin_sig,material='42CrMo4 QT Sy 750',SF=750/pin_sig),
 clamp_fatigue=fat,legs_FEA=dict(vm_max=c['vm_max'],SF=c['SF_yield_max']))
json.dump(out,open(f'{H}/results/clamp_review.json','w'),indent=1); print(json.dumps(out,indent=1))
