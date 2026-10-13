# Thigh clamp bond spec (R-020 A7). Collar to femur tube, plus internal sleeve to tube

Joint: 7075-T6 split collar (ID 50, length 34 mm) bonded to the 7075-T6 femur tube (Ø50 × 1.2 mm). A 7075 sleeve (47.6/43.6 × 34) is bonded inside the tube. Two Ø6 42CrMo4 cross pins act as positive backup (DECISIONS L22).

## 1. Adhesive: 3M Scotch-Weld DP490 (two-part epoxy, black, thixotropic, gap-filling)
Values cited from 3M datasheets, retrieved 2026-10-13:
- [A] 3M TDS "3M™ Scotch-Weld™ Epoxy Adhesive DP490", https://multimedia.3m.com/mws/media/2409614O/3m-scotch-weld-epoxy-adhesive-dp490.pdf
- [B] 3M UK product data sheet "EPX Adhesive DP490", https://multimedia.3m.com/mws/media/82790O/dp490-scotch-weld-tm-adhesive.pdf

| property | value | source |
|---|---|---|
| overlap shear, sandblasted Al, 23 °C | 23 MPa (3336 psi), cohesive failure | [A] |
| overlap shear, sandblasted Al, −40 °F | 23 MPa | [A] |
| overlap shear, sandblasted Al, 82 °C | 9.5 MPa (1378 psi) | [A] |
| shear, etched Al, cure 1 / cure 2: −55 °C | 23.7 / 31.6 MPa | [B] (BS 5350 C5) |
| shear, etched Al: 23 °C | 30.2 / 28.7 MPa | [B] |
| shear, etched Al: 80 °C | 11.9 / 12.7 MPa | [B] |
| shear, etched Al: 120 °C | 2.8 / 3.2 MPa | [B] |
| floating-roller peel, 23 °C | 9.24 daN/cm | [B] |
| work life | 90 min (45 g mixed, [A]); 1.5 h minimum at 23 °C ([B]) | [A][B] |
| time to structural strength (6.9 MPa) | 24 h at 23 °C | [A] |
| time to full strength | 7 days at 23 °C | [B] |
| mix ratio | 2:1 by volume (base 100 : accelerator 50) | [B] |
| bondline for max shear | 0.08–0.13 mm (3–5 mil) | [A] |

**Not verified, so no value is given:** fatigue (S-N) data, creep under sustained shear, humidity-aged values at 60 °C, and values on anodized 7075.

**Design allowable used:** 23 MPa sandblasted ([A], the lower of the two sources) × 0.5 knock-down = 11.5 MPa at 23 °C, and 9.5 × 0.5 = 4.75 MPa at 82 °C.
- Recomputed with these values (L22 had used 31 MPa):
  - static, both screws: 1.64 MPa → SF 7.0 at 23 °C, 2.9 at 82 °C
  - one-screw fault: 5.54 MPa → SF 2.08 at 23 °C, **0.86 at 82 °C**
- **The bond alone does not hold the one-screw fault hot. The pins are the retention in that case.** Backup alone: pin shear SF 6.7, bearing SF 4.41.
- Requirement: collar bondline ≤ 60 °C in service. Measure on the G5 bench, because the hip_pitch motor cans sit next to the clamp.

## 2. Surface prep (both adherends)
1. Solvent degrease with isopropanol, using lint-free wipes, until a clean wipe stays clean.
2. Grit-blast the bond areas (tube OD under the collar, collar ID, tube ID and sleeve OD) with clean 80–120 mesh alumina, to match the [A] "sandblasted" test basis. Mask everything else.
3. Solvent wipe again. Bond within 4 h. Handle with clean nitrile gloves only.
4. Do not anodize the bond areas. If the parts are anodized, mask the bond areas before anodizing.

## 3. Bondline
- Target 0.10 mm, range 0.08–0.13 mm per [A].
- Set it with the radial fit: collar ID and sleeve OD diametral clearance 0.20 ± 0.03 mm.
- Add 0.1 mm glass beads (≤ 1 % by weight) if the fit tolerance can't hold it.
- Fill: apply to both surfaces and twist on 1/4 turn. A continuous fillet must show at both collar ends.

## 4. Cure
- Hold position with the 3 MPa clamp bolts snug. Torque to spec only after cure. The cross pins go in after cure.
- Cure cycle 2 from [B]: 24 h at 23 °C, then 1 h at 80 °C. Alternative: 7 days at 23 °C (cure cycle 1).
- Do not load before 24 h at 23 °C or above ([A]).

## 5. Proof load, every joint (R-020 condition a)
- Load: **13.1 kN axial** (1.5 × 8.76 kN, both screws at max), tension and compression, 30 s each.
  - Bond shear at 13.1 kN = 13100 / (π·50·34) = 2.45 MPa: 21 % of the 23 °C allowable.
  - Fixture: collar through the two eye pins, femur clamped ≥ 40 mm from the collar.
- Measure relative slip collar-to-tube with a dial indicator (0.002 mm) across the witness mark. **Pass: residual slip ≤ 0.01 mm and no acoustic crack event.**
- Proof before the cross pins are drilled, so the bond alone is proven. Then drill and ream through the cured joint, fit the pins, and record the serial number.

## 6. Witness mark (R-020 condition b)
- After the proof test, paint a 2 mm torque-seal stripe axially across collar edge and tube at 2 positions 180° apart. Add a laser-etched 0.2 mm line across the joint for the permanent record.
- Inspect at every service interval. Any offset or a cracked stripe means the bond has slipped and the pins are carrying load: replace the femur assembly.
- Log the inspection in the robot service record.
