import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
out={}
for r in (0,-3,-6):
  for y in (16,19,22,25):
    for k in (0,):
      ps=M.build({'L_hip_yaw':y,'R_hip_yaw':-y,'L_hip_roll':r,'R_hip_roll':-r,'L_knee':k,'R_knee':k})
      A=[p for p in ps if p['name'].startswith('L_knee twin housing')];B=[p for p in ps if p['name'].startswith('R_knee twin housing')]
      out[f'roll{r}_yaw{y}']=round(min(float(a['solid'].distance(b['solid'])) for a in A for b in B),2); print(r,y,out[f'roll{r}_yaw{y}'],flush=True)
json.dump(out,open(f'{HERE}/results/r031/yaw_housing_l93.json','w'),indent=1)
