"""D73 wrist pitch/yaw unit placement (Arms A42 440c7a8): D70 units (TBM2G-05008C + CSG-14-100, Ø56 x 54 [EST envelope]) ride on the
roll output ABOVE the pivot (z >= +27), axes parallel to their joint axes, each driving its joint through one short link (2 pins).
Frame: pivot at origin, z up toward elbow, y = pitch axis. Palm swept zone: r >= 27 from pivot with |y| <= 43 below (z<0) - kept clear.
Outboard (|y| >= 45) rejected: two Ø56 x 54 units outboard give a 2 x (45+54) = 198 mm wrist, ~3x the Ø70 forearm."""
import cadquery as cq, json, math, os
H=os.path.dirname(os.path.abspath(__file__))
D,L=56.0,54.0; zc=27+D/2+1     # unit axis height: bottom of can at z=+28 (>= 27)
pitch=cq.Workplane('XZ').center(0,zc).circle(D/2).extrude(L/2,both=True)                       # axis along y, |y|<=27
yaw=cq.Workplane('XY').workplane(offset=zc+D/2+2).center(0,0).circle(D/2).extrude(L)            # axis along z, stacked above
cheeks=cq.Workplane('XZ').circle(24.5).circle(18).extrude(4).translate((0,24,0)).union(cq.Workplane('XZ').circle(24.5).circle(18).extrude(4).translate((0,-20,0)))
# links: 7075 bar 6 x 3, length = crank geometry from unit output (z=zc) to fork pin at r 20 below axis
Lk=zc-0+0.0; link=cq.Workplane('XY').box(6,3,Lk).translate((30,0,zc/2))
asm=pitch.union(yaw).union(cheeks).union(link).union(link.translate((-60,0,0)))
cq.exporters.export(asm,f'{H}/cad/wrist_place_d73.step')
link_kg=Lk*6*3*2.81e-6; pin_kg=math.pi/4*9*10*7.85e-6
per_side=2*(link_kg+2*pin_kg)
# backlash: ISO 286 H7/g6 at Ø3: hole 0/+10 µm, shaft -2/-8 µm -> clearance 2..18 µm per pin; 2 pins/link, crank r 25 mm
cl=2*18e-3; back_deg=math.degrees(cl/25.0)
out=dict(unit_axis_z_mm=zc,link_len_mm=Lk,link_kg=link_kg,pin_kg=pin_kg,per_side_kg=per_side,both_kg=2*per_side,
 backlash_per_link_max_deg=back_deg,backlash_basis='ISO 286-2 H7/g6 Ø3 (published fit limits), 2 pins in series; gear: CSG-14 lost motion not added',
 rejected_outboard_width_mm=2*(45+L))
json.dump(out,open(f'{H}/results/wrist_place_d73.json','w'),indent=1); print(out)
