"""L35 re-check in model_v4: swap the hip_pitch lever STEP for Legs' merged-web R-031 lever and measure min distance
lever <-> every non-mate L-leg part (thigh, hip, screws/rods) over hip_pitch -107.3..+40. Usage: TAG=b30_d36 python3 lever_l35_model.py"""
import os,sys,json,math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
tag=os.environ.get('TAG','b30_d36'); _st=M.step
def step(n):
    if n=='hip_pitch_lever_B_needle_sf15' and tag!='stock': return cq.importers.importStep(f'{HERE}/cad/hip_pitch_lever_r031_mw_{tag}.step').val()
    return _st(n)
M.step=step
MATE=('shaft','TLA3520','roll-output bracket','GE12','RV12 rod','top eye')
res={}; 
for th in (-107.3,-90,-60,-30,0,20,40):
    parts=M.build({'L_hip_pitch':th}); lev=[p for p in parts if 'lever B' in p['name'] and p['name'].startswith('L')][0]
    lb=lev['solid'].BoundingBox(); out=[]
    for p in parts:
        if p is lev or not p['name'].startswith('L') or any(k in p['name'] for k in MATE): continue
        b=p['solid'].BoundingBox()
        if b.xmin>lb.xmax+30 or b.xmax<lb.xmin-30 or b.ymin>lb.ymax+30 or b.ymax<lb.ymin-30 or b.zmin>lb.zmax+30 or b.zmax<lb.zmin-30: continue
        try: d=lev['solid'].distance(p['solid'])[0] if hasattr(lev['solid'],'distance') else None
        except Exception: d=None
        if d is None:
            d=cq.Compound.makeCompound([lev['solid']]).distance(cq.Compound.makeCompound([p['solid']]))
        iv=round(lev['solid'].intersect(p['solid']).Volume(),1) if d<0.01 else 0.0
        out.append((round(float(d),2),iv,p['name']))
    out.sort(); res[th]=out[:10]; print(th,out[:8],flush=True)
json.dump(res,open(f'{HERE}/results/r031/lever_l35_model_{tag}.json','w'),indent=1)
