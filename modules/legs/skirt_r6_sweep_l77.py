"""L77 (1)(2): rev 6 skirt solid (design/cad/covers/hip_skirt_r6.stl, pelvis-fixed) vs P-156 rev 6b stack+shroud (ID point sets, thigh-fixed,
raised for the +4 plate) and the D96 r116b knee housing (tessellated from model_v4 at knee 0/90/135/145, thigh frame), over the full hip grid
pitch -107.3..40 (10 deg) x roll -20,0,15,30,45 x yaw -35,0,45 (as ID) + roll 10/-10. Pivots as skirt_outlet_l75. Distances via cKDTree on
skirt vertices + sampled surface (~1 mm). Free air path: shroud aft louvre panel (x -100 face, y 86-150, z 842-904): curtain area ~ sum over
the panel outline of min(local gap, 20) * ds, plus the face area where gap >= 20 [EST rough]."""
import os,sys,json,math,numpy as np,trimesh
from scipy.spatial import cKDTree
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
SK=trimesh.load(os.path.join(HERE,'../design/cad/covers/hip_skirt_r6.stl')); KS=cKDTree(np.vstack([SK.vertices,trimesh.sample.sample_surface_even(SK,120000)[0]]))
def pts(x0,x1,y0,y1,z0,z1,n=7): return np.array([[x,y,z] for x in np.linspace(x0,x1,n) for y in np.linspace(y0,y1,n) for z in np.linspace(z0,z1,n)])
OUT=np.vstack([pts(-62.2,-33.3,102.8,157.2,820,831),pts(-76.4,-33.3,100,148,831,842),pts(-100,-20,86,150,842,904)])
import model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
HOUS={}
for a in (0,90,135,145):
    h=[p for p in M.build({'L_knee':a}) if p['name'].startswith('L_knee twin housing')][0]['solid']
    v,_=h.tessellate(0.5); HOUS[a]=np.array([[q.x,q.y,q.z] for q in v])
def R(ax,a):
    c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
    return {'y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'x':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[ax]
def pose(S,p,r,yw):
    P=(S-[0,130,920])@R('y',p).T+[0,130,920]; P=(P-[0,130,1045])@R('x',r).T+[0,130,1045]; return (P-[0,130,0])@R('z',yw).T+[0,130,0]
G=[(p,r,y) for p in list(range(-100,41,10))+[-107.3] for r in (-20,-10,0,10,15,30,45) for y in (-35,0,45)]
res=[]
for q in G:
    d=float(KS.query(pose(OUT,*q))[0].min()); hd=min(float(KS.query(pose(H,*q))[0].min()) for H in HOUS.values())
    res.append(dict(pose=q,outlet_min=round(d,1),housing_min=round(hd,1)))
wo=min(res,key=lambda t:t['outlet_min']); wh=min(res,key=lambda t:t['housing_min'])
# free area at the 5 worst outlet poses
ys=np.linspace(86,150,33); zs=np.linspace(842,904,32); ds=2.0
face=np.array([[-100,y,z] for y in ys for z in zs]); outline=np.array([[-100,y,842] for y in ys]+[[-100,y,904] for y in ys]+[[-100,86,z] for z in zs]+[[-100,150,z] for z in zs])
fa=[]
for t in sorted(res,key=lambda t:t['outlet_min'])[:5]:
    g=KS.query(pose(outline,*t['pose']))[0]; curtain=float(np.minimum(g,20).sum()*ds)
    gf=KS.query(pose(face,*t['pose']))[0]; open_face=float((gf>=20).mean()*64*62)
    fa.append(dict(pose=t['pose'],outlet_min=t['outlet_min'],curtain_mm2=round(curtain),face_open_mm2=round(open_face),est_free_mm2=round(min(64*62*0.6,curtain+open_face))))
out=dict(n_poses=len(G),worst_outlet=wo,worst_housing=wh,pass_3mm=wo['outlet_min']>=3 and wh['housing_min']>=3,free_area_worst5=fa,
         zero=[r for r in res if r['pose']==(0,0,0)][0])
json.dump(out,open(os.path.join(HERE,'results/r031/skirt_r6_sweep_l77.json'),'w'),indent=1); print(json.dumps(out,indent=0))
