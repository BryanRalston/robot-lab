# Chest pad core re-spec: 11.2 kN weakest plateau (Materials, 2026-10-21)
Request: T&R 3eacd56 (TORSO_BC_P160_REVIEW §A). Envelope: 101 × 101 land (A = 0.0102 m²), 116 mm core, 81.2 mm usable (70 %), 73.8 mm with 10 % margin, 824 J.

**Need:** weakest corner (15°, QS) ≥ 11.2 kN → 0° QS min ≥ 11.2/0.93 = 12.04 kN → σ_crush,min ≥ **1.18 MPa**.

**Pick: HexWeb CR III 5/32-5052-3.8 (pre-crushed), row HC5052_3.8.**
- Crush 185 psi = **1.276 MPa typ** (HEX_CRIII Table I). Hexcel publishes no crush min. Lot band ±3 % (the repo T031 basis) [EST] → 1.238–1.314 MPa. Specify a crush cert of 1.24–1.31 MPa on the PO (RFQ via Robot Lab).
- Rate: up to ×1.30 dynamic (HEX_ATTR). ×0.93 at 15° (HC_ANGLE_PMC, as in T031).

| case | kN |
|---|---|
| QS 0°: min / nom / max | 12.6 / 13.0 / 13.4 |
| QS 15° weakest | **11.7** (≥ 11.2 PASS, 1.05×) |
| dynamic upper (max × 1.30) | 17.4 |
| upper/weakest ratio | 1.49 (≤ 1.60 T&R basis, so LC1 = 17.9 is conservative) |

- Energy at the weakest plateau over 73.8 mm = 864 J ≥ 824 J: **PASS**. Stroke used is 70.4 mm.
- Stroke efficiency is 70 % (same basis as T031 and the 81.2 mm in 3eacd56; HEX_ATTR crush method) [EST for the 3.8 pcf grade].
- Core mass: 0.0102 × 0.116 × 61 kg/m³ = **0.072 kg**, vs 0.085 kg at 4.5 pcf (**−13 g**). Faces and bond are unchanged.
- Alternatives: 3/8-5052-3.7 (180 psi, 1.24 MPa). At ±3 % its weakest corner is 11.3 kN, which is marginal. 1/4-3.4 (150 psi) fails at 9.4 kN.
- **Risk:** if the real lot spread is ±10 %, the weakest corner is 10.9 kN and FAILS. In that case, hold the ±3 % cert or grow the land to 104 × 104 mm.

Sources: HEX_CRIII https://www.hexcel.com/wp-content/uploads/2025/12/HexWeb_CRIII_DataSheet.pdf ; HEX_ATTR https://www.hexcel.com/wp-content/uploads/2026/01/HexWebHoneycombAttributesandProperties.pdf
