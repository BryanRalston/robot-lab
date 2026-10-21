"""P-023 rev 7: thigh-fixed rear skirt flap carrying the P-156 rev 6b shroud; pelvis-fixed skirt cut only where flap+shroud sweep,
plus Thermal 5fd6a54 rule: no fixed skirt panel in the jet path aft of the louvres at any hip pose (jet = louvre panel extruded 150 mm
along its 45 deg up/aft normal, +-10 mm spread). Flap = PC 1.5 panel hugging the thigh skin (<=3 mm offset; sweeps inside the thigh's own
skirt clearance), 15 mm margin above the shroud, 4 new P-023 inserts on the thigh skin. Pinch check: cut-edge to flap/shroud gap per pose."""
import numpy as np, trimesh, json, math, os
from scipy.spatial import cKDTree
from trimesh.grouping import group_rows
H=os.path.dirname(os.path.abspath(__file__)); L=os.path.join(H,'../../../legs')
GATE=3.0; REM=GATE+2.5
M=trimesh.load(os.path.join(L,'results/v5/hip_skirt_keepout.stl')); A0=M.area
v,f=trimesh.remesh.subdivide_to_size(M.vertices,M.faces,4.0); M=trimesh.Trimesh(v,f)
def pts(x0,x1,y0,y1,z0,z1,n=5): return np.array([[x,y,z] for x in np.linspace(x0,x1,n) for y in np.linspace(y0,y1,n) for z in np.linspace(z0,z1,n)])
S=np.vstack([pts(-62.2,-33.3,102.8,157.2,820,831),pts(-76.4,-33.3,100,148,831,842),pts(-100,-20,86,150,842,904),pts(-115,-5,71,150,904,919,n=4)])
d=np.array([-1,0,1])/math.sqrt(2); base=np.array([[-100+0.0*t,y,z] for y in np.linspace(90,146,6) for z in np.linspace(860,904,5) for t in [0]])
JET=np.vstack([base+d*s for s in np.linspace(5,150,12)])
def R(ax,a):
    c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
    return {'y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'x':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[ax]
def pose(X,p,r,yw):
    P=(X-[0,130,920])@R('y',p).T+[0,130,920]; P=(P-[0,130,1045])@R('x',r).T+[0,130,1045]; return (P-[0,130,0])@R('z',yw).T+[0,130,0]
POSES=[(p,r,y) for p in list(range(-100,41,10))+[-107.3,-60] for r in (-20,0,15,30,45) for y in (-35,0,45)]
T=cKDTree(np.vstack([pose(S,*q) for q in POSES])); TJ=cKDTree(np.vstack([pose(JET,*q) for q in POSES]))
c=M.triangles_center
body_cut=(T.query(c)[0]<=REM)|(T.query(M.vertices)[0][M.faces].min(1)<=REM)
jet_cut=TJ.query(c)[0]<=10
keep=~(body_cut|jet_cut)
K=trimesh.Trimesh(M.vertices,M.faces[keep]); K.remove_unreferenced_vertices(); cut=A0-K.area
jet_only=float(M.area_faces[jet_cut&~body_cut].sum())
e=K.edges_sorted; EP=K.vertices[np.unique(e[group_rows(e,require_count=1)])]
KS=cKDTree(np.vstack([K.vertices,trimesh.sample.sample_surface_even(K,30000)[0]])); ET=cKDTree(EP)
worst=(1e9,None); trap=[]; eg=[]; jetmin=1e9
for q in POSES:
    P=pose(S,*q); g=float(KS.query(P)[0].min()); ge=float(ET.query(P)[0].min()); eg.append(ge)
    jetmin=min(jetmin,float(KS.query(pose(JET,*q))[0].min()))
    if g<worst[0]: worst=(g,q)
    if 5<ge<25: trap.append(q)
K.export(os.path.join(H,'hip_skirt_r7.stl'))
out=dict(rev=7,poses=len(POSES),skirt_area_mm2=round(A0),cut_mm2=round(cut),cut_pct=round(100*cut/A0,1),jet_only_cut_mm2=round(jet_only),
 worst_gap_mm=round(worst[0],1),worst_pose_pitch_roll_yaw=worst[1],jet_to_fixed_skirt_min_mm=round(jetmin,1),
 edge_gap_range_mm=[round(min(eg),1),round(max(eg),1)],finger_trap_poses_5_25=len(trap),trap_examples=trap[:8],skirt_pc_removed_kg=round(-cut*1.5*1.2e-6,4))
json.dump(out,open(os.path.join(H,'hip_skirt_r7.json'),'w'),indent=1); print(out)
