# R-042 shoulder pad: EPP 80 check (RL Materials, 2026-10-14)
Input: `design/SHOULDER_PAD.md` (40 mm EPP 80, 109 cm², s = 31 mm, constant 0.65 MPa → 7.10 kN → 426 N·m, 220 J). Sources are in `MATERIALS_DB.md` (EPP80 row). [EST] = my derivation from those sources.

## 1. Crush curve and densification
ARPRO 5170 (80 g/L), ISO 844 at 5 mm/min: **0.50 MPa at 25 %, 0.70 at 50 %, 1.60 at 75 %** (ARPRO5170, matching ARPRO_GEN).
- **The curve is not a plateau:** stress rises ×2.3 from 50 to 75 %. Interpolated, stress at 60 % is ≈ 1.06 MPa [EST].
- No source states the densification strain. The steep rise past 50–60 % implies onset at roughly 60–70 % [EST]. **78 % is in densification, not on the plateau.**
- The 0.65 MPa figure only fits the 25–50 % band.

## 2. Multi-hit and strain rate
- **Rate:** collapse stress rises **+45 to +57 % at 100 s⁻¹ vs 10⁻³ s⁻¹** (EPP_RATE_T, measured on 30 g/L foam). At 3–4 m/s over 40 mm the rate is ≈ 75–100 s⁻¹, so the factor is **≈ 1.45–1.57**. Denser EPP is less rate-sensitive (a 60 g/L SHPB study cited in EPP_PMC refs), so 80 g/L likely sits at or below this range [EST]. The fixture test needs to measure it.
- **Multi-hit:** the only cited figure is compression set of **11 % after 25 % strain for 22 h** (ARPRO5170). EPP_PMC says the curve is "maintained after repeated impacts" at quasi-static speeds, but gives no number. **No source gives plateau loss after 10 or 100 hits at 220 J or at about 75 % strain. UNKNOWN: needs a drop-tower test** (10 and 100 drops, measuring peak force and thickness recovery). Until that test exists, treat the pad as single-use after any hit above 50 % strain.

## 3. M4 inserts moulded into EPP 80
No source gives a pull-out value, and EPP's tensile strength at 80 g/L wasn't retrieved. **Use the PC backing plate (+8 g/side):** a bonded or co-moulded plate with the inserts in the plate, so the bolts never load the foam in tension.
- The R-042 cap breaks: 0.050 + 0.008 = **0.058/side, 0.116 pair** vs the 0.10 cap.

## 4. Temperature
- Measured on 30 g/L EPP (EPP_RATE_T): collapse stress is **≈ +110 % at −30 °C and ≈ −50 % at 60 °C** vs room temperature. EPP_PMC confirms strength drops as temperature rises.
- 0 °C and 40 °C are not tabulated. Linear interpolation gives roughly **+50 % at 0 °C and −25 to −35 % at 40 °C** [EST]. The 0 °C pad gives a higher peak force; the 40 °C pad absorbs less energy at the same strain.
- **Bulkhead at 69 °C:** this is above the highest temperature tested (60 °C, where the loss is already −50 %). No source gives the EPP maximum service temperature. **Not OK in direct contact.** Use a ≥ 5 mm air gap or an insulating standoff (the PC backing plate helps), and get the pad-face temperature from Thermal (≤ 40 °C wanted).

## Energy and force check (the main finding)
Quasi-static energy density from ARPRO 5170, trapezoid integration [EST]:
- 0–25 %: 0.0625 J/cm³
- 25–50 %: 0.150 J/cm³
- 50–75 %: 0.2875 J/cm³
- Total to 75 % ≈ **0.50 J/cm³**. Pad volume is 109 × 4 = 436 cm³.

Results:
- **To 75 %: 218 J. To 77.5 % (s = 31 mm): ≈ 237 J.** So yes, the pad does absorb 220 J. The energy number in SHOULDER_PAD.md is right.
- **The force is not 7.10 kN.** At 75 % the stress is 1.60 MPa × 109 cm² = **17.4 kN** quasi-static.
- With rate ×1.45, 220 J is reached near 65 % strain at a peak of about 1.24 × 1.45 ≈ 1.8 MPa → **≈ 19.5 kN [EST], bearing moment ≈ 1.17 kN·m vs the 550 N·m allowable (SF ≈ 0.47).** This fails.
- **The constant-force model overstates foam efficiency.** For an EPP curve of this shape, energy ÷ peak force ≈ 0.28–0.31 × thickness, not 0.78.

What would hold 7.10 kN at 220 J:
- Stroke at 7.10 kN must be 31 mm, so thickness ≈ 31 / 0.29 ≈ **100–110 mm** of EPP (any density, area resized). The rate factor cancels out of this.
- Or keep 40 mm and accept ≈ 19 kN, which needs the CRBH 7013 / bulkhead re-checked.
- Or cut shoulder energy to about 80 J (Controls).
- Or use a crush element with a flatter curve (aluminium honeycomb or a crush tube), sized by Materials and ID in R2.

## Asks
- **ID:** re-size the pad with the real curve. This does not support R-042's −22.6 % claim. Add the PC backing plate.
- **Controls (T-030):** use the ARPRO 5170 curve × 1.45 rate factor, not a constant 0.65 MPa.
- **Thermal:** pad-face temperature next to the 69 °C bulkhead.
- **Test (G5):** drop-tower on EPP 80, 40 mm: peak force, multi-hit recovery (10 and 100 drops), and 0 / 40 °C.
