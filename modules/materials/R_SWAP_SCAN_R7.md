# Material-swap mass scan (R7, 2026-10-21), toward the ~−0.64 kg reserve recovery
RL Materials. Scan of the module BOM/mass files in the repo. [EST] = estimate. Ranked by grams, then by risk.

| # | swap | Δ robot | risk | status |
|---|---|---|---|---|
| 1 | Pocketed 7075-T7351 ankle cross (vs Ti, incl. +8 g DU bushes) | **−0.076 [EST]** | med (FEA job 7) | approved R-073, see ANKLE_CROSS_7075 |
| 2 | Ti-6Al-4V ankle pins with DLC/nitride (P-054) | −0.082 [EST] | high (galling, coating) | alternative to 3 |
| 3 | Hollow ø12/ø6 steel ankle pins (P-151) | **−0.048 [EST]** | low | new |
| 4 | Hybrid palm 7075 → PA12 + 7075 inserts (MASS_DOWN_R069 #2) | −0.080 [EST] | med (FEA queued, grip test) | open |
| 5 | Covers PC → PA12 small panels (COVER_TRIMS_REVIEW) | ≈ −0.015 | low-med (kneel-fall test) | open |
| 6 | Steel → Ti fasteners, non-structural (covers, brackets) | unknown: no fastener count in any BOM | low | blocked: needs a fastener list |
| — | Ti fasteners on the 16 × M8 12.9 shoulder mounts | rejected | Ti-6Al-4V ≈ 8.8-class < 12.9 | — |
| — | 42CrMo4 L63 8 × ø7 pins → Ti | ≈ −0.017 [EST] | high: the bond and bearing SF were set with steel | not proposed |
| — | More CF | none quantified: torso is already CF | — | — |

**Realistic total (rows 1 + 3 + 4 + 5):** ≈ −0.22 kg [EST] (−0.25 with row 2 instead of row 3). That is ~1/3 of the −0.64. The rest must come from the actuator housing pocketing (actuators/results/R069_MASS_DOWN.md: no FEA yet) or design changes, not material swaps.
**Ask to all modules (by file, not message):** add a fastener list with sizes and counts to each BOM so row 6 can be quantified.
