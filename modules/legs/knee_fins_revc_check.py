"""R-077: clash check of Actuators rev C finned knee housing (cad/knee_twin_housing_finned_revc.step) - fins-only body (rev C minus D59
housing) swapped into model_v4, knee 0..135: min OCC distance to every L/R part except the housing's own mates, + v5 thigh fairing hull
(fins inside?) + knee-cap keep-out. Same method as knee_fins_d69c.py (L50)."""
import os,sys,json,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, trimesh, model_v4 as M
from scipy.spatial import ConvexHull
A=os.path.join(HERE,'../actuators/cad'); H0=cq.importers.importStep(f'{A}/knee_twin_housing.step').val(); RC=cq.importers.importStep(f'{A}/knee_twin_housing_finned_revc.step').val()
FIN=RC.cut(H0); print('fin vol',FIN.Volume(),'mass',FIN.Volume()*2.70e-6,flush=True)
_st=M.step; M.step=lambda n: FIN if n=='knee_twin_housing' else _st(n)
KC=np.asarray(trimesh.load(f'{HERE}/results/v5/knee_cap_keepout.stl').vertices); TF=ConvexHull(np.asarray(trimesh.load(f'{HERE}/results/v5/thigh_fairing_keepout.stl').vertices)).equations
SKIP=('knee twin housing','knee trunnion pin','RV12 roller-screw body')
rows=[]
for ang in range(0,136,15):
    P=M.build({'L_knee':ang}); F=[p for p in P if p['name'].startswith('L_knee twin housing')][0]['solid']; fb=F.BoundingBox(); near=[]
    for p in P:
        n=p['name']
        if any(k in n for k in SKIP) or n[:2] not in ('L_','R_'): continue
        b=p['solid'].BoundingBox(); m=40
        if b.xmin>fb.xmax+m or b.xmax<fb.xmin-m or b.ymin>fb.ymax+m or b.ymax<fb.ymin-m or b.zmin>fb.zmax+m or b.zmax<fb.zmin-m: continue
        near.append((round(float(cq.Compound.makeCompound([F]).distance(cq.Compound.makeCompound([p['solid']]))),2),n))
    near.sort(); vs,_=F.tessellate(1.0); V=np.array([[v.x,v.y,v.z] for v in vs])
    dk=float(np.min(np.linalg.norm(KC[None,::2,:]-V[::4,None,:],axis=2))); out=float((V@TF[:,:3].T+TF[:,3]).max(1).max())
    rows.append(dict(knee=ang,closest=near[:4],kneecap_mm=round(dk,1),max_outside_thigh_fairing_mm=round(out,1))); print(rows[-1],flush=True)
json.dump(dict(fin_mass_kg=FIN.Volume()*2.70e-6,rows=rows),open(f'{HERE}/results/r031/knee_fins_revc_check.json','w'),indent=1)
