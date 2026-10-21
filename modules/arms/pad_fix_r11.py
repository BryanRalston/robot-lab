"""R11 pad fix after FEA Job 1 FAIL (a556d44). Hand calcs only, same load and formulas as the job:
Fn 8.86 kN, Fs 2.37 kN (axial or downward), fault x1.05. IKO static equivalent P0 = Fr + 2M/dp + 0.44 Fa.
Cited: CRBH 6013 A C0 24.3 kN, dp 75 (rows 60x90x13, 0.33 kg); CRBH 8016 A C0 43.4 kN (80x120x16, 0.74 kg), dp 100 [EST from the 88/112 shoulders]
(datasheets/iko_crb_catalog.pdf). HD CSG Table 3 momentary peak: CSG-25-100 369, CSG-32-100 841, CSG-40-100 1400 N·m;
Table 8 weights 0.42/0.89/1.7 kg (datasheets/hd_csf_csg_catalog.pdf)."""
import json,os
Fn,Fs,F=8.86,2.37,1.05
def s0(C0,dp,Y,Z,e=0.0,axial=True):
    if axial: M=(Fs*(Y**2+Z**2)**0.5**1 if False else Fs*(Y*Y+Z*Z)**0.5)+Fn*e; Fr=Fn; Fa=Fs
    else: M=Fn*e+Fs*e; Fr=(Fn**2+Fs**2)**0.5; Fa=0
    return round(C0/(Fr+2*M/dp+0.44*Fa),2)
out={}
# A. as-built R8 (link centre Z=64, contact Y=87): reproduce FEA
out['R8_asbuilt']=dict(s0_axial=s0(24.3,0.075,0.087,0.064),s0_axial_e10=s0(24.3,0.075,0.087,0.064,0.010),Mx_axial=round(Fn*0.064*1e3),Mx_down=round((Fn*0.064+Fs*0.087)*1e3))
# B. carrier on roll OUTPUT, pad centre on the roll axis (Z=0), wraps the housing: contact Y = 42 + 3 gap + 3 carrier + 67.5 stack = 115.5 mm
Y=0.1155
out['B_rollaxis_6013']=dict(s0_axial=s0(24.3,0.075,Y,0.0),s0_axial_e10=s0(24.3,0.075,Y,0,0.010))
out['B_rollaxis_8016']=dict(s0_axial=s0(43.4,0.100,Y,0.0),s0_axial_e10=s0(43.4,0.100,Y,0,0.010),s0_down_e10=s0(43.4,0.100,Y,0,0.010,False),
    Mx_axial=0,Mx_down=round(Fs*Y*1e3),SF_CSG25=round(369/(Fs*Y*1e3),2),SF_CSG25_fault=round(369/(F*Fs*Y*1e3),2))
# C. keep R8 geometry, upsize gear + bearing
need=(Fn*0.064+Fs*0.087)*1e3*F
out['C_gear']=dict(need_Nm_fault=round(need),CSG32=dict(peak=841,SF=round(841/need,2),dkg=0.47),CSG40=dict(peak=1400,SF=round(1400/need,2),dkg=1.28),
    s0_8016_axial_e10=s0(43.4,0.100,0.087,0.064,0.010))
# A. grounded carrier on shoulder_P (does not roll): pitch bearing tilt moment (D71 7013 gate 550 N·m); contact y 0.3695, bearing y 0.170
L=0.3695-0.170
for nm,dz in (('A1_low_z0.19',0.001),('A2_high_z0.225',0.036)):
    Mdown=Fn*dz+Fs*L; Max=((Fn*dz)**2+(Fs*L)**2)**0.5
    out[nm]=dict(M_down=round(Mdown*1e3),M_axial=round(Max*1e3),gate=550,pitch_gear_Nm=round(Fn*0.010*1e3),abduction_roll_max_deg={'A1_low_z0.19':35,'A2_high_z0.225':80}[nm])
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'pad_fix_r11.json'),'w'),indent=1); print(json.dumps(out,indent=1))
