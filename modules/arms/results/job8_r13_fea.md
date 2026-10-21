# Job 8 add-on (Arms R13, R-120): pad stand-off + CRBH 7013 A FEA and clash, per R7_ROUND.md §G

**Overall: FAIL.** This shares its FE run with `modules/design/fea/job1_pad_r10/REPORT.md`, which has the full tables and method. Numbers are in `job8_r13_fea.json`. It ran on the Robot Lab box, not the bryan PC.

| §G item | result | verdict |
|---|---|---|
| s0 ≥ 2.0 at e5 | 2.17 axial / 3.54 down (e0 2.31, e10 2.04) | PASS |
| Mx raw, CSG-25 SF at fault ×1.05 ≥ 1.0 | 321 N·m, SF 1.10 | PASS |
| Rib weak-axis vM ≤ 335 | 524–758 MPa, 645 at e5 down | **FAIL** |
| Face-pocket vM ≤ 335 | rim 590–1129, 2 mm floor 820–1390 MPa | **FAIL** |
| Flange bolt shear (8×M4 PCD62) | 1621 N per bolt, SF 2.31 vs 5 kN | PASS |
| Dowel shear (dowels alone carry the shear) | 6.48 kN per Ø4 dowel, τ 516 MPa, SF 0.87; flange bearing SF 1.11 | **FAIL** |
| No M4 separation (flange) | worst 2.29 kN vs 4.6 kN preload, SF 2.0 | PASS |
| Tray M4: no slip / no separation | 453 N < 825 N; pad load is compressive on the tray | PASS |
| Pad deflection (e stack assumes 0.5 mm) | 3.3–6.1 mm | **FAIL**, so the e ≤ 5 stack is no longer valid |
| μ 0.15 sensitivity (not credited) | s0 2.85/2.64/2.46, Mx 239, gear SF 1.47 | info |

Mesh: 3 or more elements through every thin wall, per the T&R 7e55be7 hex8 bending note. Hex8 runs stiff in bending, so the failures are if anything understated.

## CAD clash: NOT RUN
These §G CAD checks did not run:
- pad + stand-off + Ø108 housing axial gap ≥ 3 mm
- abduction −15…180 × pitch against the head shell
- overhead pitch ≤ −150 / roll ≥ 170 against the torso cover
- tuck B
- ID cover trims

The repo has no shoulder, pad, stand-off, housing, head-shell or torso-cover CAD (`arms/cad` holds only palm_7075), and the stand-off geometry fails structurally anyway, so it will change. The R13 light-model results (`arms/clash_r13.json`) still stand: torso 9.4 mm is marginal at overhead pitch, so keep the 135° soft limit, and the housing axial gap is OPEN. Run the CAD check after Arms revises the stand-off and produces CAD.

## Needed (Arms/ID)
- Redesign the stand-off with a full-width web or box section and a thicker plate.
- Carry the flange shear in fitted or shoulder bolts, or use dowels of Ø6 or larger.
- Update the mass, then re-run this add-on.
