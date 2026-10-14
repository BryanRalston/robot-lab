"""D69/D85 knee housing fin envelope (Thermal 9b9e169 option C). Light OCC sweep.
For knee 0..135 (screw stroke follows the linkage), sample the knee twin housing outer surface (tessellation vertices, rigid -> same
ordering every pose) and take the min point-to-solid distance to every neighbour: shank/tibia parts, thigh parts outside the knee
actuator asm (trunnion cheeks, bracket, clevis, femur), knee screws/rods are part of the moving set but RV12 rods/eyes are checked,
the right leg, and the knee-cap keep-out (STL vertices, thigh frame = world for knee-only poses). Point-to-solid distance is a LOWER
bound on the free radial fin height along the normal (conservative). Sectors are about the housing screw axis (PCA of the +y knee rod).
Free fin height per sector = min over poses - 3 mm margin. Output results/r031/knee_fin_envelope.json"""
import os,sys,json,math,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
import trimesh
KC=trimesh.load(f'{HERE}/results/v5/knee_cap_keepout.stl'); kcv=np.asarray(KC.vertices)
SKIP=('knee twin housing','knee trunnion pin','knee body')
def pdist(pt,shape):
    d=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*map(float,pt))).Vertex(),shape.wrapped); d.Perform(); return d.Value()
angs=list(range(0,136,15))+[135]; clear=None; who=None; kcmin=1e9; ax=None; c0=None
for a in angs:
    parts=M.build({'L_knee':a}); H=[p for p in parts if p['name'].startswith('L_knee twin housing')][0]['solid']
    vs,_=H.tessellate(2.0); P=np.array([[v.x,v.y,v.z] for v in vs])
    if ax is None:
        rod=[p for p in parts if p['name'].startswith('L_knee screw +y') and 'rod' in p['name']][0]['solid']
        rv,_=rod.tessellate(1.0); R=np.array([[v.x,v.y,v.z] for v in rv]); w,V=np.linalg.eigh(np.cov((R-R.mean(0)).T)); ax0=V[:,-1]
        c0=P.mean(0); P0=P.copy(); clear=np.full(len(P),1e9); who=['']*len(P)
    hb=H.BoundingBox(); nb=[]
    for p in parts:
        if any(k in p['name'] for k in SKIP) or not (p['name'].startswith('L_') or p['name'].startswith('R_')) : continue
        b=p['solid'].BoundingBox(); m=40
        if b.xmin>hb.xmax+m or b.xmax<hb.xmin-m or b.ymin>hb.ymax+m or b.ymax<hb.ymin-m or b.zmin>hb.zmax+m or b.zmax<hb.zmin-m: continue
        nb.append(p)
    # coarse prefilter by bbox distance, then exact per vertex (subsample every 3rd vertex for speed)
    for i in range(0,len(P),3):
        best=clear[i]
        for p in nb:
            b=p['solid'].BoundingBox(); q=P[i]
            dbb=math.dist(q,np.clip(q,[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]))
            if dbb>=best: continue
            d=pdist(q,p['solid'])
            if d<best: best=d; who[i]=f"{p['name']} @{a}"
        clear[i]=best
    dk=np.min(np.linalg.norm(kcv[None,:,:]-P[::3,None,:],axis=2)); kcmin=min(kcmin,dk)
    print(a,len(nb),round(float(np.min(clear[::3])),1),'kneecapKO',round(float(dk),1),flush=True)
    if a==0: Pa0=P
np.savez_compressed(f'{HERE}/results/r031/knee_fin_clear.npz',P0=P0,clear=clear,who=np.array(who),ax0=ax0,c0=c0)
# sectors at pose 0: angle about the screw axis through the housing centroid
ref=np.array([1.0,0,0]); ref-=ax0*ref.dot(ax0); ref/=np.linalg.norm(ref); e2=np.cross(ax0,ref)
idx=np.arange(0,len(P0),3); tp=[np.array([M.KNEE_G['trunnion_x_mm'],M.P['hip_y']+sg*(M.P['knee_dy']+44),M.P['knee_z']+M.KNEE_G['trunnion_z_mm']]) for sg in (1,-1)]
idx=np.array([i for i in idx if min(np.hypot(*(np.delete(P0[i]-t,1))) for t in tp)>22])
rel=P0[idx]-c0; th=(np.degrees(np.arctan2(rel@e2,rel@ref))+360)%360
sec={}
for s in range(0,360,30):
    m=(th>=s)&(th<s+30)
    if not m.any(): continue
    j=idx[m][np.argmin(clear[idx[m]])]
    sec[f'{s:03d}-{s+30:03d}']=dict(min_clear_mm=round(float(clear[j]),1),fin_h_max_mm=round(max(0.0,float(clear[j])-3),1),limiter=who[j],n=int(m.sum()))
out=dict(basis=__doc__,poses=angs,axis_world_at_0=ax0.round(3).tolist(),sector_ref='0 deg = +x(world fwd) projected normal to screw axis, ccw about axis',
         sectors=sec,overall_min_mm=round(float(clear[idx].min()),1),housing_to_kneecap_keepout_min_mm=round(float(kcmin),1))
json.dump(out,open(f'{HERE}/results/r031/knee_fin_envelope.json','w'),indent=1); print(json.dumps(sec,indent=0)); print('kc',kcmin)
