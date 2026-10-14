"""L35 re-check for the R-031 hip_pitch lever with Legs' MERGED WEB (light, CadQuery/OCC).
Geometry: Actuators hp_lever_fea_v2.geom() G2 arms at B/D0/D1, bore relief R5 (G2 as briefed), PLUS Legs' merged web:
the closed 5 mm cap (r<=27, |y| 33.5..38.5) grown to a full-depth web = solid disc r<=RO(30), |y| 33.5..38.5, unioned to the arm root,
then R8 (fallback R6/R5/R4) blend attempted on the web/arm edges. Pins/needle race mass rule = hp_lever_fea_v2.
Envelope measure (L35 basis): max |y| of lever material within r<=27 of the pivot (cap zone) AND within r<=34 (Actuators' measure).
Usage: B=30 D0=36 D1=19 python3 lever_l35_r031.py"""
import os,sys,json,math,numpy as np
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'../actuators'))
from unittest import mock; sys.modules['gmsh']=mock.MagicMock()
os.environ['RJ']='5'
import hp_lever_fea_v2 as V, cadquery as cq
HERE=os.path.dirname(os.path.abspath(__file__)); tag=f"b{V.P['b']:g}_d{V.P['d0']:g}"
s=V.geom()
for sg in (1,-1):
    disc=cq.Workplane('XZ').circle(V.P['RO']).extrude(5).translate((0,sg*33.5 if sg<0 else 38.5,0)) if False else \
         cq.Workplane('XZ').workplane(offset=-(33.5 if sg>0 else -38.5)).circle(V.P['RO']).extrude(-5)
    s=s.union(disc)
bb=s.solids().vals(); ok=len(bb)
fil='none'
es=[e for e in s.edges().vals() if 33.0<abs(e.Center().y)<39 and e.Center().z<-20 and e.geomType() in ('BSPLINE','LINE','ELLIPSE')]
for r in (8,6,5,4):
    try:
        t=s.newObject(es).fillet(r)
        if t.val().isValid(): s=t; fil=f'R{r} on {len(es)} web/arm edges'; break
    except Exception: pass
vol=sum(x.Volume() for x in s.solids().vals()); vp=2*np.pi*36*25
mass=(vol-vp)*V.L.RHO+vp*7.85e-6
def C(w): return cq.Compound.makeCompound(w.solids().vals())
def ymax(r):
    bx=C(s.intersect(cq.Workplane('XZ').circle(r).extrude(200,both=True))).BoundingBox(); return max(abs(bx.ymin),abs(bx.ymax))
os.makedirs(f'{HERE}/cad',exist_ok=True); fn=f'{HERE}/cad/hip_pitch_lever_r031_mw_{tag}.step'; cq.exporters.export(s,fn)
res=dict(tag=tag,b=V.P['b'],d0=V.P['d0'],d1=V.P['d1'],fillet=fil,valid=s.val().isValid(),solids=len(s.solids().vals()),mass_kg=round(mass,4),
         ymax_r27=round(ymax(27),2),ymax_r34=round(ymax(34),2),step=os.path.relpath(fn,HERE))
os.makedirs(f'{HERE}/results/r031',exist_ok=True); json.dump(res,open(f'{HERE}/results/r031/lever_mw_{tag}.json','w'),indent=1); print(json.dumps(res))
