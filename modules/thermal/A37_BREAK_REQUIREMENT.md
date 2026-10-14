# A37 / T1: hip_pitch motor-to-collar break requirement (RL Thermal, 2026-10-14)
Answers RL Materials input T1 (`materials/A37_THERMAL_BREAK.md`, f7d4230). Basis D68 (hot R/Kt, η 0.84, 155 °C abs, trip 130, target ≤ 120). Worst side hip_pitch, 1.0 m/s + 20 kg carry, 35 °C, **A35 vented (h 15)**. Hand calc (`a37_a43b.py`, `results/a37_a43b.json`); R_col is [EST] until Legs CAD / J-T1.

## Network
case (+ΔT_case) → R_break → collar → R_col (collar + femur fin to air, 3–14 K/W [EST]) → 35 °C air.
Bond ≤ 60 °C ⇒ collar rise ≤ 25 K ⇒ **R_break ≥ R_col·(ΔT_case/25 − 1)**. The break leak (≤ 4 W) is < 10 % of the 43 W housing heat, so it does not change ΔT_case.

| case | ΔT_case | R_break needed, R_col 3 / 8 / 14 |
|---|---|---|
| **A35 vented h 15 (design case)** | 50 K (85 °C) | 3 / 8 / **14 K/W** |
| R1 open h 12 (vents under-perform) | 62.6 K | 4.5 / 12 / **21 K/W** |
| running up to the 130 °C trip | 73.9 K | 5.9 / 16 / **27 K/W** |

## Heat flow through the break (answer T1)
| R_break | R_col 3 | 8 | 14 |
|---|---|---|---|
| 10 K/W (sleeves only) | 3.9 W, collar 47 °C | 2.8 W, 57 °C | **2.1 W, 64 °C FAIL** |
| 4.6 K/W (A37 as drawn, see below) | 6.6 W, 55 °C | **4.0 W, 67 °C FAIL** | 2.7 W, 73 °C FAIL |
| 20 K/W | 2.2 W, 42 °C | 1.8 W, 49 °C | 1.5 W, 56 °C |
**Motor-to-collar heat flow ≈ 2–4 W at 10 K/W, ≈ 1.5–2.2 W at 20 K/W.**

## Is 10 K/W enough? **No, not as a design value.**
- 10 K/W holds 60 °C only if R_col ≤ 10 K/W; not guaranteed (R_col up to 14 [EST]), and no margin for vents below h 15.
- **The 1 mm G10 eye-face thrust washers are in parallel with the pin path**, not in series: inner ring face → washer → tine. Full-face washer (OD20/ID12) = 17 K/W each, 8.6 K/W for both, so the drawn design is **≈ 4.6 K/W net. FAIL** unless R_col ≤ 4.6.
- **Required: R_break ≥ 20 K/W total** (all paths in parallel: pin sleeves, eye faces, lever cheeks, any bolts). ≥ 14 is the bare minimum at h 15/R_col 14; 20 covers h 12 and is what A35 asked for.

## Getting to 20 K/W
- Thicker G10 does **not** get there: OD22 sleeve 20.8 K/W pin path, but with 1–3 mm full-face washers the net is 6–11.5 K/W.
- **PEI does, with face lands:** PEI sleeve OD20/ID12 × 8 per tine (pin path 25.4 K/W; tine bore 20, Legs L2/FEA) **plus** a 2 mm PEI flange whose contact land is ≤ 15 % of the face annulus (≈ 166 K/W per face; the rest an air gap ≥ 0.3 mm) ⇒ **≈ 19.5–20 K/W**. G10 with the same lands: OD22 sleeve ≈ 17 K/W (short).
- Bearing check at the larger bore is unchanged (bearing stress on the sleeve ID), but PEI SF ≈ 2.05 knocked down (Materials) – Materials to confirm the land bearing stress.
- If the lever cheeks bolt to the collar (L1), each bolt needs a Ti limiter + PEI washer and that path must be ≥ 60 K/W, or the 20 K/W total is lost.
- Alternative that avoids enlarging the tine bore: insulate the bearing outer ring in the eye (PEI sleeve 22/26 × 7 ≈ 19 K/W, single path) – Legs/Materials option.

## Reconciliation with A35 (≥ 20 K/W incl. bolts)
Same answer. A35's ≥ 20 came from ΔT_case 62.6 K (R1 h 12) and R_col up to 14 → 21 K/W. At the A35 h 15 design point the strict need is 14 K/W; **keep ≥ 20 K/W** as the spec for vent shortfall margin. Materials' ~10 K/W is the pin sleeves only; the parallel face path roughly halves it. J-T1 (bryan PC, queued) to confirm R_col and the collar temperature; G5 collar thermocouple.
