"""Pad R10 stand-off LAYOUT PROPOSAL (R-120). ARMS-OWNED PART (roll-output structure, Arms ledger).
ID lays out envelope + pad interface only; Arms finalizes roll-output bolt interface, wall sizes, drawing."""
import json
RHO = 2.81e-3  # g/mm3 7075-T6
parts = {  # name: (dims mm, solid volume mm3, fill fraction)
 "pad_face_plate": ("62 x 62 x 4 (Y 23..27), 4x M4 tapped in 8 mm bosses on +-24 mm square; rear pocketed, 2 mm floor", 62*62*4, 0.45),
 "web_neck":       ("2 ribs 5 thk x 30 wide, Y 0..23 from roll-output face, span Z 0..-20", 2*5*30*21, 1.0),
 "roll_flange":    ("ring OD 60 / ID 40 x 4 on roll output (CRBH 7013 A side), bolt pattern TBD by Arms", 3.1416/4*(60**2-40**2)*4, 0.80),
}
m = {k: round(v[1]*v[2]*RHO/1000, 4) for k, v in parts.items()}
out = {"part": "P-arms pad stand-off (Arms-owned; ID layout proposal)", "ruling": "R-120 (12f68a4); Arms R12 (488206d)",
 "replaces": "integral 62x62x10 boss (0.024/side booked)",
 "geometry": {"pad_centre_Z_mm_below_roll_axis": 20, "pad_mount_face_Y_mm": 27.0, "contact_face_Y_mm": 102.3,
              "pad_interface": "62x62 face, 4x M4 on +-24 mm square, tray 0.5 mm 7075 unchanged, core 54.8 sq centred",
              "e_axial_offset_mm": "<=5 qualified (Arms tolerance stack)"},
 "parts": {k: v[0] for k, v in parts.items()}, "kg_side_EST": m, "kg_side_total_EST": round(sum(m.values()), 3),
 "kg_pair_EST": round(2*sum(m.values()), 3), "ledger": "Arms, outside 0.100 pad cap (R-120 item 2)",
 "Arms_to_confirm": ["roll-output bolt pattern/PCD and fastener size on CRBH 7013 A inner ring",
   "web/flange sizing under 7.0 kN @15 deg (FEA Job 8 add-on)", "e<=5 mm tolerance stack", "clash check pad+stand-off+7013 housing through abduction ROM, tuck, cover set",
   "Y datum: pad mount face kept at Y 27 so R10 contact Y 102.3 holds"]}
json.dump(out, open("pad_r10_standoff.json", "w"), indent=1); print(m, out["kg_side_total_EST"])
