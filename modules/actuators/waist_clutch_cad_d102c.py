"""D102c integrated torque limiter: CAD volumes -> mass, STEP. Axis z. Stack (from the CSG-25 output flange outward):
output flange face (existing) | lining A | yoke slip ring (steel) | lining B | pressure plate (7075 + steel wear face) | Belleville DIN 2093 B 80/41/3 [EST] | lock nut ring.
Friction annulus Ro 45 / Ri 33 (inside the ø100 keep-out)."""
import cadquery as cq, math, json, os
H=os.path.dirname(os.path.abspath(__file__))
def ring(ro,ri,t,z): return cq.Workplane('XY').circle(ro).circle(ri).extrude(t).translate((0,0,z))
P={}; z=0
P['lining A sintered bronze 1.5']=(ring(45,33,1.5,z),8.8e-3); z+=1.5
P['yoke slip ring 42CrMo4 4 mm (+ 3 drive lugs to yoke, 3x12x8)']=(ring(46,33,4,z).union(cq.Workplane('XY').polarArray(48,0,360,3).rect(12,8).extrude(4).translate((0,0,z))),7.85e-3); z+=4
P['lining B sintered bronze 1.5']=(ring(45,33,1.5,z),8.8e-3); z+=1.5
P['pressure plate steel wear face 1.5']=(ring(45,30,1.5,z),7.85e-3); z+=1.5
P['pressure plate 7075 body 4']=(ring(45,30,4,z),2.81e-3); z+=4
P['Belleville DIN 2093 B 80/41/3 [EST size check]']=(ring(40,20.5,3,z),7.85e-3); z+=4.6
P['lock nut ring M68x1.5 7075 6 mm (on output hub thread) [EST]']=(ring(36,30,6,z),2.81e-3); z+=6
P['anti-rotation pins/keys + bushing [EST]']=(ring(33,31,6,1.5),7.85e-3)
asm=None; mass={}
for k,(s,rho) in P.items():
    mass[k]=round(s.val().Volume()*rho/1000,3); asm=s if asm is None else asm.union(s)
cq.exporters.export(asm,f'{H}/cad/waist_torque_limiter_d102c.step')
tot=round(sum(mass.values()),3); print(json.dumps(dict(parts_kg=mass,total_kg=tot,stack_mm=round(z,1)),indent=1))
json.dump(dict(parts_kg=mass,total_kg=tot,stack_axial_mm=round(z,1)),open(f'{H}/results/waist_torque_limiter_mass_d102c.json','w'),indent=1)
