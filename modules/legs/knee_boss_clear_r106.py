"""R-106: clearance of grown trunnion bosses (ø26, outward 10 mm from cheek outer face, axis at cheek bbox xz-centre [EST pin axis]) to rev B fins AND full housing, cheeks at L60 DY=3."""
import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'../model'))
import cadquery as cq, model_v4 as M
A=os.path.join(HERE,'../actuators/cad'); FIN=cq.importers.importStep(f'{A}/knee_twin_housing_finned_revb.step').val()
_st=M.step; M.step=lambda n: FIN if n=='knee_twin_housing' else _st(n)
rows=[]
for ang in range(0,136,15):
    P=M.build({'L_knee':ang}); H=[p for p in P if p['name'].startswith('L_knee twin housing')][0]['solid']; d={}
    for p in P:
        n=p['name']
        if not n.startswith('L_knee trunnion cheek'): continue
        sg=1 if '+y' in n else -1; s=p['solid'].translate(cq.Vector(0,3.0*sg,0)); b=s.BoundingBox()
        yo=b.ymax if sg>0 else b.ymin
        boss=cq.Solid.makeCylinder(13,10,cq.Vector((b.xmin+b.xmax)/2,yo,(b.zmin+b.zmax)/2),cq.Vector(0,sg,0))
        d[n+' boss']=round(float(H.distance(boss)),2)
    rows.append(dict(knee=ang,**d)); print(ang,d,flush=True)
mins={k:min(r[k] for r in rows) for k in rows[0] if k!='knee'}
json.dump(dict(rows=rows,mins=mins),open(f'{HERE}/results/r031/knee_boss_clear_r106.json','w'),indent=1); print('mins',mins)
