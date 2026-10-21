"""L84: D99 r75 PU knee stop, Legs side [EST geometry; D99 STEP not in the repo]. Strikers = 2 lugs machined on the knee tongue neck block (shank),
behind the tibia at shank-frame (x -8.5..-40, z 428-446), y 98-108 / 152-162 (tried y 84-94/166-176: 0.0 mm to the GE12 rod-end eyes at knee 0, worse) (lug 10 thick x 18 along the shank, 31.5 long, contact face r ~75 from the
knee axis). Seats = 2 short struts integral with the existing o64 thigh split collar (z 603-637) hanging to z 575 (x -30..-8, same y), carrying the PU stacks.
Sweep: knee 0..145 (+ hip extremes, mirrored yaw) at 3 mm, excluding the striker<->own seat pair (intended contact at 130)."""
import os,sys,json,math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
def bx(x0,x1,y0,y1,z0,z1): return M.box(x1-x0,y1-y0,z1-z0,c=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
_bl=M.build_leg
def bl(s):
    _bl(s)
    if s>0:
        for i,(y0,y1) in enumerate(((98,108),(152,162))):
            M.add(f'S_striker{i}','L_shank',bx(-40,-8.5,y0,y1,428,446),asm=f'S{i}'); M.add(f'S_seat{i}','L_thigh',bx(-30,-8,y0,y1,575,603),asm=f'T{i}')
M.build_leg=bl
P=[{'L_knee':k} for k in (0,30,60,90,110,120,125,130,135,140,143.6,145)]+[{'L_hip_pitch':-105,'L_knee':135},{'L_hip_pitch':40,'L_knee':130},{'L_hip_yaw':-35,'R_hip_yaw':-35},{'L_hip_yaw':45,'R_hip_yaw':45},{'L_hip_roll':-12,'R_hip_roll':-12}]
res={}; contact={}
for pz in P:
    parts=M.build(pz); X=[p for p in parts if p['name'].startswith('S_')]
    for v in X:
        bb=v['solid'].BoundingBox()
        for p in parts:
            if p['name']==v['name']: continue
            same=(p['name'].startswith('S_') and p['name'][-1]==v['name'][-1])
            if p['seg']==v['seg'] and not p['name'].startswith('S_') and pz.get('L_knee',0)!=0 and 'knee twin housing' not in p['name']: continue
            b=p['solid'].BoundingBox(); m=15
            if b.xmin>bb.xmax+m or b.xmax<bb.xmin-m or b.ymin>bb.ymax+m or b.ymax<bb.ymin-m or b.zmin>bb.zmax+m or b.zmax<bb.zmin-m: continue
            d=round(float(v['solid'].distance(p['solid'])),1)
            if same: contact[str(pz)]=d; continue
            k=v['name']+' | '+p['name']
            if d<res.get(k,(1e9,))[0]: res[k]=(d,str(pz))
rows=sorted([[k,d,pz] for k,(d,pz) in res.items()],key=lambda t:t[1])
out=dict(min_pairs=rows[:14],striker_to_own_seat_by_pose=contact)
json.dump(out,open(f'{HERE}/results/r031/knee_stop_d99_l84.json','w'),indent=1); print(json.dumps(out,indent=0))
