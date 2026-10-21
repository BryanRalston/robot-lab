"""L77 (4): raised L60 top plate (z 820-828, x -175..-40, y 32-228, notch x -61..-34.5 y 104-156 R8) + twin straps (x -40..-8.5, y 84-104/156-176,
z 820-828) vs release housing (D95) and every non-thigh part over knee 0..145 + hip ROM. The original model_v4 plate/strut are excluded."""
import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
def bx(x0,x1,y0,y1,z0,z1): return M.box(x1-x0,y1-y0,z1-z0,c=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
notch=cq.Workplane('XY').box(26.5,52,20).edges('|Z').fillet(8).translate((-47.75,130,824)).val()
plate=bx(-175,-40,32,228,820,828).cut(notch)
_bl=M.build_leg
def bl(s):
    _bl(s)
    if s>0:
        M.add('N_plate','L_thigh',plate,asm='N_p'); M.add('N_strap_ny','L_thigh',bx(-40,-8.5,84,104,820,828),asm='N_s1'); M.add('N_strap_py','L_thigh',bx(-40,-8.5,156,176,820,828),asm='N_s2')
M.build_leg=bl
SKIP=('knee trunnion bracket top plate','knee trunnion bracket strut')
POSES=[{}]+[{'L_knee':a} for a in (30,60,90,110,120,130,135,140,143,145)]+[{'L_hip_pitch':-100,'L_knee':135},{'L_hip_pitch':20,'L_knee':145},{'L_hip_roll':-20,'R_hip_roll':-20},{'L_hip_yaw':-35,'R_hip_yaw':-35}]
res={}
for pz in POSES:
    parts=M.build(pz); N=[p for p in parts if p['name'].startswith('N_')]
    for p in parts:
        if p['name'].startswith('N_') or any(s in p['name'] for s in SKIP): continue
        if p['seg']=='L_thigh' and 'knee twin housing' not in p['name'] and pz: continue
        b=p['solid'].BoundingBox()
        for v in N:
            bb=v['solid'].BoundingBox(); m=20
            if b.xmin>bb.xmax+m or b.xmax<bb.xmin-m or b.ymin>bb.ymax+m or b.ymax<bb.ymin-m or b.zmin>bb.zmax+m or b.zmax<bb.zmin-m: continue
            d=round(float(v['solid'].distance(p['solid'])),2); k=v['name']+' | '+p['name']
            if d<res.get(k,(1e9,))[0]: res[k]=(d,str(pz))
rows=sorted([[k,d,pz] for k,(d,pz) in res.items()],key=lambda t:t[1])
json.dump(dict(min_pairs=rows[:20],under_3=[r for r in rows if r[1]<3]),open(f'{HERE}/results/r031/knee_rom_raised_plate_l77.json','w'),indent=1)
print(json.dumps(rows[:12],indent=0))
