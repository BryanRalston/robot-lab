"""L84 rev 2: D99 STEP / Actuators placement (contact 130, t0 -20, stacks y 46/214, strikers = lugs+arms on the tibia, seat bar to the o64 collar).
Actuators' sweep (knee_stop_sweep_d99.json) skips same-segment pairs. This adds them: seats/bar vs every thigh part and strikers vs every shank part
(static), plus the Legs mounts: the tibia knee-end collar ring (o53 x 24, bonded) that carries the arms, and the o64-collar tie lugs. Reports CAD mass growth."""
import os,sys,json,math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model')); sys.path.insert(0,os.path.join(HERE,'../actuators'))
import cadquery as cq, model_v4 as M
import importlib.util as iu
src=open(os.path.join(HERE,'../actuators/knee_stop_sweep_d99.py')).read().split('def bl(')[0].replace('t0-16,t0-4','t0-22,t0-4'); ns={'__file__':os.path.join(HERE,'../actuators/knee_stop_sweep_d99.py')}; exec(src,ns)
pad,seat,strk=ns['parts'](-20.0); kz=ns['kz']; C=ns['C']
s0=strk.translate(cq.Vector(0,0,-kz)).rotate(cq.Vector(0,0,0),cq.Vector(0,1,0),-C*1).translate(cq.Vector(0,0,kz))
parts=M.build({}); tib=[p for p in parts if p['name'].startswith('L_tibia tube')][0]['solid'].BoundingBox()
# Legs mounts
tx=(tib.xmin+tib.xmax)/2; ring_z0=tib.zmax-30
ring=cq.Workplane('XY').circle(26.5).circle(22.5).extrude(24).translate((tx,130,ring_z0)).val()
rho=2.81e-6; out={'ring_kg':round(ring.Volume()*rho,4)}
bb=s0.BoundingBox(); out['striker_shank_frame_bbox']=[round(v,1) for v in (bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax)]
out['striker_kg']=round(s0.Volume()*rho,4); out['seat_bar_kg']=round(sum(x.Volume() for x in seat)*rho,4)
res=[]
for nm,sol,seg in [('seat/bar','x','L_thigh')]+[('striker',s0,'L_shank')]:
    for i,x in enumerate(seat if nm=='seat/bar' else [s0]):
        for p in parts:
            if p['seg']!=seg or 'tibia tube' in p['name'] or 'tongue neck' in p['name']: continue
            res.append((round(float(x.distance(p['solid'])),1),f'{nm}{i}',p['name']))
res.sort(); out['same_segment_min']=res[:10]
# o64 collar tie: distance from the bar to the collar
col=[p for p in parts if 'split collar' in p['name'] and p['seg']=='L_thigh'][0]['solid']
out['bar_to_o64_collar_mm']=round(float(seat[-1].distance(col)),1)
json.dump(out,open(f'{HERE}/results/r031/knee_stop_d99_r2_l84.json','w'),indent=1); print(json.dumps(out))
