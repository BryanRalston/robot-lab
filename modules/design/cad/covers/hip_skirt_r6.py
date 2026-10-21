"""P-023 hip skirt rev 6: relief over the P-156 rev 6 outlet (stack/shroud raised +4 mm per Legs L75 ae8b9a4).
Method = Legs skirt_outlet_l75.py (same pivots, pelvis-fixed v5 keep-out skirt) but dense pose grid; skirt faces within GATE of the swept
outlet+shroud are removed (relief), the rest is thickened 1.5 mm inward (PC) -> solid STL. Re-checks the min gap on the result."""
import numpy as np, trimesh, json, math, os
from scipy.spatial import cKDTree
H=os.path.dirname(os.path.abspath(__file__)); L=os.path.join(H,'../../../legs')
GATE=3.0; DZ=4.0
M=trimesh.load(os.path.join(L,'results/v5/hip_skirt_keepout.stl'))
v,f=trimesh.remesh.subdivide_to_size(M.vertices,M.faces,4.0); M=trimesh.Trimesh(v,f)
def pts(x0,x1,y0,y1,z0,z1,n=5): return np.array([[x,y,z] for x in np.linspace(x0,x1,n) for y in np.linspace(y0,y1,n) for z in np.linspace(z0,z1,n)])
S=np.vstack([pts(-62.2,-33.3,102.8,157.2,820,831),pts(-76.4,-33.3,100,148,831,842),pts(-100,-20,86,150,842,904)])  # rev 6b shroud (T&R 925d72e ruling)
def R(ax,a):
    c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
    return {'y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'x':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[ax]
def pose(p,r,yw):
    P=(S-[0,130,920])@R('y',p).T+[0,130,920]; P=(P-[0,130,1045])@R('x',r).T+[0,130,1045]; return (P-[0,130,0])@R('z',yw).T+[0,130,0]
POSES=[(p,r,y) for p in list(range(-100,41,10))+[-107.3,-60] for r in (-20,0,15,30,45) for y in (-35,0,45)]
SW=np.vstack([pose(*q) for q in POSES]); T=cKDTree(SW)
dc=T.query(M.triangles_center)[0]; dv=T.query(M.vertices)[0]
REM=GATE+2.5; keep=(dc>REM)&(dv[M.faces].min(1)>REM)
R6=trimesh.Trimesh(M.vertices,M.faces[keep]); R6.remove_unreferenced_vertices()
removed=M.area-R6.area
# thicken 1.5 mm inward (toward the thigh) -> closed solid
n=R6.vertex_normals; inner=R6.vertices-1.5*n; nv=len(R6.vertices)
F=[R6.faces, R6.faces[:,::-1]+nv]
from trimesh.grouping import group_rows
e=R6.edges_sorted; b=e[group_rows(e,require_count=1)]
for a,c in b: F.append(np.array([[a,c,c+nv],[a,c+nv,a+nv]]))
SOL=trimesh.Trimesh(np.vstack([R6.vertices,inner]),np.vstack(F)); trimesh.repair.fix_normals(SOL)
SOL.export(os.path.join(H,'hip_skirt_r6.stl'))
# recheck: every pose vs remaining skirt (both skins)
KS=cKDTree(np.vstack([SOL.vertices,trimesh.sample.sample_surface_even(SOL,30000)[0]]))
worst=min(((float(KS.query(pose(*q))[0].min()),q) for q in POSES[::1]),key=lambda t:t[0])
zero=float(KS.query(pose(0,0,0))[0].min())
hole=M.triangles_center[~keep]
out=dict(gate=GATE,poses=len(POSES),relief_area_mm2=round(removed),relief_bbox=[hole.min(0).round(1).tolist(),hole.max(0).round(1).tolist()],
 worst_gap_mm=round(worst[0],1),worst_pose_pitch_roll_yaw=worst[1],zero_pose_gap=round(zero,1),
 skirt_mass_delta_kg=round(-removed*1.5*1.2e-6,4), watertight=bool(SOL.is_watertight))
json.dump(out,open(os.path.join(H,'hip_skirt_r6.json'),'w'),indent=1); print(out)
