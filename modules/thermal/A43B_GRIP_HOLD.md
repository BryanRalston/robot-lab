# A43B: 30 N continuous grip hold, 6 × DCX 22 S flexors (RL Thermal, 2026-10-14)
For RL Arms & Hands (`arms/A42_A43_R4.md` hold case: friction × 1.3 → 0.952 A = 1.10 × I_nom; rails 17.5 / 15.2 W). 40 °C forearm ambient. Hand calc `a37_a43b.py`.
Data: maxon DCX 22 S 24 V (`actuators/datasheets/maxon_dcx22s_innodrive.pdf`): R25 3.69 Ω, I_nom 0.869 A, Rth1 7, Rth2 16 K/W, τ_w 20 s, τ_motor 528 s, **max winding 125 °C**. R(T) Cu α 0.00393. Stall hold, so P = I²R(T).

## Verdict: **FAIL** at 1.10 × I_nom continuous. Rails **PASS**.
| model | steady winding at 0.952 A | time to 125 °C from 40 °C | max continuous current |
|---|---|---|---|
| single motor, catalog free-air Rth 23 K/W | **156 °C** (5.0 W) | **≈ 14 min** | 0.85 A (0.98 I_nom) |
| 6 in forearm, clamped to Al shell, R_h-shell 4 K/W [EST], shell → air 1.4 K/W (h 12) | 132 °C | ≈ 97 min | 0.92 A |
| 6 in forearm, loose mount R_h-shell 8 K/W [EST] | **159 °C** | **≈ 32 min** | **0.84 A (0.97 I_nom)** |
The six flexors share the forearm shell: 6 × ~4.8 W ≈ 29 W lifts the shell ~+40 K.

## Allowed (design values, worst case)
- **Continuous: ≤ 0.84 A per flexor** (≈ 0.97 × I_nom), ≈ **26 N tip** at friction 1.3 (scaled by current; less the hot-magnet Kt drop of a few %).
- **30 N hold (0.952 A): ≤ 14 min from cold**, then drop to ≤ 0.84 A; for cyclic grips, RMS current ≤ 0.84 A, i.e. hold duty ≤ 78 %.
- Better paths: clamp the drives to the Al forearm with paste (gets 0.92 A), measure friction (≤ 1.2 makes 30 N continuous fit), or a non-backdrivable/brake hold. Firmware: I²t limit on each flexor at 0.84 A RMS, winding model or NTC on the shell; trip ≤ 115 °C est. winding.

## Rails vs d4cca06 sign-off
Hold load 17.5 / 15.2 W per rail vs the 40 W continuous signed off (71 °C case at 35 °C, 34 K margin). Loss ≈ 1.9 W/module vs 4.4 W assumed. **PASS**, no change to A43 sign-off.
