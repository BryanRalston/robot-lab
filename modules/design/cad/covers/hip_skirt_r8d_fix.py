"""P-023 rev 8c fixes for Legs 916c57f (L77). Hem gate now includes the REAL rev 6b shroud wedge (top slopes z 861.5 at x -20 -> 904 at x -100)
+ stack, the rev 8b panel (y 86 + 40 mm inboard-rear chamfer) with a local +2 mm relief over the knee housing (modelled as panel R 152 everywhere,
conservative), and JCH 3.0 mm J-channel. Grid = T&R ca68f3a 2240 poses + Legs L77 grid (roll to 45). Hem radius sized on the contract ROM
(roll -12..15) + 2.5 deg overtravel for >= 27.5 mm; Legs' roll 30/45 poses reported separately. Exports rev 8c STLs."""
import numpy as np, math, json, os, trimesh
from scipy.spatial import cKDTree
H=os.path.dirname(os.path.abspath(__file__)); L=os.path.join(H,'../../../legs')
C1=np.array([0,130,1045.]); JCH=3.0; GATE=27.5
def R(ax,a):
    c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
    return {'y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'x':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[ax]
def T(X,p,r,yw):
    P=(X-[0,130,920])@R('y',p).T+[0,130,920]; P=(P-[0,130,1045])@R('x',r).T+[0,130,1045]; return (P-[0,130,0])@R('z',yw).T+[0,130,0]
def panel(Rp=152,y0=86,c=40,phi0=45):
    P=[]
    for ph in np.linspace(35,60,26):
        for y in np.linspace(y0,200,30):
            if y < y0 + c*max(0,(ph-phi0))/(60-phi0): continue
            r=math.radians(ph); P.append([-Rp*math.sin(r),y,920-Rp*math.cos(r)])
    return np.array(P)
def shroud():
    P=[]
    for x in np.linspace(-100,-20,17):
        zt=861.5+(904-861.5)*(-20-x)/80
        for y in np.linspace(86,150,9):
            for z in np.linspace(842,zt,6): P.append([x,y,z])
    for x in np.linspace(-76.4,-33.3,6):
        for y in np.linspace(100,148,6):
            for z in (820,831,842): P.append([x,y,z])
    return np.array(P)
S=np.vstack([panel(),shroud()])
TR=[(p,r,y) for p in list(range(-105,41,5))+[-107.5,42.5] for r in (-20,-15.6,-14.5,-12,-8,-4,0,5,10,15,17.5,18.6) for y in (-37.5,-35,-17,0,22,45,47.5)]
LG=[(p,r,y) for p in list(range(-100,41,10))+[-107.3] for r in (-20,-10,0,15,30,45) for y in (-35,0,45)]
dist=lambda q: float(np.linalg.norm(T(S,*q)-C1,axis=1).min())
ovt=[(dist(q),q) for q in TR if -14.5<=q[1]<=17.5]
dmin=min(ovt); R1=math.floor((dmin[0]-GATE-JCH)*2)/2
rom=[(d,q) for d,q in ovt if -12<=q[1]<=15 and -35<=q[2]<=45 and -105<=q[0]<=40]
leg=[(dist(q)-R1-JCH,q) for q in LG]; legmin=min(leg); leg_out=[(round(g,1),q) for g,q in leg if g<3]
M=trimesh.load(os.path.join(L,'results/v5/hip_skirt_keepout.stl')); v,f=trimesh.remesh.subdivide_to_size(M.vertices,M.faces,4.0); M=trimesh.Trimesh(v,f)
keep=np.linalg.norm(M.triangles_center-C1,axis=1)<=R1; K=trimesh.Trimesh(M.vertices,M.faces[keep]); K.remove_unreferenced_vertices()
pass  # rev 8d: empty sphere-only skirt no longer exported (T&R 76de66a)
pp=panel(); trimesh.convex.convex_hull(np.vstack([pp,pp+[1.5,0,0]])).export(os.path.join(H,'hip_skirt_r8c_thigh_panel.stl'))
out=dict(rev="8c (Legs L77 fixes)",hem_R=R1,gate_mm=GATE,JCH=JCH,includes="panel (R152 relief-conservative, y86+chamfer) + real shroud wedge + stack",
 min_ovt=[round(dmin[0]-R1-JCH,1),dmin[1]],min_ovt_minus_tol2=round(dmin[0]-R1-JCH-2,1),min_ROM=[round(min(rom)[0]-R1-JCH,1),min(rom)[1]],
 legs_grid_min=[round(legmin[0],1),legmin[1]],legs_grid_below3=leg_out[:10],legs_pose_10_45_45=round(dist((10,45,45))-R1-JCH,1),
 fixed_skirt_retained_pct=round(100*K.area/M.area,1),fixed_skirt_removed_kg=round(-(M.area-K.area)*1.5*1.2e-6,4))
json.dump(out,open(os.path.join(H,'hip_skirt_r8d_fix.json'),'w'),indent=1,default=str); print(json.dumps(out,default=str))
# --- Option: keep hem R141.5 for the panel, add a LOCAL notch in the pelvis skirt where the shroud/stack sweep comes within GATE+JCH (contract ROM + overtravel)
R2=141.5; NM=float(os.environ.get('NM','4.0')); SH=shroud(); OV=[q for q in TR if -15.6<=q[1]<=18.6]  # rev 8d: T&R 76de66a 3.6 deg bottom-out overtravel
SW=cKDTree(np.vstack([T(SH,*q) for q in OV]))
keep2=(np.linalg.norm(M.triangles_center-C1,axis=1)<=R2)&(SW.query(M.triangles_center)[0]>GATE+JCH+NM)
K2=trimesh.Trimesh(M.vertices,M.faces[keep2]); K2.remove_unreferenced_vertices(); K2.export(os.path.join(H,'hip_skirt_r8d_pelvis_notched.stl'))
nc=M.triangles_center[(np.linalg.norm(M.triangles_center-C1,axis=1)<=R2)&~keep2]
KS=cKDTree(np.vstack([K2.vertices,K2.triangles_center]))
g_pan=min((float(KS.query(T(panel(),*q))[0].min())-JCH,q) for q in OV); g_sh=min((float(KS.query(T(SH,*q))[0].min())-JCH,q) for q in OV)
lg=min((float(KS.query(T(S,*q))[0].min())-JCH,q) for q in LG)
out2=dict(option="hem R141.5 + local shroud notch",notch_margin_mm=NM,shroud_gap_minus_tol2=round(g_sh[0]-2,1),retained_pct=round(100*K2.area/M.area,1),notch_area_mm2=round(float(M.area_faces[(np.linalg.norm(M.triangles_center-C1,axis=1)<=R2)&~keep2].sum())),
 notch_bbox=[nc.min(0).round(1).tolist(),nc.max(0).round(1).tolist()] if len(nc) else None,gap_panel_ovt=[round(g_pan[0],1),g_pan[1]],gap_shroud_ovt=[round(g_sh[0],1),g_sh[1]],
 legs_grid_min=[round(lg[0],1),lg[1]],fixed_removed_kg=round(-(M.area-K2.area)*1.5*1.2e-6,4))
out["option_notch"]=out2; json.dump(out,open(os.path.join(H,'hip_skirt_r8d_fix.json'),'w'),indent=1,default=str); print(json.dumps(out2,default=str))
