# Pad R10 FEA rerun — stand-off Z −20, CRBH 7013 A (R-120 / CASE.md 00ff254)

**Overall: FAIL.** The bearing (s0), the gear and the flange bolts pass. The stand-off **structure as drawn** (ID 00ff254 / Arms R13: 2 ribs 30×5, 62×62×4 plate pocketed to a 2 mm floor) fails von Mises and deflection by a wide margin in every case.

Run on the Robot Lab box (numpy/scipy, under 6 GB), not on the bryan PC. Script `fea_r10.py`, numbers `results.json`.

## Gates, 15° governing (Fn 6761 N, Fs 1812 N, no μ credit), arm weight tuck B included in s0

| case | s0 (≥2.0) | Mx raw N·m | CSG-25 SF ×1.05 (≥1.0) | rib vM | plate-rim vM | floor vM (≤320/335) | defl mm (≤1) | bond shear / peel / comp MPa (≤7.7) | tray M4 slip | tab SF | case |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---|
| axial e0 | 2.31 P | −135 | 2.60 P | 556 F | 590 F | 820 F | 3.3 F | 0.60 / 2.7 / 7.2 P | no (453 < 825) P | 2.12 P | FAIL |
| axial e5 | 2.17 P | −135 | 2.60 P | 661 F | 715 F | 1007 F | 4.2 F | 0.62 / 3.0 / 7.6 P | P | 2.12 P | FAIL |
| axial e10 (info) | 2.04 P | −135 | 2.60 P | 758 F | 870 F | 1193 F | 4.8 F | 0.68 / 4.7 / **9.7 F** | P | 2.12 P | FAIL |
| down e0 | 3.92 P | **−321** | 1.10 P | 524 F | 913 F | 1111 F | 4.4 F | 0.60 / 2.7 / 7.2 P | P | 2.12 P | FAIL |
| down e5 | 3.54 P | −321 | 1.10 P | 645 F | 1032 F | 1254 F | 5.4 F | 0.62 / 2.9 / 7.5 P | P | 2.12 P | FAIL |
| down e10 (info) | 3.20 P | −321 | 1.10 P | 748 F | 1129 F | 1390 F | 6.1 F | 0.68 / 4.0 / **9.1 F** | P | 2.12 P | FAIL |

vM values are linear-elastic hex8 peaks with singular bands excluded (rib root 3 mm, rib/plate re-entrant edges 2.5 mm). They are far above the 503 MPa yield, so the real part would yield. Treat these numbers as "fails by 2 to 4×", not as real stresses.

**s0 reproduces R-120:** 2.31/2.16/2.04 on the Arms scalar method. The vector method gives the same values for the axial cases, and the down cases are higher because the tilt moment is smaller. Gear SF 1.10 also reproduces.

**μ 0.15 sensitivity (Fs 1014 N, not credited):** s0 is 2.85/2.64/2.46 in the axial cases and 4.02/3.62/3.28 in the down cases. Mx is 239 N·m, so gear SF is 1.47. This matches the R-120 values of 2.86/2.64/2.45 and Mx 239. No FE was run for this case because the 15° FE already fails.

## Roll flange joint (R13: 8×M4 12.9 PCD 62 + 2×Ø4 dowels, 5 mm 7075), from the FE support reactions
- **Bolts sharing shear:** 1621 N per bolt in the down case, SF 2.31 against 5 kN. **PASS** (matches Arms).
- **No separation:** preload 4.6 kN, worst bolt tension 2.29 kN in axial e10, SF 2.0. **PASS**
- **Dowels taking all shear** (the R13 note says "dowels take shear"): 6.48 kN per dowel, τ 516 MPa, SF **0.87** against 600 MPa. Flange bearing is 324 MPa, SF **1.11** against 480. **FAIL** if the dowels carry the shear alone. The drawing has to put the shear in the bolts (fitted or shoulder bolts), or use larger dowels (Ø6 or more).

## Method
- This reuses `job1_pad_r8/fea_job1.py`: the same hex8 element, 7075 E 71.7 GPa / ν 0.33, the IKO P0 = Fr + 2M/dp + 0.44Fa formula, the arm weight, and the six gates. The CRBH 7013 A is modelled with C0 27.7 kN and dp 85 mm.
- **Geometry:**
  - Two ribs, each 30 (X) × 5 (Z), running Y 0–23, at Z [−5, 0] and [−20, −15].
  - The face plate is 62×62, Y 23–27, centred at Z −20. Its rear 2 mm is pocketed except for a 4 mm rim, the 8 mm M4 bosses and the rib lands, leaving a 2 mm floor.
  - The tray is 0.5 mm.
  - The rib roots at Y 0 are fixed, which models a rigid hub/flange. The flange itself is checked by hand.
- **Core load transfer:** the R10 core patch is 54.8² centred on (e, −20). The shears are applied uniformly. The normal load is applied as a linear pressure field whose resultant sits at the pad point and carries Fs × (102.3 − 27.5) mm. FE support reactions match the hand statics (Mx −321 / −135 N·m).
- **Mesh:** 1 mm in X/Z. There are 3 elements through the 2 mm floor, 5 through each rib's 5 mm, and 3 through the rim layer, about 27k elements. This follows the T&R 7e55be7 note that hex8 runs about 37% stiff in bending with one element through the thickness.
- **Convergence:** the down e10 case at 2 mm gives a floor value of 1414 MPa and rib 576. These numbers are not converged at singular points, but every case fails by a wide margin. Since hex8 is stiff, the true values are probably higher still.
- **Deflection:** plate deflection of 4–6 mm is also outside the 0.5 mm the R13 e-stack assumes.

## Cause and what to change (for Arms/ID; nothing has been changed)
Two narrow ribs carry a 62×62 plate. The plate overhangs about 16 mm in X and 26 mm in Z, and the floor is only 2 mm. Mx 321 N·m goes through the ribs in weak-axis bending. Options are a full-width web, meaning ribs at the plate edges (±27) or a box section, plus a solid 4–6 mm plate. This adds mass to the +0.096 pair stand-off booking, and Arms owns that trade. Re-run once the geometry is revised.
