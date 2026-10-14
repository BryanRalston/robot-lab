# A37 rev B: hip_pitch motor-to-collar thermal break (RL Materials, 2026-10-14)
**Rev B replaces rev A** (G10, f7d4230). RL Thermal (6cf74d2) requires a total thermal resistance R_break ≥ 20 K/W, counting every path in parallel. Rev A's full-face washers sat in parallel with the pin path, which gave about 4.6 K/W, so **rev A is withdrawn**. Data is in `MATERIALS_DB.md` (PEI1000). [EST] marks an estimate. Numbering clash: R-030 calls this P-027, but P-027 is already the Arms wrist item. The Arbiter should renumber.

## Basis
- Loads: 4 542 N per body when walking (clamp_review.py), 6 550 N per body at fault/proof (BOND_SPEC §5).
- Case temperature: checked at 98 °C, the worst case.
- Geometry: Ø12 pin through 2 tines, 8 mm each.
- **The axial load on the eye is unknown (Legs L4).**

## PEI Ultem 1000 (ULTEM_PP, ULTEM_PL)
- Compressive strength 152 MPa (10 % deformation), compressive modulus 3.31 GPa, shear strength 103 MPa.
- Thermal: k 0.12 W/m·K, CTE 56 µm/m·K, Tg 215 °C.
- Creep: SABIC publishes only tensile creep curves, up to 120 h, at 80 °C/41 MPa and 121 °C/14–28 MPa. There is no compressive creep data at 98 °C.
- **Rule used:** sustained or cyclic stress ≤ 28 MPa (the highest level SABIC characterised at 121 °C); short fault stress ≤ 76 MPa (0.5 × 152 [EST]). Confirm both with a G5 creep test.

## Option A (recommended): PEI tine sleeve OD20/ID12 × 8 mm + 2 mm flange with 15 % contact lands
- **Pin bearing on the sleeve bore** (96 mm² per tine):
  - walking 23.7 MPa, within the 28 MPa creep rule;
  - fault 34.1 MPa, **SF 2.2 hot** (4.5 at room temperature).
- **4 mm wall:** bearing on the 7075 at OD20 is 20.5 MPa. OK.
- **CTE:** PEI grows about 48 µm more than the 7075 bore on diameter from 25 to 98 °C. Use a line-to-line/slip fit with a DP490 film; no press fit.
- **Lands** (15 % of the OD20/ID12 face = 30 mm² per face):
  - capacity: 0.84 kN sustained, 2.3 kN fault;
  - if the axial load is ≤ 10 % of radial, SF is 1.9 sustained / 3.5 fault. **This depends on L4.**
  - Use 3 × 120° pads, a ≥ 0.3 mm air gap elsewhere, and a ±0.05 mm land tolerance.
  - PEI sliding on the steel inner-ring face has no wear data; bench-test it in G5.
- **Mass for 8 sleeves:**
  - PEI +20.9 g;
  - bore growing from 12 to 20 mm removes 7075, −36.2 g;
  - tines widened +8 mm, +34.5 g [EST];
  - rev A washers dropped, −2 g;
  - **net ≈ +17 g [EST].**

## Option B (not recommended): insulated bearing outer ring, PEI 22/26 × 7 mm
- Bearing on one sleeve (154 mm²) is 29.5 MPa walking, **above the 28 MPa creep rule**, and 42.5 MPa at fault (SF 1.8).
- The 2 mm polymer seat would let the spherical plain bearing's outer ring ovalise, so SKF liner-life data no longer applies.
- Thermal resistance ≈ 19 K/W, which misses 20.
- **Ceramic coating:** 0.2–0.3 mm gives < 1 K/W. Rejected.
- Mass ≈ +21 g [EST].

## Lever-cheek bolts (if bolted, L1): ≥ 60 K/W each
- A PEI washer in the preload path would see 10.4 kN on 81 mm² = 128 MPa. It would creep and lose preload. **Not allowed.**
- **Fix:** a Ti-6Al-4V compression limiter OD8.5/ID6.4 carries the preload (433 MPa vs 910 MPa yield, SF 2.1).
  - Each mm of length adds 6.1 K/W, so it needs L ≥ 10 mm.
  - PEI is used only as an unloaded spacer beside it, with a ≥ 0.3 mm air gap at the faces.
  - ≈ +1 g per bolt [EST].

## Recommendation
**Option A.**
- Margins: SF 2.2 on pin bearing at fault/98 °C; walking stress within the creep rule; land SF 1.9/3.5 subject to L4.
- Mass ≈ +17 g for both legs, plus ≈ 1 g per cheek bolt [EST].
- Gates: Legs FEA of the Ø20 tine; G5 PEI compressive creep at 25 MPa/100 °C for 100 h; land wear; J-T1.

## Asks for Legs (A38)
- **L1:** Are the cheeks bolted to the collar? Bolt count and size?
- **L2:** Recheck the Ø20 tine bore: edge distance, the +8 mm tine clearance over the full hip ROM, and FEA at 6.55 kN per body.
- **L3:** Pin retention with the flanged sleeve, and flange clearance to the GE 12 E inner ring.
- **L4:** Axial load on the eye at walking and at fault.
