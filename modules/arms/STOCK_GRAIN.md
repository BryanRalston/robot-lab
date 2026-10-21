# Arms stock form, thickness and grain, per R-128 (9e49b7a / Materials 01982fc), 2026-10-21
Every Arms 7075 drawing or spec carries the row below. Single-path limits are the MIL-HDBK-5H A-basis band ÷ 1.5, LT unless the drawing fixes L. An unstated row takes 257. Frame for the shoulder parts: X = roll axis, Y outboard, Z up. No 3D printing.

| part (spec) | stock | finished envelope mm | stock thickness | grain (L / LT / ST) | single-path limit |
|---|---|---|---|---|---|
| **W2 carrier** (R15_W2_CARRIER.md, cad/r15) | 7075-T651 plate | 73 (X) × 63.4 (Y) × 62 (Z). Every dimension exceeds 50.8, so **≤ 2 in stock is not possible** | **2.5 in (63.5 mm)**, ST = Z | **L = Y** (arm radial = arm root primary bending direction), LT = X (plate cantilever bending), ST = Z (no through-thickness load path) | **294** (2.001–2.5 in, LT; the plate root governs) |
| roll output hub Ø70/Ø54 × 18.5 (R13/R15) | 7075-T651 plate | Ø70 × 18.5 | 1.0 in, ST = X (axial) | L in-plane, any; bolt bearing in plane | 313 |
| roll housing seat flange OD108/Ø100 × 15 + clamp ring (R13) | 7075-T651 plate | Ø108 × 15 | 0.75 in, ST = X | L in-plane; ring hoop: LT governs | 313 |
| stand-off R11/R14 (superseded by the W2 carrier; for record) | 7075-T651 plate | 76 × 88 × 32 | 1.5 in, ST = Y | L = Z | 308 |
| palm (A32_PALM_7075.md, cad/palm_7075) | 7075-T651 plate | ≈ 32 × 86 × 90 | 1.5 in, ST = palm thickness | L = finger axis (grip bending; R19 heel band bending along L) | 308 |
| roll-yaw link 60 × 40 × 50 (model_v4) | 7075-T651 plate | 60 × 40 × 50 | 2.0 in, ST = 40 dim (lateral) | L = Z (arm axis) | 308 |
| elbow clevis 60 × 96 × 58 (model_v4) | 7075-T651 plate | 60 × 96 × 58. All dimensions exceed 50.8 | 2.5 in, ST = 58 (Z) | L = 96 (Y, across the clevis lugs); lug bearing LT | 294 |
| upper-arm tube Ø50 × 2 (model_v4) | 7075-T6511 extruded / drawn tube [Materials to cite tube A-basis] | Ø50 × 87 | 2 mm wall | L = tube axis | 257 until cited |
| forearm shell Ø70/66 (model_v4, R7 forearm 287) | 7075-T6511 tube [cite] | Ø70 × 194 | 2 mm wall | L = tube axis | 257 until cited |
| forearm wrist end cap Ø70 × 4 | 7075-T651 plate | Ø70 × 4 | 0.25 in, ST = axial | L in-plane | 308 |
| wrist fork (A42) | 7075-T651 plate | per A42 [EST ≤ 1 in] | 1.0 in | L = forearm axis | 313 |
