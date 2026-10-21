"""Torso-owned cell-holder layout, Option A (Robot Lab ruling; Electronics P-057 6b976bd).
Frame: sim-torso (global z - 1280; x fwd, y left). Molicel P45B 21700, 20S5P, cells vertical, 2 tiers, 22 mm pitch [Electronics EST pitch].
Writes pack_layout_optA.json + .md table + .svg plan; computes pack COM vs the model_v4 envelope centre (sim_torso_body basis)."""
import json, math
P = 22.0; R = 11.0; m_cell = 0.0700   # P45B ~70 g [Molicel spec 70 g]
X_FRONT_CELL = 52.0 - 0.3 - 1.5      # land back face 52 - liner 0.3 - air 1.5 (P-057 item 6)
X_REAR_WALL = -107.0 + 2.0           # box rear web inner (web outer at shell inner -107)
T = {"T1": (131.6, 201.6), "T2": (203.6, 273.6)}   # floor top 129.6 + 2 mm holder; 70 mm cells
# columns from front: c3..c7 = front block (c1/c2 = notch + FET/busbar zone, no cells)
xc = {f"c{i}": round(X_FRONT_CELL - R - P*(i-3), 1) for i in range(3, 8)}
rows = {"y-": [-11 - P*k for k in range(5)], "y+": [11 + P*k for k in range(5)]}
order = [("T1","c3","y-"),("T1","c3","y+"),("T1","c4","y+"),("T1","c4","y-"),("T1","c5","y-"),("T1","c5","y+"),("T1","c6","y+"),("T1","c6","y-"),
         ("T2","c6","y-"),("T2","c6","y+"),("T2","c5","y+"),("T2","c5","y-"),("T2","c4","y-"),("T2","c4","y+"),("T2","c3","y+"),("T2","c3","y-"),
         ("T2","c7","y-"),("T2","c7","y+"),("T1","c7","y+"),("T1","c7","y-")]
BMS = (-95.0, 0.0, 200.0)   # BMS host + 2x BQ79616 board on the rear web (x -105 inner, ~10 mm deep), centre
groups = []
for s, (t, col, h) in enumerate(order, 1):
    zc = sum(T[t])/2; cells = [(xc[col], y, zc) for y in rows[h]]
    ys = rows[h]; yend = ys[-1]   # + bus at the outboard end, - at the inboard end (serpentine alternates)
    groups.append(dict(S=s, tier=t, col=col, half=h, x=xc[col], y_range=[min(ys)-R, max(ys)+R], z=[T[t][0], T[t][1]],
                       bq=("BQ79616 #1" if s <= 10 else "BQ79616 #2"), relocated=(col == "c7"), cells=cells))
# tap points: each group's + bus (top for T2, bottom for T1 is avoided: taps taken at the group's top strip)
taps = []
for gp in groups:
    tz = gp["z"][1]; ty = sum(gp["y_range"])/2
    L = abs(gp["x"]-BMS[0]) + abs(ty-BMS[1]) + abs(tz-BMS[2])   # Manhattan route [EST]
    ic = 1 if gp["S"] <= 10 else 2; vc = gp["S"] if ic == 1 else gp["S"]-10
    taps.append(dict(tap=f"BQ#{ic} VC{vc}", node=f"S{gp['S']}+", at=[gp["x"], round(ty,1), tz], len_mm=round(L)))
