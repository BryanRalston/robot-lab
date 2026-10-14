"""R-069 / Legs query: do rev B fins sit on the +-y (world) = +-x (local) trunnion cheek faces of the knee twin housing?
Cheek pads measured from cad/knee_twin_housing.step: planar faces at local x=+-92, y -10..10, z 11.5..31.5 (20x20 mm).
A flush cheek occupies x beyond +-92. Checks: (1) fin material inside the pad footprint prism (|x|>=92, |y|<=10, z 11.5-31.5);
(2) min distance fin->pad prism; (3) fin material outboard of the +-92 planes at all (any y,z), with a +-20 mm cheek-plate
footprint variant [EST cheek size]. Fix option: clip fins at |x|<=92 (flush plane) and measure area/mass change.
-> results/knee_fin_cheek_check.json"""
import cadquery as cq, json, os
H = os.path.dirname(os.path.abspath(__file__)); RHO = 2.70e-6
a = cq.importers.importStep(f'{H}/cad/knee_twin_housing.step').val()
b = cq.importers.importStep(f'{H}/cad/knee_twin_housing_finned_revb.step').val()
F = b.cut(a)
def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))
r = {}
for s, nm in ((1, 'pos'), (-1, 'neg')):
    x0, x1 = (92, 130) if s > 0 else (-130, -92)
    pad = box(x0, x1, -10, 10, 11.5, 31.5); padw = box(x0, x1, -20, 20, 0, 43.5)
    out = box(x0, x1, -80, 80, -1, 50)
    r[nm] = dict(fin_vol_in_pad_prism_mm3=round(F.intersect(pad).Volume(), 1), min_dist_fin_to_pad_prism_mm=round(F.distance(pad), 2),
                 fin_vol_in_40mm_cheek_prism_mm3=round(F.intersect(padw).Volume(), 1), min_dist_fin_to_40mm_cheek_mm=round(F.distance(padw), 2),
                 fin_vol_outboard_plane_mm3=round(F.intersect(out).Volume(), 1))
    ob = F.intersect(out).BoundingBox(); r[nm]['outboard_bb_y_z'] = [round(v, 1) for v in (ob.ymin, ob.ymax, ob.zmin, ob.zmax)]
clip = b.cut(box(92, 130, -80, 80, -1, 50)).cut(box(-130, -92, -80, 80, -1, 50))
r['clip_option'] = dict(d_area_m2=round((clip.Area() - b.Area()) * 1e-6, 4), d_mass_kg_per_knee=round((clip.Volume() - b.Volume()) * RHO, 4),
                        note='area change includes the new cut end faces')
json.dump(r, open(f'{H}/results/knee_fin_cheek_check.json', 'w'), indent=1); print(json.dumps(r, indent=1))
