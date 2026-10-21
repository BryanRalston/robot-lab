"""P-154 knee fin guard (ID part): perforated thermoformed 1.5 mm PC cap over the Actuators D91 knee plate rev 3 fins
(100x48 window, 8 fins 13 x 1.0 @ 6.0, fins out), per T&R 447aa8e (ISO 13732-1 contact-burn guard). Thigh frame (L leg; R mirrored),
window centred y 130 / z 740, plate outer face x -34.5 (fins point -x). Writes knee_fin_guard.stl + .json. Plain python, no CAD kernel."""
import json, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__))
G = dict(t=1.5, win=(100, 48), wall_out=(104, 52), flange_w=4, proud_outer=24.5, fin_h=13, inner_face=23.0,
         slot_w=3.5, slot_pitch=6.0, face_slot_len=90, side_slot=(3.5, 12, 14), x_plate=-34.5, yc=130, zc=740,
         fasteners="4x M2.5 x6 A2-70 pan head, captive, into M2.5 heat-set inserts in the thigh-fairing window frame (non-structural)")
fin_gap = G["inner_face"] - G["fin_h"]                                     # >= 8 (A35)
n_face = int((G["wall_out"][1] - 2*G["t"] - 4) // G["slot_pitch"])         # slots across the 48-ish face, along z (fin stream)
face_open = n_face * G["slot_w"] * G["face_slot_len"] / 100                # cm2
side_open = 2 * G["side_slot"][2] * G["side_slot"][0] * G["side_slot"][1] / 100   # 14 slots 3.5x12 per long side wall
L, W, Hh = G["wall_out"][0], G["wall_out"][1], G["proud_outer"]
area = L*W + 2*(L+W)*(Hh-G["t"]) + ((L+2*G["flange_w"])*(W+2*G["flange_w"]) - L*W)   # mm2
vol = (area - (face_open+side_open)*100) * G["t"] / 1000                  # cm3
m_side = round(vol*1.20/1000 + 0.0006, 4)                                  # PC 1.20 g/cm3 + 4x M2.5 + inserts [EST]
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
           fin_tip_to_guard_inner_mm=fin_gap, A35_fin_rule_ge8=fin_gap >= 8,
           open_area_cm2=dict(face=round(face_open, 1), sides=round(side_open, 1), total=round(face_open+side_open, 1), A35_min_per_bay=25),
           IP2X="3.5 mm slots: 12 mm test finger cannot enter; fin tips 10 mm behind the inner face (burn: T&R to re-run ISO 13732-1 on the PC outer face)",
           kg_side_EST=m_side, kg_pair_EST=round(2*m_side, 3),
           confirm=dict(Actuators=["fins unchanged 13 mm and plate face at x -34.5 (L51 26 mm boundary)", "UA re-check with guard (R-143 2b, Thermal)", "plate edge seal vs guard flange stack"],
                        Legs=["window frame inserts (4x M2.5) in the thigh fairing / drive-bay panel", "L51 plate placement y 130 +-24, z 690-790 (no assembly CAD)", "knee lever eye r 47.5 and RV12 rod path; rod clearance 6.6 mm at 141 deg [EST]", "fall/side impact: guard sacrificial, drive bay stays closed (R-143 2c)"]))
json.dump(out, open(os.path.join(H, "knee_fin_guard.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("fin_tip_to_guard_inner_mm", "open_area_cm2", "kg_side_EST", "kg_pair_EST")}))
