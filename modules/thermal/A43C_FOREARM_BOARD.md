# A43C: 2× RP40-11024SFR + hand board in the forearm (R-046) (RL Thermal, 2026-10-14)
**Supersedes the shoulder-bay sign-off (d4cca06, `A43_HAND_SUPPLY_SIGNOFF.md`) for this layout.** Hand calc on the A43B forearm model (`A43B_GRIP_HOLD.md`): Al shell ø70 × 270, shell → air 1.4 K/W (h 12 walking; ~2.4 K/W still air), RP40 case → bore via gap pad + strap 0.4 K/W, hand board → shell ~2 K/W [EST]. 35 °C ambient. RP40 limits: 105 °C case max; full power only to 60 °C ambient (local air ≈ shell here). RP40 above-60 °C derate slope not in repo; assumed linear to 0 at ~100 °C [EST, Electronics to cite].

## Forearm heat and temperatures (walking airflow)
| case | heat in forearm | shell | RP40 case (limit 105) | local ambient vs 60 °C derate | hand board |
|---|---|---|---|---|---|
| burst 1 s (on top of hold) | +4.4 W/module for 1 s | no change (τ ~ minutes) | ≤ +2 K | as hold | as hold |
| 30 N hold, 6 flexors 0.952 A (A43B), 2 × 1.9 W, board 3 W | ≈ 28 + 3.8 + 3 ≈ 35 W | **≈ 84 °C** | **≈ 85 °C (PASS, 20 K)** | **84 °C > 60: DERATE REQUIRED** | ≈ 90 °C [EST] |
| 30 N hold, still air | 35 W | ≈ 119 °C | ≈ 120 °C **FAIL** | FAIL | ≈ 125 °C FAIL |
| 2 × 40 W continuous (80 W into the stalled flexors ends as heat) | ≈ 80 + 8.8 + 3 ≈ 92 W | ≈ 164 °C | **FAIL** | FAIL | FAIL (and DCX windings fail first, A43B) |
| converters only (motors idle), 2 × 4.4 + 3 W | 11.8 W | ≈ 52 °C | ≈ 54 °C PASS | 52 °C PASS | ≈ 58 °C |

## Verdict
- **The forearm can sink the RP40 losses themselves** (case ≤ 85 °C at the 30 N hold, walking), **but not alongside the flexors.** The six DCX 22 heat the shell to ~84 °C, above the RP40's 60 °C full-power ambient, and still air or 2 × 40 W continuous is a FAIL. **Conditional PASS only with the derate rule below**; otherwise keep the RP40s in the shoulder bay (d4cca06 stays valid there, 71 °C case).
- Board: spec components ≥ 105 °C rated; shell temperature is the board's ambient.

## Derate rule for T-029 (shell NTC on the bore next to the RP40s, plus winding I²t from A43B)
| shell temp | per-rail cap | flexor hold current |
|---|---|---|
| ≤ 60 °C | 40 W | ≤ 0.84 A RMS each (A43B) |
| 60–80 °C | linear 40 → 20 W | ≤ 0.70 A |
| 80–90 °C | 10 W | ≤ 0.5 A (hold via brake/latch if fitted) |
| > 90 °C | shut rails off (soft release, warn) | 0 |
Hysteresis 5 K. Equivalent steady goal: total forearm heat ≤ 18 W keeps the shell ≤ 60 °C at walking airflow (≤ 10 W in still air). Bench G5: shell + RP40 case thermocouples at the 30 N hold.
