# Material-swap mass scan (R7, 2026-10-21), toward the ~−0.64 kg reserve recovery
RL Materials. Scan of the module BOM/mass files in the repo. [EST] = estimate. Ranked by grams, then by risk.

| # | swap | Δ robot | risk | status |
|---|---|---|---|---|
| 1 | Pocketed 7075-T7351 ankle cross (vs Ti, incl. +8 g DU bushes) | **−0.076 [EST]** | med (FEA job 7) | approved R-073, see ANKLE_CROSS_7075 |
| 2 | Ti-6Al-4V ankle pins with DLC/nitride (P-054) | −0.082 [EST] | high (galling, coating) | alternative to 3 |
| 3 | Hollow ø12/ø6 steel ankle pins (P-151) | **−0.048 [EST]** | low | new |
| 4 | Hybrid palm 7075 → PA12 + 7075 inserts (MASS_DOWN_R069 #2) | −0.080 [EST] | med (FEA queued, grip test) | open |
| 5 | Covers PC → PA12 small panels (COVER_TRIMS_REVIEW) | ≈ −0.015 | low-med (kneel-fall test) | open |
| 6 | Steel → Ti fasteners, non-structural (covers, brackets) | unknown: no fastener count in any BOM | low, qualified below | blocked: needs a fastener list (design/FASTENERS_BOM.json started) |
| — | Ti fasteners on the 16 × M8 12.9 shoulder mounts | rejected | Ti-6Al-4V ≈ 8.8-class < 12.9 | — |
| — | 42CrMo4 L63 8 × ø7 pins → Ti | ≈ −0.017 [EST] | high: the bond and bearing SF were set with steel | not proposed |
| — | More CF | none quantified: torso is already CF | — | — |

**Realistic total (rows 1 + 3 + 4 + 5):** ≈ −0.22 kg [EST] (−0.25 with row 2 instead of row 3). That is ~1/3 of the −0.64. The rest must come from the actuator housing pocketing (actuators/results/R069_MASS_DOWN.md: no FEA yet) or design changes, not material swaps.
**Ask to all modules (by file, not message):** add a fastener list with sizes and counts to each BOM so row 6 can be quantified.

## Row 6 qualification: Ti-6Al-4V non-structural fasteners in 7075 (R-123 §5)
1. **Fastener coating:** Type II anodize per **SAE AMS 2488** (the Ti anodize spec; spec text not fetched, citation by number only) for anti-galling, *or* a bonded solid-film lubricant (MoS₂ class) on the threads.
2. **Anti-seize:** nickel- or moly-based paste only. **No copper-bearing anti-seize on Ti** [EST: industry practice, no primary source fetched]. Silver and cadmium are prohibited on fastener systems by MSFC-STD-557B (https://standards.nasa.gov/sites/default/files/standards/MSFC/B/0/MSFC-STD-557-B.pdf).
3. **Galvanic isolation against 7075 (Ti is cathodic):**
   - The 7075 must be protected: conversion coat or anodize plus primer. Bare 7075 next to Ti fasteners showed considerable galvanic corrosion (NASA NTRS 19640001472, https://ntrs.nasa.gov/api/citations/19640001472/downloads/19640001472.pdf).
   - **Wet-install** with primer or sealant: NASA-STD-6012A §4.9.2 CPR 31 (https://standards.nasa.gov/sites/default/files/standards/NASA/A/2022-01-11-NASA-STD-6012A-Approved.pdf).
   - Apply sealant to the underhead, shank, washer underside and hole, keeping the **threads free of sealant**: NASA JSC PRC-4004 §6.4 (https://www.nasa.gov/wp-content/uploads/2023/03/prc-4004-current.pdf).
   - PTFE or nylon washers under the heads [EST]. They lose preload under creep, so use them only on non-structural joints.
4. **Caveats:**
   - Wet install changes the torque-tension relation (NASA-STD-6012A), so re-derive the torques.
   - Not for preloaded structural joints: Ti-6Al-4V is below the 12.9 class (row "—" above).
- Mass: still unquantified until the fastener list exists [EST ~ 40 % saving per fastener, ρ 4.4 vs 7.8].
