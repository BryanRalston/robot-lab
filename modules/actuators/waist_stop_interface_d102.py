"""D102 rev b: + reflected drivetrain inertia (Jm 0.239e-4, TBM2G §9.4.1 p.272; wave generator 0.413e-4 kg.m2, HD Table 3 CSG-25 moment of inertia at the input),
KE at 6.3 rad/s output (Controls tripped-waist case) and gear impact torque through K3.
D102: waist-pitch actuator data for the P-160 yoke hard stop (T&R 3eacd56): 1.55 kN.m design / 2.3 kN.m ultimate.
Actuator (CONTRACTS.md row waist_pitch): TBM2G-06808A + HD CSG-25-100 component set (peak 115.4 N.m, sim v3 ctrlrange 116), output bearing IKO CRBH 6013 A (size.py BEAR[25]).
Sources: HD CSF/CSG catalog (datasheets/hd_csf_csg_catalog.pdf) CSG rating table (CSG-25-100 row), Table 6 ratcheting / Table 7 buckling (p.16),
Table 43 torsional stiffness ratio>=80 and Table 44 hysteresis (p.50); TBM2G manual §9.4.1 p.272 (Jm 0.239 kg.cm2);
IKO CRB catalog CRBH 6013 A row (C 18.8 kN, C0 24.3 kN) and eq.(2) P0r = Fr + 2M/Dpw + 0.44 Fa."""
import json,math,os
N=100; T1,K1,T2,K2,K3=14,3.1e4,48,5.0e4,5.7e4          # Table 43, size 25
LM=2.9e-4                                             # Table 44 hysteresis loss ratio>=80, size 25 (1 arc-min)
T_rated,T_rep,T_avg,T_mom,T_rat,T_buck=87,204,140,369,650,1700
Jm=0.239e-4; J_refl=Jm*N**2; T_mot=115.4
def wind(T):
    T=abs(T)
    if T<=T1: return T/K1
    if T<=T2: return T1/K1+(T-T1)/K2
    return T1/K1+(T2-T1)/K2+(T-T2)/K3
def Tg(th):  # inverse
    if th<=T1/K1: return K1*th
    if th<=T1/K1+(T2-T1)/K2: return T1+K2*(th-T1/K1)
    return T2+K3*(th-T1/K1-(T2-T1)/K2)
d=lambda r: round(math.degrees(r),4)
# A) input locked (brake/held rotor): stop in parallel with the gear; gap g incl. lost motion
th_rep=wind(T_rep); th_mom=wind(T_mom)
g=0.10*math.pi/180                                      # recommended total budget (gap + lost motion) [design choice]
Ks=(1550-T_rep)/(th_rep-g)                              # gear exactly at repeated peak at 1.55 kN.m
def solve(Text):
    lo,hi=0,0.05
    for _ in range(80):
        m=(lo+hi)/2; f=Tg(m)+(Ks*(m-g) if m>g else 0)-Text
        lo,hi=(m,hi) if f<0 else (lo,m)
    return m
A={}
for Text in (1550,2300):
    th=solve(Text); A[Text]=dict(theta_deg=d(th),stop_defl_deg=d(th-g),gear_Nm=round(Tg(th)),stop_Nm=round(Text-Tg(th)))
# B) no brake (as built): gear torque = motor torque + rotor inertia; current limit caps static share at T_mot
Ib=3.0                                                  # torso+arms pitch inertia about the waist [EST]
B=dict(J_refl_kgm2=round(J_refl,3),static_gear_Nm=T_mot,
  soft_stop_gear_Nm={T:round(T_mot+T*J_refl/(Ib+J_refl)) for T in (1550,2300)},
  impact_Nm_per_rad_s=round(math.sqrt(J_refl*K3),1),
  w_max_rad_s={'repeated_peak_motor_on':round((T_rep-T_mot)/math.sqrt(J_refl*K3),2),'repeated_peak_motor_off':round(T_rep/math.sqrt(J_refl*K3),2),
               'momentary_motor_on':round((T_mom-T_mot)/math.sqrt(J_refl*K3),2),'ratchet_motor_off':round(T_rat/math.sqrt(J_refl*K3),2)})
C0,C,Dpw=24300,18800,0.075
brg=dict(C_N=C,C0_N=C0,Dpw_m=Dpw,M_allow_static_fs1_Nm=round(C0*Dpw/2),M_allow_fs1p5_Nm=round(C0/1.5*Dpw/2),
  combined='Fr + 2M/0.075 + 0.44 Fa <= 24300/fs (fs>=1.5 shock -> 16.2 kN)',
  one_lug_10kN_radial_fs=round(C0/10000,2))
res=dict(gear='HD CSG-25-100 component set (strain wave), ratio 100',T1_Nm=T1,K1=K1,T2_Nm=T2,K2=K2,K3=K3,
  windup_deg={'T1':d(T1/K1),'T2':d(wind(T2)),'rated_87':d(wind(T_rated)),'rep_peak_204':d(th_rep),'mom_369':d(th_mom),'ratchet_650':d(wind(T_rat))},
  lost_motion_deg=d(LM),torques_Nm=dict(rated=T_rated,repeated_peak=T_rep,avg_limit=T_avg,momentary=T_mom,ratchet=T_rat,buckling=T_buck,motor_peak_output=T_mot),
  A_input_locked=dict(budget_gap_plus_lost_motion_deg=d(g),max_budget_deg_absolute=d(th_rep),physical_gap_deg=d(g-LM),
     Ks_kNm_per_rad=round(Ks/1000),cases=A),B_no_brake=B,bearing=brg)
Jwg=0.413e-4; Jin=Jm+Jwg; Jr=Jin*N**2; w=6.3
def U(T):  # gear strain energy up to T (piecewise linear)
    th=wind(T); n=400; return sum(Tg(th*(i+0.5)/n)*th/n for i in range(n))
Ti=w*math.sqrt(Jr*K3)
lo,hi=0,5000
for _ in range(60):
    m=(lo+hi)/2; lo,hi=(m,hi) if U(m)<0.5*Jr*w**2 else (lo,m)
res['rev_b']=dict(Jm_kgm2=Jm,J_wave_generator_kgm2=Jwg,J_input_kgm2=round(Jin,7),J_reflected_output_kgm2=round(Jr,3),
  w_output_rad_s=w,KE_drivetrain_J=round(0.5*Jr*w**2,1),impact_torque_linearK3_Nm=round(Ti),impact_torque_energy_piecewise_Nm=round(m),
  plus_motor_peak_Nm=round(m+T_mot),gear_energy_to_ratchet_J=round(U(T_rat),2),gear_energy_to_momentary_J=round(U(T_mom),2),
  w_max_momentary_motor_off=round(T_mom/math.sqrt(Jr*K3),2),w_max_ratchet_motor_off=round(T_rat/math.sqrt(Jr*K3),2),
  w_max_repeated_motor_off=round(T_rep/math.sqrt(Jr*K3),2),
  verdict='EXCEEDS ratchet (650) and approaches buckling (1700): a rigid stop at 6.3 rad/s ratchets the CSG-25 even with the motor off')
json.dump(res,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'results/waist_stop_interface_d102.json'),'w'),indent=1)
print(json.dumps(res,indent=1))
