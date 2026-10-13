# Proof-load test: hip_pitch lever (config B, needle cheeks, SF 1.5 design), R-016 condition for SF 2.0 → 1.5
Applies to every production lever (100 % proof), plus one destructive qualification part per material lot.

**Basis.**
- Design load is 4542 N per pin: actuator max 454.2 N·m / 50 mm / 2.
- FEA (hp_lever_fea.py, HUB=needle, h 4 mm) gives SF 1.51 on yield at the worst direction φ = −60°. 7075-T6 Sy is 503 MPa.
- Proof factor **1.25 × design = 5680 N per pin, both pins together**. The FEA-predicted peak at proof is 332 × 1.25 = 415 MPa, which is 0.83 Sy, so no yield is expected.
- R-016 also asks for 1.5 × the fall load. The fall load per the Legs structure case (3 BW through the pivot) is lower than the actuator max on the lever, so 1.25 × actuator max governs.

**Fixture.**
- The lever is mounted on a hardened ø35 h6 dummy shaft through both TLA 3520 Z bearing bores.
- The cheek outer faces are bolted to a rigid yoke plate, as in service.
- Load goes in through ø12 pins in both ears, in single shear like the rod-ends. A hydraulic or servo-press whiffletree splits the load equally to the two pins.
- The load direction is set by an indexable fixture to φ = −60° (governing), then 0° and +60°.

**Instrumentation.**
- Load cell ±0.5 % on each pin.
- Two dial gauges or LVDTs at the pin centres, measuring relative to the shaft.
- Two rosette strain gauges at the arm-root FEA hot spot (|y| ≈ 34, z ≈ −17, x ≈ ±12) on the qualification part.

**Procedure.**
1. Preload 500 N per pin; zero the gauges.
2. Ramp to the design load (4542 N) in 5 steps, then unload. Record pin deflection; the FEA predicts 0.16 mm. Accept if within ±25 %.
3. Ramp to proof (5680 N), hold 30 s, unload to 500 N.
4. **Accept** if residual set is ≤ 0.02 mm at the pins and dye-penetrant shows no cracks (arm roots, ear bores, cheek bores). Strain-gauge peak must be within ±15 % of FEA. This check also covers mesh convergence (O13).
5. Repeat for φ 0° and +60° on the qualification part only.
6. Qualification part only: continue to rupture or 2 × design. Record the yield onset (0.2 % strain at the rosette) and confirm SF_yield ≥ 1.5 against the measured Sy of the lot.

**Records.** Serial number, material cert (7075-T6 or T651 plate, Sy ≥ 503 MPa), load–deflection curves and photos. The test goes into G5 bench week W2 (BENCH_TEST_PLAN.md §7).
