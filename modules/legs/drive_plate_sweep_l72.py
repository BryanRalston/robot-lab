"""L72: Actuators D94 drive heat plate placements [EST] (DRIVE_HEAT_PLATES rev 4b). Each plate modelled as a slab = 1.5 mm plate
+ 8.5 mm G10 standoff layer (10 mm in x, plate centre x given, standoff layer toward +x = back face side), face size per D94.
Drive bodies on the plate face are NOT modelled (no size given). Min OCC distance to every other part over the joint ROM poses."""
import os,sys,json,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
C={'HP1':('pelvis',(84,84),(-45,88,905)),'HP2':('pelvis',(84,84),(-45,172,905)),
   'AN1':('L_shank',(56,60),(-40,130,150)),'AN2':('L_shank',(56,60),(-40,130,215))}
_bl=M.build_leg
def bl(s):
    _bl(s)
    if s>0:
        for k,(seg,(w,h),c) in C.items(): M.add('PL_'+k,seg,M.box(10,w,h,c=(c[0]+0.75+3.5,c[1],c[2])),asm='PL_'+k)  # x span c-0.75 .. c+9.25
M.build_leg=bl
POSES=[{}]+[{'L_knee':a} for a in (30,60,90,120,135,145)]+[{'L_hip_pitch':a} for a in (-107.3,-60,-30,20,40)]+[{'L_ankle_pitch':a} for a in (-40,-20,20,30)]+[{'L_ankle_roll':a} for a in (-20,20)]+[{'L_hip_roll':-20},{'L_hip_roll':45},{'L_hip_yaw':45},{'L_hip_yaw':-35},{'L_hip_pitch':-100,'L_knee':135}]
res={k:dict(cand=C[k],min=1e9,lim=None,near={}) for k in C}
for pz in POSES:
    try: parts=M.build(pz)
    except Exception as e: print('pose fail',pz,e); continue
    for k in C:
        pl=[p for p in parts if p['name']=='PL_'+k][0]; bb=pl['solid'].BoundingBox()
        for p in parts:
            if p['name'].startswith('PL_'): continue
            b=p['solid'].BoundingBox(); m=30
            if b.xmin>bb.xmax+m or b.xmax<bb.xmin-m or b.ymin>bb.ymax+m or b.ymax<bb.ymin-m or b.zmin>bb.zmax+m or b.zmax<bb.zmin-m: continue
            d=round(float(pl['solid'].distance(p['solid'])),1)
            n=res[k]['near']; n[p['name']]=min(n.get(p['name'],1e9),d)
            if d<res[k]['min']: res[k]['min']=d; res[k]['lim']=f"{p['name']} @{pz}"
    print(pz,{k:(v['min'],(v['lim'] or '')[:70]) for k,v in res.items()},flush=True)
for k in res: res[k]['near']=dict(sorted(res[k]['near'].items(),key=lambda t:t[1])[:8])
res['_P']={k:M.P[k] for k in ('hip_z','knee_z','ankle_z','hip_y','pelvis_bot','pelvis_top') if k in M.P}
json.dump(res,open(f'{HERE}/results/r031/drive_plate_sweep_l72.json','w'),indent=1); print(json.dumps(res,indent=1))
