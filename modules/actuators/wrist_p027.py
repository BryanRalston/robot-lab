"""P-027 check of D65 wrist pair (TBM2G-05008 + THK BNK1004-2.5) vs Arms R2 357b72a exact numbers."""
import json, math, os
H=os.path.dirname(os.path.abspath(__file__)); r=0.025; eta=0.9; lead=0.004; Tp=0.72   # eta [EST], Tp tbm2g_manual §9.2.1 p252
Ca=2100.0   # THK BNK1004-2.5 Ca (thk_bnk_lmsystems.html)
Fcap=Tp*2*math.pi*eta/lead
need=dict(pitch=14.7/r/2, yaw=8.9/r/2, pitch_plus_yaw=(14.7+8.9)/(2*r))
F30=0.3*need['pitch']; T30=F30*lead/(2*math.pi*eta)
rpm_axis=6*r/lead*60; rpm_both=2*rpm_axis
# duty profile [EST - no arm duty sim exists, arms/R1_ARCHITECTURE O-A2]: time fraction, load N, speed fraction of 2250 rpm
duty=[(0.05,need['pitch'],1.0),(0.25,148.0,0.3),(0.70,20.0,0.3)]  # peak / 7.4 N·m static hold (arm_loads_r1) / idle
fw=1.5  # THK load factor, "with normal motion" upper bound
nm=sum(t*s for t,_,s in duty)*rpm_axis
Fm=(sum(t*F**3*s for t,F,s in duty)/sum(t*s for t,_,s in duty))**(1/3)
L10_h=(Ca/(fw*Fm))**3*1e6/(nm*60)
L10_peak_cont_h=(Ca/(fw*need['pitch']))**3*1e6/(rpm_axis*60)
m_mech=0.8646   # D65 wrist_r1.json pair_kg/side
enc=2*(0.0027+0.0070)   # 2x RLS AksIM-2 MB022 readhead 2.7 g + MRA022 ring 7.0 g (MBD01_15 selection table)
drv=2*0.0222            # 2x Elmo Gold Twitter EtherCAT, no heatsink 22.2 g (MAN-G-TWI v2.011 tech spec table)
L10_fw12=L10_h*(fw/1.2)**3
alt_BNK1404=dict(Ca_N=4200,L10_h_fw15=L10_h*(4200/Ca)**3,shaft_mass_add_per_side_kg=2*math.pi/4*(196-100)*110*7.85e-6,note='ø14 lead 4, nut ø26 x 33 (lmsystems table); same force/speed; fails 0.90 kg')
out=dict(L10_h_fw12=L10_fw12,alt_BNK1404=alt_BNK1404,F_cap_N=Fcap,need_N=need,SF={k:Fcap/v for k,v in need.items()},T_motor_at_30pct_Nm=T30,rpm_axis=rpm_axis,rpm_pitch_plus_yaw=rpm_both,
 Ca_N=Ca,fw=fw,duty=duty,Fm_N=Fm,n_mean_rpm=nm,L10_h=L10_h,L10_h_if_294N_continuous_full_speed=L10_peak_cont_h,
 mass_mech_kg=m_mech,encoders_kg=enc,drives_kg=drv,side_with_encoders_kg=m_mech+enc,side_with_encoders_and_drives_kg=m_mech+enc+drv)
json.dump(out,open(f'{H}/results/wrist_p027.json','w'),indent=1,default=str); print(json.dumps(out,indent=1,default=str))
