"""D92 G3 lever fix (job2 334e848 FAIL): Legs L47 merged-web lever + resized section + fillets at the singular corners.
Hot spots fixed: (a) upper web/arm edge at |y|=38.5, z>-20 (job2 peak (-15.7,38.6,-10.0)) -> R RU fillet;
(b) ear/arm root at |y|~50, z~-52 (job2 L2 / b35 peak) -> ear dia ED, R RE fillet. Section B/D0/D1 enlarged.
Usage: B=38 D0=40 D1=22 ED=34 RU=8 RE=3 python3 lever_g3_fillet.py"""
import os,sys,json,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from unittest import mock; sys.modules['gmsh']=mock.MagicMock()
os.environ.setdefault('RJ','5')
import hp_lever_fea_v2 as V, cadquery as cq
ED=float(os.environ.get('ED',26)); RU=float(os.environ.get('RU',8)); RE=float(os.environ.get('RE',5))
s=V.geom()
for sg in (1,-1):   # Legs merged web (lever_l35_r031.py)
    s=s.union(cq.Workplane('XZ').workplane(offset=-(33.5 if sg>0 else -38.5)).circle(V.P['RO']).extrude(-5))
    if ED>26:  # enlarged ear boss, same 12 mm thickness |y| 50..62
        s=s.union(cq.Workplane('XZ').center(0,-50).circle(ED/2).extrude(-12 if sg>0 else 12).translate((0,sg*50,0)))
log=[]
def fil(sel,rs,name):
    global s
    es=[e for e in s.edges().vals() if sel(e.Center())]
    for r in rs:
        try:
            t=s.newObject(es).fillet(r)
            if t.val().isValid() and len(t.solids().vals())==2: s=t; log.append(f'{name} R{r:g} on {len(es)} edges'); return r
        except Exception: pass
    log.append(f'{name} FAILED on {len(es)} edges'); return 0
rl=fil(lambda c:33<abs(c.y)<39 and c.z<-20,(8,6,5,4),'lower web/arm')
# BRep fillet fails on the loft/union edges (tried R8..2 / R5..1), so blends are built as explicit concave fillet solids
# (corner prism minus tangent cylinder) unioned in: exact for planar faces, which these are (arm side x=+-xa, web face y, ear face y).
def blend(xa,y0,R,zlo,zhi,clip):
    global s
    for sx in (1,-1):
        for sy in (1,-1):
            # concave corner region: |x|>xa, sy*y on the far side of the face y0 (toward the arm)
            dy = 1 if y0==38.5 else -1      # web face: arm lies at |y|>38.5 ; ear face: arm lies at |y|<50
            xc=sx*(xa+R); yc=sy*(y0+dy*R)
            box=cq.Workplane('XY').box(R+0.2,R,zhi-zlo,centered=False).translate((0,0,zlo))
            box=box.translate((xa-0.2 if sx>0 else -xa-R,(y0 if dy>0 else y0-R) if sy>0 else (-y0-R if dy>0 else -y0),0))
            cyl=cq.Workplane('XY').circle(R).extrude(zhi-zlo+2).translate((xc,yc,zlo-1))
            s=s.union(box.cut(cyl).intersect(clip(sy)))
xa=V.P['b']/2
web=lambda sy: cq.Workplane('XZ').circle(V.P['RO']).extrude(200,both=True)
blend(xa,38.5,RU,-24.0,-6.0,web); ru=RU; log.append(f'upper web/arm R{RU:g} explicit blend (|x|={xa:g}, |y|=38.5, z -24..-6), 4 places')
earc=lambda sy: cq.Workplane('XZ').center(0,-50).circle(ED/2).extrude(200,both=True)
xe=float(os.environ.get('XE',16.4)); blend(xe,50.0,RE,-60.0,-40.0,earc); re=RE; log.append(f'ear root R{RE:g} explicit blend (|x|={xe:g}, |y|=50), 4 places')
vol=sum(x.Volume() for x in s.solids().vals()); vp=2*np.pi*36*25
mass=(vol-vp)*V.L.RHO+vp*7.85e-6
tag=f"g3_b{V.P['b']:g}_d{V.P['d0']:g}_e{ED:g}"
fn=f'{V.H}/cad/hip_pitch_lever_{tag}.step'; cq.exporters.export(s,fn)
res=dict(tag=tag,b=V.P['b'],d0=V.P['d0'],d1=V.P['d1'],ear_dia=ED,fillets=log,R_upper=ru,R_lower=rl,R_ear=re,valid=s.val().isValid(),
         volume_mm3=round(vol,1),mass_kg=round(mass,4),step=os.path.relpath(fn,V.H))
json.dump(res,open(f'{V.H}/results/lever_{tag}.json','w'),indent=1); print(json.dumps(res))

# RV12 rod sweep + eye (same as lever_r031.py checks 2/3)
import math
def C(w): return cq.Compound.makeCompound(w.solids().vals())
def d(a,b): return float(C(a).distance(C(b)))
rodmin=1e9
for sg in (1,-1):
    y0=sg*62.5
    for ang in range(-110,46,10):
        a_=math.radians(ang); u=(math.cos(a_),0,math.sin(a_))
        rod=cq.Workplane(cq.Plane(origin=(15*u[0],y0+sg*6,-50+15*u[2]),xDir=(0,1,0),normal=u)).circle(6).extrude(120)
        rodmin=min(rodmin,d(s,rod))
res.update(rod_min_mm=round(rodmin,2),valid=s.val().isValid(),solids=len(s.solids().vals()))
json.dump(res,open(f'{V.H}/results/lever_{tag}.json','w'),indent=1); print(json.dumps(res))
