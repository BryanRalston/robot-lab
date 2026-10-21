# L81: L39 hip-roll PU bumper — cited curve, energy, bottomed path (T&R side fall rev B 3b4c449; Controls 464b25b)
Script `hip_roll_bumper_l81.py` → `hip_roll_bumper_l81.json`.

## Source (cited)
Freelin-Wade **PUR90A** technical data sheet (92A, ASTM D575 compressive load): 2/5/10/15/20/25/50 % = **160/325/705/1050/1380/1690/3590 psi**.
https://www.freelin-wade.com/documents/data%20sheets%2C%20technical%20sheets%2C%20statements/PUR90A%20%20Technical%20Data%20Sheet.pdf
D575 specimen ø28.6 × 12.7 mm → shape factor 0.56 ≈ the bumper's 0.50, so used as is. 30/40 % are **linear interpolations between the 25 and 50 % points [EST]**. Gallagher design limit for 90A: 25 % strain at 0.16 Hz dynamic service (https://gallaghercorp.com/polyurethane-shape-factor/).

## Baseline ø20 × 10 at r63 (per bumper, one bumper loaded)
| strain | stress MPa | force kN | defl mm | joint torque N·m | θ° | energy J |
|---|---|---|---|---|---|---|
| 10 % | 4.86 | 1.53 | 1.0 | 96 | 0.91 | 0.75 |
| 20 % | 9.51 | 2.99 | 2.0 | 188 | 1.82 | 3.02 |
| 25 % | 11.65 | 3.66 | 2.5 | 231 | 2.27 | **4.68** |
| 30 % [EST] | 14.27 | 4.48 | 3.0 | 282 | 2.73 | **6.71** |
| 40 % [EST] | 19.51 | 6.13 | 4.0 | 386 | 3.64 | 12.0 |
Secant k ≈ 1.46–1.53 kN/mm → **5.8 kN·m/rad** at the joint (25 %). (L80's E-45 estimate, 2.1 kN/mm / 8.4 kN·m/rad, is stiffer than the cited curve.)

## Fallback ø24 × 16 at r63 (+6 mm bracket) — HELD, not adopted (SF 0.375, scaled ×0.787 by (1+2f²) [EST])
| strain | stress | force kN | defl | torque N·m | θ° | energy J |
|---|---|---|---|---|---|---|
| 25 % | 9.17 | 4.15 | 4.0 | 261 | 3.64 | **8.49** |
| 30 % [EST] | 11.24 | 5.08 | 4.8 | 320 | 4.37 | **12.2** |
| 40 % [EST] | 15.36 | 6.95 | 6.4 | 438 | 5.82 | 21.8 |
k ≈ 1.04–1.09 kN/mm → 4.1 kN·m/rad.

## L39 "4 J" basis
L39 (15c602d) gives "impact 0.76 J vs 4 J" with **no source** (no PU datasheet existed; hip_stop_r6 used an uncited linear E 25 MPa). **Replaced: capacity 4.7 J at 25 % (cited) / 6.7 J at 30 % [EST interp]** per bumper.
- Controls 464b25b with the swing tuck: 1.33 J max → **SF 3.5 (25 %)**: baseline OK. Without the tuck: 10.6 J → baseline FAILS (> 6.7); fallback 12.2 J at 30 % [EST] (Controls quotes 15.3 J) → covers it with margin 1.15 (30 %); at 25 % (8.5 J) it does NOT. Hold the fallback; the tuck rule is preferred.

## Bottomed-out path stiffness (hand beam + shear, 7075 [EST])
Lug 12 × 12 × 26 cantilever 18.1 kN/mm; deck bracket (6 × 30 leg, 20 mm arm) 13.5; yoke plate (8 × 40, 30 span) 177 → series **7.4 kN/mm = 29.4 kN·m/rad** at the joint. Fallback (+6 mm bracket arm): bracket 6.3 → series 4.6 kN/mm = **18.1 kN·m/rad**. Bolt/joint compliance ignored (stiff side).

## Mirroring and ROM
R leg roll mirrored **−15/+12** (L −12/+15). Overtravel from the cited curve: 25 % = 2.27° → sweeps use −14.5/+17.5 (L) and −17.5/+14.5 (R).

## Swing-foot landing 1.70 m/s (tuck) vs 1.40 [EST]
No explicit 1.40 m/s landing case exists in the Legs repo; the ankle envelope is the R-020 proof case (screws 13.1 kN = 1.5 × 8.76; GRF 1.31 BW). Scaling: force ∝ v for a linear contact (impulse ratio **1.214**); energy ratio **1.474** (conservative upper bound).
- Ankle screws: 13.1 kN × 1.214 = 15.9 kN (SF 1.72 vs C0a 27.3) / × 1.474 = 19.3 kN (SF 1.41).
- Ankle cross, DU bushes, sole: their SFs come from the Job 7 FEA (not yet returned). **Requirement: proof-case SF ≥ 1.22 (impulse) / ≥ 1.48 (energy) for the 1.70 m/s landing to pass.** DU liner 250 MPa static → the landing contact must be ≤ 206 / 170 MPa at the proof-case scale.
- Knee contact 0.62 m/s (always after the foot): below the foot case, not governing.
