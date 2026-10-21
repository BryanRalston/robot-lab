# Elmo G-TWI standoff heat plates — R-134/R-135/R-136 (RL Actuators, 2026-10-21)
Script `drive_heat_plates.py` (CadQuery 2.8) → `results/drive_heat_plates.json`, STEP in `cad/drive_plate_*.step`. Masses are CAD volume × 2.70 g/cm³ (6061-T6).
Basis: losses from Thermal R131_ELMO_MG.md (MAN-G-TWI v2.011 §11.2.1 chart −25 % + 1 W control): knee 6.0, hip_pitch 6.2, ankle 3.0, shoulder_pitch 4.2 W carry; R-096 duty = 0.6× carry. Air 35 °C, h 8 (standing/duty), h 12 check. Pad: 1 mm gap pad ≥3 W/mK, 0.3 K/W per drive. Limit: baseplate ≤80 °C (Elmo 85 − 5); firmware derate 75 → 50 % at 85 → off 90 (Electronics/Controls). All plates sit on G10/PEEK standoffs (4 × M3 corners, ø3.4) with no metal path to motor housings or femur (R-066, R-136 §1, hip_pitch off-housing per R-136 §2).

| plate | qty | geometry (6061) | area m² (wetted − drive faces) | mass g each | T base duty h8 | carry cont h8 | carry cont h12 |
|---|---|---|---|---|---|---|---|
| knee (2 drives/plate) | 2 | 100 z × 48 y × 1.5 base + 12 axial fins 8 × 1.0 (4 mm pitch) toward femur, η 0.998 | 0.0273 | 45.0 | **69.2** | 91.9 (derate) | 73.6 |
| hip_pitch | 4 | 80 × 80 × 1.5 flat | 0.0122 | 25.8 | **75.3** | 102.2 (derate) | 80.4 |
| ankle | 4 | 60 × 56 × 1.5 flat | 0.0060 | 13.5 | **74.1** | 100.2 (derate) | 78.8 |
| shoulder_pitch | 2 | 80 × 80 × 1.5 flat | 0.0122 | 25.8 | **62.3** | 80.5 | 65.8 |

Others (hip roll/yaw, elbow, waist, neck) stay on housings (Thermal PASS). Wrist pair: no plate; bay vent or derate (Electronics), per R-136.

**Mass:** plates 298.4 g + standoffs/screws 40.8 g [EST: G10 tube 0.25 g + M3 A2 0.6 g, 4/plate] = **0.339 kg robot**. Bare knee plates already in R-066 (2 × ≈19.4 g) ⇒ new addition 0.300 kg vs R-136's implied +0.256 ⇒ **+0.044 kg over booking** (over the 0.005 freeze; Arbiter to book — see D89).

**L51 envelope (knee):** stack = standoff 8.5 + base 1.5 + pad 1.0 + drive 14.4 = 25.4 of 26 mm (0.6 margin); y 48 of 52; z 100 of 104; 2 drives use 75 mm of z. Fins capped at 8 mm by depth; 0.0273 m² is 9 % under Thermal's 0.03 but the duty case still meets 80 with 10.8 K margin. Connector mating height above the 14.4 drive body is NOT inside the 26 mm box — Electronics to confirm.

**Findings:** continuous carry at h 8 exceeds 85 on knee/hip/ankle; it is held by the R-096 duty limit and firmware derate (or h ≥12 vent flow). hip_pitch duty (75.3) sits at the derate start. Next: G3 thermal re-check with plates in CAD (R-136).

## Rev 2 — D90 (Electronics 23f6992 §18.5 P-055, R-140, R-141), 2026-10-21
Supersedes the knee/hip_pitch rows and the L51 stack above. Same model (h 8 duty, 35 °C, pad 0.3 K/W); only geometry changed.
- **Drive mount (all plates):** G-TWI base 4 × M2 on 30.6 × 25.6 ±0.1 (MAN-G-TWI p.79). Plate and gap pad get Ø2.4 clearance holes only; M2 × 6 screws go up from the femur/structure side (screws booked by R-141). M3 G10/PEEK corner standoffs unchanged.
- **PE:** no PE lead per plate. One serrated washer per plate on a bare/masked seat; the heat sink is at PE inside the drive (Electronics §8.3). +0.1 g/plate [EST].
- **Knee re-solved inside 26 mm:** fins moved off the femur face onto the **drive side**: 6 axial fins 15 × 1.0 (3 per 7.5 mm strip either side of the 30 mm drive footprint, 100 long). They sit beside the drives and top out at 20.5 mm, below the PCB underside plane at 21.4. The femur side now only clears the Ø3 M2 heads: **standoff 4.0** (head 2.0 + 2.0). Stack 4.0 + 1.5 + 1.0 + 14.9 + 1.6 = **23.0 mm**: 3.0 mm to the 26 wall, so ID's 3 mm fits exactly (0.0 left). The plug exits sideways at −z, so it adds no depth. No extra Legs/ID depth needed.
- **Knee thermal (existing model, h 8):** area 0.0261 m², duty **70.7 °C** (rev 1 69.2; R-140 accepted ≤75.3), carry continuous h8 94.6 (derate), h12 75.3. A femur gap under 4 mm would credit only 30 % of that face [EST]; at 3.5 mm the duty temperature is 75.9 °C, so 4.0 is the minimum standoff. **Thermal re-run requested** to confirm the femur-gap credit and drive-side fin flow (R-140 vent-stream h 8 condition).
- **Hip pitch ≤72 °C:** flat plate 80 → **84 × 84 × 1.5**, duty **71.5 °C** (83 mm gives 72.4). Fits off-housing per R-136 §2 [EST: pelvis bay clearance not yet checked in CAD].
- **Harness:** knee −z, hip pitch to pelvis, ankle +z, shoulder to bay; MRTA2P26S bend radius 31.5 mm.
- **Mass:** knee 43.4 g each (−1.6), hip_pitch 28.4 g each (+2.6), washers +1.2 g. Total **0.347 kg** vs 0.339 (R-140) ⇒ **+0.008 kg**, which is over the 0.005 freeze, so it goes to the Arbiter (P-153).
