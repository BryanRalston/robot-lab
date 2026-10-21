# P-161 crown liner: materials check (Materials, 2026-10-21)
Inputs: design/HEAD_IMPACT_LINER.md (P-161, 8e0c0d6). LD29 25 mm, crown cap Ø110 mm (A = 95 cm²), E = 20.9 J, head mass 1.104 kg, shell XC110 1.5 mm / 2.0 mm local.

## 1. Foam energy (flat-contact model)
- LD29 CLD: 61 / 126 kPa at 25 / 50 % (PLZ_LD29, ISO 7214).
- At 70 % (densification onset for PE foam, ZHANG_PE): 250 kPa [EST, extrapolated]. Zotefoams publishes no data above 50 %.
- QS energy density (trapezoid): to 50 % = 31 kJ/m³; to 70 % = 69 kJ/m³ [EST].
- Rate factor ×1.7 (PE foam, intermediate-rate 0.17 vs QS 0.10 MJ/m³, ZHANG_PE) [EST for LD29 at 4–5 m/s].

| case, 25 mm × 95 cm² | absorbed | vs 20.9 J | peak F | peak p | peak g (1.104 kg) |
|---|---|---|---|---|---|
| QS to 70 % | 16.3 J | **FAIL (0.78)** | 2.4 kN | 0.25 MPa | 218 |
| dynamic ×1.7 to 70 % | 27.7 J | pass 1.33 | 4.0 kN [EST] | 0.43 MPa | 366 [EST] |
| ID basis (126 kPa flat, 70 %) | 21 J | — | 1.2 kN | 0.13 MPa | 110 |

- ID's 110 g figure assumes a flat 126 kPa plateau. That is unconservative: LD29 stiffens beyond 50 %. The real peak is **2.4–4.0 kN, 220–370 g [EST]**, which is above any likely ÷1.5 electronics rating. A domed contact (area rising with stroke) would change this; a drop test is needed.

## 2. Minimum thickness
| rule | t min | Δmass vs 25 mm |
|---|---|---|
| QS to 70 % (no rate credit) | **32 mm** | +2 g foam + ~3 g shell growth [EST] → **+0.005 kg** |
| dynamic, strain capped at 50 % (keeps peak ≤ 2.0 kN, 188 g) | 42 mm | +5 g foam + ~7 g shell [EST] → +0.012 kg |
| alternative: keep 25 mm, grow the cap to Ø125 (123 cm²) | QS 21.1 J, bare pass | +2 g [EST] |

## 3. Shell laminate (XC110 210 gsm twill: σ_flex 777, σ_t 521, σ_c 483, E_flex 46.7 GPa, ILSS 64.7 MPa, Tg onset 121 °C, service 115 °C; XC110_TDS)
- Distributed load (foam outboard of the shell), q = 0.43 MPa over a clamped plate, a = 55 mm, t = 2.0 mm: σ = 3qa²/4t² = **244 MPa** against 777/1.5 = 518. PASS (SF 2.1).
- Shell outboard, 10 mm floor-edge indentor:
  - At 1.2 kN (ID): punch shear 19 MPa against ILSS 64.7 [EST proxy]. Pass.
  - At 4.0 kN: 64 MPa, **SF 1.0, FAIL**.
  - Point-load bending (clamped, r0 = 5 mm) is about 1500 MPa: **FAIL**.
- **So the foam must be outboard of the shell, with a thin skin**, or the 2.0 mm local shell must go to 3.0 mm+ (+~10 g [EST]). ID to state the stack order.

## 4. Bondline / thermal
- Limits: LD29 95 °C (5 % shrink), XC110 115 °C, EA 9396 Tg 112 °C post-cured (64 °C RT cure).
- EA 9396 does not bond untreated PE. Use a PE-rated contact adhesive or corona/flame treatment [EST]. No cited adhesive yet: OPEN.
- The head internal temperature is not in the doc. Thermal to confirm the crown is ≤ 60 °C (a 35 K margin on LD29). Until then: **pass conditional**.

## Verdict
**25 mm FAILS quasi-static (16.3 J < 20.9 J) and peak g is ~2–3× ID's 110 g.**
- Recommend **32 mm LD29 on the Ø110 cap (+0.005 kg [EST])**, or Ø125 at 25 mm.
- Foam outboard of the shell.
- Drop-test one coupon at 4.9 m/s, 1.104 kg, to fix the rate factor and peak g.

Sources:
- PLZ_LD29: https://www.zotefoams.com/wp-content/uploads/2025/03/PIS-A008-Plastazote-LD29.pdf
- ZHANG_PE: https://pmc.ncbi.nlm.nih.gov/articles/PMC8269678/
- XC110_TDS: https://media.easycomposites.co.uk/datasheets/EC-TDS-XC110-Out-of-Autoclave-Component-Prepreg.pdf
- EA9396: MATERIALS_DB
