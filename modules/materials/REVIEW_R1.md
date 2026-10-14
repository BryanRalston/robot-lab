# RL Materials review R1 (2026-10-14)
Properties: `MATERIALS_DB.md`. Geometry and masses come from the repo (cited per item). [EST] = estimate. Mass deltas are per robot unless noted. Nothing here is booked; any changes go through PROPOSALS.md. Bryan clarified (2026-10-14) that 3D printing is allowed, so printed options are back in scope. That reopens R-027 §2.

## 1. P-020 covers: thermoformed PC 1.5 mm (R-027, trimmed by R-029)
- Basis: 0.643 m² × 1.5 mm × 1.20 = **1.157 kg of PC skin** (COVER_COST.md area). R-027 paper 1.567 includes EPP 0.36 [EST]. R-029 trimmed the set and added P-022..025.
- Risks:
  - Thermoforming thins the sheet at draws up to 3:1, so corners can end up well under 1.5 mm. Spec the minimum wall after forming, not the sheet gauge.
  - PC suffers solvent and stress-cracking from threadlockers and IPA-based cleaners. That matters at screw bosses: use PC-safe threadlocker or none.
  - Tg is 150 °C, so heat is not an issue near the motors.
  - Impact is good: notched Izod 140–440 J/m (MIF) and ductile. **Keep PC.**
- Options:
  - **(a) PC 1.2 mm on low-draw panels: −231 g** if applied across all 0.643 m² (0.3 mm × 0.643 m² × 1.20). It needs a dent check against EPP backing.
  - (b) PA12 MJF 1.5 mm, now allowed again: 0.643 × 1.5 × 1.01 = 0.974 kg, **−183 g** vs PC. PA12 is less tough than PC (not verified: MJF impact data not yet pulled), but it needs no mould tooling (COVER_COST first set ≈ $19.8k [EST]).
  - (c) CF fairings per R-029 where they are lighter.
- Recommendation: use PC on the large fall-exposed panels and PA12 MJF on small complex parts (skirt, knee caps, brain lid A31). That removes the moulds for those parts.

## 2. P-021 palm: machined 7075, 0.0924 kg/hand (A32 CAD)
- Risks:
  - **Galvanic: the CF backplate (arms R1 l.45) against 7075 is a severe couple.** Carbon is cathodic to Al, and 7075 sits at −750 mV calomel (MIF). Isolate with a glass-fibre ply or film adhesive plus sealed fasteners.
  - Fatigue at the R3 window corners: 7075 fatigue strength is 160 MPa (MIF). Corners are fine at hand loads but should be checked under grip loads (10 kg carry, arms_loads_r1).
  - Anodize everything except the bond faces.
- Options:
  - 6061-T6 (2.70): −3.6 g/hand, but 44% lower yield. Not worth it.
  - **PA12 MJF palm, printed (allowed now): ~0.033 kg/hand** (PA12 1.01 × CAD volume scaled 0.0924/2.81), **−119 g both hands**. Needs metal inserts at the knuckle bar and wrist plate. Strength check required.
  - A hybrid of a 7075 knuckle bar and wrist plate with a PA12 skin [EST] gives about −80 g both hands.

## 3. Ti-6Al-4V ankle cross (model_v4 l.194: 30×46×30 box; structure_mass.md 0.120 kg/leg)
- Risks:
  - **Galvanic, Ti against 7075 clevis tines** (D60/D63). Ti is noble to Al, so the Al corrodes at the pin bores and contact faces. Specify anodize plus sealant or PTFE washers (already PTFE washers at top clevis, good), and use wet-assembled pins.
  - Fretting/galling of Ti at the pins: Ti galls on itself and on steel, so hard-coat or bush the bores.
  - Mass check: a solid 30×46×30 envelope is 41.4 cm³ × 4.43 = 183 g, against 120 g booked. That implies about 35% pocketing, which is unverified in CAD.
- Options:
  - 7075-T6 at the same volume: 120 × 2.81/4.43 = 76 g, **−44 g/leg, −88 g total**. But fatigue drops from 530–630 to 160 MPa (MIF) and E from 110 to 70 GPa. It only works if the cross FEA stress is below ~80 MPa (SF 2 on 160). **Needs Legs FEA (none exists for the cross).**
  - Steel 4140 Q&T: heavier (+91 g/leg). No.
