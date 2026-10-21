# Mg actuator housings (Elektron 43): allowables and galvanic plan (R-131 §3)
RL Materials, 2026-10-21. Basis: actuators/results/R127_MG_HOUSINGS.md (hip yaw, hip roll, ankle, hip-pitch bodies; knee housing excluded). [EST] = estimate.

## 1. Allowables
**Source:** Luxfer MEL DS-490 "Elektron 43 Extruded Products", https://www.luxfermeltechnologies.com/wp-content/uploads/2026/05/DS-490-Elektron-43-0526.pdf. UNS M18434 / ASTM WE43C; specs AMS 4485 (extrusion) and ASTM B107. The datasheet states that MMPDS-08 holds A/B-basis values for extrusion and plate. MIL-HDBK-5H has **no** WE43/Elektron 43 (Mg alloys covered: AZ31B, AZ61A, ZK60A, ZE41A, etc.).

| property | value | basis | note |
|---|---|---|---|
| Fty, L, extruded T5 | **195 MPa** (28.2 ksi) | **A-basis** (spec min, per DS-490) | extrusion, longitudinal only |
| Ftu, L, extruded T5 | **303 MPa** (43.9 ksi) | A-basis | |
| elongation, L | 6 % (A min); typical 11.5 % | | |
| typical, bar L | 243 / 352 MPa | typical | |
| typical, bar **transverse** | **183** / 305 MPa, 11.3 % | typical | T yield below L A-basis |
| E / ν / ρ | 44.1 GPa / 0.3 / 1.83 g/cc | typical | |
| fatigue | 195 MPa max at R 0.1, 5×10⁷ (ASTM E466) | typical | |
| Fbry | **not published** in DS-490; not in 5H | — | MMPDS-08 table not accessed |
| AMS 4371 | not verified as an Elektron 43 spec (DS-490 lists AMS 4485) | — | |

**R-125(b) limits:**
- **Single-path, L-dominated stress in extruded bar: 195/1.5 = 130 MPa.** This matches R-131.
- **Transverse / multi-axial (housing walls usually are):** there is no published T A-basis. [EST] scale: 195 × 183/243 = 147 MPa → **98 MPa**. Use 98 for any wall whose principal stress is not along the extrusion axis, until the MMPDS-08 table is in hand.
- **Plate:** DS-490 claims MMPDS-08 plate values but gives no numbers, so plate is **unverified**. Specify **extruded bar (AMS 4485) with the bar axis on the housing axis**, or obtain the MMPDS-08 plate table first.
- **Bearing (inserts carry the bearings, so Mg bearing is only under washers/inserts) [EST]:** 1.2 × Fty = 234 MPa → 156 single-path. Verify before use.
- Compressive yield asymmetry: Luxfer says Elektron 43 has reduced, but not zero, asymmetry. Check compression-dominated seats at the T value.

## 2. Galvanic plan (ranked by severity: worst couple first)
Mg is the most anodic structural metal. Coatings alone are not enough; the parts must be **isolated + sealed** (MIL-STD-171 §4.6–4.7.1, https://metalfinishesandfinishingprocessesa.emilspec.com/MIL-STD-171/page16.html).

| rank | couple | rule | ref |
|---|---|---|---|
| 1 | Mg – steel bearings (outer ring) | Never in Mg. Bearings sit in **7075-T7351 (or 6061) seat rings** bonded and doweled into the Mg (R127 §4); seat ring wet-assembled with epoxy primer / sealant | MIL-STD-171 4.7.1 |
| 2 | Mg – Ti fasteners/parts | **Prohibited** (large potential gap, small Mg anode). Ti screws stay off Mg (R-123 Ti list re-routed) | MIL-STD-171 4.7 (≤ 0.25 V couples) |
| 3 | Mg – steel fasteners (12.9) | **Zn-Ni** (or tin/Geomet [EST]) plated steel, **5052-Al washer** under head with ⅛–¼ in overlap, **wet-installed in MIL-PRF-81733** on fastener and hole; thread into **Al thread inserts** (Keensert-type), not Mg threads. Cd plating per older guidance is not used (restricted). Tin plating alone is not relied on. | MIL-STD-171 4.6; Tagnite note https://www.tagnite.com/tagnite-coating/galvanic-corrosion/ |
| 4 | Mg – 7075 inserts/rings | Mildest structural couple. Both parts coated (Mg PEO/anodic + epoxy primer, Al conversion/anodize), faying surfaces sealed (MIL-PRF-81733 or AMS-S-8802), bondline DP490/EA 9396 as isolation | MIL-STD-171 4.7.1 |
| 5 | Mg – Al 5052/6061 washers, 5056/6061 Al screws | Acceptable with sealant; preferred for non-structural Mg–Mg/cover joints | mypdh Mg lesson (Al fasteners list) [secondary] |

**Mg surface system (in order of effectiveness, MIL-STD-889C via Abbott Aerospace, https://www.abbottaerospace.com/aa-sb-001/4-materials/4-4-corrosion/4-4-5-galvanic-corrosion/):**
1. **Anodic coating** (ASTM D1732 class: Tagnite / Keronite-type PEO, 10–20 µm), then an alkali-resistant epoxy primer (**MIL-PRF-23377** class, chromate-free) [primer spec cited by number].
2. Conversion coat (**SAE AMS-M-3171**) + primer is the fallback, e.g. for touch-up after machining.
3. **Bare Mg must not be used.** Re-treat machined faces before assembly; Tagnite coats threaded holes too (dielectric).
- AMS 2466 (Mg hard anodize) is cited by number only, not verified.

## 3. Mass impact [EST]
| item | per housing | robot (≈ 12 housings, R127 count) |
|---|---|---|
| PEO 15 µm + primer 25 µm on ~0.04 m² | ≈ 2–3 g | ≈ +0.03 kg |
| 5052 washers (≈ 0.5 g × 12) | ≈ 6 g | ≈ +0.07 kg |
| Al thread inserts vs tapped Mg (≈ 0.4 g × 12) | ≈ 5 g | ≈ +0.06 kg |
| Zn-Ni plating, sealant | ≈ 1 g | ≈ +0.01 kg |
| 7075 seat rings | already in R127 | 0 |
| **Total** | ≈ 14–15 g | **≈ +0.17 kg** against R127's −0.263 (stiffness-thickened) → **net ≈ −0.09 kg** |

Fastener and housing counts should be confirmed from Actuators' per-unit table. If the counts are lower, the adder scales down.

## 4. Inspection and qualification
- **G5:** salt-fog (ASTM B117, 500 h [EST]) and humidity coupons. Use Elektron 43 + PEO + primer with a wet-installed Zn-Ni screw, a 5052 washer and a bonded 7075 ring.
- **Service:** at each interval, check under washers, at counterbores and at seat-ring edges for white powdery corrosion product or lifted primer. Loose washers mean corrosion is likely under them (AC 43.13-1B 6-149, https://www.landseaskyspace.com/ac4313/p6-29.html).
- Fill counterbores with sealant where water can be trapped.
- No steel wire brushes or steel-contaminated abrasives on Mg (AC 43.13-1B 6-149b).
- Re-torque check: wet install changes torque-tension, and Mg creep at 120 °C is low for Elektron 43 (DS-490) but should be confirmed in the G5 bolt-load-retention coupon.
