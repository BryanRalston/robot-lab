"""L78: (1) D97/P-159 knee PU stop stacks placed in model_v4 [EST placement]: 2 thigh-fixed stacks 40 (radial) x 40 (y) x 41 (tangential) centred at
r 60 on the 135-deg ray from the knee axis (contact at 135, crush to 141.9), outboard of the clevis cheeks (y 62-102 / 158-198, the 28 mm tongue
y 116-144 leaves no room inside the clevis). Swept vs shank parts over knee 0..141.9 (the shank striker itself is not modelled -> its contact is excluded
by reporting per part). (2) ID P-158 thigh-front pad (thigh-fixed) x 46..72 (skin 48.7-55.6 + 16.4 proud, conservative box), y 95-165, z 540-590,
vs shank parts over knee 0..145 + hip ROM + other leg. Gate 3 mm. Housing r116b."""
import os,sys,json,math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
kz=M.P['knee_z']; a=math.radians(135)
def stack(yc):
    b=cq.Workplane('XY').box(40,40,41).val()   # local x radial, z tangential
    b=b.rotate(cq.Vector(0,0,0),cq.Vector(0,1,0),-135)  # radial dir from 'down' rotated rearward
    return b.translate(cq.Vector(-60*math.sin(a),yc,kz-60*math.cos(a)))
_bl=M.build_leg
def bl(s):
    _bl(s)
    if s>0:
        M.add('X_stop_ny','L_thigh',stack(82),asm='X1'); M.add('X_stop_py','L_thigh',stack(178),asm='X2')
        M.add('X_pad_P158','L_thigh',M.box(26,70,50,c=(59,130,565)),asm='X3')
M.build_leg=bl
P1=[{'L_knee':k} for k in (0,30,60,90,120,130,135,138,141.9)]
P2=[{'L_knee':k} for k in (0,10,20,40,60,90,120,145)]+[{'L_hip_pitch':p} for p in (-107.3,-60,20,40)]+[{'L_hip_roll':-20,'R_hip_roll':-20},{'L_hip_yaw':-35,'R_hip_yaw':-35},{'L_hip_yaw':45,'R_hip_yaw':45},{'L_hip_pitch':-100,'L_knee':135}]
res={}
def run(poses,names):
    for pz in poses:
        parts=M.build(pz); X=[p for p in parts if p['name'] in names]
        for p in parts:
            if p['name'].startswith('X_') or (p['seg']=='L_thigh' and pz!={} and 'knee twin housing' not in p['name']): continue
            b=p['solid'].BoundingBox()
            for v in X:
                bb=v['solid'].BoundingBox(); m=15
                if b.xmin>bb.xmax+m or b.xmax<bb.xmin-m or b.ymin>bb.ymax+m or b.ymax<bb.ymin-m or b.zmin>bb.zmax+m or b.zmax<bb.zmin-m: continue
                d=round(float(v['solid'].distance(p['solid'])),1); k=v['name']+' | '+p['name']
                if d<res.get(k,(1e9,))[0]: res[k]=(d,str(pz))
run(P1,('X_stop_ny','X_stop_py')); run(P2,('X_pad_P158',))
rows=sorted([[k,d,pz] for k,(d,pz) in res.items()],key=lambda t:t[1])
out=dict(stops=[r for r in rows if r[0].startswith('X_stop')][:12],pad=[r for r in rows if r[0].startswith('X_pad')][:10])
json.dump(out,open(f'{HERE}/results/r031/knee_stop_pad_sweep_l78.json','w'),indent=1); print(json.dumps(out,indent=0))
