"""L75: D95 ankle plates AN1/AN2 (shank-fixed) vs v5 shin fairing keep-out (results/v5/shin_fairing_keepout.stl, shank frame) + ID rev 6 +2.0 mm blister
(z 180-325, 80 wide, outward). Both parts are shank-fixed, so the gap is static through knee/ankle ROM (ankle -55 moves only the foot)."""
import numpy as np,trimesh,json
from scipy.spatial import cKDTree
M=trimesh.load('results/v5/shin_fairing_keepout.stl'); K=cKDTree(np.vstack([M.vertices,trimesh.sample.sample_surface_even(M,200000)[0]]))
def pts(x0,x1,y0,y1,z0,z1,n=10): return np.array([[x,y,z] for x in np.linspace(x0,x1,n) for y in np.linspace(y0,y1,n) for z in np.linspace(z0,z1,n)])
out={}
for k,zc in (('AN1',215),('AN2',290)):
    P=np.vstack([pts(40,50,102,158,zc-30,zc+30),pts(50,66.5,112.5,147.5,zc-15,zc+15)])
    d=float(K.query(P)[0].min()); from scipy.spatial import ConvexHull; E=ConvexHull(M.vertices).equations; inside=bool(((P@E[:,:3].T+E[:,3]).max(1)<=0).all())
    out[k]=dict(gap_to_v5_keepout_mm=round(d,1),with_rev6_blister_mm=round(d+2.0,1),envelope_inside_keepout=inside)
print(out); json.dump(out,open('results/r031/shin_plate_l75.json','w'),indent=1)
