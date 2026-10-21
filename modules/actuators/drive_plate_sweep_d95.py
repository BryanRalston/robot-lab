"""D95: drive heat plate placements re-check (after Legs L72 e44c588 FAIL), based on legs/drive_plate_sweep_l72.py + model_v4.
Envelope per plate (D94 rev 4b): G10 standoff layer 8.5 (back face side, toward the structure) + 6061 plate 1.5 +
G-TWI drive 35 x 30 x 14.9 + integration PCB 1.6 (Electronics 23f6992) on the outer face. Plate face size W x H.
Normal n = direction from structure to drive (outward). ROM pose set = L72. Pass: min clearance >= 3 mm to every other part."""
import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
# name: (segment, (W along a, H along z), back-face contact point (structure surface + 3 mm gap), normal)
C={
 # Lateral/medial tibia faces were tried first and FAIL (0.0 mm to the knee twin housing at knee 145 / other leg at hip roll -20); see DRIVE_HEAT_PLATES rev 4c
 # ankle: shin front (Legs L72 suggestion), normal +x, back face 4 mm off the tibia tube front (x 36), long side along z
 'AN1':('L_shank',(56,60),(36+4,130,215),'+x'), 'AN2':('L_shank',(56,60),(36+4,130,290),'+x'),
 # hip pitch: outboard face of the pelvis shell rear wall (x -85, Torso), normal -x, z centre 1178 (shell 1126-1230), side by side in y
 'HP1':('pelvis',(84,84),(-85-3,45,1178),'-x'), 'HP2':('pelvis',(84,84),(-85-3,135,1178),'-x'),
}
def env(w,h,c,n):
    s=1 if n[0]=='+' else -1; ax=n[1]; L=8.5+1.5; D=16.5
    if ax=='x':
        st=M.box(L,w,h,c=(c[0]+s*L/2,c[1],c[2])); dr=M.box(D,35,30,c=(c[0]+s*(L+D/2),c[1],c[2]))
    else:
        st=M.box(w,L,h,c=(c[0],c[1]+s*L/2,c[2])); dr=M.box(35,D,30,c=(c[0],c[1]+s*(L+D/2),c[2]))
    return st,dr
_bl=M.build_leg
def bl(s):
    _bl(s)
    if s>0:
        for k,(seg,(w,h),c,n) in C.items():
            st,dr=env(w,h,c,n); M.add('PL_'+k,seg,st,asm='PL_'+k); M.add('DR_'+k,seg,dr,asm='PL_'+k)
M.build_leg=bl
# use the RELEASE knee housing (rev B front 9 / rear 25 mm fins, R-116 boss) instead of model_v4's plain D59 STEP
_st=M.step
M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116' if n=='knee_twin_housing' else n,*a,**k)
POSES=[{}]+[{'L_knee':a} for a in (30,60,90,120,135,145)]+[{'L_hip_pitch':a} for a in (-107.3,-60,-30,20,40)]+[{'L_ankle_pitch':a} for a in (-40,-20,20,30)]+[{'L_ankle_roll':a} for a in (-20,20)]+[{'L_hip_roll':-20},{'L_hip_roll':45},{'L_hip_yaw':45},{'L_hip_yaw':-35},{'L_hip_pitch':-100,'L_knee':135}]
res={k:dict(cand=[C[k][0],C[k][1],C[k][2],C[k][3]],min=1e9,lim=None,near={}) for k in C}
for pz in POSES:
    try: parts=M.build(pz)
    except Exception as e: print('pose fail',pz,e); continue
    for k in C:
        mine=[p for p in parts if p['name'] in ('PL_'+k,'DR_'+k)]
        for pl in mine:
            bb=pl['solid'].BoundingBox()
            for p in parts:
                if p['name'].startswith(('PL_','DR_')): continue
                b=p['solid'].BoundingBox(); m=30
                if b.xmin>bb.xmax+m or b.xmax<bb.xmin-m or b.ymin>bb.ymax+m or b.ymax<bb.ymin-m or b.zmin>bb.zmax+m or b.zmax<bb.zmin-m: continue
                d=round(float(pl['solid'].distance(p['solid'])),1)
                nn=res[k]['near']; nn[p['name']]=min(nn.get(p['name'],1e9),d)
                if d<res[k]['min']: res[k]['min']=d; res[k]['lim']=f"{p['name']} @{pz}"
    print(pz,{k:v['min'] for k,v in res.items()},flush=True)
for k in res: res[k]['near']=dict(sorted(res[k]['near'].items(),key=lambda t:t[1])[:6]); res[k]['pass']=res[k]['min']>=3
json.dump(res,open(f'{HERE}/results/drive_plate_sweep_d95.json','w'),indent=1)
for k,v in res.items(): print(k,v['min'],v['pass'],v['lim'],list(v['near'].items())[:4])
