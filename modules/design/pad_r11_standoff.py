"""Stand-off R11 LAYOUT PROPOSAL (Arms-owned part; ID proposes, Arms finalizes). Fixes R10/R13 FEA fail
(bc6ad91, e02c34b): two 30x5 ribs in weak-axis bending + 2 mm floor. R11 = closed box section + solid plate.
Hand calc calibrated to the R10 FEA (same loads)."""
import json, math
E, SY, RHO = 71700, 503, 2.81e-3
Fn, Fs, Yc, Zp = 6761, 1812, 102.3, 20.0
Mx = Fn*Zp/1e3 + Fs*Yc/1e3          # 321 N.m down case (gear/roll axis moment at root)
Mz = Fs*(Yc)/1e3 + Fn*0.005         # axial case e5: 185+34 N.m about the other root axis
H = 23.0                            # box height Y 0..23 (mount face Y 27 with 4 mm plate)
# --- calibration on R10 geometry (2 ribs 30x5 at Z -2.5/-17.5, rigid-plate couple) ---
I_old = 2*(30*5**3/12 + 30*5*7.5**2); s_old = 321e3*10/I_old       # 183 MPa hand
K_s = 524/s_old                                                    # FEA down e0 rib / hand
th_old = 321e3*H/(E*I_old); d_old = th_old*Zp                      # 0.12 mm hand rotation term
K_d = 4.4/d_old                                                    # FEA down e0 defl / hand (floor-dominated)
# --- R11 box: 44 (X) x 44 (Z) outer, wall 2.5, centred X 0, Z -15 (spans Z +7..-37, inside OD70 ring footprint & plate)
B, t = 44.0, 2.5; Bi = B-2*t
I = (B**4-Bi**4)/12; Zs = I/(B/2); A = B**2-Bi**2
s_bend = max(Mx, math.hypot(Mz, Fn*0.0/1e3))*1e3/Zs
s_ax = Fn/A
J = 2*t*(B-t)**2*(B-t)**2/(2*(B-t)); tau = (Fs*0.005*1e3)/(2*t*(B-t)**2)  # small torsion (Fs x e)
s_box_hand = s_bend + s_ax
s_box_cal = s_box_hand*K_s          # conservative: apply full rib calibration (open-frame Kt) to the box
# --- plate: solid 4 mm 7075, 62x62, clamped on box walls (span 41.5), 9 mm overhang
tp, a, pmax = 4.0, B-t, 2*Fn/54.8**2   # linear field peak ~2x mean
s_plate = 0.308*pmax*a**2/tp**2
s_ovh = 6*(pmax*(27.4-22)**2/2)/tp**2
D = E*tp**3/(12*(1-0.33**2)); w_plate = 0.00126*pmax*a**4/D
th = Mx*1e3*H/(E*I); d_box = th*Zp; d_comp = Fn*H/(E*A)
d_cal = d_box*K_d + d_comp + w_plate   # floor term gone; keep full calibration on rotation term (conservative)
# --- flange shear: FEA 12.96 kN total (6.48/dowel). R11: 2x dia 6 m6 fitted dowels (or 8x M4 shoulder bolts)
Vtot = 2*6480; tau_d = Vtot/2/(math.pi*6**2/4); brg = Vtot/2/(6*5)
vol = {"roll_flange_R13_OD70_ID44x5_less_8xM4_2xD6": math.pi/4*(70**2-44**2)*5 - 8*math.pi/4*4.5**2*5 - 2*math.pi/4*6**2*5,
       "box_44x44x2.5_H23": A*H, "plate_62x62x4_solid_less_4xM4": 62*62*4 - 4*math.pi/4*3.3**2*4,
       "M4_bosses_4x_D8x4": 4*math.pi/4*(8**2-3.3**2)*4}
m = {k: round(v*RHO/1e3, 4) for k, v in vol.items()}; ms = round(sum(m.values()), 3)
out = {"part": "Pad stand-off R11 (ARMS-OWNED; ID layout proposal; Arms finalizes roll-output interface/drawing)",
 "basis": "R-120; R10 FEA bc6ad91; Arms job8 e02c34b; Arms R13 1ee8d73",
 "geometry": {"roll_flange": "R13 kept: ring OD70/ID44 x5, 8x M4 12.9 PCD62, + 2x dia 6 m6 fitted dowels (was dia 4) or fitted shoulder bolts",
   "box": "closed square tube 44x44 outer, 2.5 wall, Y 0..23, centred X 0 / Z -15 (Z +7..-37); welded-free: machined from solid with the flange and plate as one part",
   "plate": "62x62x4 SOLID (no pocket), Y 23..27, centred X 0 / Z -20; 4x M4 tapped on +-24 square through 8 mm bosses; 9 mm overhang beyond box",
   "pad_centre_Z": -20, "mount_face_Y": 27, "contact_face_Y": 102.3},
 "loads": {"Fn": Fn, "Fs": Fs, "Mx_down_Nm": round(Mx), "M_axial_e5_Nm": round(Mz)},
 "calibration": {"R10_rib_hand_MPa": round(s_old), "FEA_MPa": 524, "K_stress": round(K_s, 2), "K_defl": round(K_d, 1)},
 "stress_MPa": {"box_hand": round(s_box_hand), "box_calibrated": round(s_box_cal), "plate_span": round(s_plate), "plate_overhang": round(s_ovh),
   "limit_0p67Sy": round(0.67*SY), "dowel_tau": round(tau_d), "dowel_SF_vs600": round(600/tau_d, 2), "flange_bearing": round(brg), "bearing_SF_vs480": round(480/brg, 2)},
 "deflection_mm": {"box_rot_hand": round(d_box, 3), "box_rot_cal": round(d_box*K_d, 2), "axial": round(d_comp, 3), "plate": round(w_plate, 3), "total_cal": round(d_cal, 2), "limit": 1.0},
 "kg_side_CALC": m, "kg_side": ms, "kg_pair": round(2*ms, 3),
 "vs_R13": {"R13_kg_side": 0.072, "R13_pair_booking_delta": 0.096, "R11_pair_delta_vs_boss": round(2*(ms-0.024), 3), "extra_vs_booking_pair": round(2*(ms-0.024)-0.096, 3)},
 "Arms_to_confirm": ["one-piece machined box/flange/plate vs bolted; corner radii R3 at box roots (stress raiser)",
   "dowels dia 6 m6 (or shoulder bolts) and ring ligament with 8x M4 + 2x dia 6 on PCD62",
   "box footprint Z +7..-37 vs OD70 ring and CRBH 7013 inner ring; hollow box keeps access to the 8x M4 heads? (box ID 39 inside ring ID 44: M4 heads on PCD62 sit outside box, OK)",
   "e<=5 stack with 0.6 mm defl; clash vs OD108 housing flange (>=3 mm fore-aft)"]}
json.dump(out, open("pad_r11_standoff.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("stress_MPa", "deflection_mm", "kg_side", "vs_R13", "calibration")}))
