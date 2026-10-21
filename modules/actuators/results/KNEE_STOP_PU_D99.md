# D99 — r75 PU knee stop re-sized to T&R L60 rev C (8c7ac56) (2026-10-21, ~10:35 ET)
Supersedes D98 sizing (rejected for mass). Basis: design 44.1 J (Controls 3d1da26 powered max 40.1 × 1.1); motors-off fault 92.5 J must stay inside 25 % strain.
Scripts: knee_stop_pu_d99.py (→ knee_stop_pu_d99.json, cad/knee_stop_pu_r75_d99.step), knee_stop_sweep_d99.py (→ knee_stop_sweep_d99.json). Armature and rotor-sign findings as D98 §1/§3.

## Design
- **Contact moved to 130°.** This is needed so that 92.5 J fits within 25 % strain by 143.6°, with the bottoming moment × rate factor inside T&R C2.
- Per knee: 2 stacks, each 24 (y) × 20 (radial). 7 × 10.17 mm PUR90A layers, 6 × 1 mm 7075 shims, 2 × 3 mm end plates, ø6 guide pin. Stack length 83 mm, centroid r 75. Shape factor 0.50 (at the limit). V = 64.3 cm³.
- Thigh-fixed outboard of the knee screws (y 34–58 / 202–226). Strikers are tibia lugs; t0 −20 as in D98.

| energy | strain | knee ° | pad force | moment (quasi-static) |
|---|---|---|---|---|
| 40.1 J (powered max) | 16.0 % | 138.7 | 6.9 kN | 521 N·m |
| **44.1 J (design)** | 16.7 % | 139.1 | 7.3 kN | **544 N·m** |
| **92.5 J (fault)** | 25 % | 143.6 | 10.5 kN | 790 N·m |
| 95.8 J (25 % bottoming) | 25 % | 143.6 | 10.5 kN | **789 N·m** |

Curve (strain / knee° / N·m / J): 2 % 131.1/75/0.7 · 5 % 132.7/152/3.9 · 10 % 135.4/329/15.4 · 15 % 138.2/491/34.8 · 20 % 140.9/645/61.8 · 25 % 143.6/790/95.8.

## Rate factor
- Strain rate at contact ≈ ω·r/T = 6.7 s⁻¹, against the quasi-static ASTM D575 data.
- Cast PU stiffens with strain rate: Sarva, Deschanel, Boyce & Chen, *Polymer* 48 (2007) 2208, doi 10.1016/j.polymer.2007.02.058 (rubbery to glassy over 10⁻³–10⁴ s⁻¹). That paper gives no factor for PUR90A at ~10 s⁻¹.
- **I use ×1.3 on stress/moment [EST]** (T&R used 1.2). It is to be measured in the TP-G5-20 D99 drop test.

## Check against T&R 8c7ac56 limits (tibia 45×2.0 Z 2781, femur 50×1.5 Z 2691, DLF 1.05, cap 50 N·m)
| item | value | limit | result |
|---|---|---|---|
| C1 44 J: tube M = (544×1.3 + 50)×1.05 | 795 N·m: tibia SF 1.37, femur SF 1.33 | SF ≥ 1.0 vs 393 | **PASS** |
| Bottoming energy at 25 % | 95.8 J | ≥ 92.5 J | **PASS** (1.04) |
| C2 fault: (789×1.3)×1.05, cap 0 | 1077 N·m: tibia 387, femur 400 MPa | no rupture ≤ 469 (yield 393 accepted with inspection, F1) | **PASS**: tibia elastic; femur slight yield, inspect |
| Top-out | 143.6° | ≤ 143.6° | **PASS** |
| Speed cap (contact at 130°) | 5.58 rad/s → 44.1 J; 8.22 rad/s → 25 % bottoming | informational (optional per Robot Lab) | n/a |
| Placement sweep (t0 −20, knee 0–145 + poses) | min 10.3 mm (pad ↔ ankle screw, knee 145/ankle −45); strikers ≥ 6.4 | ≥ 3 mm | **PASS** (t0 −30 fails, 2.7) |
| Screw axial (motor peak; rotor term relieves) | 3.63 kN/screw = 0.13 C0a | — | PASS |
| **Mass** | **0.242 kg/knee, 0.484 kg robot** [EST] | ≤ 0.35 kg | **FAIL (+0.134)** |

