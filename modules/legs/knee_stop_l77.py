"""L77: knee PU stop impact (Controls 0fb7c0e: 6.2 rad/s design, T_STOP 1.7-6.8 kN.m [EST]) vs the 29 kN drive fall case. Hand [EST]."""
import json,math
def Z(D,t): d=D-2*t; return math.pi/32*(D**4-d**4)/D
T=6.8e3; out={}
out['drive_case_knee_torque_kNm']=round(29e3*0.0475/1e3,2)
for n,D,t in (('femur 50x1.5',50,1.5),('tibia 45x1.5',45,1.5),('tibia 45x1.2 (model)',45,1.2)):
    z=Z(D,t); s=T*1e3/z; out[n]=dict(Z_mm3=round(z),sigma_at_6p8=round(s),SF_393=round(393/s,2),T_allow_kNm=round(393*z/1e6,2))
Fs=T/0.080/2; s=Fs/160*1.5; out['straps_if_stop_via_L60']=dict(strap_kN=round(Fs/1e3,1),sigma_root=round(s),SF_393=round(393/s,2),T_allow_kNm=round(393/1.5*160*2*0.08/1e3,2))
Ta=min(v['T_allow_kNm'] for k,v in out.items() if isinstance(v,dict)); out['T_allow_kNm']=Ta
I=4*0.25**2; E=0.5*I*6.2**2   # shank+foot 4 kg at 0.25 m (T&R L60_FALL_LOAD) [EST]
out['PU_requirement']=dict(E_J_est=round(E,1),k_theta_max_Nm_per_rad=round((Ta*1e3)**2/(2*E)),travel_min_deg=round(math.degrees(2*E/(Ta*1e3)),2),
   note='linear PU: T_max = sqrt(2 E k); use Controls whole-body energy if larger than this shank-only estimate')
json.dump(out,open('results/r031/knee_stop_l77.json','w'),indent=1); print(json.dumps(out,indent=0))
