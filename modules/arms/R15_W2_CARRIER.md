# RL Arms & Hands R15 (2026-10-21): W2 wrap carrier per R-125 (61122a8/829c65c)
CadQuery: `cad/r15/r15_w2.py` → `carrier_w2`, `housing_7013_coaxX`, `hub_r15`, `pad_envelope_w2` (.step + .stl), `r15_w2.json`. Cover clash: `cad/r15/r15_cover_clash.py/.json`. e stack: `e_stack_r15.py/.json`. Image: `R15_w2_carrier.png`.
Frame: X = roll axis (true), Y outboard, Z up, origin at the CRBH 7013 A plane. One-piece machined 7075-T6, no 3D printing. Basis Sy 480 / gate 320 (R-125). [CALC] means computed, not measured; measured masses come at G5.

## Geometry (Arms-owned; ID's R11 stand-off with the R14 fixes is absorbed into the carrier)
- **Stator, unchanged:** CRBH 7013 A, r 35–50, x ±6.5. OD108 seat flange, r 50–54, x ±7.5.
- **Rotating:** hub Ø70/Ø54, x −6.5…+12 [EST].
- **Flange:** OD76/ID36 × 5 at x 12–17; 8 × M4 12.9 PCD62; 2 × Ø6 m6 dowels on PCD57.
- **Radial box arm:** 25 (X) × 56 (Z) × 3.5 wall, x 17–42, Y 0–63.0; R3 edge fillets. A haunch steps in to x 10.5 above the housing (Y ≥ 45).
- **Outboard plate:** 6 mm thick, inner face at Y 57.0 (housing r54 + 3.0), spanning X −31…42 and Z ±31. Two edge ribs 8 wide on the inner face at Z ±(23…31), Y 52.25–57, follow the housing at ≥ 3 mm.
- **Pad:** centred X0 / Z0 (on the roll axis). Mount face Y 63.0, **contact Y 138.8** (the R-125 value). The tray's 4 × M4 on ±24 are unchanged.
- The 3 × Ø8 access holes (R14) are no longer needed: the flange bolts are reached from +X beside the arm. **Confirm in drawing.**

## Checks
| item | value | gate | result |
|---|---|---|---|
| s0 at e0 / e2.4 | 2.056 / 1.999 | ≥ 2.0 | PASS at e ≤ 2.4 (1.999 rounds to 2.0, matching R-125's interpolation) |
| Mx raw | 251 N·m, CSG-25 SF at fault 1.4 | ≤ 351, ≥ 1.3 | PASS |
| arm root vM (hand × 2.86) | 289 MPa | 320 | PASS (SF 1.11 on gate, 1.66 on Sy) |
| plate root (rib-stiffened T, Kt 1.5 [EST]) | 295 MPa | 320 | PASS, thin, so FEA decides |
| pad X deflection | 0.27 mm cal (plate tip 0.147 mm) | ≤ 1 | PASS |
| carrier → housing/OD108 | **3.0 mm** (OCC min distance) | ≥ 3 | **PASS at nominal, with 0 margin.** The drawing needs +0.0/−0 on the plate inner face, or a 3.3 mm nominal gap (s0 then 1.996 at e2.4) |
| pad → housing | 9.0 mm | ≥ 3 | PASS |
| head shell (ID STEP, transformed) | ≥ 114.3 mm over the full sweep; tuck B 253.6 | ≥ 3 | PASS |
| torso cover (coarse 28-tri) | tuck B 74.1 mm; roll 0–90 at 74 mm; **roll ≥ ~118–128° penetrates** (last ≥ 3 mm pose: {'-150': [128, 5.0], '-90': [128, 5.2], '-30': [118, 22.8], '0': [122, 18.5], '30': [118, 22.7]}) | ≥ 3 | **FAIL above ~118°** |
Cover transform: site → sim world x = x_s, y = −z_s, z = y_s − 57.1 mm. The offset comes from aligning the head_shell bbox centre with the sim head geom.
**Finding:** the +36.5 mm pad on the coarse torso envelope cuts the roll soft limit from 135° to **≈ 118°** (all pitches). That's indicative only, since the torso envelope is coarse, but ID should re-check with a real torso cover. **Proposed interim soft limit: roll ≤ 115°.** This changes Controls' joint-limit value.

## e stack (R-125 limit 2.4; ID 0.3 tolerances)
Worst **1.92 mm**, RSS 0.86 mm, margin 0.48 mm. s0 is 2.01 at worst case and 2.035 at RSS. **PASS.** Deflection is carried at 0.69 mm (ID R11) until Job 8b reports e under load.

## Mass [CALC] vs booked
- Carrier, stand-off and flange in one part, with fasteners and dowels: **0.2657 kg/side**.
- Booked: 0.102/side (R-121/R-123), plus R-125 +0.044 pair (stand-off net), plus +0.140 pair (carrier [EST]) = 0.194/side.
- **Δ = +0.143 kg pair over booking.** The carrier replaces the R11 box/plate, so there's no separate stand-off.
- Lightening for Job 8b to confirm: pocket the arm side walls and trim the plate X extent to 42. About −0.03/side [EST].