## Mass
- Breakdown per knee: PU 73 g (energy-bound, irreducible at 92.5 J), shims 15, end plates 6, strikers + arms 75, seats 13, femur collar bar 40, guide pins/fasteners ~20 [EST].
- Route to ≤ 0.35 [EST, needs Legs]:
  - machine the strikers as lugs on the tibia knee-end collar (−40 g/knee);
  - carry the seat bar on the existing thigh split collar ø64 (−30 g/knee).
  → ≈ 0.17 kg/knee, **≈ 0.34 kg robot**, only if Legs books the collar growth in this line.
- Other levers lower the fault energy, which is set by Robot Lab: 92.5 → 80 J saves ≈ 10 g/knee of PU.
- Cost of contact at 130°: free flexion ends 5° earlier than 135° (Controls TUCK check).

## Rev r75b (2026-10-21 ~10:45 ET) — Legs L84 r2 (6a3d84c)
- **Striker arm 24 (radial) × 18 (tangential) × 63 mm** (was 24×12; 399 MPa root FAIL per Legs). Legs: SF 1.05 design / 1.10 bottoming with Kt 1.4.
- **Tibia ring ø51 × 3 × 24, bonded + 2× ø6 pins** (bond alone SF 0.92 at bottoming; pins SF 4.65/3.23, Legs).
- Arm deepened **toward the striker face (t0−18…t0, flush)**, not Legs' t0−22 side. With t0−22 the arm comes within **0.5 mm** of the ankle screw body (knee 145°, ankle −45°), which fails.
- **Re-sweep (knee_stop_sweep_d99.py → knee_stop_sweep_d99b.json),** now including striker ↔ ankle parts on the same segment:
  - **min 4.5 mm**: striker arm ↔ ankle screw body at knee 145°, ankle −45°;
  - strut 6.7; pad ↔ ankle screw 10.3; R-leg plate 12.0;
  - pad ↔ own striker 2.3 at 128° (intended approach).
  - **PASS ≥ 3.**
- STEP: cad/knee_stop_pu_r75b_d99.step (stack + seat + lug + 24×18 arm + ring + 2× ø6 pins). The r75 STEP is kept for history.
- Loads unchanged: 7.3 kN design / 10.5 kN bottoming (Legs confirmed).
- **Mass line: 0.487 kg robot** (D99 0.344 + Legs leg-side 0.143 = ring 28.7 + arm deepening 38 + tie boss 5 g/knee; Legs L84 r2 6a3d84c). **FAIL vs 0.35, pending the Robot Lab ruling.**

### Mass-saving options on our side [EST]
| option | saving (robot) | verdict |
|---|---|---|
| Thinner/smaller pads at 92.5 J: PU is energy-bound (62.1 cm³ minimum vs 64.3 now) | −0.005 kg | negligible |
| Fault energy 92.5 → 80 J (Robot Lab bound) | −0.02 kg | needs a ruling |
| PU 95A instead of 90A (≈1.4× energy density) → PU, shims and plates ≈ −30 % | −0.04 kg | needs data for 95A and a re-check of the shape factor |
| Lighter striker material: Ti-6Al-4V (+20 %) or 4340 steel (+90 %) at equal SF | none (heavier) | 7075 is already the lightest |
| Tapered/pocketed 7075 arm (equal-strength taper ≈ ⅔ volume, I-section): the arms are ≈ 0.30 kg robot as 24×18×63 solid | −0.08 to −0.10 kg | best option. Legs owns the arm; needs FEA with Kt |
| 1 stack per knee | −0.10 kg | **not viable**: 10.5 kN at 84 mm offset → 0.88 kN·m tibia torsion → von Mises ≈ 540 MPa > 469 |
| Combined realistic (taper arms + 95A + 80 J) | ≈ −0.13 to −0.16 → **≈ 0.33–0.36 kg** | borderline vs the 0.35 cap |
