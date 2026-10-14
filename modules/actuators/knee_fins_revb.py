"""D69 rev B fins on the existing D59 knee twin housing (cad/knee_twin_housing.step, 07613D, can r41 z0-44 at local x=+-45).
Legs L48 envelope (legs/results/r031/knee_fin_envelope.json, fin height after 3 mm margin, sectors about the screw axis,
0 deg = world fwd): front +-30 deg 12 mm, 30-60 deg 7.6, sides 60-120 / 240-300 none, rear 120-240 28.3-30.4.
Frame (model_v4 frame(step, origin, uk, bdk)): local x = world y (twin spacing), local z = screw axis uk, local y = uk x y_world
= world rear, so front = local -y. Fins: 6061, t 1.0 mm, axial over z 2-42 (motor can, nearest the heat), 10 deg pitch.
-> cad/knee_twin_housing_finned_revb.step, results/knee_fins_revb.json"""
import cadquery as cq, json, math, os
H = os.path.dirname(os.path.abspath(__file__)); T = 1.0; Z0, Z1 = 2.0, 42.0; RC = 41.0; RHO = 2.70e-6
FRONT_H, REAR_H = 9.0, 25.0   # RL Thermal D69C b785697 layout; Legs envelope 12 / 28.3
Z0, Z1 = 1.0, 43.0   # full can length 42 mm
PITCH = math.degrees(6.6 / RC)   # 6.6 mm root pitch (Thermal ~6.7; keeps rear 14 inside 120-240), gap 5.6 >= 5
hs = cq.importers.importStep(f'{H}/cad/knee_twin_housing.step'); A0 = hs.val().Area(); V0 = hs.val().Volume()
fins = []
def fin(xc, phi, h):   # phi from local -y (front), ccw about +z
    b = cq.Workplane('XY').box(T, h + 0.5, Z1 - Z0).translate((0, -(RC + h / 2 - 0.25), (Z0 + Z1) / 2))
    return b.rotate((0, 0, 0), (0, 0, 1), phi).translate((xc, 0, 0))
for xc in (-45.0, 45.0):
    for i in range(7): fins.append(fin(xc, (i - 3) * PITCH, FRONT_H))
    for i in range(14): fins.append(fin(xc, 180 + (i - 6.5) * PITCH, REAR_H))
F = fins[0]
for f in fins[1:]: F = F.union(f)
Vf = F.val().Volume() - 0  # includes 0.25 mm root overlap
out = hs.union(F); A1 = out.val().Area(); V1 = out.val().Volume()
cq.exporters.export(out, f'{H}/cad/knee_twin_housing_finned_revb.step')
res = dict(pitch_deg=round(PITCH, 2), front_span_deg=round(3 * PITCH, 1), rear_span_deg=round(6.5 * PITCH, 1), n_fins=len(fins), t_mm=T, L_mm=Z1 - Z0, front_h=FRONT_H, rear_h=REAR_H, added_area_m2=round((A1 - A0) * 1e-6, 4),
           fin_mass_kg_per_knee=round((V1 - V0) * RHO, 4), valid=out.val().isValid())
json.dump(res, open(f'{H}/results/knee_fins_revb.json', 'w'), indent=1); print(res)
