"""D70-D72: wrist option compare (O-A3), shoulder_pitch output bearing vs 690 N·m side fall, wrist motor leads shoulder bay -> wrist."""
import json, math, os
H=os.path.dirname(os.path.abspath(__file__))
# ---- (b) rotary: per axis TBM2G-05008C + CSG-14-100 (HD Table 3: rated 10, rep peak 36, avg 14, mom 70 N·m; max input 8500 rpm grease; set 0.09 kg)
eta=0.70   # [EST] HD p.38 chart size 8-14 ratio 100 ~80 % at 500 r/min 25 C, x part-load factor
N=100; Tp=0.72; Tmc2=0.20; Kt_hot=0.040   # tbm2g_manual §9.2.1 p.252-253 (winding C)
b=dict(T_out_motor_pk=Tp*N*eta, T_out_gear_rep=36.0, need_pk=14.7, SF_pk=36.0/14.7,
 rpm_in_6rads=6*N*60/(2*math.pi), T_motor_30pct=0.3*14.7/(N*eta), T_motor_hold_7p4=7.4/(N*eta), SF_hold_cont=Tmc2/(7.4/(N*eta)),
 I_pk_A=14.7/(N*eta)/Kt_hot, I_hold_A=7.4/(N*eta)/Kt_hot)
unit=dict(motor_TBM2G05008=0.111,CSG14_100_set=0.09,out_bearing_CRBH258A=0.05,encoder_AksIM2_MB022=0.0097,housing_7075_EST=0.06,fasteners_EST=0.015)
b.update(unit_kg=unit,axis_kg=sum(unit.values()),side_kg=2*sum(unit.values()))
# ---- (a) push rods from elbow: D67 pair 0.884 + 2 rods ø8x1 steel tube L 0.30 + 4 rod ends [EST 5 g]
L=0.30; A=math.pi/4*(8**2-6**2); I=math.pi/64*(8**4-6**4); rod=A*1e-6*L*7850
a=dict(rod_kg=rod,Pcr_N=math.pi**2*200e3*I/(L*1e3)**2,need_N=294.0,side_kg=0.884+2*rod+4*0.005,backlash='rod-end radial play not published (QA1/SKF) - not found; 4 joints in series per axis')
a['SF_buckle']=a['Pcr_N']/294.0
# ---- D71 shoulder_pitch output bearing IKO CRBH 6013 A (C0 24.3 kN; catalog dims table), P0r = Fr + 2M/Dpw + 0.44 Fa (catalog eq.2)
def fs(C0,dpw,M=690.0,Fa=11.5e3,Fr=0.0): P=Fr+2*M/dpw+0.44*Fa; return C0/P,P
s=dict(CRBH6013A=dict(C0=24300,Dpw_EST=0.075),CRBH7013A=dict(C0=27700,Dpw_EST=0.085),CRBH8016A=dict(C0=43400,Dpw_EST=0.100))
for k,v in s.items():
    v['fs_moment_plus_axial'],v['P0r_N']=fs(v['C0'],v['Dpw_EST']); v['fs_if_force_radial']=fs(v['C0'],v['Dpw_EST'],Fa=0,Fr=11.5e3)[0]
# ---- D72 wrist leads shoulder bay -> wrist motors, per side, L 1.7 m (Electronics §10.6)
Lw=1.7; SIF025=5.4; MF=25.9   # Lapp SiF 0.25 mm2 g/m; Belden MRTA2P26S g/m (datasheets)
per_motor=dict(phase_3xSiF025_twisted=3*SIF025,encoder_MRTA2P26S_plus_2xSiF025=MF+2*SIF025,thermistor_2xSiF025=2*SIF025)
gpm=sum(per_motor.values()); R=0.01724/0.25*1.4   # ohm/m (Cu at 20C x ~1.4 hot [EST])
dV=b['I_pk_A']*2*Lw*R
wire=2*gpm*Lw/1000; con=2*(0.000384*2)   # 2 JST-GH 4p pairs per motor (harness.py evidence)
leads=dict(L_m=Lw,gpm_per_motor=gpm,wire_kg=wire,connectors_kg=con,sleeve_12pct_EST=0.12*wire,side_kg=wire*1.12+con,dV_pk_V=dV,dV_pct_68V=100*dV/68,
 ecat_sto_taps='2 drive tees move forearm -> shoulder bay: EtherCAT branch unchanged (still runs to hand), STO tee pigtails 2x3x0.08 m SiF 0.25 relocate, ~0 kg net')
out=dict(option_a_pushrod=a,option_b_rotary=b,shoulder_bearing=s,wrist_leads=leads,
 mass=dict(D67_side=0.884,D70_side=b['side_kg'],delta_vs_D67_side=b['side_kg']-0.884,leads_side=leads['side_kg'],net_both=2*(b['side_kg']-0.884+leads['side_kg'])))
json.dump(out,open(f'{H}/results/d70_wrist.json','w'),indent=1); print(json.dumps(out,indent=1))
