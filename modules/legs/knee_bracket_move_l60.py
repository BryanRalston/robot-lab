"""L60: move our [EST] knee trunnion cheeks (outward |y| +DY) and bracket top plate (+DZ up, thigh frame) and re-measure clearance to
Actuators rev B fins (fins only = revb - D59) over knee 0..135. Knee-only poses => thigh frame = world."""
import os,sys,json,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
A=os.path.join(HERE,'../actuators/cad'); FIN=cq.importers.importStep(f'{A}/knee_twin_housing_finned_revb.step').val().cut(cq.importers.importStep(f'{A}/knee_twin_housing.step').val())
_st=M.step; M.step=lambda n: FIN if n=='knee_twin_housing' else _st(n)
DY=float(os.environ.get('DY',1.5)); DZ=float(os.environ.get('DZ',1.5)); rows=[]
for ang in range(0,136,15):
    P=M.build({'L_knee':ang}); F=[p for p in P if p['name'].startswith('L_knee twin housing')][0]['solid']; r={}
    for p in P:
        n=p['name']
        if n.startswith('L_knee trunnion cheek'):
            s=p['solid'].translate(cq.Vector(0,(DY if '+y' in n else -DY),0)); r[n]=s
        elif n.startswith('L_knee trunnion bracket top plate'):
            r[n]=p['solid'].translate(cq.Vector(0,0,DZ))
    d={k:round(float(cq.Compound.makeCompound([F]).distance(cq.Compound.makeCompound([s]))),2) for k,s in r.items()}
    rows.append(dict(knee=ang,**d)); print(ang,d,flush=True)
mins={k:min(r[k] for r in rows) for k in rows[0] if k!='knee'}
json.dump(dict(DY=DY,DZ=DZ,rows=rows,mins=mins),open(f'{HERE}/results/r031/knee_bracket_move_l60.json','w'),indent=1); print('mins',mins)
