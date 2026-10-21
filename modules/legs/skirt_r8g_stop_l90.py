import numpy as np,json
from scipy.spatial import cKDTree
exec(open('skirt_r8g_lr_l90.py').read().split('res={}')[0])
S=np.vstack([Pn,SHR]); out={}
for r in (-15.6,-12,-9,-6,-3,0):
  for y in (-38.6,-20,0,10,20,30,40,43.6):
    m=1e9
    for p in PI:
      m=min(m,float(cKDTree(pose(S,p,r,y)).query(pose(mir(S),p,r,y,side=-1),distance_upper_bound=60)[0].min()))
    out[f'{r},{y}']=round(m,1); print(r,y,out[f'{r},{y}'],flush=True)
json.dump(out,open('results/r031/skirt_r8g_stop_map_l90.json','w'),indent=1)
