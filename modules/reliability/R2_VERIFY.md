# R2 independent verification — RL Test & Reliability (2026-10-21)
Light box work only: re-ran job 1's own validation (1 s), my hex8 convergence benchmark `r2_hex8_bench.py` → `r2_hex8_bench.json` (2 s), hand recomputation of job 1 bearing s0, and the job 4 normalizer/reward numbers. No solves were re-run.

## Verdicts
| # | Claim | Source | Verdict |
|---|---|---|---|
| J1-1 | Overall FAIL: both axial cases fail CRBH 6013 s0 ≥ 2.0 (1.45 / 1.29) | `design/fea/job1_pad_r8/REPORT.md` | **CONFIRMED** |
| J1-2 | Down cases pass s0 (2.63 / 2.09) | same | **CONFIRMED** (2.09 margin thin) |
| J1-3 | numpy hex8 (full 2×2×2) is a valid stand-in for CalculiX here | same §Method | **CONFIRMED for this job**, with limits (below) |
| J1-4 | von Mises 11.7–17.2 MPa ≪ 320, deflection ≤ 0.024 mm | same | **CONFIRMED** in conclusion (margin ≥ 6× even at the unfiltered 51 MPa); absolute values not converged |
| J1-5 | Mesh convergence (4 → 2 mm, one case) | same | **QUESTIONABLE** as a convergence study (2 levels, one case, filtered peak); irrelevant to the verdict |
| J1-6 | Bond 0.62 MPa shear, M4 no slip (593 < 825 N), tab bearing SF 1.62 | same | **CONFIRMED** (arithmetic) |
| J1-7 | Roll torque Mx −566/−773 N·m vs CSG-25 peak 369 N·m needs a look | same | **CONFIRMED** — that is a second failure, not a footnote; Arms R11/R13 already act on it |
| J4-1 | walk_a/b <1 s falls = eval obs mismatch (payload_frac 0 vs trained 5e-5, std 1e-6 → −50 σ) | `controls/rl/RETRAIN_PLAN_J10.md` §2.1 (5ecdbf4) | **CONFIRMED** |
| J4-2 | Lateral drift = no heading obs; yaw-rate reward too loose | §2.2 | **CONFIRMED** |
| J4-3 | Push failures = gate impulse never trained, residual ±0.25 rad too small | §2.3 | **CONFIRMED** on the impulse evidence; residual-limit cause is **QUESTIONABLE** (plausible, not isolated) |
| J4-4 | Carry 0.722 m/s = carry stage never converged | §2.4 | **CONFIRMED** |
| J4-5 | Knee peak 243.5 N·m vs rev B continuous 76.9 N·m not seen in training | §2.4 | **CONFIRMED** as stated; hardware thermal risk, tracked |

## Job 1 detail
**Element/method.** 8-node trilinear hex, full integration, linear elastic 7075 (E 71.7 GPa, ν 0.33), sparse direct solve. This is the textbook C3D8 element (CalculiX C3D8 is the same formulation). Patch test passes exactly (re-run: 100.000 MPa).
**Benchmark (mine).** Slender cantilever L/h = 10, using job 1's own `assemble()`:

| elements through depth | tip error vs Timoshenko |
|---:|---:|
| 1 | −37.3 % |
| 2 | −14.1 % |
| 4 | −4.7 % |

That is shear locking, and it converges at about O(h²). Implications: (a) deflections and bending stresses are **under-predicted** on coarse meshes; (b) the 0.5 mm tray with one element through thickness would lock in bending — acceptable here only because the tray is backed by the solid boss and carries mostly compression. Job 1's own stocky-beam check (−8.9 %) partly reflects the clamped root, not only the element. For thin-wall parts (tubes, clevis cheeks, webs) this element must be used with ≥ 4 through thickness, or swapped for C3D20R / P2 tets. **Not acceptable for job 9.**
**BCs.** Fixed roll-output face: stiff, raises local stress near it (correctly excluded, 6 mm band). Core load as uniform traction: fine for a honeycomb at plateau.
**Load cases.** 9.17 kN at 15° (normal 8857.5 N, tangential 2373.4 N) ✓ (9170·cos15° = 8857, ·sin15° = 2373).
**Bearing s0 (hand, mine).** r = (e, 87, −64) mm. Axial shear along X: Mtilt components Mz = −e·Fn − 87·Fs, My = −64·Fs.
- e = 0: |M| = 2373·√(87²+64²)/1000 = 256 N·m (+ weight → 258) → P0 = 8857 + 2·258/0.075 + 0.44·2373 = 16 781 N → **s0 = 24 300/16 781 = 1.45 ✓**
- e = 10: Mz = 88.6 + 206.5 = 295, My = 152 → 332 N·m → P0 = 18 790 → **s0 = 1.29 ✓**
The R7 table (2.45/1.98) left out the tangential force's lever arm; job 1 is right to gate on the full moment. The verdict does not depend on FE accuracy: s0 is pure statics.

## Job 4 detail
- From the job 4 policies (`policy_walk_a/b.npz`): `norm mean state[12] = 5.0e-5`, `std = 1.0e-6` → z(0) = **−50.0** ✓ for both.
- Reward: exp(−0.05²/0.25) = **0.990** for a constant 0.05 rad/s turn = 57.3° per 20 s ✓.
- Re-score `results_j4_rescore/walk_a_walk.json`: no fall over 20 s, 1.227 m/s horizontal, but net x/t 1.04, y 11.96 m, heading 47.5° → fails drift, which matches the diagnosis.
- Residual note: the harness fix (auto empty-payload value + t=0 obs z-check with |z| ≤ 8) is the right guard. Job 10 should also clip normalized obs in training/eval, so a std floor of 1e-6 can't amplify a 1e-5 difference again.

## P-046 … P-050 (landed as hand checks, `legs/R031_FIXES.md`; no FEA yet)
| P | Claim | Check | Verdict |
|---|---|---|---|
| P-046 clevis | cheek 14→17 mm, R6→R8 → Goodman ≥ 1.5 | (14/17)² = 0.678; σa = σm = 49.8 → 1/(49.8/87 + 49.8/572) = **1.52** | arithmetic ✓; **QUESTIONABLE**: assumes the R-023 hot spot is cheek bending (the h4 peak was at the bridge/cheek re-entrant edge). 1 % margin. Needs job 9(b) |
| P-046 clamp | root 24→28 mm → ~1.5 | (28/24)² = 1.36 × 1.1 = **1.50** | **QUESTIONABLE**: zero margin on a scaled base value |
| P-047 | tube 1.6 mm → SF 1.58 / 1.52 | 1.07·(1.6/1.2)^1.35 = 1.58 ✓; 1.03 → 1.52 ✓ | arithmetic ✓; relies on the R-023 empirical exponent; **pending FEA** |
| P-048 | ø6 dowel + bore-opening check | no calc given | **OPEN** (in job 9) |
| P-049 | collar OD R2 + 10° taper, anodize + MoS2 | no calc | **OPEN** (in job 9) |
| P-050 | DP490 per-lot coupons (ASTM D1002, 5 per lot, 23/60 °C, ≥ 80 %) | plan is sound | **CONFIRMED**; added to G5 as TP-G5-13 |
