"""L62 (R-111): thin-wall ULTEM 4001 knee trunnion bush, alternate to L61. Same hand-calc model as knee_trunnion_bush_r106.py [EST].
ULTEM 4001 k 0.26 W/mK (ISO 8302), rho 1.33 g/cc (SABIC EMEA TDS, cited in TRUNNION_BREAK.md). Al 2.7, steel 7.85.
Criteria: R_joint >=10 K/W on worn wall (t-0.2), p_design <=14.6 MPa, 3 mm ULTEM thrust washer 10% pads (no metal path),
boss OD = bush OD + 5 (2.5 mm Al wall, as R-106), boss grows outward only (cheek 6 mm). Mass vs bare L60 cheek + L61-baseline pin (12 mm)."""
import json, math
Fd=240/0.0475/2; Fw=159.8/0.0475/2; k=0.26; rho=1.33e-3; wear=0.2; tw=3.0; f=0.10
def case(d,L,t):
    od=d+2*t; bo=od+5; tw_=t-wear
    Rb=tw_/1e3/(k*math.pi*d*L*0.5e-6); Rw=tw/1e3/(k*f*math.pi*(od**2-d**2)/4*1e-6)
    Rs=1/(1/Rb+1/Rw)
    m=2*(rho*math.pi*(od**2-d**2)/4*L+rho*f*math.pi*(od**2-d**2)/4*tw)+2*2.7e-3*math.pi*(bo**2-od**2)/4*(L-6)+2*7.85e-3*math.pi*d**2/4*(L-12)
    return dict(d=d,L=L,t=t,od=round(od,2),boss_od=round(bo,2),boss_protrusion_mm=L-6,p_walk=round(Fw/(d*L),1),p_design=round(Fd/(d*L),2),
                R_side_worn=round(Rs,1),R_joint_worn=round(Rs/2,2),mass_knee_g=round(m,1),mass_robot_kg=round(2*m/1e3,4))
ok=[]
for d in [8,9,10,11,12]:
  for L in range(10,26):
    if Fd/(d*L)>14.6: continue
    for t in [x/10 for x in range(10,61)]:
      c=case(d,L,t)
      if c['R_joint_worn']>=10: ok.append(c); break
ok.sort(key=lambda c:c['mass_knee_g'])
l61=case(9,20,6.0)
best=ok[0]; low=min(ok,key=lambda c:(c['boss_protrusion_mm'],c['mass_knee_g']))
out=dict(basis=__doc__,L61_check=l61,best_mass=best,min_protrusion=low,top=ok[:8],
 delta_vs_L61_robot_kg=round(best['mass_robot_kg']-0.074,4),delta_vs_pre_L61_booking_kg=round(best['mass_robot_kg']-0.004,4))
json.dump(out,open('results/r031/knee_trunnion_bush_l62.json','w'),indent=1)
print(l61);[print(c) for c in ok[:8]];print(low);print(out['delta_vs_L61_robot_kg'],out['delta_vs_pre_L61_booking_kg'])
