"""R19 (R-150, Controls 019f0c6): hands-first kneel hand plant check + elbow 2 s capability at 82 C drive temp. Hand calcs.
Sources: CSG Table 3 (actuators/datasheets/hd_csf_csg_catalog.txt l.414-432): CSG-14-100 rep 36 / mom 70; CSG-20-100 rated 52 / rep 107 / mom 191;
IKO CRBH 258 A C0 2810 N, d25 D41 (iko_crb_catalog.txt l.796); CSG-25-100 momentary 369 (RULINGS R-058 area l.796);
palm A32 (1.5 mm skin, 4 mm wrist plate), STOCK_GRAIN palm 308 MPa; CONTRACTS 1a elbow 76 avail; DRIVE_DERATE (0.5 x 76 = 38 at 82 C);
O-A2 (K_m 0.082, C_w 0.149x460, R_th 3.4); DRIVE_DERATE sit table (drive-only adiabatic 1.19 K/s at full current, bound)."""
import json,os,math
F={'L':1525.0,'R':1520.0}; Fw=max(F.values()); out={'F_peak_N':F}
dp=(25+41)/2; C0=2810
def s0(F,e,ax=0): return C0/(F+2*F*e/dp+0.44*ax)
out['wrist_bearing_CRBH258A']={f'e{e}mm_radial':round(s0(Fw,e),2) for e in (0,5,10,20)}
out['wrist_bearing_roll_axial_e10']=round(C0/(0.44*Fw+2*0.3*Fw*10/dp),2)
out['F_max_for_s0_2']={f'e{e}':round(C0/2/(1+2*e/dp)) for e in (0,5,10)}
out['wrist_pitch_yaw_CSG14']={f'e{e}mm':dict(M=round(Fw*e/1000,1),SF_rep=round(36/(Fw*e/1000),2),SF_mom=round(70/(Fw*e/1000),2)) for e in (10,20,45)}
out['wrist_roll_CSG14']=dict(M=round(0.3*Fw*0.016,1),SF_rep=round(36/(0.3*Fw*0.016),1))
# palm: uniform flat plant on the 1.5 mm grip face (83x80 panel, SS beta 0.287) vs heel plant on a 4 mm heel band
q=Fw/(60*70); out['palm_flat_face_MPa']=round(0.287*q*83**2/1.5**2); out['palm_heel_cantilever_1p5_MPa']=round(6*(Fw/86*10)/1.5**2)
out['palm_heel_4mm_MPa']=round(6*(Fw/86*10)/4**2); out['palm_limit']=308; out['palm_heel_band_mass_kg']=round(86*20*2.5*2.81e-6,3)
out['forearm']=dict(CF_buckling_N=round(math.pi**2*75e3*189.5e3/194**2),bond_shear_MPa=round(Fw/(math.pi*67*20),2),bond_SF=round(4.6/(Fw/(math.pi*67*20)),1))
out['elbow_lug_MPa']=round(245*(Fw/2)/1146); out['elbow_offset_max_mm']={'cap38':round(38/Fw*1000),'cap76':round(76/Fw*1000)}
out['shoulder_offset_max_mm']={'derated83.5':round(83.5/Fw*1000),'momentary369_SF1.5':round(369/1.5/Fw*1000)}
# elbow 2 s
Km=0.082/math.sqrt(1.4); Cw=0.149*460
def Pcu(T): return (T/(100*0.75)/Km)**2
out['elbow_2s']=dict(gear_rep=107,gear_mom=191,motor_peak_avail=76,hard_cap=69,
   winding_rise_2s_K={T:round(Pcu(T)*2/Cw,1) for T in (38,49,69,76)},
   drive_rise_2s_K_bound={T:round(1.19*(T/76)**2*2,2) for T in (38,49,69,76)},
   T_for_drive_rise_le_1K=round(76*math.sqrt(1/(1.19*2))))
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'kneel_plant_r19.json'),'w'),indent=1); print(json.dumps(out,indent=1))
