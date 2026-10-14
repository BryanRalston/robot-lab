# R-069 mass-down pass: NEW cover trims beyond R-047 (RL Industrial Design, 2026-10-14)
Script `cover_trims_r069.py` → `cover_trims_r069.json`. Baseline: trimmed v5 set with the R-047 items already taken (A35 vents, PC 1.2 on thigh outboard + foot top, PA12 rim strips). Areas [EST] (measured: false), so covers count at half credit (R-040). Fabric weights from Materials COVER_TRIMS_REVIEW (silicone 70D ripstop ≈ **71 g/m²** finished, RBTR_SILPOLY).

## Item status (R-075 / R-079 / R-080 / R-081)

| item | Δ kg pair (full) | status | notes |
|---|---|---|---|
| A  CF 1.0 mm louvred thigh FRONT | **−0.026** | **booked** half credit (R-075) | Materials slot-edge rules binding |
| B  knee PC 1.5 → 1.2 | −0.020 | **dropped** (Materials dent FAIL / R-080) | replaced by B2 |
| **B2 PA12 1.5 mm knee cap** | **−0.016** | **test-gated** (kneel-fall) | either-or with B; Materials/R-080 |
| C1 foot 1.2 → 1.0 | −0.023 | **superseded by C2** | dent test dropped |
| **C2 foot top shell DELETED** | **−0.133** | **booked** −0.13 est → **−0.065** half (R-081) | see C2 breakdown |
| D  ankle boot → silpoly 0.071 | **−0.046** | **booked** half (R-075); silpoly delta R-080 | **replaceable wear part; inspection interval = 4,250 h rod-end service** |
| E  hip skirt → silpoly 0.071 | **−0.052** | **booked** half (R-075/R-079); was −0.045 at 0.10 assumed | hem ring + 70 cm² exhaust kept |
| F1 TPU-film bellows | −0.025 | **test-gated** (cycle) | R-075 |
| F2 delete bellows | −0.055 | **rejected** (R-075 ingress/pinch) | — |
| G snap hooks | −0.032 | **test-gated** (retention/fall) | R-075; rigid-panel count falls if C2 deletes M5–M6 |

**Booked now (A + D + E + C2): −0.257 full → ≈ −0.129 half credit** (Arbiter figures may round C2 as −0.13/−0.065 and silpoly D+E extra −0.003 at half per R-080).
**Test-gated upside (B2 + F1 + G): −0.073 full** once `R069_TESTS.md` passes.

## C2 net mass (Legs L54 / R-081)
| line | kg pair |
|---|---|
| Foot top shell skin deleted (PC 1.2, already R-047) | **−0.137** |
| 4× M3 web inserts **kept** (boot hem re-anchor) | 0 |
| Boot extension over instep rod ends/pins (~0.025 m²/side silpoly) [EST] | **+0.004** |
| **Net C2** | **−0.133** (−0.065 at half credit) |

Conditions (binding): (1) boot hem re-anchors through the 4 existing foot-box M3 inserts; (2) boot covers instep rod ends and pins down to the foot top; (3) Legs breaks R2 edges on exposed outrigger and lug ends. **Sole pad + toe/heel bumpers** are a separate R-081 requirement (Legs/Materials; not in this trim).

## R-075 fold-in (Arbiter)
- **D** must be **replaceable**, with an **inspection interval** (4,250 h rod-end service).
- **C1, F1, G** (and **B**, now dropped) were test-gated; **C1 is withdrawn** (C2 replaces it). Remaining gates: **B2 kneel-fall**, **F1 cycle**, **G retention/fall** — see `R069_TESTS.md`.
- **C2** went to Legs → **accepted** R-081.
- **F2 rejected**.

## Pad / R-079
Option **B** (replaceable bolted 7075 tray) **adopted** at **+0.024** vs the R-073 0.092 booking (0.116 pair). Field rebonding (option A) **rejected**. Materials remaining pad credit vs R-073: **−4.4 g** (pending FEA job 1 + link face). See `SHOULDER_PAD.md`.

## Confirmations
Materials: CF slot edges (done in review), kneel-fall (B2), F1 cycle, G retention, fabric TDS cited. Legs: C2 conditions + sole pad proposal. Thermal: drive-bay rear vent open areas in `a36_vents.json` (`knee_drive_bay`).
