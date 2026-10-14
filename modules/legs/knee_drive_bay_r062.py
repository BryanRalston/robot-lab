"""R-062: candidate volumes for the 2 knee Elmo Gold Twitter drives (EtherCAT: 35x30x14.4 bare, 47x41.3x18.4 with heatsink, 43.2 g each
[MAN-G-TWI]). Candidate boxes are added as parts on the L thigh (A,B) or pelvis (C) and the min OCC distance to every other part is
measured over hip_pitch -107.3..+40, knee 0/135, hip roll/yaw extremes. A/B also checked inside the v5 thigh fairing keep-out hull
(thigh frame) - a drive bay must sit INSIDE the fairing, so inside = good."""
import os,sys,json,math,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M, trimesh
from scipy.spatial import ConvexHull
C=json.loads(os.environ.get('CAND','{}')) or {
 'A_front_of_femur': dict(seg='thigh',size=(22,70,120),c=(57,130,700)),
 'B_rear_above_knee_housing': dict(seg='thigh',size=(60,70,40),c=(-70,130,850)),
 'C_lateral_thigh': dict(seg='thigh',size=(60,24,120),c=(-40,225,700)),
 'D_pelvis_underside_mid': dict(seg='pelvis',size=(80,60,30),c=(-20,0,1105)),
}
_bl=M.build_leg
def bl(s):
    _bl(s)
    if s>0:
        for k,v in C.items():
            if v['seg']=='thigh': M.add('BAY_'+k,'L_thigh',M.box(*v['size'],c=v['c']),asm='BAY_'+k)
            else: M.add('BAY_'+k,'pelvis',M.box(*v['size'],c=v['c']),asm='BAY_'+k)
M.build_leg=bl
FIN=os.environ.get('FINSTEP')
if FIN:
    _FS=cq.importers.importStep(FIN).val(); _st=M.step; M.step=lambda n: _FS if n=='knee_twin_housing' else _st(n)
POSES=[{'L_knee':a} for a in (0,30,60,90,120)]+[{'L_hip_pitch':a} for a in (-107.3,-90,-60,-30,0,20,40)]+[{'L_knee':135},{'L_hip_pitch':-100,'L_knee':135},{'L_hip_roll':-20,'R_hip_roll':-20},{'L_hip_roll':45},{'L_hip_yaw':45},{'L_hip_yaw':-35,'R_hip_yaw':-35}]
res={k:dict(cand=v,min=1e9,lim=None) for k,v in C.items()}
for pz in POSES:
    parts=M.build(pz)
    for k in C:
        bay=[p for p in parts if p['name']=='BAY_'+k][0]; bb=bay['solid'].BoundingBox()
        for p in parts:
            if p['name'].startswith('BAY_') or 'femur tube' in p['name'] or 'doubler sleeve' in p['name']: continue
            b=p['solid'].BoundingBox(); m=30
            if b.xmin>bb.xmax+m or b.xmax<bb.xmin-m or b.ymin>bb.ymax+m or b.ymax<bb.ymin-m or b.zmin>bb.zmax+m or b.zmax<bb.zmin-m: continue
            d=float(cq.Compound.makeCompound([bay['solid']]).distance(cq.Compound.makeCompound([p['solid']])))
            if d<res[k]['min']: res[k]['min']=round(d,1); res[k]['lim']=f"{p['name']} @{pz}"
    print(pz,{k:(v['min'],(v['lim'] or '')[:60]) for k,v in res.items()},flush=True)
TF=ConvexHull(np.asarray(trimesh.load(f'{HERE}/results/v5/thigh_fairing_keepout.stl').vertices)).equations
for k,v in C.items():
    if v['seg']!='thigh': continue
    c=np.array(v['c']); h=np.array(v['size'])/2; corners=np.array([c+h*np.array(s) for s in np.ndindex(2,2,2)])*1.0
    corners=np.array([c+h*(2*np.array(s)-1) for s in np.ndindex(2,2,2)]); res[k]['max_outside_thigh_fairing_mm']=round(float((corners@TF[:,:3].T+TF[:,3]).max()),1)
json.dump(res,open(f'{HERE}/results/r031/knee_drive_bay_r062.json','w'),indent=1); print(json.dumps(res,indent=0))
