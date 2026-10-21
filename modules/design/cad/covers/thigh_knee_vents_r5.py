"""P-156 rev 5 (Legs L72 e44c588 real geometry + T&R 67e6eed + Thermal rev 4e 218a541 shroud). Thigh frame, L leg.
Real geometry (Legs p156_vent_check_l72.json): knee housing thigh-fixed x -176.1..-79.4, y 38-222, z 684.9-805.5;
L60 trunnion top plate x -175..-40, y 32-228, z 816-824; strut x -45..5, y 110-150, z 816-824; hull rear (y 104-156)
x -94.1@643, -135.3@690, -168.8@740, -180.7@792, -157.2@837, -105.6@860. Plate D94: face x -34.5, window y 107-153, z 690-790, fins to -53.
Finding: the fins face the housing front (-79.4) across 26.4 mm; the rear hull is behind the housing, so a rear grille cannot see the fins
and the rear chimney turn above the housing is only 4.5 mm (808.5-813) -> 52 x 4.5 = 234 mm2 << 1200: FAIL. Rear-grille scheme dropped.
Rev 5 route (no mechanism change): inlet on the lower rear hull under the housing -> fin chimney (baffle x -56) -> top transfer duct
z 793-813 running OUTBOARD in front of the housing (x -8.5..-76.4) -> exit on the outboard side skin z 785-813 under a T&R/Thermal hood."""
import json, os, math
H = os.path.dirname(os.path.abspath(__file__))
HOUS = dict(x=(-176.1, -79.4), y=(38, 222), z=(684.9, 805.5)); PLATE_TOP = dict(x=(-175, -40), y=(32, 228), z=(816, 824)); STRUT = dict(x=(-45, 5), y=(110, 150), z=(816, 824))
inlet = dict(where="lower rear hull slope z 643-675 (x -94.1 -> -122), y 104-156", slots=8, slot_w=4.5, slot_len=40, plenum="z 643-681.9 (3 mm under housing bottom 684.9), x -34.5 -> hull, y 104-156")
inlet["free_mm2"] = inlet["slots"]*inlet["slot_w"]*inlet["slot_len"]; inlet["gross_mm2"] = round(52*math.hypot(32, 28))
baffle = dict(x=(-56, -57), y=(104, 156), z=(688, 792), t=1.0, fin_side="Al tape eps<=0.1", to_fin_tips=3.0, to_housing_front=round(-57-(-79.4), 1)*-1)
transfer = dict(z=(793, 813), x=(-8.5, -76.4), y=(104, 228+20), section_mm2=round((813-793)*(76.4-8.5)), to_plate_top=816-813, to_housing_front=round(79.4-76.4, 1),
                to_housing_top="n/a (in front of the housing, x > -79.4)", to_strut=816-813, route="outboard in y past the housing (y 222) and the plate edge (228) to the side skin")
exit_ = dict(where="outboard side skin, x -10..-84, z 785-813 (below the trunnion top plate, below the rear skirt keep-out line z 793 is NOT required at the side: side skirt hem Legs to confirm)",
             slots=11, slot_w=4.5, slot_len=26, recessed_mm=11, webs="recessed 4.5 mm slots 11 mm inboard of the hood skin (Thermal: thermally equal to plain webs)")
exit_["free_mm2"] = exit_["slots"]*exit_["slot_w"]*exit_["slot_len"]; exit_["gross_mm2"] = 74*28
hood = dict(t=1.5, material="PC, Al foil inner eps<=0.05, cover colour outside, R15 blend", standoff_mm=26, proud_of_skin_mm=15,
            open_up=74*26, open_aft=28*26, dilution="lower edge 10x 4.0x16 + sides 2x 3x 4.0x16 = 1024 mm2 (<=5 mm)", kg_side=0.005)
hood["open_free_mm2"] = hood["open_up"]+hood["open_aft"]
H_m = round(((785+813)/2 - (643+675)/2)/1000, 3)
housing_fairing = dict(foil="0.05 mm Al on fairing inner face only (~0.03 m2), housing bare", gap="10 mm to the housing body (no front fins, Legs L72 b); +2 mm bulge kept",
                       slots="5x 4.0+-0.3 x 20 top + 5x bottom: <=4.3 mm, 370 mm2 min per end", kg_side=0.006)
