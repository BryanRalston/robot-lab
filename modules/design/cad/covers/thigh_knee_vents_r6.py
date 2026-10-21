"""P-156 rev 6 (Option B, Robot Lab ruling after T&R 7f12ce9; Thermal B2 a32d341; Legs L74 af1b331 notch). Thigh frame, L leg.
Route: lower-rear-hull inlet (unchanged) -> fin chimney (baffle x -56/-57) -> rises STRAIGHT through the Legs L60 top-plate notch
x -34.5..-61 x y 104-156 R8 (z 816-824; Legs twin straps replace the central strut) -> stack to z 860 -> rev 4e-type shroud
(PC 1.5, Al foil inner, 20 mm standoff, slotted walls, dilution ring). No bare louvres at the outlet. P-023 skirt inner face over
the outlet: Al foil + >=15 mm gap. Rev 5 transfer duct and outboard side exit/hood REMOVED.
NOTCH IS PENDING the Legs FEA/fall/thermal-break check (L74) and Thermal's area recheck (1320 vs B2 basis)."""
import json, os, math
H = os.path.dirname(os.path.abspath(__file__))
NOTCH = dict(x=(-61, -34.5), y=(104, 156), z=(816, 824), r=8)
notch_free = round((61-34.5)*52 - 4*(8*8 - math.pi*64/4), 0)
inlet = dict(where="lower rear hull slope z 643-675, y 104-156 (rev 5, unchanged)", slots=8, slot_w=4.5, slot_len=40, free_mm2=1440.0)
chimney = dict(x=(-56, -34.5), y=(104, 156), z=(682, 813), section_mm2=round(21.5*52), baffle="1.0 PC Al-taped x -56..-57, 3.0 to fin tips, 4.0 to release-housing front fins (x -61)")
stack = dict(lower_top_z=817, gap_to_plate_underside=3.0, plate_z="820-828 (Legs L75 +4 mm)", pass_through="notch edges = duct, foam seals",
             upper=dict(z=(831, 840), transition="26.5x52 notch -> mouth x -76.4..-33.3 x y 100-148 (2069 mm2), shifted inboard so shroud outboard edge <=150",
                        walls="PA12 1.2", gap_to_plate_top=3.0, status="stack top z 840: PENDING Thermal area OK (was 860, B2 basis)"), free_through_notch_mm2=notch_free)
shroud = dict(rev="6b (T&R 925d72e hand-swing hit; Robot Lab ruling)", material="PC 1.5 (2.0 at bosses), Al foil inner eps<=0.05, cover colour outside",
              bounds=dict(x=(-100, -20), y=(86, 150), z=(840, 904)), standoff_mm=20, top="slopes from z 861.5 (front) to 904 (aft)",
              openings="AFT WALL ONLY: inclined 45 deg louvre panel 64 wide x 62 slant (z 860-904), 11 horizontal slots 4.5+-0.3 x 58; side/top/front walls closed",
              free_nom_mm2=11*4.5*58, free_min_mm2=round(11*4.2*58), dilution="aft lower band z 842-860: 12 vertical slots 4.0+-0.3 x 16", dil_nom_mm2=12*4*16, dil_min_mm2=round(12*3.7*16),
              outboard_top_edge="chamfer 40 deg, R10 blends, TPU 90A wear strip 2.0 x 15 x 80 bonded + 2 M3 ends",
              IP2X="all openings <=4.8 incl tol; mouth >=20 mm behind them", kg_side=0.0327,
              strike_100N=dict(load="100 N hand strike on the chamfered outboard-top edge, TPU spreads it over ~15x20 -> 0.33 MPa (TPU OK)",
                  edge="folded 40-deg corner as an angle beam, legs 20/20 x 1.5 PC: I~1000 mm4, c~14 -> Z~71 mm3; span 80 between mounts simply supported: M=PL/4=2000 N.mm -> 28 MPa vs PC yield 62 -> SF 2.2",
                  mounts="4x M3 (2 front into stack bosses, 2 aft into thigh-cover inserts): 50 N shear each (M3 A2 capacity >2 kN); PC bearing 50/(3x2.0)=8.3 MPa vs ~60 -> SF 7",
                  status="[EST hand calc], TP-G5-15 add 100 N strike"))
