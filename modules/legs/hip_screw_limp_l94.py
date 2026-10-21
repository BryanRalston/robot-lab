import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import model_v4 as M
_st=M.step; M.step=lambda n,*a,**k: _st('knee_twin_housing_release_r116b' if n=='knee_twin_housing' else n,*a,**k)
out={}
for nm,pz in (('L-10_Rstraight',{'L_hip_roll':-10}),('both-10',{'L_hip_roll':-10,'R_hip_roll':10}),('both-3',{'L_hip_roll':-3,'R_hip_roll':3})):
    ps=M.build(pz); L=[p for p in ps if p['name'].startswith('L_') and 'hip' in p['name'].lower()]; R=[p for p in ps if p['name'].startswith('R_') and 'hip' in p['name'].lower()]
    if 'Rstraight' in nm: R=[p for p in ps if p['name'].startswith('R_')]
    pr=[]
    for a in L:
        ab=a['solid'].BoundingBox()
        if ab.ymin>60: continue
        for b in R:
            bb=b['solid'].BoundingBox()
            if bb.ymax<ab.ymin-10 or bb.zmax<ab.zmin-10 or bb.zmin>ab.zmax+10: continue
            d=float(a['solid'].distance(b['solid']))
            if d<15: pr.append((round(d,2),a['name'][2:60],b['name'][2:60]))
    out[nm]=sorted(pr)[:8]; print(nm,out[nm],flush=True)
json.dump(out,open(f'{HERE}/results/r031/hip_screw_limp_l94.json','w'),indent=1)
