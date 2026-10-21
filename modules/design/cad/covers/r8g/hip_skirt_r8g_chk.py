import numpy as np,trimesh,math
from scipy.spatial import cKDTree
CV='/workspace/rl-id-wt/modules/design/cad/covers'
exec(open('/workspace/rl-id-wt/modules/legs/skirt_r8c_sweep_l79.py').read().split("G=[(p")[0].replace("r8c_pelvis_notched","r8f_pelvis_notched").replace("r8c_thigh","r8f_thigh").replace("150000","40000").replace("60000","15000").replace("HERE=os.path","HERE='/workspace/rl-id-wt/modules/legs';_=os.path"))
q=(42.5,-14.5,-35)
for nm,S in (('panel',PAN),('shroud',SHR)): print(nm,round(float(KH.query(pose(S,*q))[0].min()),1))
C1=np.array([0,130,1045.]); print('sphereR141.5 metric',round(float(np.linalg.norm(pose(np.vstack([PAN,SHR]),*q)-C1,axis=1).min())-141.5-3,1))