skirt = dict(part="P-023 hip skirt rev 6 (hip_skirt_r6.stl/.json)", relief="faces of the v5 skirt within 5.5 mm of the swept outlet+shroud (255 poses) removed; outlet air path open through the relief",
             gate="min 3 mm (Robot Lab alternative to 15 mm) with air path unobstructed", foil="0.05 Al on the remaining inner face around the relief edge (40 mm band)", kg_side=None)
mass = dict(baffle=0.007, chimney_walls=0.007, inlet_plenum=0.0095, skin_slots=-0.002, housing_fairing=0.006, bulge=0.0005, fasteners=0.0006,
            notch_seal=0.001, upper_stack=0.0025, shroud=0.0327, skirt_foil_band=0.002)
ks = round(sum(mass.values()), 4)
out = dict(part="P-156 rev 6 thigh knee venting (ID), Option B", basis="T&R 7f12ce9; Thermal a32d341 B2; Legs L74 af1b331", notch=NOTCH,
  notch_status="PENDING Legs FEA + fall case + thermal-break (L74); Thermal area recheck (notch 1320 / chimney 1118 mm2)",
  inlet=inlet, chimney=chimney, stack=stack, shroud=shroud, skirt=skirt, removed=["rev 5 transfer duct (-0.015/side)", "rev 5a side exit + hood (-0.0125/side)"],
  H_m_Thermal=0.217,
  clearances_mm=dict(baffle_to_fins=3.0, baffle_to_housing_front_fins=4.0, lower_stack_to_plate=3.0, upper_stack_to_plate_top=3.0, plenum_to_housing_bottom=3.0,
     fin_tips_to_inlet_grille=41, fin_tips_to_shroud_slots=">=70", shroud_to_skirt_inner=">=15 (gate) through hip ROM [Legs CAD]",
     housing_top_to_plate="2.0 FLAG (Legs L74, Actuators/Legs, not ID)", ROM="all P-156 parts thigh-fixed: knee ROM unaffected; hip ROM only vs skirt (15 mm gate)"),
  areas_mm2=dict(inlet=1440, chimney=1118, notch=notch_free, shroud_free_nom=shroud["free_nom_mm2"], shroud_free_min=shroud["free_min_mm2"], dilution_min=shroud["dil_min_mm2"], stack_mouth=2069),
  mass_kg=mass, kg_side=ks, kg_pair=round(2*ks, 3), knee_venting_total_pair=round(2*ks-0.050, 3), legs_plate_delta_pair=-0.029)
json.dump(out, open(os.path.join(H, "thigh_knee_vents.json"), "w"), indent=1)
def box(x0, x1, y0, y1, z0, z1):
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]; q = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    return [(v[a], v[b], v[c]) for a, b, c, d in q] + [(v[a], v[c], v[d]) for a, b, c, d in q]
B = [box(-57, -56, 104, 156, 688, 792), box(-56, -34.5, 102.9, 104.1, 682, 817), box(-56, -34.5, 155.9, 157.1, 682, 817),
     box(-122, -34.5, 104, 156, 642.4, 643.6), box(-122, -34.5, 104, 156, 680.7, 681.9),
     box(-76.4, -33.3, 100, 148, 831, 840), box(-100, -20, 86, 150, 902.5, 904), box(-100, -98.5, 86, 150, 842, 904)]
with open(os.path.join(H, "thigh_knee_vents.stl"), "w") as f:
    f.write("solid v\n")
    for tris in B:
        for t in tris: f.write(" facet normal 0 0 0\n  outer loop\n" + "".join("   vertex %.2f %.2f %.2f\n" % p for p in t) + "  endloop\n endfacet\n")
    f.write("endsolid v\n")
print(json.dumps(dict(areas=out["areas_mm2"], kg_pair=out["kg_pair"], total=out["knee_venting_total_pair"])))