- Recommendation: keep Ti until the cross is in FEA. Add a galvanic isolation spec now.

## 4. Femur tubes (7075 ø50×1.2, model_v4 l.148) and DP490 bondline (BOND_SPEC.md)
- Tube: 184 mm² × ~298 mm (length from structure_mass 0.204 kg at 1.6 wall) × 2.81 = **145 g/leg**.
- Risks:
  - 7075-T6 tube is SCC-prone in T6 and is under sustained clamp hoop stress (62.5 MPa, structure_r5).
  - Dent sensitivity at 1.2 mm (GB FEA flagged tube dent; A15).
  - **Bond: one-screw fault SF 0.86 at 82 °C** (BOND_SPEC). Above 80 °C the bond falls off sharply (2.8–3.2 MPa at 120 °C, DP490_B). Bond fatigue and creep data are missing.
  - The pins carry the hot fault, and the bond must stay ≤ 60 °C.
  - Grit-blast-only prep on 7075 is weaker in durability (humidity) than a sol-gel or phosphoric-acid anodize. Add a sol-gel primer (e.g. 3M AC-130 class, not verified) for long-term humidity.
- Options:
  - **7050-T7451 tube/collars: 0 g**. Same ρ/E/yield, fatigue 200 vs 160 MPa, overaged for SCC and toughness (MIF). This is the best near-free upgrade, if 7050 tube stock exists in ø50 (open question).
  - CF tube (ρ 1.55, same section): 51.7 cm³ × 1.55 = 80 g, **−65 g/leg, −130 g total** [EST]. Laminate stiffness/strength are not verified, the Al collars bonded to CF are a galvanic couple, and buckling/dent behaviour changes. Not recommended without test data.
  - Thermal: put the 60 °C bondline limit into the G5 bench plan explicitly (thermocouple at the collar).

## 5. GE 12 C / QA1 MGF12T PTFE liners
- GE 12 C: C 11.4 kN, C0 28.5 kN, steel/PTFE sintered bronze (SKF_GE12C). The screw loads are 2.2–4.3 kN/screw (actuators D5), so the load ratio is fine.
- Risks:
  - PTFE cold-flows: bulk HDT is 66–70 °C and CTE 110–120 µm/m·K (MIF bulk values; the liner composite is better but not quantified). Liner wear sets the 5 250 h / 4 250 h replacement intervals.
  - **The QA1 MGF12T has no dynamic rating (A22 open).** It is the weakest-documented load-path part in the leg.
  - The rod end is open to grit at the ankle. The boot (P-025) helps; specify a sealed variant if available.
  - Galvanic: the steel/bronze bearing sits in a 7075 eye. Anodize the eye bore and use a sealant fit.
- Options: no mass lever (bearings are catalog parts). Action: replace the QA1 with a rated part (SKF/Hirschmann high-misalignment, ≥ 27°) or bench test it.

## Top findings (mass delta)
1. Palm: CF backplate on 7075 is a galvanic couple. Isolate it (0 g). A printed PA12 palm option gives −119 g.
2. Covers: printed PA12 on small parts and PC 1.2 mm on low-draw panels gives up to −183 to −231 g. Spec the post-form minimum wall.
3. Femur: 7050-T7451 in place of 7075-T6 gives better fatigue and SCC at 0 g. The bond is hot-fault limited, so add the ≤ 60 °C bench measurement and a sol-gel prep.
4. Ti ankle cross: needs Ti/Al isolation and anti-galling. 7075 would give −88 g but only after FEA. The booked 120 g implies about 35% pocketing that is not shown in CAD.
5. QA1 rod end: still unrated. Choose a rated part. 0 g.

## Open questions
- Is 7050-T7451 (or 7075-T73) available as a ø50×1.2 tube? Otherwise use T73 temper for SCC.
- Legs: is there an ankle cross FEA or CAD with pockets?
- ID: does the itemized trimmed cover JSON (R-029) change the 0.643 m² area?
- MJF PA12 impact/fatigue datasheet and CFRP laminate properties are to be pulled in R2. ASM MatWeb timed out this round.
- EPP grade, PU 90A, silicone and TPU fabric have no datasheets in the repo.
