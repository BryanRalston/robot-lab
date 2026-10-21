import numpy as np,json
from scipy.spatial import cKDTree
exec(open('skirt_r8g_lr_l90.py').read().split('res={}')[0])
def lim(r):
    d=min(max(0,-3-r),9); return -12+7/9*d, 28-2*d
S={'panel':Pn,'shroud':SHR}; out={}
pts=[(r,y) for r in (0,-3,-6,-9,-12,-12.3) for y in lim(r)]+[(18.6,-12),(18.6,28)]
for nm,X in S.items():
  best=(1e9,)
  for p in PI:
    for (rl,yl) in pts:
      L=cKDTree(pose(X,p,rl,yl))
      for (rr,yr) in pts:
        d=float(L.query(pose(mir(X),p,rr,yr,side=-1),distance_upper_bound=80)[0].min())
        if d<best[0]: best=(round(d,1),(p,rl,yl),(p,rr,yr))
  out[nm]=best; print(nm,best,flush=True)
json.dump(out,open('results/r031/skirt_r8g_l92.json','w'),indent=1)
