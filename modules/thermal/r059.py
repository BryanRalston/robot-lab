# R-059 wrist pitch/yaw under fairing + shoulder-roll pad face; A43C 4.3 W rerun inputs. RL Thermal hand calc.
import json
Ta=35; out={}
# --- wrist: 2 units TBM2G-05008, P per motor [EST]: carry 3 W, sustained 10 N.m 6 W
def wrist(P,open_frac,Tshell):
  A_f=0.026; Ah=0.008                     # fairing area, motor housing area m2 [EST]
  UA_out=1/(1/(5*A_f)+1/(12*A_f))         # closed fairing wall (in h5, out h12)
  UA_vent=open_frac*A_f*0.6*1.0*1.15*1007*0.5 if open_frac else 0   # ram through slots, Cd .6, 1 m/s, half effective [EST]
  Rhc=1/(8*Ah); Rst=6.0; Rwc=1.5          # housing->cavity, housing->forearm structure, winding->case [EST]
  import numpy as np
  U=UA_out+UA_vent; g=1/Rhc; s=1/Rst
  M=np.array([[g+s,-g],[2*g,-(2*g+U)]]); b=np.array([P+s*Tshell,-U*Ta])
  Th,Tc=np.linalg.solve(M,b)
  return dict(cavity=round(Tc,1),housing=round(Th,1),winding=round(Th+P*Rwc,1))
for P in (3,6):
  for of in (0,0.2):
    for nm,Ts in (('walk',60),('still',70)):
      out[f'wrist P{P}W open{of} {nm}']=wrist(P,of if nm=='walk' else of*0.4,Ts)
# --- shoulder roll pad: housing rise; stack PC3/k0.2, Al honeycomb 57 mm k 2 [EST], EPP 6 mm k .04, outer h 10
for case,P,Rh in (('carry',3.5,3.0),('P-042',2.0,3.0),('carry still air',3.5,5.0)):
  Th=Ta+P*Rh+5            # +5 K from shoulder_pitch neighbour [EST]
  Rs=[0.003/0.2,0.057/2.0,0.006/0.04,1/(10 if 'still' not in case else 6)]
  q=(Th-Ta)/sum(Rs); Tin=Th-q*(Rs[0]+Rs[1]); Tout=Ta+q*Rs[3]
  out['roll '+case]=dict(housing=round(Th,1),EPP_inner=round(Tin,1),EPP_outer=round(Tout,1))
print(json.dumps(out,indent=1)); json.dump(out,open('results/r059.json','w'),indent=1)
