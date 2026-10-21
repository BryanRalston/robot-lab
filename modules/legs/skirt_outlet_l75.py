"""L75: P-156 rev 6 outlet (stack x -62.2..-33.3, y 102.8-157.2, z 827-860; shroud cap x -76.2..-19.7, y 89-171, z to 881.5, standoff 20 -> walls z ~860-881.5)
vs P-023 hip skirt keep-out (pelvis-fixed, results/v5/hip_skirt_keepout.stl) over hip pitch/roll/yaw. Thigh-fixed parts rotated about the hip joints
(pitch about (0,130,920) +y; roll about x at z 1045; yaw about z at (0,130)). Distance = unsigned distance to the skirt keep-out surface mesh (sampled ~1 mm, cKDTree; +-1 mm); gate >= 15."""
import numpy as np,trimesh,json,math
from scipy.spatial import ConvexHull
from scipy.spatial import cKDTree
MS=trimesh.load('results/v5/hip_skirt_keepout.stl'); SP=np.vstack([MS.vertices,trimesh.sample.sample_surface_even(MS,200000)[0]]); KT=cKDTree(SP)
def pts(x0,x1,y0,y1,z0,z1,n=8): return np.array([[x,y,z] for x in np.linspace(x0,x1,n) for y in np.linspace(y0,y1,n) for z in np.linspace(z0,z1,n)])
S=np.vstack([pts(-62.2,-33.3,102.8,157.2,816,860),pts(-76.2,-19.7,89,171,860,881.5)])
def R(ax,a):
    c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
    return {'y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'x':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[ax]
res=[]
for p in (-107.3,-90,-60,-30,0,20,40):
  for r in (-20,0,45):
    for yw in (-35,0,45):
        P=(S-[0,130,920])@R('y',p).T+[0,130,920]; P=(P-[0,130,1045])@R('x',r).T+[0,130,1045]; P=(P-[0,130,0])@R('z',yw).T+[0,130,0]
        d=KT.query(P)[0]; res.append(dict(pitch=p,roll=r,yaw=yw,min_mm=round(float(d.min()),1)))
res.sort(key=lambda d:d["min_mm"]); byroll={r:min([d for d in res if d["roll"]==r],key=lambda d:d["min_mm"]) for r in (-20,0,45)}; zero=[d for d in res if d["pitch"]==0 and d["roll"]==0 and d["yaw"]==0][0]; out=dict(min=res[0],worst5=res[:5],by_roll=byroll,zero_pose=zero,gate=15,pass_=res[0]["min_mm"]>=15)
json.dump(out,open('results/r031/skirt_outlet_l75.json','w'),indent=1); print(json.dumps(out))
