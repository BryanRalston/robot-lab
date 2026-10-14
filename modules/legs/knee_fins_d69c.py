"""D69C knee housing fins (Thermal b785697 baseline) on the D59 knee_twin_housing STEP + clearance sweep (light).
Fins: axial 6061 plates, length 101 (z 2..103 of the housing), constant height h above the local surface (root r41 on the
gearbox section z<35, r19.5 on the upper tube z>=35 -> stepped outer edge), thickness T. Per tube (centres local x +-45):
rear sector 120-240 deg: 7 fins/tube (14 total) h25; front 330-030: 4+3 fins (7 total) h9; sides and bracket faces bare.
Angle convention = L48: 0 deg = world front (+x) = housing local -y, ccw about the screw axis: dir = (sin a, -cos a).
Sweep: model_v4 knee 0..135 (15 deg), housing STEP swapped for the finned one; min OCC distance fins/housing to every
L-leg/R-leg part except the housing's own mates (trunnion pins, knee screw bodies) + knee-cap keep-out STL + thigh fairing keep-out."""
import os,sys,json,math,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, trimesh
T=float(os.environ.get('T',1.0)); RHO=2.70e-6
H0=cq.importers.importStep(os.path.join(HERE,'../actuators/cad/knee_twin_housing.step')).val()
def fin(cx,a,h,z0,z1,r0):
    d=np.array([math.sin(math.radians(a)),-math.cos(math.radians(a))]); n=np.array([-d[1],d[0]])
    c=np.array([cx,0])+d*(r0-0.8+(h+0.8)/2)   # 0.8 mm embed into the wall for the union
    w=cq.Workplane('XY').rect(h+0.8,T).extrude(z1-z0).rotate((0,0,0),(0,0,1),math.degrees(math.atan2(d[1],d[0]))).translate((c[0],c[1],z0))
    return w.val()
def angles(lo,hi,n):
    span=(hi-lo)%360; return [(lo+span*(i+0.5)/n)%360 for i in range(n)]
F=[]
for cx in (-45,45):
    for a in angles(120,240,int(os.environ.get('REAR_N',7))): F.append((cx,a,25))
for cx,nf in (((-45,4),(45,3)) if not os.environ.get('NOFRONT') else ()):
    for a in angles(330,30,nf): F.append((cx,a,9))
fins=[]
for cx,a,h in F:
    fins+= [fin(cx,a,h,float(os.environ.get('ZBOT',2)),35,41.0), fin(cx,a,h,35,float(os.environ.get('ZTOP',103)),19.5)]
FC=cq.Compound.makeCompound(fins); FV=FC.fuse(H0) if False else None
vol=sum(f.Volume() for f in fins)   # includes 0.8 mm embed: subtract
emb=len(fins)*0.8*T*0
# exact added volume = fused - housing
fused=cq.Workplane().add(H0).union(cq.Workplane().add(FC)); add_v=fused.val().Volume()-H0.Volume()
step=f'{HERE}/cad/knee_twin_housing_fins_d69c_T{T:g}'+('_z'+os.environ['ZTOP'] if os.environ.get('ZTOP') else '')+('_b'+os.environ['ZBOT'] if os.environ.get('ZBOT') else '')+('_r'+os.environ['REAR_N']+'nf' if os.environ.get('NOFRONT') else '')+'.step'; cq.exporters.export(fused,step)
area=sum(2*h*101 for _,_,h in F)/1e6
res=dict(T_mm=T,n_fins=len(F),fins=[dict(tube=cx,ang=round(a,1),h=h) for cx,a,h in F],added_volume_mm3=round(add_v),mass_kg_per_knee=round(add_v*RHO,4),
         fin_area_both_faces_m2=round(area,4),step=os.path.relpath(step,HERE))
print(json.dumps({k:v for k,v in res.items() if k!='fins'}),flush=True)
if os.environ.get('NOSWEEP'): sys.exit()
import model_v4 as M
_st=M.step; FUSED=FC if os.environ.get('FINSONLY') else fused.val()
M.step=lambda n: FUSED if n=='knee_twin_housing' else _st(n)
KC=np.asarray(trimesh.load(f'{HERE}/results/v5/knee_cap_keepout.stl').vertices); TF=trimesh.load(f'{HERE}/results/v5/thigh_fairing_keepout.stl')
SKIP=('knee twin housing','knee trunnion pin','knee body','knee screw +y RV12 roller-screw body','knee screw -y RV12 roller-screw body')
rows=[]
for ang in list(range(0,136,15))+[135]:
    parts=M.build({'L_knee':ang}); H=[p for p in parts if p['name'].startswith('L_knee twin housing')][0]['solid']; hb=H.BoundingBox(); near=[]
    for p in parts:
        n=p['name']
        if any(k in n for k in SKIP) or not n[:2] in ('L_','R_'): continue
        b=p['solid'].BoundingBox(); m=40
        if b.xmin>hb.xmax+m or b.xmax<hb.xmin-m or b.ymin>hb.ymax+m or b.ymax<hb.ymin-m or b.zmin>hb.zmax+m or b.zmax<hb.zmin-m: continue
        d=cq.Compound.makeCompound([H]).distance(cq.Compound.makeCompound([p['solid']])); near.append((round(float(d),2),n))
    near.sort(); vs,_=H.tessellate(1.0); P=np.array([[v.x,v.y,v.z] for v in vs])
    dk=float(np.min(np.linalg.norm(KC[None,::2,:]-P[::4,None,:],axis=2)))
    from scipy.spatial import ConvexHull
    hq=ConvexHull(np.asarray(TF.vertices)).equations; dout=(P@hq[:,:3].T+hq[:,3]).max(1); out_tf=dict(n_out=int((dout>0).sum()),max_out_mm=round(float(dout.max()),1))
    rows.append(dict(knee=ang,closest=near[:5],to_kneecap_keepout=round(dk,1),verts_outside_thigh_fairing_keepout=out_tf,n_verts=len(P)))
    print(ang,near[:3],'KC',round(dk,1),'outTF',out_tf,flush=True)
res['sweep']=rows
json.dump(res,open(f'{HERE}/results/r031/knee_fins_d69c_T{T:g}'+(('_finsonly' if os.environ.get('FINSONLY') else '')+('_z'+os.environ['ZTOP'] if os.environ.get('ZTOP') else '')+('_b'+os.environ['ZBOT'] if os.environ.get('ZBOT') else '')+('_r'+os.environ['REAR_N']+'nf' if os.environ.get('NOFRONT') else ''))+'.json','w'),indent=1)
