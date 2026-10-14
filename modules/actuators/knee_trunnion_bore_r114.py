"""R-114: can the knee twin housing trunnion bore open Ø9 -> Ø12 (Legs L62 Ultem bush, d2f8e8a)?
CAD (cad/knee_twin_housing_finned_revb.step): trunnion boss Ø20 x 7 at local x 85..92 (sunk 1 mm into the r41 can), centre y 0, z 21.5;
can r41 / bore r39 about (+-45, 0); no bore modelled -> blind bore modelled x 86..92 (6 mm engagement outside the can, floor = 2 mm can wall).
Loads per pin (2 trunnion pins share the knee screw pair force; Legs TRUNNION_BREAK.md L61 / legs DECISIONS l.25):
  actuator max 7267 N total (345 N·m / 47.5 mm) -> 3634 N; design 5053 N (240/47.5) -> 2526 N; walk 3364 N -> 1682 N (fatigue, taken R=-1 [conservative EST]).
6061-T6 (ASM): Sy 276, Su 310, Se 96.5 MPa (5e8, R=-1). Margins: static Sy/1.5, fatigue Se/1.5 (repo rule as G3). Lug Kt (pin-loaded, Peterson chart,
d/W 0.45-0.6) 2.2-2.4 [EST]. Lug model ignores the can-wall backing under the boss (conservative). -> results/knee_trunnion_bore_r114.json"""
import cadquery as cq, json, math, os
H = os.path.dirname(os.path.abspath(__file__))
hs = cq.importers.importStep(f'{H}/cad/knee_twin_housing_finned_revb.step').val(); bare = cq.importers.importStep(f'{H}/cad/knee_twin_housing.step').val()
fins = hs.cut(bare)
cav = cq.Solid.makeCylinder(39, 43.1 - 2.5, cq.Vector(45, 0, 2.5))            # can interior (stator space)
stator = cq.Solid.makeCylinder(38, 40, cq.Vector(45, 0, 2.5))                 # TBM2G-07613 OD 76 [cad_mass MOT]
nut = cq.Solid.makeCylinder(20.5, 56, cq.Vector(45, 0, 49.1))                  # nut section incl. 7202 bearing seats z 49..105
Sy, Su, Se = 276., 310., 96.5; L = 6.0; F = dict(max=3634., design=2526., walk=1682.)
def chk(d, D=20.0, Kt=None):
    bore = cq.Solid.makeCylinder(d / 2, L, cq.Vector(86, 0, 21.5), cq.Vector(1, 0, 0))
    g = dict(radial_wall_to_boss_OD=round((D - d) / 2, 2), floor_to_can_cavity=round(bore.distance(cav), 2), to_stator_OD=round(bore.distance(stator), 2),
             to_nut_bearing_section=round(bore.distance(nut), 2), to_fin_roots=round(bore.distance(fins), 2), bolt_holes='none in CAD near the boss')
    Kt = Kt or (2.4 if d / D > 0.55 else 2.2)
    An = (D - d) * L; As = 2 * L * (D / 2 - d / 2 * math.cos(math.radians(40)))
    s = dict(bearing_MPa={k: round(v / (d * L), 1) for k, v in F.items()}, net_MPa={k: round(v / An, 1) for k, v in F.items()}, shearout_MPa={k: round(v / As, 1) for k, v in F.items()})
    s['SF_static_net_max'] = round(Sy / s['net_MPa']['max'], 2); s['SF_shear_max'] = round(0.577 * Sy / s['shearout_MPa']['max'], 2)
    s['SF_bearing_max_vs_Sy'] = round(Sy / s['bearing_MPa']['max'], 2)
    s['fatigue_peak_MPa'] = round(Kt * s['net_MPa']['walk'], 1); s['Kt_EST'] = Kt; s['fatigue_ratio_Se'] = round(Se / s['fatigue_peak_MPa'], 2)
    s['pass_static_1p5'] = min(s['SF_static_net_max'], s['SF_shear_max'], s['SF_bearing_max_vs_Sy']) >= 1.5; s['pass_fatigue_1p5'] = s['fatigue_ratio_Se'] >= 1.5
    return dict(geom_mm=g, stress=s)
out = dict(d9_boss20=chk(9.0), d12_boss20=chk(12.0), d12_boss23=chk(12.0, 23.0, 2.3))
out['boss23_mass_g_per_knee'] = round(2 * math.pi / 4 * (23**2 - 20**2) * 7 * 2.70e-3, 2)
json.dump(out, open(f'{H}/results/knee_trunnion_bore_r114.json', 'w'), indent=1); print(json.dumps(out, indent=1))
