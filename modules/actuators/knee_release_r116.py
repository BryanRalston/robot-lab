"""Job 9 (c) release geometry: rev B finned knee twin housing + R-116 trunnion boss (Ø20 -> Ø23, 7 mm, outward only) + Ø12 blind bore 6 mm (D80).
Input cad/knee_twin_housing_finned_revb.step (Thermal f2da3ab kept rev B; rev C withdrawn, Controls a5e14ff).
Boss location from cad_mass.py linear_body/knee_twin: twin at x +-45, motor OD 76 -> can D 82, outer boss x 85..92, centre z Lm/2 = (23.09+20)/2, y 0.
The Ø23 cylinder starts at x 84 (not 85) so it fuses with the r41 can over its full face (can surface at y +-11.5 is x 84.35).
-> cad/knee_twin_housing_release_r116.step, results/knee_release_r116.json"""
import cadquery as cq, json, os
H=os.path.dirname(os.path.abspath(__file__)); ZC=(23.09+20)/2; R7075=2.81e-6; R6061=2.70e-6
s=cq.importers.importStep(f'{H}/cad/knee_twin_housing_finned_revb.step'); V0=s.val().Volume()
B=[];C=[]
for sg in (1,-1):
    x0,x1=(84,92) if sg>0 else (-92,-84)
    B.append(cq.Solid.makeCylinder(11.5,x1-x0,cq.Vector(x0,0,ZC),cq.Vector(1,0,0)))
    xb=86 if sg>0 else -92
    C.append(cq.Solid.makeCylinder(6,6,cq.Vector(xb,0,ZC),cq.Vector(1,0,0)))
v=s.val().fuse(*B).cut(*C).clean().fix(); V1=v.Volume(); s=cq.Workplane().add(v)
cq.exporters.export(s,f'{H}/cad/knee_twin_housing_release_r116.step')
bb=v.BoundingBox()
r=dict(valid=v.isValid(),solids=len(v.Solids()),vol_mm3=round(V1),d_vol_vs_revb_mm3=round(V1-V0),mass_7075_kg=round(V1*R7075,4),mass_6061_kg=round(V1*R6061,4),
       bbox_x=(round(bb.xmin,2),round(bb.xmax,2)),boss=dict(d=23,depth_x='84..92 (85..92 proud + 1 sink)',bore=12,bore_depth=6,zc=ZC))
json.dump(r,open(f'{H}/results/knee_release_r116.json','w'),indent=1); print(r)
