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