mass = dict(baffle=0.007, chimney_walls=0.007, transfer_duct=0.015, inlet_plenum=0.0095, skin_slots=-0.002, hood=0.005, housing_fairing=0.006, bulge=0.0005, fasteners=0.0006)
ms = round(sum(mass.values()), 4)
out = dict(part="P-156 rev 5 thigh knee venting (ID)", basis="Legs L72 e44c588; T&R 67e6eed; Thermal 218a541", real_geometry=dict(housing=HOUS, trunnion_top_plate=PLATE_TOP, strut=STRUT),
  finding_rear_route="FAIL: rear turn over housing top only 4.5 mm tall (234 mm2 free) and rear hull is behind the housing; the -82.5 skin plane does not exist (2.6 mm to housing at 145)",
  inlet=inlet, baffle=baffle, chimney_walls="PA12 1.2, y 130+-26.5 (side gap 5.0), x -34.5..-56, z 682-793; L58 tabs notched >=3", transfer_duct=transfer, exit=exit_, hood=hood,
  H_inlet_to_exit_m=H_m, rear_grille="DROPPED (fins not visible from the rear hull; pocket sealed by baffle + duct)", housing_fairing=housing_fairing,
  clearances_mm=dict(baffle_to_fins=3.0, baffle_to_housing=22.4, transfer_to_plate_top=3, transfer_to_strut=3, transfer_to_housing_front=3.0, plenum_to_housing_bottom=3.0,
                     rods_to_duct_Legs=13.8, tibia_to_skin_Legs=4.7, housing_to_skin="hull unchanged (no -82.5 plane); housing rear exposed through the existing rear opening",
                     bosses_Legs="13.7/16.9 at 145/60 deg (boss positions move with the inlet/transfer frame: Legs recheck)"),
  sweep="all new parts thigh-fixed; static gaps >=3.0 to housing/plate/strut; moving: rods 13.8, tibia 4.7 (Legs CAD) -> min 3.0 mm static PASS (at gate), Legs CAD recheck required",
  mass_kg=mass, kg_side=ms, kg_pair=round(2*ms, 3),
  smallest_mechanism_options=["L60 top-plate cut-out ~52 x 40 over the chimney (y 104-156, x -40..-79) -> rear/up outlet with full height; Legs structural check", "lower the housing top 5-10 mm (Actuators) -> rear turn >=10 mm tall still < 1200 mm2 unless 25 mm"],
  confirm=dict(Legs=["clearance of the transfer duct (x -8.5..-76.4, z 793-813, y 104-248) to femur/clamps/drives outside the plate box", "outboard side skin at x -10..-84 z 785-813 exists; L61 cheek windows not overlapped; P-053 rear window/pins elsewhere", "side skirt hem above z 813 at the outboard side through hip ROM", "inlet plenum vs rods/tibia (13.8 / 4.7) and the new boss frame", "full CAD ROM with rev 5"],
               Thermal=["re-run with H 0.14 m (was 0.18), 90-deg turns, transfer section 1358 mm2, exit 1287 mm2 free", "hood 26 mm standoff, 2652 mm2 open + 1024 dilution"],
               TR=["hood/exit on the outboard thigh is near the hanging-hand zone: touch + probe B on the hood and recessed webs", "housing-fairing slots 4.0+-0.3"]))
json.dump(out, open(os.path.join(H, "thigh_knee_vents.json"), "w"), indent=1)
def box(x0, x1, y0, y1, z0, z1):
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]; q = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    return [(v[a], v[b], v[c]) for a, b, c, d in q] + [(v[a], v[c], v[d]) for a, b, c, d in q]
B = [box(-57, -56, 104, 156, 688, 792), box(-56, -34.5, 102.9, 104.1, 682, 793), box(-56, -34.5, 155.9, 157.1, 682, 793),
     box(-122, -34.5, 104, 156, 642.4, 643.6), box(-122, -34.5, 104, 156, 680.7, 681.9),            # inlet plenum floor/roof
     box(-76.4, -8.5, 104, 248, 792.4, 793.6), box(-76.4, -8.5, 104, 248, 811.8, 813.0),              # transfer duct floor/roof
     box(-84, -10, 246.5, 248, 785, 813), box(-84, -10, 259.5, 261, 780, 815)]                       # exit face (recessed) + hood skin
with open(os.path.join(H, "thigh_knee_vents.stl"), "w") as f:
    f.write("solid v\n")
    for tris in B:
        for t in tris: f.write(" facet normal 0 0 0\n  outer loop\n" + "".join("   vertex %.2f %.2f %.2f\n" % p for p in t) + "  endloop\n endfacet\n")
    f.write("endsolid v\n")
print(json.dumps(dict(inlet=inlet["free_mm2"], transfer=transfer["section_mm2"], exit=exit_["free_mm2"], hood=hood["open_free_mm2"], H=H_m, kg_pair=out["kg_pair"])))
