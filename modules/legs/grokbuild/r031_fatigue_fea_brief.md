# Brief: R-031 converged fatigue FEA (for RL T&R on the bryan PC; never the box)
Inputs: `legs/R031_FIXES.md`, `legs/hp_lever_family_r031.py`, `actuators/results/GROKBUILD_lever_fea_v2.md` (G2 geometry + Amendment 1), `reliability/R1_FEA_REVIEW.md`, `legs/grokbuild/fea_r5.py` (solver base).

## Common settings
- 7075-T6 (R-123, ca66b9b): Sy 480 MPa, Su 560 MPa, E 70 GPa (ν 0.33). Se = 87 MPa (kept). **Static allowable 320 MPa** (480/1.5) at design/fault; any peak > 320 MPa is a **FAIL** (the 320–335 band is FAIL, not marginal).
- Pass: hot-spot von Mises amplitude ≤ 58 MPa at the walk load, fully reversed. Also design/fault peak ≤ 320 MPa (SF_yield ≥ 1.5 on Sy 480).
- Convergence: h-refine to < 5 % peak change across three levels, with local h ≤ 0.5 mm at the fillets. Also report linearised membrane + bending through the root.

## Runs
1. Hip lever family, at 2030 N/pin walk and 4542 N/pin design (one-screw fault case too). G2 + modifications:
   - cap merged into a full-depth web, R8 cap/arm blends, bore-lip chamfer
   - (a) b 30 / d0 36 (pick)
   - (b) b 35 / d0 40 (fallback)
   - (c) b 32 / d0 36 / R12
   - Report the converged Kt (peak/nominal; nominal = F·35/(d0·b²/6)).
   - If (b) still exceeds 58 MPa, run 17-4PH H1025 at (a) (Se ≈ 294 MPa [EST], allowable 196 MPa) and report the mass.
2. Clevis cheek 17 mm, R8 (P-046), at R-023 loads. Goodman with Se 87 ≥ 1.5.
3. Clamp arm root 28 deep (P-046). Goodman ≥ 1.5.
4. Femur 7050-T7451 1.6 wall and tibia 1.6 wall outside the sleeve (P-047), with dent/bending at the R-023 load. Sleeve-end peel with DP490 cohesive layer E 2.5 GPa.
5. Femur tongue + A16 dowel, interference 60 MPa, bore opening under fault (P-048).
6. Foot collar OD edge with R2/taper (P-049).
7. Knee twin-housing centre web at 3.6 kN/screw (T&R #8), with D69 ø85 frame geometry from Actuators.

Output: `reliability/results/r031_*.json` with the peak, amplitude, Kt, SF and mesh-level table for each run.
