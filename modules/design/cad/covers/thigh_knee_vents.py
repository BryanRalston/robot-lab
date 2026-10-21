"""P-156 thigh-fairing knee venting (ID), replaces withdrawn P-154 guard. Governing spec: Thermal 389f91b (R131 rev 4b) via Legs:
(1) grille over the full fin field >=104x52, >=60 % open, slots <=5 mm, inner face eps<=0.1; (2) low inlet below z 690 and high
outlet above z 792 on the rear skin, each >=1200 mm2 free, aligned with the fin channels; pocket walls duct to the fin ends,
side gaps <=5 mm; >=3 mm to L58 tabs; knee ROM (Legs min 18.1 mm housing case). Thigh frame, L leg (R mirrored).
Plate (Actuators D91 rev 4 / 5008683): face x -34.5, y 130+-24, z 690-790, 8 fins 18.5 (tips x -53.0, outer fin faces y 130+-21.5).
v5 fairing rear skin over the pocket: x -82.5 (fins 48 mm inside the hull from the plate face; 30 mm tip->skin, Thermal).
Knee twin housing front face in the pocket at x -66..-71 (13-18 mm aft of the tips, Thermal) [Legs to confirm y extent]."""
import json, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__))
X_SKIN, T, PC, PA12 = -82.5, 1.5, 1.20, 1.01
grille = dict(z=(688, 792), y=(104, 156), slots=8, slot_w=4.5, rib=2.0, slot_len=98, dir="along z (fin channels)")
g_open = grille["slots"]*grille["slot_w"]*grille["slot_len"]; g_gross = 104*52
inlet = dict(z=(643, 681), y=(104, 156), slots=8, slot_w=4.5, slot_len=36); outlet = dict(z=(799, 837), y=(104, 156), slots=8, slot_w=4.5, slot_len=36)
free = lambda v: v["slots"]*v["slot_w"]*v["slot_len"]
bars = "6 mm solid bars at z 681-687 and 793-799 carry the 4 ribbed PA12 bosses dia 6 x >=5 at y 112/148, z 684/796 (reused P-154 positions)"
duct = dict(walls_y=(130-26.5, 130+26.5), side_gap_mm=26.5-21.5-0.0, x=(-34.5, -63.0), z=(643, 837), t=1.2, material="PA12, inner faces bare",
            tab_notches="10 (z) x 7 (x) at L58 tabs y 100/160 z 700/780: >=3 mm", note="walls stop at x -63 (>=3 mm to the housing front at -66); beyond, the fairing pocket ducts")
# clearances
side_gap = duct["side_gap_mm"]                                   # <=5 required
rod_wall = round((130-45) and (duct["walls_y"][0]-T) - (85+6), 1)  # rod y 85 r6 vs outer face of the y 103.5 wall
house_gap = round(-63.0 - (-66.0), 1) * -1
tab_gap = 3.0
l61 = "L61 40x30 cheek windows / 14 mm boss window sit on the outboard cheek (y >= ~225); grille edge y 156 -> >= 69 mm apart, separate faces: no interaction"
# mass per side
g_rm = (g_open + free(inlet) + free(outlet))/1000*T*PC                     # g of PC removed from the skin
liner = (g_gross - g_open)/100*2.7e-4*2.5e-3*1000*0 + 0.2                  # Al liner on grille inner bars ~0.2 g
duct_g = (2*(duct["z"][1]-duct["z"][0])*abs(duct["x"][1]-duct["x"][0]) - 4*70)/1000*duct["t"]*PA12
fast = 0.6
m_side = round((duct_g + liner + fast - g_rm)/1000, 4)
out = dict(part="P-156 thigh-fairing knee venting (ID)", spec="Thermal 389f91b R131 rev 4b; Legs steer", skin_x=X_SKIN,
 grille=dict(**grille, open_mm2=g_open, gross_mm2=g_gross, open_frac=round(g_open/g_gross, 2), IP2X="4.5 mm slots: 12 mm finger cannot enter; 80 mm reach from the skin reaches x -162 > tips x -53 behind 30 mm air -> finger stopped by slots; T&R touch check now on the grille (TP-G5-15, <=48 C; Thermal est 39 C)",
             inner_face="vapour-deposited Al / 25 um Al foil PSA eps<=0.1", outer_face="cover colour, matte 2K 20 um; slots flush, R0.5 edges, integrated in the fairing skin (slim Optimus line)"),
 inlet=dict(**inlet, free_mm2=free(inlet), gross_mm2=38*52), outlet=dict(**outlet, free_mm2=free(outlet), gross_mm2=38*52), bars_bosses=bars, duct=duct,
 knee_housing_face="low-eps (<=0.1) face toward the grille/plate (Legs/Actuators part; note only)",
 clearances_mm=dict(side_gap=side_gap, rods_to_duct_wall=rod_wall, housing_to_duct_wall_end=3.0, L58_tabs=tab_gap, knee_ROM_housing_Legs=18.1), L61=l61,
 mass_kg_side=m_side, mass_kg_pair=round(2*m_side, 3),
 confirm=dict(Legs=["skin x -82.5 over the pocket and housing front x -66..-71 / y extent (duct walls stop at x -63)", "bosses y 112/148 z 684/796 on the fairing bars", "full-ROM recheck in Legs CAD with the duct insert"],
              Thermal=["grille 65 % / inlet-outlet 1296 mm2 free each meet rev 4b (duct ends at x -63, pocket beyond)"],
              TR=["touch check moves to the grille (TP-G5-15)", "IP2X 12 mm/80 mm on the grille and inlet/outlet"]))
json.dump(out, open(os.path.join(H, "thigh_knee_vents.json"), "w"), indent=1)
# STL: grille/inlet/outlet panels as thin plates at the skin + two duct walls
def box(x0, x1, y0, y1, z0, z1):
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]; q = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    return [(v[a], v[b], v[c]) for a, b, c, d in q] + [(v[a], v[c], v[d]) for a, b, c, d in q]
B = [box(X_SKIN-T, X_SKIN, 104, 156, 643, 837)] + [box(-63.0, -34.5, y-0.6, y+0.6, 643, 837) for y in duct["walls_y"]]
with open(os.path.join(H, "thigh_knee_vents.stl"), "w") as f:
    f.write("solid v\n")
    for tris in B:
        for t in tris: f.write(" facet normal 0 0 0\n  outer loop\n" + "".join("   vertex %.2f %.2f %.2f\n" % p for p in t) + "  endloop\n endfacet\n")
    f.write("endsolid v\n")
print(json.dumps({k: out[k] for k in ("clearances_mm", "mass_kg_side", "mass_kg_pair")}), out["grille"]["open_frac"], free(inlet))
