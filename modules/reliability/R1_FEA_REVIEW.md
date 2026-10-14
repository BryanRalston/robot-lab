# R1 independent FEA review — RL Test & Reliability (2026-10-14)
Method: hand checks only on the box (no new FEA solves, per Bryan's light-work rule). Script `r1_checks.py` → `r1_checks.json`.
Material 7075-T6: Sy 503, Su 572, Se' 159 MPa R=-1 @5e8 (repo values). **My corrected endurance limit: Se = 159 × 0.75 (machined) × 0.9 (size) × 0.814 (99 % reliability) = 87 MPa.** The repo uses 159 (clevis Goodman) or 127 (`actuators/hp_lever_fea.py`); both are unconservative for a production part.

## Verdict summary
| # | Claim (source) | Verdict |
|---|---|---|
| 1 | Hip pitch lever: SF 1.51 at h4 (`results/PROOF_TEST_hip_lever.md` basis) | **WRONG** (already retracted by D58/O13 report) |
| 1b | Hip lever: "not converged, fix is topological, G2 cap+flanks" (`hp_lever_fea_O13_REPORT.md`, D58) | **CONFIRMED** — and fatigue makes it worse (below) |
| 2 | R-023 clevis 549.7 → 147 MPa, SF 3.42, pulse Goodman 1.69 | static **confirmed** at h4; Goodman **QUESTIONABLE** (1.03 with corrected Se) |
| 3 | R-023 clamp −24 %, rev Goodman ~1.95 | **QUESTIONABLE** (scaled, not solved) |
| 4 | R-023 femur tongue SF 2.15 press+fault; fault-only 1.48 | arithmetic **confirmed**; design **QUESTIONABLE/fails** 1.5 criterion; bore opening unchecked |
| 5 | R-023 foot collar hand SF 2.55 | **QUESTIONABLE** (arithmetic ok; ignores new collar-OD notch) |
| 6 | R-023 tube doublers SF 1.65–1.72 | **QUESTIONABLE** (only valid inside the 100 mm sleeve, fully bonded) |
| 7 | R-023 hip ring retired | **CONFIRMED** (obsolete geometry, L21) |
| 8 | Knee v4 D59 merged twin housing, clash-free 0–135° | **CONFIRMED** kinematically; no FEA of the new centre web |
| 9 | Ankle v4 D60/D63: stroke 112.6 / margin 13.9; QA1 20.8° vs 27°; tine checks | **CONFIRMED** (one labelling error); life [EST] → wear part |

## 1. Hip pitch lever
- Load: 454.2 N·m / 0.050 / 2 = **4542 N/pin ✓**.
- Peaks 335.5 → 359.5 → 378.9 MPa at h 3/2.5/2; local 1.5 mm gives 489.5 MPa (SF 1.03), above the 412 MPa Richardson value. Rising without bound = re-entrant-corner singularity (bore lip vs arm root). No converged peak exists for this geometry; SF 1.5 is not shown. The proof-test plan correctly holds release.
- **New finding — fatigue not checked and fails.** Walk 1.2 m/s hip_pitch peak 203 N·m (`legs/results/walk_1p2.json`) = 0.447 × design. Torque reverses each stride → treat as fully reversed. Hot-spot amplitude 153 MPa (h4) to 219 MPa (local) vs Se 87 → **fatigue SF 0.57–0.40**. ~5.8e7 cycles over T9 14 600 h. Even if G2 hits exactly SF_yield 1.5 (peak 335 MPa), walk amplitude ≈ 150 MPa > Se → still fails infinite life.
- Recommendation: G2 pass criterion must add **fatigue: hot-spot amplitude at walk_1p2 ≤ Se/1.5 ≈ 58 MPa** (i.e. design-load peak ≲ 130 MPa) or a cited S-N/finite-life case with shot-peen. That likely needs a much bigger section or steel lever. **Heavy rerun → bryan PC (Grok Build), not the box.**

## 2. Clevis (R-023)
503/549.7 = 0.915, 503/147 = 3.42 ✓; fall 233→62 same ratio (linear) ✓. But the 1.69 pulse Goodman back-solves to Se = 158.7 MPa: raw polished-specimen value. With Se 87: **Goodman 1.03**. h4 mesh on an R6 fillet (~1.5 elements across) likely under-reads the peak. Needs converged solve + corrected Se.

## 3. Clamp
182 → 137.6 MPa relative at h3 is plausible; the 1.95 Goodman is a linear scale of GB's h1.5 baseline that **failed** (1.47), and uses the same raw Se. With Se 87 the scaled value would fall to ~1.1. Not verified.

## 4. Femur tongue
503/340 = 1.479 < 1.5. Interference fit (60 MPa) + bore-opening under fault not checked; Loctite 648 is not a structural credit at fault loads. Add the dowel (A16) unless converged FEA shows ≥ 1.5.

## 5. Foot collar
443.8 × (6/9)² = 197 MPa, SF 2.55 ✓ arithmetic. It moves the hot spot to the collar OD (r45) step on a 3 mm plate — unanalysed. Also steel flange/7075 fretting under gait cycles: fatigue unchecked.

## 6. Tube doublers
SF ∝ t^1.35: 1.07 × (1.7/1.2)^1.35 = 1.71 ✓, 1.03 → 1.65 ✓. Only true (a) within the 100 mm mid-span sleeve, (b) if the DP490 bond carries full shear. Outside the sleeve the wall is still 1.2 mm (SF 1.07/1.03) — the dent location must be shown to lie inside the sleeve, and sleeve ends add a stiffness step/peel stress. The 0.267 kg hold is correctly kept.

## 7. Hip ring — confirmed retired (geometry replaced by ø35 tongue, R-020/L21). Agree with Arbiter that compressive neck Goodman 1.21 would have failed; retirement rests on obsolescence.

## 8. Knee v4 (D59)
Merged twin housing removes the 1257 mm³ boss overlap; `results/verify_v4.json` shows no clash 0–135° (min_body_gap 0.0 is reported for the merged part touching itself — confirm the checker excludes self-contact). Crossbar 503/192 = 2.62 ✓ (beam calc, no Kt; fatigue at knee walk 154 N·m not shown). The new 6 mm centre web carries both screw reactions in phase and has **no stress check**.

## 9. Ankle v4 (D60/D61/D63)
Stroke 414.17 − 301.59 = 112.58 ✓; margin 13.90 ✓; QA1 margin 6.2° ✓. Tine: 1109 N/tine ✓, bearing 15.4 MPa (D63 says SF 21.8 vs 1.5Sy; it is 49 — labelling error, conservative), tear-out 18.8 ✓, net Kt 35.9 MPa ✓. Loads are motor-peak limited only — fall/impact back-driving not included. Top rim clearance margin 0.27 mm is a tight tolerance stack. QA1 life is [EST] C (G_h 8 523 h < T9) → wear part 4 250 h until supplier rating (A22). Accepted as maintenance item.

## Heavy reruns requested (run on the bryan PC / Grok Build, never on the box or DESKTOP-B115PVV)
1. Hip lever G2 converged FEA **plus walk-load fatigue check** (criterion above).
2. A15 structure r2: clevis/clamp/tongue converged (h ≤ 1.5 at fillets), tongue bore-opening contact, foot collar OD, tube doubler bond, with Se_corrected 87 MPa in Goodman.
3. Knee twin-housing centre web stress at 3.6 kN/screw.
