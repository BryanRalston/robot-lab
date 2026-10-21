"""P-023 rev 8 FINAL = open-break variant (cuff dropped: a sliding cuff opens a 3->236 mm scissor gap over the 147 deg pitch range).
Original cuff study notes follow.
P-023 rev 8 (Robot Lab ruling option i): rear skirt split per leg. Kinematic break lines so every moving-cover gap is CONSTANT:
Legs' hip chain (skirt_outlet_l75): thigh = yaw(z axis at x0,y130) . roll(x axis at y130,z1045) . pitch(y axis at x0,z920).
- Thigh panel (thigh-fixed, carries the rev 6b shroud: its outer wall is the panel skin, louvres aft-only): cylinder R 150 about the PITCH axis,
  phi 35..75 deg (phi from straight down toward aft), y 60..200.
- Hip cuff (rides the hip ROLL link = pitch-housing side, new P-023 inserts on existing cover bosses; no mechanism change [Legs confirm]):
  cylinder R 153 about the pitch axis, phi 70..100 -> nests 3 mm outside the panel, 5 deg (13 mm) overlap lip near the pitch axis.
  Relative motion panel/cuff = pitch only -> radial gap 3.0 constant.
- Pelvis hem (pelvis-fixed): spherical lip about the yaw/roll intersection C1 (0,130,1045), radius = cuff-top distance + 3 -> constant 3.0.
Numeric checks over the 255 poses: L/R panel+cuff gaps (mirror y), jet path vs cuff and pelvis skirt, retained fixed skirt."""
import numpy as np, trimesh, json, math, os
from scipy.spatial import cKDTree
H=os.path.dirname(os.path.abspath(__file__)); L=os.path.join(H,'../../../legs')
PA=np.array([0,0,920.]); C1=np.array([0,130,1045.])
def cyl(R,p0,p1,y0=60,y1=200,n=40):
    P=[]
    for ph in np.radians(np.linspace(p0,p1,n)):
        for y in np.linspace(y0,y1,25): P.append([-R*math.sin(ph),y,920-R*math.cos(ph)])
    return np.array(P)
PANEL=cyl(150,35,75); CUFF=cyl(153,70,100)
d=np.array([-1,0,1])/math.sqrt(2); ph=np.radians(58); o=np.array([-150*math.sin(ph),0,920-150*math.cos(ph)])
JET=np.array([o+[0,y,0]+d*s for y in np.linspace(90,146,6) for s in np.linspace(5,150,15)])
def R(ax,a):
    c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
    return {'y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'x':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[ax]
def T(X,p,r,yw,pitch=True):
    P=X
    if pitch: P=(P-[0,130,920])@R('y',p).T+[0,130,920]
    P=(P-[0,130,1045])@R('x',r).T+[0,130,1045]; return (P-[0,130,0])@R('z',yw).T+[0,130,0]
mir=lambda X: X*[1,-1,1]
POSES=[(p,r,y) for p in list(range(-100,41,10))+[-107.3,-60] for r in (-20,0,15,30,45) for y in (-35,0,45)]

# FINAL: thigh panel R150 about the pitch axis, phi 35..60, y 60..200; NO cuff; pelvis hem = sphere about C1 sized so the panel stays >=25 mm away at every pose.
P=cyl(150,35,60,y0=60)
dmin=min((float(np.linalg.norm(T(P,*q)-C1,axis=1).min()),q) for q in POSES); R1=dmin[0]-25
M=trimesh.load(os.path.join(L,'results/v5/hip_skirt_keepout.stl')); v,f=trimesh.remesh.subdivide_to_size(M.vertices,M.faces,4.0); M=trimesh.Trimesh(v,f)
keep=np.linalg.norm(M.triangles_center-C1,axis=1)<=R1; K=trimesh.Trimesh(M.vertices,M.faces[keep]); K.remove_unreferenced_vertices(); ret=K.area/M.area
KT=cKDTree(np.vstack([K.vertices,K.triangles_center]))
hem=[(float(KT.query(T(P,*q))[0].min()),q) for q in POSES]; hemmin=min(hem,key=lambda t:t[0]); hem_trap=[q for g,q in hem if 5<g<25]
jet=min(((float(KT.query(T(JET,*q))[0].min()),q) for q in POSES),key=lambda t:t[0])
AX=np.array([[0,130,z] for z in np.linspace(500,900,9)])
lr=[];lr_bad=[]
for q in POSES:
    A=cKDTree(T(P,*q))
    for q2 in ((0,0,0),q):
        g=float(A.query(mir(T(P,*q2)))[0].min()); lr.append(g)
        if 5<g<25 or g<3:
            legs=float(np.linalg.norm(T(AX,*q)[:,None]-mir(T(AX,*q2))[None],axis=2).min())
            lr_bad.append(dict(q=q,q2=q2,gap=round(g,1),thigh_axes_mm=round(legs,1),cause="thighs themselves collide (infeasible)" if legs<60 else "cover (both-leg adduction roll -20 in flexion, or both-leg yaw 45)"))
single=[b for b in lr_bad if b["q2"]==(0,0,0)]
cover_bad=[b for b in lr_bad if b["cause"].startswith("cover")]
K.export(os.path.join(H,'hip_skirt_r8_pelvis.stl'))
pts_panel=P; tri=trimesh.convex.convex_hull(np.vstack([P,P*[1,1,1]-[0,0,0]+np.array([1.5,0,0])])); tri.export(os.path.join(H,'hip_skirt_r8_thigh_panel.stl'))
mass=dict(panel=round(150*math.radians(25)*140*1.5*1.2e-6,4),edge_lips_inserts=0.006,foil_band_40mm=0.002)
out=dict(rev="8 (open break)",poses=len(POSES),thigh_panel=dict(R=150,axis="hip pitch (x0,z920, along y)",phi=[35,60],y=[60,200],carries="rev 6b shroud aft louvres in its skin (Thermal 5fd6a54 specs unchanged)",mount="4 new P-023 inserts on the thigh skin"),
 pelvis_hem=dict(type="spherical about the yaw/roll intersection C1",C1=C1.tolist(),R=round(R1,1),break_line="one clean symmetric arc per side"),
 fixed_skirt_retained_pct=round(100*ret,1),
 gap_hem_to_panel=dict(min=round(hemmin[0],1),pose=hemmin[1],trap_5_25=len(hem_trap)),
 gap_panel_to_thigh="static: panel on the thigh skin (bonded/insert lip, <=1 mm) PASS; panel to shank NOT modelled (no shank skin in this model): Legs CAD knee 145",
 gap_LR=dict(min=round(min(lr),1),bad_total=len(lr_bad),bad_single_leg=len(single),bad_cover_cause=len(cover_bad),examples=cover_bad[:6]),
 jet_to_fixed_skirt_min=[round(jet[0],1),jet[1]],
 cuff_study=dict(result="REJECTED: panel/cuff edge gap 3.0 -> 236 mm over pitch (scissor), jet 1.4 mm to cuff"),
 mass_kg_side=mass,kg_side=round(sum(mass.values()),4),fixed_skirt_removed_kg=round(-(M.area-K.area)*1.5*1.2e-6,4))
json.dump(out,open(os.path.join(H,'hip_skirt_r8.json'),'w'),indent=1,default=str); print(json.dumps(out,default=str))
