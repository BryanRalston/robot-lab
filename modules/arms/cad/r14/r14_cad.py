"""R14 minimal STEP models (CadQuery 2.8, RL box). Frame: X roll axis (sim l_shoulder_roll), Y outboard, Z up, origin roll axis at bearing plane.
standoff_r14.step: ID R11 stand-off (ec12542) + Arms R14 fixes (flange OD76, bore D36 under box, 3x D8 wrench holes, R3 root fillets omitted
in STEP [simplified]). It is placed exactly as the FEA/R-120 geometry places it (flange seat Y0 . .. note: the flange ring axis is Y as ID drew it).
housing_7013_r14.step: CRBH 7013 A envelope (r35-50, W13) + seat flange OD108 (r50-54, W15), coaxial with X, centred x=0.
Run: python3 r14_cad.py -> STEPs + interference volume (the R14 geometry blocker)."""
import cadquery as cq, json, os, math
H=os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
fl=(cq.Workplane('XZ').circle(38).circle(18).extrude(5)).translate((0,0,0))   # XZ normal is -Y: occupies Y -5..0
box=cq.Workplane('XY').box(44,23,44).translate((0,11.5,-15)).cut(cq.Workplane('XY').box(39,23,39).translate((0,11.5,-15)))
plate=cq.Workplane('XY').box(62,4,62).translate((0,25,-20))
for a in (-135,-90,-45):
    x,z=31*math.cos(math.radians(a)),31*math.sin(math.radians(a))
    plate=plate.cut(cq.Workplane('XZ').center(x,z).circle(4).extrude(-30))
so=fl.union(box).union(plate)
pad=cq.Workplane('XY').box(54.8,75.8,54.8).translate((0,27+75.8/2,-20))
hous=(cq.Workplane('YZ').circle(50).circle(35).extrude(13).translate((-6.5,0,0))).union(
      cq.Workplane('YZ').circle(54).circle(50).extrude(15).translate((-7.5,0,0)))
cq.exporters.export(so,'standoff_r14.step'); cq.exporters.export(hous,'housing_7013_r14.step'); cq.exporters.export(pad,'pad_envelope_r14.step')
v=lambda w:w.val().Volume()
res=dict(standoff_vol_cm3=round(v(so)/1e3,2),standoff_kg_CALC=round(v(so)*2.81e-6,4),
         interference_standoff_housing_cm3=round(v(so.intersect(hous))/1e3,2),interference_pad_housing_cm3=round(v(pad.intersect(hous))/1e3,2))
json.dump(res,open('r14_cad.json','w'),indent=1); print(res)
# real housing for ID's shoulder_pad CAD placeholder (same frame as ID geometry.json origin; coaxial with X = roll axis)
cq.exporters.export(hous,'housing_7013_real_coaxX.stl'); cq.exporters.export(hous,'housing_7013_real_coaxX.step'); cq.exporters.export(so,'standoff_r14.stl')
