# A37: thermal-break material at the motor-to-collar joints (R-030 / P-027 thermal; with Legs A38)
RL Materials, 2026-10-14. Properties and sources are in `MATERIALS_DB.md` (G10FR4, PEEK, PEI added). [EST] = estimate.
**Numbering clash:** RULINGS R-030 uses "P-027" for this thermal break, but PROPOSALS.md P-027 is the Arms wrist downsize. The Arbiter should renumber one of them.

## Joint and loads used (repo)
- The hip_pitch screw body hangs on the clamp collar through an SKF GE 12 E eye in a 7075 body eye. The ø12×28 42CrMo4 pin sits in two clamp-arm tines, each 8 mm thick (model_v4 l.154–156; CONTRACTS/PROPOSALS D46).
- The metal heat path is: can → eye → pin → tines → collar → DP490 bond.
- Max force is 4 542 N per body (clamp_review.py). Fault and proof force is 13.1 kN for both bodies, so 6 550 N per body (BOND_SPEC §5).
- Temperatures: case is 98 °C worst (Thermal R1_BUDGET, 35 °C covered). The bond limit is ≤ 60 °C.
- Legs must confirm whether any *bolted* motor/lever-to-collar flange exists. In the current model the only contact is the pinned eye (and the hip_pitch lever cheeks if they bolt to the collar). → input L1.

## Concept
Put an insulating flanged sleeve in each tine bore: ID 12 (pin H7/g6), OD 16, wall 2 mm, length 8 mm, with a 1 mm flange facing the eye.
- The pin is loaded in **bearing** on the sleeve. No bolt preload passes through the polymer, which removes the preload-creep risk.
- Wherever a bolted flange must be insulated, use **Ti-6Al-4V compression-limiter bushings** through the insulator so that preload goes metal-to-metal. Ti k = 6.8 W/m·K vs 7075 130 (MIF). The insulator then only takes shear and bearing.

## Comparison (room-temperature cited values; hot values not available)
| property | G10/FR4 | PEEK unfilled… 30CF | PEI | source |
|---|---|---|---|---|
| compressive, MPa | flatwise 414–483, **edgewise 172–241** | 120–300 | 140–180 | G10_CC/GUND, MIF |
| shear, MPa | 148 punch | 50–100 | — | GUND, MIF |
| k, W/m·K | 0.29 through-plane | 0.25 (unfilled) … 0.93 (CF) | 0.18–0.23 | RAX, MIF |
| CTE, µm/m·K (Al 23) | 13–18 in-plane | 15–52 | 20–53 | RAX, MIF |
| temp limit | temp index 130–140 °C | Tg 240, HDT 160–300 | Tg 210, HDT 200–210 | CC/GUND, MIF |
| density | 1.85 | 1.3–1.5 | 1.3–1.5 | CC, MIF |
| creep at 100 °C under load | **not verified** | **not verified** | **not verified** | need supplier curves |

## Checks (worst case: 6 550 N fault, 98 °C)
- Bearing per tine = 6 550 / 2 / (12 × 8) = **34.1 MPa** (23.7 MPa at max walk force).
- G10, radial loading of a sleeve = edgewise. Lower bound 172 MPa gives SF 5.0 at room temperature. With a 0.5 hot/creep knock-down [EST] it is **SF 2.5**.
- PEEK unfilled at 120 MPa gives SF 3.5 at room temperature, **1.76** knocked down. CF-PEEK at up to 300 MPa gives higher strength but k rises to 0.93 (×3.7 heat leak).
- PEI at 140 MPa gives SF 4.1 at room temperature, 2.05 knocked down. Its mechanical limit is 170 °C (MIF), which is fine.
- Shear-out of the 2 mm flange is not loaded (the pin is axially retained by circlip).
- Thermal resistance per tine sleeve is R = ln(16/12)/(2πkL).
  - Pin path across both tines (L = 16 mm): G10 **9.9 K/W**, PEEK 11.5, PEI 12.5–16, CF-PEEK 3.1.
  - The flange faces add more resistance in series.
  - Whether this is enough depends on the heat flow to the collar, which Thermal must supply (input T1).
- CTE / fit loss over 25→98 °C:
  - G10 in a 7075 bore: (23 − 15) × 10⁻⁶ × 16 mm × 73 K ≈ **9 µm diametral loosening**.
  - PEEK unfilled (~50) tightens by 31 µm, then relaxes by creep and is loose when cold.
  - → **Bond the sleeve with DP490 (≤ 60 °C side) or retain it with the flange plus a press of 0.01–0.02 mm.** G10 is preferred because its CTE is closest to the steel pin (13, MIF 4140) and to Al.
- Preload loss (bolted variant only): with Ti limiters the insulator sees no preload. Without limiters, preload loss in polymer at 98 °C is **not quantified**, and that design is not acceptable until creep data exists.

## Recommendation
- **G10/FR4 (NEMA LI-1 G10 or FR4, EPGC 202) flanged sleeves**: 2.0 mm wall, OD16/ID12 × 8 mm, plus a 1.0 mm flange. Machine from convolute or wound tube or from plate with the load edgewise.
  - Margin: SF 5.0 at room temperature, SF ≈ 2.5 at fault + 98 °C after a 0.5 [EST] knock-down. The knock-down must be replaced by data (G5 bench creep, 100 h at 34 MPa / 100 °C).
  - Add a G10 1 mm thrust washer at each eye face, replacing metal contact there. Note DECISIONS L-173 already uses PTFE washers at the ankle.
  - Ti-6Al-4V compression-limiter bushings wherever a bolted flange is insulated.
- Backup: PEI if a machinable, lower-k part is wanted (equal strength margin, k 0.2). Don't use CF-PEEK: it is too conductive for a thermal break.
- **Mass, 8 sleeves (2 tines × 2 bodies × 2 legs):**
  - G10: 5.63 cm³ × 1.85 = **+10.4 g**.
  - The tine bore grows from 12 to 16 mm, removing 7075: 5.63 × 2.81 = −15.8 g.
  - The tines need +2 mm of material around the larger bore, ≈ +18 g [EST].
  - Thrust washers: +2 g.
  - **Net ≈ +15 g both legs [EST]**. Legs books the final figure under A38.

## Inputs needed from Legs (A38) / Thermal
- L1: the full list of metal contacts between hip_pitch and knee motor/lever and the collar. Are there bolted flanges, and are the lever cheeks bolted to the collar? This decides whether Ti limiters are needed.
- L2: tine edge distance at a ø16 bore and an FEA re-check of the tines (bore growth).
- L3: pin retention method (circlip) and whether a sleeved pin is acceptable for G2 clearance.
- T1 (Thermal): heat flow can → collar and the required R (K/W) so the bondline reaches ≤ 60 °C at 35 °C ambient. The sleeve alone gives about 10 K/W. A conjugate check is J-T1.
- Bench (G5): G10 sleeve creep at 34 MPa / 100 °C for 100 h, and the collar thermocouple.
