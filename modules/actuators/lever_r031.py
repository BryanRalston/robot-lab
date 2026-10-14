"""R-031 hip_pitch lever section check + STEP (Legs R031_FIXES pick b30/d0 36/d1 19, fallback b35/d0 40/d1 21.3, R8 blends).
Geometry = hp_lever_fea_v2.geom() (G2 arms) with B/D0/D1/RJ=8. Checks (light, OCC distances):
 1 envelope: max |y| of the lever inside r<34 about the pivot (y) axis <= 38.5 (Legs L35)
 2 rod-end eye: GE12 C eye proxy dia 30 x 12 on each pin, outboard of the ear face (model_v4 convention), clearance >= 1 mm,
   eye tilted +/-10 deg (GE12 C alpha) about x and z
 3 RV12 rod sweep: rod r6 from the eye along the screw direction, screw angle swept over the stroke (rotation about y, -110..+45)
 4 femur: tube dia 50 at x 18 (model_v4) rotated about y over hip_pitch -107.3..+40; min distance to the lever (>=1 mm) and
   angle between arm axis and femur axis at the extremes (>=30 deg).
Run: B=30 D0=36 D1=19 python3 lever_r031.py  -> results/lever_r031_<tag>.json, cad/hip_pitch_lever_r031_<tag>.step"""
import os, sys, json, math, numpy as np
os.environ.setdefault('RJ', '8')
sys.argv = [sys.argv[0]]
from unittest import mock
for _m in ('gmsh',): sys.modules[_m]=mock.MagicMock()   # geometry only, no meshing
import hp_lever_fea_v2 as V, cadquery as cq
tag = f"b{V.P['b']:g}_d{V.P['d0']:g}"
s = V.geom(); sol = s.val()
vol = sum(x.Volume() for x in s.solids().vals())
mass = (vol - 2*np.pi*36*25)*V.L.RHO + 2*np.pi*36*25*7.85e-6   # same rule as hp_lever_fea_v2 --mass
cq.exporters.export(s, f'{V.H}/cad/hip_pitch_lever_r031_{tag}.step')
def dist(a, b): return a.distance(b)[0] if hasattr(a, 'distance') else None
def C(w): return cq.Compound.makeCompound(w.solids().vals())
def d(a, b): return float(C(a).distance(C(b)))
# 1 envelope
cyl = cq.Workplane('XZ').circle(34).extrude(200, both=True)
inner = s.intersect(cyl); bb = C(inner).BoundingBox(); ymax = max(abs(bb.ymin), abs(bb.ymax))
res = dict(tag=tag, b=V.P['b'], d0=V.P['d0'], d1=V.P['d1'], RJ=V.P['RJ'], fillet=V.geom.fillet, mass_kg=mass, valid=sol.isValid(), env_ymax_r34=ymax)
# 2/3 eye + rod per side (pin at y=+-50.., z=-50)
eyemin = 1e9; rodmin = 1e9
for sg in (1, -1):
    y0 = sg*(62 + 0.5)   # 0.5 mm washer/axial gap [EST]
    for tx in (-10, 0, 10):
        for tz in (-10, 0, 10):
            e = cq.Workplane('XZ').circle(15).circle(6).extrude(-12*sg).translate((0, y0, -50))
            e = e.rotate((0, y0, -50), (0, y0+1, -50), 0).rotate((0, y0, -50), (1, y0, -50), tx).rotate((0, y0, -50), (0, y0, -49), tz)
            eyemin = min(eyemin, d(s, e))
    for ang in range(-110, 46, 10):
        a = math.radians(ang); u = (math.cos(a), 0, math.sin(a))
        rod = cq.Workplane(cq.Plane(origin=(15*u[0], y0+sg*6, -50+15*u[2]), xDir=(0, 1, 0), normal=u)).circle(6).extrude(120)
        rodmin = min(rodmin, d(s, rod))
res.update(eye_min_mm=eyemin, rod_min_mm=rodmin)
# 4 femur
fmin = 1e9; worst = None
fem0 = cq.Workplane('XY').center(18, 0).circle(25).circle(23.8).extrude(-300).translate((0, 0, -40))
for th in list(np.arange(-107.3, 40.1, 7.5)) + [40.0]:
    f = fem0.rotate((0, 0, 0), (0, 1, 0), float(th)); dd = d(s, f)
    if dd < fmin: fmin, worst = dd, float(th)
ax = np.array([0, 0.717, -0.698])   # arm axis (G2 loft, lever frame)
ang = {th: math.degrees(math.acos(abs(ax @ np.array([math.sin(math.radians(-th)), 0, -math.cos(math.radians(th))])))) for th in (-107.3, 40.0)}
res.update(femur_min_mm=fmin, femur_min_at=worst, arm_femur_angle_deg=ang)
res['pass'] = dict(envelope=ymax <= 38.5, eye=eyemin >= 1, rod=rodmin >= 1, femur=fmin >= 1, angle=min(ang.values()) >= 30)
json.dump(res, open(f'{V.H}/results/lever_r031_{tag}.json', 'w'), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
