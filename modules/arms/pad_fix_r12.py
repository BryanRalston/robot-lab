"""R12: ID R9 (a688e28) pad core 55.3 sq -> 7.0 kN peak, PTFE slip skin mu<=0.15. Fn = 7.0 cos15 = 6.76 kN; tangential capped
at min(7.0 sin15, mu Fn) = 1.01 kN. Fault x1.05. Same IKO P0 formula as pad_fix_r11.py. CRBH 6013 A C0 24.3 kN dp 0.075, 0.33 kg;
CRBH 7013 A C0 27.7 kN, 70x100x13, 0.38 kg, dp 0.085 [EST from 76/94 shoulders] (iko_crb_catalog.pdf). CSG-25-100 momentary 369 N·m."""
import json,os,numpy as np
Fn=7.0*np.cos(np.radians(15)); Fs=min(7.0*np.sin(np.radians(15)),0.15*Fn); F=1.05
B={'6013':(24.3,0.075),'7013':(27.7,0.085)}
def case(bear,Y,Z):
    C0,dp=B[bear]; r={}
    for e in (0,0.005,0.010):
        M=Fs*np.hypot(Y,Z)+Fn*e; r[f's0_e{int(e*1000)}']=round(C0/(Fn+2*M/dp+0.44*Fs),2)
    Mx=(Fn*Z+Fs*Y)*1e3; r['Mx_down_Nm']=round(Mx); r['SF_CSG25_fault']=round(369/(F*Mx),2)
    r['pass']=bool(min(r['s0_e0'],r['s0_e10'])>=2.0 and r['SF_CSG25_fault']>=1.0); return r
out=dict(Fn_kN=round(Fn,2),Fs_kN=round(Fs,2),
 i_R9_alone=case('6013',0.087,0.064),
 ii_R9_carrier_axis_6013=case('6013',0.1155,0.0),
 iii_R9_partial_z20_6013=case('6013',0.105,0.020),
 iii_R9_partial_z37_6013=case('6013',0.100,0.037),
 iv_R9_7013_no_carrier=case('7013',0.087,0.064),
 ii_plus_iv=case('7013',0.1155,0.0))
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'pad_fix_r12.json'),'w'),indent=1); print(json.dumps(out,indent=1))
