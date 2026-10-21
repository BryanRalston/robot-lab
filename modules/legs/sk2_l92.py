import numpy as np
from scipy.spatial import cKDTree
exec(open('skirt_r8g_lr_l90.py').read().split('res={}')[0])
for y in (24,25,26,27):
  m=min(float(cKDTree(pose(Pn,p,r,y)).query(pose(mir(Pn),p,r,y,side=-1),distance_upper_bound=80)[0].min()) for p in PI for r in (0,-3))
  print(y,round(m,1),flush=True)
