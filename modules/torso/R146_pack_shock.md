# R-146: pack shock allowables vs chest-pad / prone-landing demand (Torso, 2026-10-21)

## 1. Cited cell and pack ratings
| Item | Value | Source |
|---|---|---|
| P45B cell shock (spec) | **150 g, 6 ms half-sine**, 3 shocks per direction, 6 directions (18 total); no leak, vent, rupture or fire; OCV ≥90 % | Molicel cell spec INR21700P45B: https://www.rotorama.com/assets/docs/980676faf74edb56f615f314dd6e3c2c/30769-1/en-datasheet-p45b.pdf (plus copy at cdn03.plentymarkets.com …/p45b-datasheet.pdf) |
| P45B UN 38.3 T4 | **PASS** (cell, 150 g / 6 ms) | Molicel test report: https://www.molicel.com/wp-content/uploads/Q1201-UN-P45B-4.35Ah-R7A1-TW2305060-001.pdf |
| P45B crush / drop (spec) | crush ~13 kN between flat plates: no fire; 4 ft drop onto concrete, 3× each orientation | same Molicel spec |
| UN 38.3 T4 rule | Cells: 150 g / 6 ms (large cells >500 g may use 50 g / 11 ms; P45B is 70 g, so small). Batteries: small (≤12 kg) min(150, √(100850/m)) g, 6 ms; large (>12 kg) min(50, √(30000/m)) g, 11 ms | UN Manual of Tests and Criteria §38.3.4.4: https://www.prba.org/wp-content/uploads/Sub-section-38.3-UN-Manual-6th-Revised-Edition-with-corrections.pdf |
| **Our pack T4 level** | 8.75 kg (small battery): √(100850/8.75) = **107.4 g, 6 ms**, Δv = (2/π)·107.4·9.81·0.006 = **4.0 m/s** | [CALC] from the rule above |
| IEC 62133-2 | no mechanical-shock test (it relies on UN 38.3) | **unknown; not verified against the standard text** |
| UL 2580 / SAE J2464 / ISO 12405 | pack mechanical-shock levels | **not cited (paywalled)**; automotive/EV levels do not apply directly. Unknown. |

The Molicel spec gives no allowable beyond the 150 g / 6 ms qualification. **A test level is not a design limit**: it shows survival of 18 such pulses, not a capacity.

## 2. Pack and structure allowables vs demand (38–104 g, 3.3–8.9 kN)
- **Cells, 150 g:** demand 104 g peak ≤ 150. **PASS** on peak.
- **Pack T4 level, 107 g / 6 ms:** demand 104 g ≤ 107. **PASS** on peak, but only by 3 %.
- **Pulse/Δv is NOT enveloped.** The fall pulse is 7–23 ms, Δv up to 5.67 m/s (screen model), against T4's 6 ms, 4.0 m/s. A longer pulse at the same peak puts more energy into the cell holders. **Unknown until a pack drop test at the fall pulse** (G5).
- **Cell holder:** 70 g × 104 g = 71 N per cell, through the cell can into the holder pocket. The holder is PC/ABS [EST]. **No cited allowable.** Mark it unknown; G5 test.
- **Rails (7075, multi-path, 320 MPa, R-128):** 8.9 kN over 2 rails, assuming 12 × 15 mm section and 220 mm span [EST]: M = wL/8 = 122 N·m per rail, σ = 272 MPa. **PASS, 85 % used** (on [EST] section).
- **Rail bolts (BOM row 5, 6 × M5 10.9 BHCS):** shear allowable 0.6 × 1040 × 14.2 mm² / 1.5 = 5.9 kN each. 4 effective = 23.6 kN against 8.9. **PASS (2.6×)**.
- **Latch (along the insertion axis):** no cited part. Must hold 8.9 × 1.5 = **13.4 kN**. **OPEN**: cite a latch or add a positive stop shoulder on the rails.
- **Screen model** (`fea_chest_pad.py`, lot band 19.5–22.3 kN × dynamic factor 1.10–1.30): peak pack g **25–46 g at 64 kg** and **59–85 g at 34.9 kg** (and kneel tip). Rail load **2.2–7.3 kN**. These sit inside the 38–104 g demand band.
  - **Stroke margin fails at 25° on the soft lot (2.5 %, need 10 %).** R-102 was sized at 15°. 25° is new demand.

## 3. Mitigation
1. **Latch: cited ≥13.4 kN latch, or an integral 7075 stop shoulder** on the rail ends (positive stop; the latch then only retains). +0.010 kg [EST]. **Recommended.**
2. **Pack drop test at the fall pulse** (half-sine 104 g, 20 ms, Δv 5.7 m/s, 3 axes) at G5. That replaces the missing allowable. No mass.
3. **25° case:** either Controls caps the TUCK chest angle at ≤15° (no mass), or take the R-102 fallback core 95 mm (+0.004 kg [EST], 67 mm stroke). Need: the 25° soft lot reaches 64.4 mm, against 0.9 × 0.75 × 95 = 64.1, so marginal. 100 mm core: +0.006 [EST], **PASS**.
4. **Pack isolators** (elastomer mounts, 4 × ~8 g, +0.03 kg [EST]): **not recommended**. They add stroke and rattle and lengthen the pulse, and peak g already passes. Keep as a fallback only if the G5 drop test fails.
5. **Rail section:** upsizing to 12 × 17 mm (+0.012 kg [EST]) gives 66 % used, if Materials wants margin on the [EST] section.

Inputs: `fea_chest_pad.yaml`; results: `fea/chest_pad_SCREEN_results.json` [SCREEN, 1-DOF].
