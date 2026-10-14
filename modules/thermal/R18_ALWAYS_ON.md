# R18: hand always-on logic supply, RECOM RP03-11012SRAW (Electronics §18.2b, 80e8aad) (RL Thermal, 2026-10-14)
One per arm, in the shoulder bay; 3 W, 14 g, −40…+105 °C with derating.

## (1) Always-on load (bridges off; motor VM comes from the RP40 rails, not this supply)
"Hot" means a realistic maximum: MCU junction at 85–90 °C (A43C), not 150 °C.

| item | typ W | hot W | basis |
|---|---|---|---|
| XMC4800 | 0.45 | **0.60** | Electronics Table 33: 0.45 typ / 0.90 worst. The worst case is at T_j max; leakage at 85–90 °C is ≈ +1/3 [EST] |
| 2× DP83822HF | 0.40 | 0.44 | < 0.22 W each (Electronics) |
| 6× ENX 22 EASY encoders | 0.48 | 0.72 | ≈ 16 mA typ / 24 mA max at 5 V each [EST, maxon class figure; confirm from the ENX datasheet] |
| 11× DRV8874-Q1 logic, bridges off | ≈ 0 | 0.01 | logic is driven from the MCU pins; VM quiescent (~3 mA each when awake) is on the RP40 rail, and it is µA in sleep |
| TMP117, NTC + LM2903B-Q1, misc. pull-ups | 0.02 | 0.03 | datasheet class |
| fingertip tactile (T4, part TBD) | 0.10 | 0.25 | [EST] **largest unknown** |
| subtotal at 3.3/5 V | 1.45 | 2.05 | |
| bucks 12 → 5/3.3 V, η 85 % typ / 82 % hot | +0.26 | +0.45 | |
| cable 12 V, ≈ 3 m loop at 0.4 Ω, 0.15–0.21 A | +0.01 | +0.02 | |
| **RP03 output load** | **≈ 1.7 W** | **≈ 2.5 W** | Electronics' 3.0 W ≈ this with the MCU at its 0.90 W worst (≈ 2.9 W) |

## (2) RP03 in the shoulder bay
**Datasheet** (RP03-RAW REV 0/2023, `recom-power.com/pdf/Powerline_DC-DC/RP03-RAW.pdf`):
- η 84.5 % at full load.
- Thermal impedance 19.22 K/W (natural convection 0.1 m/s).
- Max case 105 °C.
- **Derating graph** (plotted for the 11024SRAW only, natural convection): full load to **≈ 90 °C ambient** ("−40 °C to more than 90 °C without derating"), linear to 0 % at 105 °C. Reading is from the graph and the text; the exact knee is ±3 K.

**Self-heating:** loss at 2.5 W out ≈ 2.5 × (1/0.84 − 1) ≈ 0.48 W, so +9 K over the bay air (bay air +≈ 1 K from it).

| case | bay air (7f2fa7d + RP03) | RP03 case | to the 90 °C full-load ambient | to the 105 °C case |
|---|---|---|---|---|
| walking | ≈ 41 °C | ≈ 50 °C | 49 K | 55 K |
| still air | ≈ 49–54 °C | ≈ 58–63 °C | ≥ 36 K | ≥ 42 K |

## Verdict
- **Thermally the RP03 has big margin.** The bay never approaches its derating knee.
- **Electrically, 3 W is enough but tight:**
  - **Realistic hot load ≈ 2.5 W, 83 % of rating (≈ 0.5 W / 17 % margin).** Typical 1.7 W.
  - At Electronics' MCU-worst figure (≈ 2.9 W) margin drops to ≈ 3 %.
  - The tactile sensors and the ENX current are the open items.
- **Recommendation:** keep RP03 if the T4 tactile part comes in ≤ 0.25 W and the ENX draw is confirmed ≤ 25 mA. Otherwise (or for start-up inrush/cap-charge headroom), step up to a **RECOM RP05/RP06-class** wide-input (36–160 V) part in the same DIP24 footprint (≈ +0–5 g). Electronics to confirm part availability and the 11012 derating curve with RECOM.
