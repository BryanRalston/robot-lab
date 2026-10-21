"""L77: P-023 rev 8 (ID df1e9e3) thigh panel (thigh-fixed) + spherical pelvis hem (pelvis-fixed) vs leg model.
(a) pelvis hem vs thigh panel / rev 6b shroud / outlet stack, both legs, hip grid pitch -107.3..40 x roll -20..45 x yaw -35..45 (+ cross-leg R leg mirror poses);
(b) thigh panel vs shank parts (tibia, calf, ankle plates D95 envelopes) + v5 shin fairing keep-out + r116b housing over knee 0..145;
(c) outlet air path: free curtain between the shroud aft louvre panel and the thigh panel/hem; (d) panel insert sites.
Distances: cKDTree on surface samples (~1-1.5 mm), unsigned [EST +-1.5 mm]."""
import os,sys,json,math,numpy as np,trimesh
from scipy.spatial import cKDTree
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model')); CV=os.path.join(HERE,'../design/cad/covers')
def samp(m,n): return np.vstack([m.vertices,trimesh.sample.sample_surface_even(m,n)[0]])
HEM=trimesh.load(f'{CV}/hip_skirt_r8_pelvis.stl'); PAN=trimesh.load(f'{CV}/hip_skirt_r8_thigh_panel.stl')
HEMp=samp(HEM,150000); PANp=samp(PAN,60000); KH=cKDTree(HEMp); KP=cKDTree(PANp)
def box(x0,x1,y0,y1,z0,z1,n=9): return np.array([[x,y,z] for x in np.linspace(x0,x1,n) for y in np.linspace(y0,y1,n) for z in np.linspace(z0,z1,n)])
SHR=np.vstack([box(-62.2,-33.3,102.8,157.2,820,831),box(-76.4,-33.3,100,148,831,842),box(-100,-20,86,150,842,904,12)])
def R(ax,a):
    c,s=math.cos(math.radians(a)),math.sin(math.radians(a))
    return {'y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'x':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[ax]
def pose(S,p,r,yw,side=1):
    yc=130*side; P=(S-[0,yc,920])@R('y',p).T+[0,yc,920]; P=(P-[0,yc,1045])@R('x',r*side).T+[0,yc,1045]; return (P-[0,yc,0])@R('z',yw*side).T+[0,yc,0]
mir=lambda S:S*[1,-1,1]
G=[(p,r,y) for p in list(range(-100,41,10))+[-107.3] for r in (-20,-10,0,15,30,45) for y in (-35,0,45)]
out={}
# (a) hem vs panel/shroud, L leg; cross-leg: L panel vs R panel+shroud (same pose both legs, mirror)
a=[];x=[]
for q in G:
    PL=pose(PANp[::3],*q); SL=pose(SHR,*q)
    a.append((round(float(min(KH.query(PL)[0].min(),KH.query(SL)[0].min())),1),q))
    PR=pose(mir(PANp[::3]),*q,side=-1); SR=pose(mir(SHR),*q,side=-1); K2=cKDTree(np.vstack([PL,SL]))
    x.append((round(float(K2.query(np.vstack([PR,SR]))[0].min()),1),q))
a.sort(); x.sort()
out['a_hem_vs_panel_shroud']=dict(min=a[0][0],pose=a[0][1],worst5=a[:5],zero=[v for v in a if v[1]==(0,0,0)][0][0])
out['a_cross_leg_L_vs_R_panels']=dict(min=x[0][0],pose=x[0][1],worst5=x[:5],note='same pose both legs (mirror); roll -20 = adduction')
# (b) panel vs shank structure/plates/fairing + housing over knee
import model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
SHF=trimesh.load(f'{HERE}/results/v5/shin_fairing_keepout.stl'); SHFp=samp(SHF,40000)
AN=[box(40,66.5,102,158,zc-30,zc+30,7) for zc in (215,290)]
b={}
P0=None
for kn in (0,30,60,90,120,135,145):
    parts=M.build({'L_knee':kn}); sh=[p for p in parts if p['seg']=='L_shank']; hs=[p for p in parts if p['name'].startswith('L_knee twin housing')][0]
    pts=[];names=[]
    for p in sh+[hs]:
        v,_=p['solid'].tessellate(1.0); V=np.array([[q.x,q.y,q.z] for q in v]); pts.append(V); names+= [p['name']]*len(V)
    # shank-frame extras rotated with the tibia: find rotation from tibia tube vertices
    t=math.radians(kn); best=None
    for sgn in (1,-1):
        Rk=R('y',sgn*kn); 
        tib0=[p for p in M.build({}) if p['name'].startswith('L_tibia tube')][0]['solid'].Center() if P0 is None else P0
        P0=tib0; c0=np.array([tib0.x,tib0.y,tib0.z]); c1=[p for p in parts if p['name'].startswith('L_tibia tube')][0]['solid'].Center(); c1=np.array([c1.x,c1.y,c1.z])
        e=np.linalg.norm((c0-[0,130,500])@Rk.T+[0,130,500]-c1)
        if best is None or e<best[0]: best=(e,Rk)
    Rk=best[1]; rot=lambda S:(S-[0,130,500])@Rk.T+[0,130,500]
    for nm,S in (('v5 shin fairing keep-out',SHFp[::2]),('AN1 plate+drive env',AN[0]),('AN2 plate+drive env',AN[1])):
        pts.append(rot(S)); names+=[nm]*len(S)
    A=np.vstack(pts); d,_=KP.query(A); i=int(d.argmin())
    per={}
    for nm,dd in zip(names,d): per[nm]=min(per.get(nm,1e9),float(dd))
    b[kn]=dict(min=round(float(d[i]),1),part=names[i],top=sorted([(round(v,1),k) for k,v in per.items()])[:4])
out['b_panel_vs_shank_knee']=b
# (c) air path: shroud aft louvre face (x -100) gap to panel/hem at the worst hem poses
ys=np.linspace(86,150,33); zs=np.linspace(842,904,32); face=np.array([[-100,y,z] for y in ys for z in zs])
gp=KP.query(face)[0]; out['c_aft_face_to_thigh_panel']=dict(min=round(float(gp.min()),1),frac_ge_20=round(float((gp>=20).mean()),2),note='panel is thigh-fixed: static; louvres are IN the panel skin per ID, so a ~0 gap at the panel = the louvre panel itself')
c=[]
for v,q in a[:5]:
    g=KH.query(pose(face,*q))[0]; c.append(dict(pose=q,face_open_frac_ge20=round(float((g>=20).mean()),2),free_mm2_est=round(float((np.minimum(g,20)/20).mean()*64*62*0.6))))
out['c_aft_face_vs_hem_worst']=c
# (d) inserts: panel lower/upper edges; report thigh-skin (v5 thigh keep-out) distance at panel edge points
TF=trimesh.load(f'{HERE}/results/v5/thigh_fairing_keepout.stl'); KT=cKDTree(samp(TF,80000))
ed=PAN.vertices[np.argsort(PAN.vertices[:,2])]; lo=ed[:40]; hi=ed[-40:]
out['d_panel_edge_to_thigh_skin']=dict(lower_edge=round(float(KT.query(lo)[0].min()),1),upper_edge=round(float(KT.query(hi)[0].min()),1),
   lower_edge_z=[round(float(lo[:,2].min()),1),round(float(lo[:,2].max()),1)],upper_edge_z=[round(float(hi[:,2].min()),1),round(float(hi[:,2].max()),1)])
json.dump(out,open(f'{HERE}/results/r031/skirt_r8_sweep_l77.json','w'),indent=1,default=str); print(json.dumps(out,indent=0,default=str))
