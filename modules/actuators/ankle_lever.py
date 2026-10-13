"""R-011 ankle_pitch lever 70 -> 77 mm study (linear scaling of the selected TBM2G-06013D + 2x RV12x4 unit, sizing.json)."""
import json, os, math
H=os.path.dirname(os.path.abspath(__file__)); s=json.load(open(f'{H}/results/sizing.json'))['sel']['ankle_pitch']
NMAX,RM=8000,0.95; lead=0.004
out={}
for arm in (70,73,74,77,80):
    k=arm/70; T=s['T_out']*k; ratio=2*math.pi*arm/1000/lead
    rpm=s['speed_need']*ratio*60/(2*math.pi); w30=s['w30']/k
    out[arm]=dict(T_out=round(T,1),carry_ratio_1p2=round(T/283.2,3),carry_ratio_1p0=round(T/238.3,3),carry_ratio_0p8=round(T/219.8,3),
        motor_rpm_at_speed_need=round(rpm),rpm_frac=round(rpm/NMAX,3),rpm_ok=rpm<=RM*NMAX,w30=round(w30,2),
        stroke_scale=round(k,3),lever_mass_delta_kg=round(0.032*(k-1),4))
amax=RM*NMAX*2*math.pi/60/s['speed_need']*lead/(2*math.pi)*1000
out['arm_max_for_95pct_mm']=round(amax,1); out['speed_need_rad_s']=s['speed_need']
json.dump(out,open(f'{H}/results/ankle_lever_77.json','w'),indent=1); print(json.dumps(out,indent=0))
