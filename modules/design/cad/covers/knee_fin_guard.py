"""P-154 knee fin guard (ID part): perforated thermoformed 1.5 mm PC cap over the Actuators D91 knee plate rev 3 fins
(100x48 window, 8 fins 18.5 x 1.0 (Actuators 5008683, tips x -53.0) @ 6.0 per Thermal rev 4 44b7c36), per T&R 447aa8e + Thermal rev 4 (low-eps inner face, 10 mm standoff, >=60 % open, ends open) (ISO 13732-1 contact-burn guard). Thigh frame (L leg; R mirrored),
window centred y 130 / z 740, plate outer face x -34.5 (fins point -x). Writes knee_fin_guard.stl + .json. Plain python, no CAD kernel."""
import json, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__))
G = dict(t=1.5, win=(100, 48), wall_out=(104, 66), inner_wall=(101, 63), plate_side_clear=7.5, fit_note="walls now outboard of the 48 plate (7.5 mm/side >= 0.5); guard flange seats on the drive-bay panel window frame (66 x 104 + 4 flange)", tab_notches="4 base notches 10 (z) x 7 (x) in the side walls at L58 tabs (y 100/160, z 700/780): >=3 mm to tab ends", bosses="4x ribbed PA12 bosses dia 6 x >=5 mm in the window frame at y 112/148, z 684/796 (window ends, off the L58 screw line), M2.5 heat-set", edge_seal="1 mm silicone bead inboard of x -34.5 (Actuators 5008683)", flange_w=4, proud_outer=30.0, fin_h=18.5, inner_face=28.5,
         slot_w=4.0, slot_pitch=5.5, face_slot_len=96, side_slot=(4.0, 14, 14), ends_open=True,
         liner="vapour-deposited Al (or 25 um Al foil PSA) on inner face, eps<=0.1 (Thermal 44b7c36)", outer_finish="cover colour (V5 gold/graphite per panel), matte 2K paint 20 um", x_plate=-34.5, yc=130, zc=740,
         fasteners="4x M2.5 x6 A2-70 pan head, captive, into M2.5 heat-set inserts in the thigh-fairing window frame (non-structural)")
fin_gap = G["inner_face"] - G["fin_h"]                                     # >= 10 (Thermal)
side_gap = G["inner_wall"][1]/2 - 21.5                                       # outer fin face y +-21.5 (8 fins @6, t1)
n_face = 11         # slots across the 48-ish face, along z (fin stream)
face_open = n_face * G["slot_w"] * G["face_slot_len"] / 100                # cm2
side_open = 2 * G["side_slot"][2] * G["side_slot"][0] * G["side_slot"][1] / 100   # 14 slots 3.5x12 per long side wall
L, W, Hh = G["wall_out"][0], G["wall_out"][1], G["proud_outer"]
area = L*W + 2*L*(Hh-G["t"]) - 4*10*7 + ((L+2*G["flange_w"])*(W+2*G["flange_w"]) - L*W)   # z ends open (Thermal)   # mm2
vol = (area - (face_open+side_open)*100) * G["t"] / 1000                  # cm3
solid_cm2 = (area/100 - face_open - side_open)
m_side = round(vol*1.20/1000 + 0.0006 + solid_cm2*2.7e-4*0.0025 + solid_cm2*20e-4*1.4/1000, 4)  # PC + fasteners + Al foil 25um (inner) + paint 20um (outer) [EST]
# simple STL: closed outer box of the guard envelope (perforations not modelled) for the clash sweep
x0, x1 = G["x_plate"] - Hh, G["x_plate"]; y0, y1 = G["yc"]-W/2, G["yc"]+W/2; z0, z1 = G["zc"]-L/2, G["zc"]+L/2
v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]; q = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
with open(os.path.join(H, "knee_fin_guard.stl"), "w") as f:
    f.write("solid guard\n")
    for a, b, c, d in q:
        for t in ((a, b, c), (a, c, d)):
            f.write(" facet normal 0 0 0\n  outer loop\n" + "".join("   vertex %.2f %.2f %.2f\n" % v[i] for i in t) + "  endloop\n endfacet\n")
    f.write("endsolid guard\n")
out = dict(part="P-154 knee fin guard (ID)", params=G, envelope_thigh_frame=dict(x=[x0, x1], y=[y0, y1], z=[z0, z1]),
           fin_tip_to_guard_inner_mm=fin_gap, outer_fin_to_side_wall_mm=side_gap, Thermal_ge10=fin_gap >= 10, A35_fin_rule_ge8=fin_gap >= 8,
           open_area_cm2=dict(face=round(face_open, 1), sides=round(side_open, 1), total=round(face_open+side_open, 1), A35_min_per_bay=25, face_open_frac=round(face_open/(L*W/100), 2), Thermal_min_frac=0.60, ends="open both z ends"),
           IP2X="3.5 mm slots: 12 mm test finger cannot enter; fin tips 10 mm behind the inner face (burn: T&R to re-run ISO 13732-1 on the PC outer face)",
           kg_side_EST=m_side, kg_pair_EST=round(2*m_side, 3),
           confirm=dict(Actuators=["fins 18 mm (rev 4) and plate face at x -34.5 (L51 26 mm boundary)", "UA re-check with guard (R-143 2b, Thermal)", "plate edge seal vs guard flange stack"],
                        Legs=["window frame inserts (4x M2.5) in the thigh fairing / drive-bay panel", "L51 plate placement y 130 +-24, z 690-790 (no assembly CAD)", "knee lever eye r 47.5 and RV12 rod path; rod clearance at 29.5 mm envelope (see r143_knee_sweep.json) [EST]", "fall/side impact: guard sacrificial, drive bay stays closed (R-143 2c)"]))
json.dump(out, open(os.path.join(H, "knee_fin_guard.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("fin_tip_to_guard_inner_mm", "open_area_cm2", "kg_side_EST", "kg_pair_EST")}))
