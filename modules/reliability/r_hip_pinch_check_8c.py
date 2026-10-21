"""T&R rev 8c re-check (ID d58ffa4 / ec4dde7 / ee80543). Reuses ID hip_skirt_r8c_fix.py geometry (panel R152 y86+40 chamfer,
real shroud wedge + stack, notched pelvis STL), JCH 3.0 J-channel, hem R141.5. Grid: T&R 2240 poses PLUS roll overtravel past
the L39 stop contact (-12/+15) of 2.5 (old), 3.6 (SIDE_FALL rev B 3b4c449 / Legs L80 bottom-out [EST]) and 5.8 deg (proposed big bumper)."""
import numpy as np, math, json, os, trimesh
from scipy.spatial import cKDTree
H=os.path.dirname(os.path.abspath(__file__)); D=os.path.join(H,'../design/cad/covers')
src=open(os.path.join(D,'hip_skirt_r8c_fix.py')).read().split("S=np.vstack")[0]
ns={'__file__':os.path.join(D,'hip_skirt_r8c_fix.py')}; exec(src,ns)
T,panel,shroud,C1,JCH=ns['T'],ns['panel'],ns['shroud'],ns['C1'],3.0
P=panel(); SH=shroud(); S=np.vstack([P,SH])
pit=list(range(-105,41,5))+[-107.5,42.5]; yaw=(-37.5,-35,-17,0,22,45,47.5)
G=[(p,r,y) for p in pit for r in (-17.8,-15.6,-14.5,-12,-8,-4,0,5,10,15,17.5,18.6,20.8) for y in yaw]
R1=141.5; OT={'nominal_ROM':(-12,15),'ovt2.5':(-14.5,17.5),'ovt3.6':(-15.6,18.6),'ovt5.8':(-17.8,20.8)}
def mn(L): m=min(L); return [round(m[0],1),list(m[1])]
hem=[(float(np.linalg.norm(T(S,*q)-C1,axis=1).min())-R1-JCH,q) for q in G]
out={'R_hem':R1,'JCH':JCH}
M=trimesh.load(os.path.join(D,'hip_skirt_r8c_pelvis_notched.stl')); KS=cKDTree(np.vstack([M.vertices,M.triangles_center]))
dn={q:(float(KS.query(T(P,*q))[0].min())-JCH,float(KS.query(T(SH,*q))[0].min())-JCH) for q in G}
for k,(lo,hi) in OT.items():
    s=[(g,q) for g,q in hem if lo<=q[1]<=hi]
    out['hem_'+k]=mn(s); out['hem_'+k+'_tol2']=round(min(s)[0]-2,1); out['hem_'+k+'_band5_25_tol2']=sum(5<g-2<25 for g,q in s)
    out['notch_panel_'+k]=mn([(dn[q][0],q) for g,q in s]); out['notch_shroud_'+k]=mn([(dn[q][1],q) for g,q in s])
    out['notch_shroud_'+k+'_tol2']=round(out['notch_shroud_'+k][0]-2,1)
out['r8c_pelvis_stl_bytes']=os.path.getsize(os.path.join(D,'hip_skirt_r8c_pelvis.stl'))
json.dump(out,open(os.path.join(H,'r_hip_pinch_check_8c.json'),'w'),indent=1); print(json.dumps(out))
