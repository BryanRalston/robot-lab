# A43 thermal sign-off: 2× RP40-11024SFR per hand in the shoulder bay (RL Thermal, 2026-10-14)
For: RL Electronics R1_ARCHITECTURE §14/§16.2 (413d80f), Arbiter R-038/R-039 (0.142 kg release). Hand calcs, [EST] marked.
Design: per hand, 2 independent rails (RECOM RP40-11024SFR/P-HC, 24 V, each ≤ 40 W by firmware cap 1.67 A) + hand board, in the torso shoulder bay (A42).

## Verdict
**PASS, conditional on mounting:** each RP40 must have its case top on the aluminium shoulder bulkhead (or a 6061 bracket bolted to it) through a gap pad.
- **Max case temperature: 71 °C** at 35 °C outside, with both rails at 40 W **continuous** (not just burst). **Margin 34 K** to the 105 °C datasheet max case.
- Max continuous output allowed: **40 W per rail (the full rating, 80 W per hand) continuous**, so the 1 s burst limit is thermally unconstrained. The electrical cap stays 40 W per rail, never paralleled (Electronics §16.2).
- **FAIL if it relies only on the RECOM clip heat sink inside a closed shoulder bay.** Bay air reaches ~100 °C. With the heat sink and a **vented** bay (≤ 55 °C local air) it passes with 4 K margin, which is too thin to recommend.

## Inputs
| item | value | source |
|---|---|---|
| RP40-FR full-load ambient without derating | −40…+60 °C; derated to +105 °C | RP40-FR datasheet REV 8/2020 (recom-power.com/pdf/Powerline_DC-DC/RP40-FR.pdf) |
| max case temperature | 105 °C | same |
| thermal impedance, natural convection 0.1 m/s | 10.8 K/W bare, 10.3 K/W with heat sink | same |
| efficiency | 90 %, so loss at 40 W = 4.44 W per converter | §14 / datasheet |
| package | 2″ × 1″ (50.8 × 25.4 mm) metal case, top face 12.9 cm² | datasheet |
| hand board | 2–4 W, 4 W used | Electronics [EST] |
| heat per bay (one hand) | 2 × 4.44 + 4 = **12.9 W** (continuous worst case = burst level) | |
| shoulder_pitch nearby | 38 W copper at a 61 N·m hold; P-042 carry pose ~12 W, housing ~+13 K | `A43_ARMS_CHECKS.md`, O-A2 |

## 1. Shoulder-bay local ambient (35 °C outside)
- **Closed bay** (CF/PC shell + bulkhead, ~0.08 m² walls [EST]): inside h 4 and outside h 10 give UA ≈ 0.22 W/K. Adding 12.9 W plus ~10 W from the shoulder housing [EST] gives a **+100 K rise, about 135 °C.** Unacceptable, so convection alone in a sealed bay is ruled out.
- **Thor/torso air:** the Thor heat goes out the A41 duct and is assumed not to mix into the shoulder bay. Requirement: keep the bay out of the Thor exhaust.
- **Vented bay** (≥ 25 cm² inlet and outlet, ram air at walking speed 0.6 L/s): air rise ≈ 20 K, so **local air ≈ 55 °C**. Standing still, with chimney only, it is ≈ 0.2 L/s and worse.

## 2. Mounting options
| option | path | case temperature at 35 °C outside, 40 W per rail continuous | margin to 105 °C | verdict |
|---|---|---|---|---|
| **A: case top to the Al shoulder bulkhead, 1 mm gap pad ≥ 3 W/mK, clamped ≥ 50 kPa** | R_case-structure = 0.26 (pad) + ~0.15 (contact) ≈ **0.4 K/W**; bulkhead takes 12.9 W at R ≈ 2 K/W to the outside skin/duct air [EST] plus ~+10 K from the shoulder housing, so the bulkhead is at **≈ 69 °C** | **≈ 71 °C** | **34 K** | **PASS (required)** |
| B: RECOM -HC clip heat sink, vented bay (55 °C air) | 4.44 × 10.3 = +46 K | ≈ 101 °C | 4 K (and above 60 °C local air, so in the derating region) | marginal, not accepted |
| C: -HC heat sink, closed bay | | > 105 °C | negative | **FAIL** |
Option A, sensitivity: even if the bulkhead reaches 85 °C (h −50 %, shoulder at the 61 N·m hold), the case is ~87 °C, still 18 K margin. The bulkhead (or a 6061 bracket ≥ 3 mm, ≥ 40 cm² to the bulkhead) is the heat sink. The -HC clip heat sink is optional. If the +0.011 kg/unit heat sink is dropped, the bare RP40 (32 g) can save 0.044 kg per robot (Arms/Arbiter to decide).

## 3. Requirements (mounting)
1. Each RP40 case top pressed onto the Al shoulder bulkhead/bracket with a gap pad (≥ 3 W/mK, ≤ 1 mm, e.g. Bergquist GP3000-class) under a retaining strap. The hand board lies flat on the same plate.
2. Keep the bay out of the Thor exhaust stream. A ≥ 25 cm² vent pair is recommended but not required with option A.
3. An NTC on the bracket next to the RP40s, read by the hand board: derate the rail caps at 90 °C bracket, shut off at 100 °C.
4. G5 bench: thermocouple on an RP40 case, at the carry duty, at 35 °C.

## 4. Open
- Bulkhead geometry/temperature is [EST] until Torso CAD exists; J-T2 (chest CFD) should include the shoulder bays.
- The continuous hand duty profile from Arms is still TBD. This sign-off covers the worst case, 2 × 40 W continuous.