taps.insert(0, dict(tap="BQ#1 VC0", node="S1- (pack -)", at=[xc["c3"], -66.0, T["T1"][0]], len_mm=round(abs(xc["c3"]-BMS[0])+66+abs(T["T1"][0]-BMS[2]))))
taps.insert(11, dict(tap="BQ#2 VC0", node="S10+/S11- (split)", at=[xc["c6"], 0.0, T["T2"][0]], len_mm=round(abs(xc["c6"]-BMS[0])+abs(T["T2"][0]-BMS[2]))))
cells = [c for gp in groups for c in gp["cells"]]
com = [sum(c[i] for c in cells)/len(cells) for i in range(3)]
env_c = (12.0, 0.0, 129.6 + 72)   # model_v4 pack box centre (sim_torso_body basis = envelope centre)
m_pack0 = 8.750; m_add = 0.050; m_cells = m_cell*100
m_moving = m_pack0 - 0.35          # cells+holders+strips+NTC follow the cell block; BMS/FET/busbar blocks 0.35 kg [EST] stay at envelope centre basis
link_x = (xc["c3"] + xc["c7"])/2
dx = (m_moving*(com[0]-env_c[0]) + m_add*(link_x-env_c[0]))/(m_pack0+m_add)
dz = (m_moving*(com[2]-env_c[2]))/(m_pack0+m_add)
M_robot = 65.809   # arbiter/mass_rollup_official.json credible_kg
out = dict(frame="sim-torso (global z-1280)", pitch_mm=P, tiers=T, columns_x=xc, cell_block_x=[round(xc["c7"]-R,1), X_FRONT_CELL],
           notch=dict(x=[52.0, 104.5], y=[-54.5, 54.5], z=[167.0, 278.0], note="c1/c2 (x 52-104.5) carry no cells; outboard |y|>58 = FET (left) / busbar blocks (right)"),
           groups=[{k: v for k, v in g.items() if k != "cells"} for g in groups], taps=taps,
           links=[dict(name="link A S16->S17", frm=[xc["c3"], -66, 273.6], to=[xc["c7"], -66, 273.6], section_mm2=12, len_m_est=0.19),
                  dict(name="link B pack- S1 -> SBS75X (rear web)", frm=[xc["c3"], -66, 131.6], to=[-105, -60, 160], section_mm2=12, len_m_est=0.19)],
           sbs75x=dict(at=[-100, -60, 160], facing="+x (inward, into the 35 mm BMS/c7 gap)", note="inward-facing on a G10 bracket off the rear web; robot-side half mates inside the box, main cable exits via a side-wall gland at (-80,-112,150); %.0f mm from the floor vent (-90, 0, 121.6)" % math.dist((-100,-60,160),(-90,0,121.6))),
           vent=dict(at=[-90, 0, 121.6], global_z=1401.6, part="GORE MultiVent", deflector="stainless 0.5 mm chute on the floor underside, plume turned rearward, exit plane x -107 at sim z ~110 (global ~1390)"),
           tap_fuses=dict(part="fusible element at the cell end of each of 22 taps on the tap FPC/collector; candidate Littelfuse 451/453 Nano2 0.5 A (125 V class, verify datasheet); Littelfuse 438 0603 is 63 VDC max so it fails a full-stack 84 V fault [438 datasheet 05/30/24]"),
           bms_board=dict(zone="x -105..-95 board on 3 mm G10 standoffs; back-side parts <=4.4 mm; 22-way tap connector (vertical dual-row, e.g. Molex Micro-Fit 3.0 24-ckt) and isolation transformers face +x into the 35 mm gap to c7 (mated + wire bend <=30 mm [EST])"),
           bms=BMS, cell_com=[round(v,1) for v in com], envelope_centre=env_c,
           pack_com_shift_mm=[round(dx,1), 0.0, round(dz,1)], pack_mass_kg=m_pack0+m_add,
           robot_com_shift_mm=[round((m_pack0+m_add)*dx/M_robot + 0, 2), 0.0, round((m_pack0+m_add)*dz/M_robot, 2)],
           robot_mass_basis_kg=M_robot)
json.dump(out, open("pack_layout_optA.json", "w"), indent=1)
L = ["| S | BQ | tier | col | x mm | y mm | z mm | relocated |", "|---|---|---|---|---|---|---|---|"]
L += [f"| S{g['S']} | {g['bq'][-2:]} | {g['tier']} | {g['col']} | {g['x']} | {g['y_range'][0]:.0f}..{g['y_range'][1]:.0f} | {g['z'][0]}-{g['z'][1]} | {'yes' if g['relocated'] else ''} |" for g in groups]
L += ["", "| tap | node | at (x,y,z) | route mm [EST] |", "|---|---|---|---|"] + [f"| {t['tap']} | {t['node']} | {t['at']} | {t['len_mm']} |" for t in taps]
open("pack_layout_optA_tables.md", "w").write("\n".join(L) + "\n")
# SVG plan views (top view per tier) 
sv = ['<svg xmlns="http://www.w3.org/2000/svg" width="700" height="300" viewBox="-120 -130 520 260" font-size="6">']
for k, (t, ox) in enumerate((("T1", 0), ("T2", 260))):
    sv.append(f'<rect x="{ox-107}" y="-115" width="215.5" height="230" fill="none" stroke="black"/><text x="{ox-100}" y="-118">{t} (top view, x right = fwd)</text>')
    sv.append(f'<rect x="{ox+52}" y="-54.5" width="56.5" height="109" fill="#fcc" stroke="red"/><text x="{ox+56}" y="0">notch</text>')
    for g in groups:
        if g["tier"] != t: continue
        for (x, y, z) in g["cells"]:
            sv.append(f'<circle cx="{ox+x}" cy="{-y}" r="10.8" fill="{"#9cf" if g["relocated"] else "#cfc"}" stroke="#333" stroke-width="0.3"/>')
        sv.append(f'<text x="{ox+g["x"]-6}" y="{-sum(g["y_range"])/2+2}">S{g["S"]}</text>')
    sv.append(f'<rect x="{ox-105}" y="-60" width="10" height="120" fill="#fd8"/><text x="{ox-104}" y="70">BMS</text>')
sv.append('</svg>'); open("pack_layout_optA.svg", "w").write("\n".join(sv))
print(json.dumps({k: out[k] for k in ("columns_x","cell_block_x","cell_com","pack_com_shift_mm","robot_com_shift_mm")}), [t["len_mm"] for t in taps])
