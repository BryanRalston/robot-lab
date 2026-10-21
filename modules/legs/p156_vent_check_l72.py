"""L72 (b): ID P-156 knee vents (a0b2aea) vs leg CAD. (a) v5 thigh keep-out hull rear x over the pocket; (b) knee twin housing
bbox vs duct end x -63; (d) ROM min distance with duct walls (PA12 1.2, y 130+-26.5, x -34.5..-63, z 643-837), grille/inlet/outlet
skin slab (x -82.5..-84.0 [EST 1.5 skin], y 104-156, z 643-837) and bosses (o6x5 at y112/148 z684/796, x -82.5..-77.5)."""
import os,sys,json,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M, trimesh
from scipy.spatial import ConvexHull
out={}
hull=ConvexHull(np.asarray(trimesh.load(f'{HERE}/results/v5/thigh_fairing_keepout.stl').vertices)); E=hull.equations
def xmin_at(y,z):  # most negative x inside hull along a line at (y,z)
    xs=np.linspace(-400,200,6001); P=np.c_[xs,np.full_like(xs,y),np.full_like(xs,z)]; ins=(P@E[:,:3].T+E[:,3]).max(1)<=0
    return round(float(xs[ins].min()),1) if ins.any() else None
out['a_hull_rear_x']={f'y{y}_z{z}':xmin_at(y,z) for y in (104,130,156) for z in (643,690,740,792,837)}
DU=dict(duct_py=M.box(28.5,1.2,194,c=(-48.75,156.5+0.6,740)),duct_ny=M.box(28.5,1.2,194,c=(-48.75,103.5-0.6,740)),
        skin=M.box(1.5,52,194,c=(-83.25,130,740)))
for i,(y,z) in enumerate([(112,684),(148,684),(112,796),(148,796)]): DU[f'boss{i}']=M.cyl(6,5,'x',c=(-80,y,z))
_bl=M.build_leg
def bl(s):
    _bl(s)
    if s>0:
        for k,v in DU.items(): M.add('V_'+k,'L_thigh',v,asm='V_'+k)
M.build_leg=bl
parts=M.build({})
kh=[p for p in parts if 'knee twin housing' in p['name'] or 'knee_twin' in p['name']]
out['b_knee_housing']={p['name']:[round(v,1) for v in (lambda b:(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax))(p['solid'].BoundingBox())] for p in kh}
out['c_nearby_thigh_parts']={p['name']:[round(v,1) for v in (lambda b:(b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax))(p['solid'].BoundingBox())] for p in parts if not p['name'].startswith('V_') and (lambda b:b.xmax>-90 and b.xmin<-30 and b.ymax>100 and b.ymin<160 and b.zmax>640 and b.zmin<840)(p['solid'].BoundingBox())}
POSES=[{}]+[{'L_knee':a} for a in (30,60,90,120,135,140,145)]+[{'L_hip_pitch':-100,'L_knee':135},{'L_hip_pitch':20,'L_knee':145}]
res={}
for pz in POSES:
    parts=M.build(pz); V=[p for p in parts if p['name'].startswith('V_')]
    for p in parts:
        if p['name'].startswith('V_'): continue
        for v in V:
            bb=v['solid'].BoundingBox(); b=p['solid'].BoundingBox(); m=40
            if b.xmin>bb.xmax+m or b.xmax<bb.xmin-m or b.ymin>bb.ymax+m or b.ymax<bb.ymin-m or b.zmin>bb.zmax+m or b.zmax<bb.zmin-m: continue
            d=round(float(v['solid'].distance(p['solid'])),1); k=(v['name'],p['name'])
            if d<res.get(k,(1e9,))[0]: res[k]=(d,str(pz))
out['d_rom']=sorted([[a,b,d,pz] for (a,b),(d,pz) in res.items()],key=lambda t:t[2])[:15]
json.dump(out,open(f'{HERE}/results/r031/p156_vent_check_l72.json','w'),indent=1); print(json.dumps(out,indent=1))
