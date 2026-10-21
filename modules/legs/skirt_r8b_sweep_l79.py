"""L79: P-023 rev 8b (ID acb9bd5) re-run of skirt_r8_sweep_l77. No 8b STL is published: hem = r8 pelvis STL rescaled radially about
C1 (0,130,1045) from R152.8 to R144; panel = r8 panel trimmed to y >= 86 (40 mm chamfer NOT modelled -> conservative). Hard surfaces (foam edges
counted compliant, hard gap reported). Hip grid per T&R ca68f3a: pitch -107.5..42.5 (5), roll -14.5..17.5 (stops -12/+15 + 2.5 overtravel), yaw -37.5..47.5.
Knee 0..145 with 143.6 governing (Robot Lab: 135 + crush, top-out <= 143.6). Housing r116b. Sit/kneel floor checks."""
import os,sys,json,math,numpy as np,trimesh
from scipy.spatial import cKDTree
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model')); CV=os.path.join(HERE,'../design/cad/covers')
def samp(m,n): return np.vstack([m.vertices,trimesh.sample.sample_surface_even(m,n)[0]])
C1=np.array([0,130,1045.])
HEM=samp(trimesh.load(f'{CV}/hip_skirt_r8_pelvis.stl'),150000); v=HEM-C1; HEM=C1+v*(144/np.linalg.norm(v,axis=1))[:,None]*(np.linalg.norm(v,axis=1)/152.8)[:,None]
PAN=samp(trimesh.load(f'{CV}/hip_skirt_r8_thigh_panel.stl'),60000); PAN=PAN[PAN[:,1]>=86]
KH=cKDTree(HEM); KP=cKDTree(PAN)
def box(x0,x1,y0,y1,z0,z1,n=9): return np.array([[x,y,z] for x in np.linspace(x0,x1,n) for y in np.linspace(y0,y1,n) for z in np.linspace(z0,z1,n)])
SHR=np.vstack([box(-62.2,-33.3,102.8,157.2,820,831),box(-76.4,-33.3,100,148,831,842),box(-100,-20,86,150,842,904,12)])
def R(ax,a):
    c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
    return {'y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'x':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[ax]
def pose(S,p,r,yw,side=1):
    yc=130*side; P=(S-[0,yc,920])@R('y',p).T+[0,yc,920]; P=(P-[0,yc,1045])@R('x',r*side).T+[0,yc,1045]; return (P-[0,yc,0])@R('z',yw*side).T+[0,yc,0]
mir=lambda S:S*[1,-1,1]
G=[(p,r,y) for p in list(range(-105,41,5))+[-107.5,42.5] for r in (-14.5,-12,-8,-4,0,5,10,15,17.5) for y in (-37.5,-17,0,22,47.5)]
out={}; a=[]; x=[]
TH=np.vstack([PAN[::3],SHR])
for q in G:
    a.append((round(float(KH.query(pose(TH,*q))[0].min()),1),q))
    L=pose(TH,*q); Rr=pose(mir(TH),*q,side=-1); x.append((round(float(cKDTree(L).query(Rr)[0].min()),1),q))
a.sort(); x.sort()
inrom=lambda q:-12<=q[1]<=15 and -35<=q[2]<=45 and -105<=q[0]<=40
out['1_hem_vs_panel_shroud']=dict(min_ovt=a[0],min_ROM=min(t for t in a if inrom(t[1])),zero=[t for t in a if t[1]==(0,0,0)][0][0],poses=len(G))
out['2_cross_leg']=dict(min_ovt=x[0],min_ROM=min(t for t in x if inrom(t[1])),worst5=x[:5])
import model_v4 as M
_st=M.step; M.step=lambda n,*a_,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a_,**k)
def tess(parts):
    pts=[];nm=[]
    for p in parts:
        V,_=p['solid'].tessellate(1.0); V=np.array([[q.x,q.y,q.z] for q in V]); pts.append(V); nm+=[p['name']]*len(V)
    return np.vstack(pts),nm
b={}
for kn in (0,90,135,140,143.6,145):
    parts=M.build({'L_knee':kn}); hs=[p for p in parts if p['name'].startswith('L_knee twin housing')]; sh=[p for p in parts if p['seg']=='L_shank']
    H_,_=tess(hs); S_,nm=tess(sh); d,_=KP.query(S_); i=int(d.argmin())
    b[kn]=dict(panel_to_housing=round(float(KP.query(H_)[0].min()),1),panel_to_shank=round(float(d[i]),1),shank_part=nm[i])
out['3_4_panel_knee']=b
# 5 floor: kneel (hip -34.4 [controls kneel_pose -0.6 rad], knee 145, ankle -52.5) and chair sit (hip -90, knee 90, seat 450 above the sole)
fl={}
for name,pz,seat in (('kneel',{'L_hip_pitch':-34.4,'L_knee':145,'L_ankle_pitch':-52.5},None),('chair_sit',{'L_hip_pitch':-90,'L_knee':90},450.0)):
    parts=M.build(pz); legs=[p for p in parts if p['name'].startswith('L_')]
    zmin=min(p['solid'].BoundingBox().zmin for p in legs)
    foot=min(p['solid'].BoundingBox().zmin for p in legs if p['seg']=='L_foot')
    Pp=pose(TH,pz['L_hip_pitch'],0,0)
    floor=zmin if seat is None else foot
    r=dict(floor_z=round(floor,1),panel_shroud_min_z=round(float(Pp[:,2].min()),1),gap_to_floor=round(float(Pp[:,2].min()-floor),1))
    if seat:
        thighs=[p for p in legs if p['seg']=='L_thigh']; tz=min(p['solid'].BoundingBox().zmin for p in thighs)
        r.update(seat_top_z=round(foot+seat,1),thigh_structure_min_z=round(tz,1),gap_panel_to_seat=round(float(Pp[:,2].min()-(foot+seat)),1))
    fl[name]=r
out['5_floor']=fl
# 6 lower inserts vs thigh skin; 7 air path
TF=trimesh.load(f'{HERE}/results/v5/thigh_fairing_keepout.stl'); KT=cKDTree(samp(TF,80000))
lo=PAN[PAN[:,2]<PAN[:,2].min()+3]; hi=PAN[PAN[:,2]>PAN[:,2].max()-3]
out['6_inserts']=dict(lower_edge_to_skin=round(float(KT.query(lo)[0].min()),1),upper_edge_to_skin=round(float(KT.query(hi)[0].min()),1))
ys=np.linspace(86,150,33); zs=np.linspace(842,904,32); face=np.array([[-100,y,z] for y in ys for z in zs])
out['7_air']=[dict(pose=q,gap_min=g,free_mm2_est=round(float((np.minimum(KH.query(pose(face,*q))[0],20)/20).mean()*64*62*0.6))) for g,q in a[:5]]
json.dump(out,open(f'{HERE}/results/r031/skirt_r8b_sweep_l79.json','w'),indent=1,default=str); print(json.dumps(out,indent=0,default=str))
