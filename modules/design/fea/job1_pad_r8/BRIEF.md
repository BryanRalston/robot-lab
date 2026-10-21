# Job 1 brief - ID shoulder-pad FEA, R8 option B (R-079)
Do NOT use the R7 case at 0dad225.

## Design
- Solid 7075-T6 roll-yaw link with integral 62x62x10 mm boss.
- 0.5 mm 7075 tray bolted to the boss on 4x M4; pad core sits in the tray.
- Inputs: modules/design/pad_r8.json and modules/design/SHOULDER_PAD.md (section R8); add the tray to that geometry.

## Loads
- 9.17 kN applied at 15 deg; two cases: shear along the roll axis, and shear downward.
- Plus arm weight in the tuck pose.
- Pad offsets: 0 mm and 10 mm. (4 load cases total: 2 directions x 2 offsets.)

## Pass criteria (each case)
- Peak von Mises <= 320 MPa
- Bond (core-tray adhesive) stress <= 7.7 MPa
- Bearing SF >= 2.0
- Deflection at pad <= 1 mm
- No M4 slip (preload x friction > shear per bolt)
- Tray tab bearing SF >= 1.5

## Method
- Python FEA on this PC (e.g. scikit-fem / CalculiX if available, or a validated plate/beam + hand-calc model where FE is impractical; state the method and assumptions). Keep CPU-only, modest runtime.

## Deliverables
- Script(s) and results JSON in modules/design/fea/job1_pad_r8/
- REPORT.md in the same folder: table of all criteria for all 4 cases, overall PASS/FAIL, assumptions.
- git add, commit "RL job1: pad R8 option B FEA (R-079)" and git push origin main. Do not touch other modules.
