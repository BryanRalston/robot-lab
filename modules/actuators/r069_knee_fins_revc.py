"""R-069 rev C fin layout candidate (same method as knee_fins_revb.py): drop the edge rear fins (Legs' 120/240 deg boundary flag,
and the fins that overhang the +-92 trunnion-pad planes), shorten rear fins, keep 7 front x 9 mm. Target added area >= 0.045 m2
(r069_knee_fin_trim.py: drives off the housing, every case <= rev B as booked). Args: n_rear rear_h. Writes STEP only for the chosen one."""
import cadquery as cq, json, math, os, sys
H = os.path.dirname(os.path.abspath(__file__)); T = 1.0; RC = 41.0; RHO = 2.70e-6; Z0, Z1 = 1.0, 43.0; FRONT_H = 9.0
PITCH = math.degrees(6.6 / RC)
NR, RH = int(sys.argv[1]), float(sys.argv[2]); WRITE = len(sys.argv) > 3
hs = cq.importers.importStep(f'{H}/cad/knee_twin_housing.step'); A0 = hs.val().Area(); V0 = hs.val().Volume()
def fin(xc, phi, h):
    b = cq.Workplane('XY').box(T, h + 0.5, Z1 - Z0).translate((0, -(RC + h / 2 - 0.25), (Z0 + Z1) / 2))
    return b.rotate((0, 0, 0), (0, 0, 1), phi).translate((xc, 0, 0))
fins = [fin(xc, (i - 3) * PITCH, FRONT_H) for xc in (-45., 45.) for i in range(7)]
fins += [fin(xc, 180 + (i - (NR - 1) / 2) * PITCH, RH) for xc in (-45., 45.) for i in range(NR)]
F = fins[0]
for f in fins[1:]: F = F.union(f)
out = hs.union(F); s = out.val(); bb = s.BoundingBox()
res = dict(n_rear=NR, rear_h=RH, front=7, front_h=FRONT_H, added_area_m2=round((s.Area() - A0) * 1e-6, 4), fin_mass_kg_per_knee=round((s.Volume() - V0) * RHO, 4),
           x_extent_mm=round(bb.xmax, 1), valid=s.isValid())
print(res)
if WRITE:
    cq.exporters.export(out, f'{H}/cad/knee_twin_housing_finned_revc.step'); json.dump(res, open(f'{H}/results/r069_knee_fins_revc.json', 'w'), indent=1)
