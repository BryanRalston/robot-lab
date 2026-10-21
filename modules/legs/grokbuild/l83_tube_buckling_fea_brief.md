# L83 tube local-buckling FEA brief (T&R 8c7ac56, SIDE_FALL rev C / L60 rev C, INSPECTION F1)
Owner RL Legs. Grok Build on the bryan PC. Inputs: `tube_buckling_l83.py/.json` (hand), `tibia_mass_cad_l79.py`, model_v4 (tubes, tongue neck, clevis, fork, collars), BOND_SPEC.
## Geometry
- Tibia 7075 ø45 × **2.0** (Robot Lab), length 314, 0.5 × 100 doubler sleeve OD 40.8 bonded mid-length; ends bonded onto the tongue neck (top) and ankle fork (bottom) per model_v4.
- Femur 7050-T7451 ø50 × 1.5, with the P-152 46.80 sleeve and the L22 split collar / L58 band clamps at their model_v4 positions.
- Shell (S8R/quadratic) or solid hex with ≥ 4 elements through the wall; ladder of 3 meshes, < 5 % change in the eigenvalue and peak strain.
## Load
- Pure knee moment **M = 1079 N·m** (92.5 J bottoming, T&R rev C) applied at the knee end through the actual tongue/clevis geometry, other end fixed at the next joint; plus the 0.92 kN·m design case.
- Bending plane: sagittal (knee flexion) and ±15° off-plane.
## Analyses
1. **Linear buckling eigen** (first 5 modes): report the load factor λ₁ (hand elastic SF 9.1 tibia / 5.7 femur; Brazier 6.0 / 3.8).
2. **Nonlinear** (geometric + elastic-plastic 7075-T7351 / 7050-T7451 true stress-strain, Riks/arc-length) with an imperfection of mode-1 × 0.1 t plus 0.5 mm/300 mm bow (INSPECTION F1 limit): report the limit moment, ovalisation ΔD/D at 1079 N·m, and peak plastic strain at the knee-end collar/bond.
## Acceptance
- λ₁ ≥ 3; nonlinear limit moment ≥ 1.0 × 1079 (hand inelastic SF 1.19 tibia / 1.09 femur [AISC F8 analogue, EST]); peak stress ≤ 393 at 1079 N·m (hand: tibia 388 → SF 1.01; **femur 401 → SF 0.98, FAIL by yield**: report the residual bow after unload vs the 0.5 mm/300 mm F1 limit); bond line shear at the collars per BOND_SPEC.
## Report
`results/r031/L83_TUBE_BUCKLING_FEA.md` + json; label assumptions [EST].
