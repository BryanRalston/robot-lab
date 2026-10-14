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

---
# Part 2: honeycomb crush cartridge (ID R2/R3, binding spec Arbiter R-049) — RL Materials, 2026-10-14
R-049 requires:
- 265 J absorbed at a plateau of **≤ 9.17 kN**;
- about 29 mm stroke plus margin;
- replaceable;
- **pair ≤ 0.100 kg** including backing.

The ID design on main is R3 (2af8650): 5052 3.1 pcf, 80 × 105 mm (84 cm²) × 44 mm, 6 mm EPP face, 0.5 mm Al spreader, PC backing, 0.1004 kg pair. The R2 brief (37 mm, 0.095 kg) is superseded by it.

## Cited honeycomb data (HexWeb CR III 5052, 1/8 in cell, typical, static, 0.625 in thick)
| pcf | stabilized compr. typ / min | **crush typ** | source |
|---|---|---|---|
| 3.1 | 300 / 215 psi = 2.07 / 1.48 MPa | **130 psi = 0.896 MPa** | HEX_CRIII |
| 4.5 | 570 / 405 psi = 3.93 / 2.79 MPa | **260 psi = 1.79 MPa** | HEX_CRIII |

Notes:
- Hexcel gives a typical value for crush strength but **no minimum**.
- Density tolerance is ±10 % (Plascore XR1).
- Plascore PAMG-XR1 publishes bare compressive and shear values only, no crush strength. The Gill PAA-CORE page (403 from the box) is reported to list 145 psi (1.00 MPa) for 3.1 pcf; that is not verified, so it isn't used.
- **Dynamic factor:** Hexcel says crush strength "increase[s] nonlinearly with impact velocity, … as much as 30 % higher" (HEX_ATTR). No rate curve is published. **The ID assumption of 1.10 is inside the 1.0–1.30 band, but it isn't conservative for peak force.**
- **0.85 MPa flag:** the 3.1 pcf static typical value of 0.896 is above 0.85, so the pad doesn't grow on that count. But with no published minimum, the typical value could sit lower in the minimum direction.
- **Pre-crush is mandatory.** Stabilized strength is 2.3× crush at 3.1 pcf and 2.2× at 4.5 pcf. Without pre-crushing, the initial peak would be about 17–19 kN.

## Check of ID R3 (84 cm² × 44 mm, 3.1 pcf, stroke 0.72 t = 31.7 mm [ID assumption; Hexcel gives no stroke efficiency])
| rate factor | plateau MPa | force kN | ≤ 9.17? | energy at 31.7 mm | ≥ 265 J? |
|---|---|---|---|---|---|
| 1.00 | 0.896 | 7.53 | yes | 239 J | **no** |
| 1.10 (ID) | 0.986 | 8.28 | yes | 262 J | **no (−3 J)** |
| 1.30 (Hexcel max) | 1.165 | **9.79** | **no (587 N·m)** | 310 J | yes |

**R3 has no design window.** It passes on force only at low rate factors and on energy only at high ones. The ±10 % density tolerance makes this worse.
- Any honeycomb sized against R-049 has to satisfy F(×1.30) ≤ 9.17 kN **and** E(×1.00) ≥ 265 J.
- That means stroke ≥ 265 / (9.17 / 1.30) = **37.6 mm**, so thickness ≈ 37.6 / 0.72 = **52 mm** [EST], plus a 5 mm margin → **≈ 57 mm**.
- Measuring the rate factor on the drop tower (for example 1.15 ± 0.05) would narrow the band and shorten the core to about 45 mm.

## EPP face in series
- The EPP and the honeycomb carry the same force. The EPP compresses until its stress reaches the honeycomb crush stress, then the core crushes.
- 3.1 pcf core (1.0–1.17 MPa): EPP 80 reaches that at about 55–62 % strain (ARPRO 5170 curve × rate). A 6 mm face takes about 3.5 mm and ≈ 7 J [EST], with no force spike above the plateau.
- 4.5 pcf core (2.33 MPa dynamic): EPP 80 would densify (> 75 %) before the core starts, so the face bottoms out. That's fine for force, because it acts as a stiff spacer, but the face adds no energy.
- **Don't count EPP energy toward the 265 J.** It only adds margin.

## Sizing to R-049 (both satisfy F ≤ 9.17 kN at ×1.30 and E ≥ 265 J at ×1.00)
| option | core area | core t | core g/side | EPP 6 mm, spreader, PC, sleeve, inserts [EST, scaled from ID R3 by area] | **pair kg [EST]** |
|---|---|---|---|---|---|
| 3.1 pcf | 78.7 cm² (≈ 75 × 105) | 57 mm | 22.4 | 30 | **≈ 0.105: over the cap** |
| **4.5 pcf** | **39.4 cm² (≈ 63 × 63)** | **57 mm** | **16.2** | **≈ 18** | **≈ 0.068 (−32 g margin)** |

- **Recommendation: 5052 4.5 pcf 1/8 in, pre-crushed, ≈ 63 × 63 × 57 mm core** in a replaceable cartridge.
  - Plateau 7.05 kN at ×1.0 to 9.17 kN at ×1.30. Energy ≥ 265 J at 37.6 mm stroke.
  - Pair ≈ 0.068 kg [EST]. It's single-use: swap the cartridge after any hit that crushes the core.
- Trade-offs:
  - The smaller face reduces contact coverage against the ±15 mm contact scatter (ID R3 needed 80 × 105). A stiffer spreader (1 mm Al, about +4 g/side) can spread the load over a larger face, but crush strength drops with off-axis load (HEX_ATTR), so the cartridge needs side guides.
  - The 57 mm core plus face, backing and air gap is about 75 mm proud of the shoulder. **Arms/ID envelope check needed.**
- Fallback if Arms can't take 75 mm: keep R3 geometry, measure the rate factor in a drop test, and re-rule.

## Asks
- **Arbiter:** R3 fails R-049 across the cited rate band (9.79 kN at ×1.30 / 239 J at ×1.0). Book 4.5 pcf as the candidate at ≈ 0.068 kg pair [EST]. Pad is single-use per hit.
- **ID:** resize to 4.5 pcf ≈ 63 × 63 × 57 mm with pre-crush, side guides, and an Al spreader. Give the itemised mass.
- **Arms (shoulder):** envelope for about 75 mm lateral build-up at the shoulder roll face, mounting through existing bulkhead holes, and arm-tuck clearance.
- **Controls (T-030):** model a constant 7.05–9.17 kN plateau (rate band), stroke ≤ 41 mm (0.72 × 57), and confirm the contact-point scatter against a 63 mm face.
- **Test (G5):** drop tower at 3–4 m/s on 4.5 pcf pre-crushed cores to measure the rate factor and stroke efficiency.

---
# Part 3: follow-ups for Controls (T-030) and Arms (shoulder-cap mount), 2026-10-14

## A1. Crush strength vs off-axis load angle (Controls)
- **Hexcel** (HEX_ATTR): "crush strength … decreases with increasing angle loading from the thickness". The brochure has no curve.
- **Al honeycomb, wedge tests** (HC_ANGLE_PMC, quasi-static): normalised out-of-plane plateau **0.98 at 0°, 0.93 at 15°, 0.73 at 25°**. The peak falls from 1.80 to 1.04 MPa at 15° on non-pre-crushed specimens. The plateau stays flat at 15° and degrades beyond it.
- **5052-H38 dynamic, 15° inclined** (HONG2008, Int J Plasticity 2008): normal crush strength rises with impact velocity and shear strength stays about constant. The normalised trend is similar for 0°, 30° and 90° in-plane orientation. The tabulated values are paywalled and not extracted.
- Combined compression-shear (scientific.net KEM.626.127 abstract): the normal plateau falls more steeply at 30–45°. No numbers were taken from it.
- **Angle limit recommendation: ≤ 15° (plateau ≥ 0.93).** Energy at 25° is about 0.73× the 0° value. Controls should keep the shoulder impact vector within 15° of the core axis, or the core has to be resized by 1/0.73.

## A2. Pre-crush spike and the rate/scatter basis (Controls)
- **Spike:** Hexcel says the core "is often precrushed slightly to remove the compressive peak". Stabilized strength is 2.2× crush at 4.5 pcf, so an un-pre-crushed core would spike to about 2.2× plateau. **A pre-crushed core has no initial spike.** Specify a pre-crush of about 2–3 mm [EST] and check each lot on a quasi-static press (no peak above the plateau).
- **Basis correction (supersedes Part 2 sizing):**
  - The Hexcel crush values are **typical**, with no published minimum.
  - Hexcel states that "for all other [densities ≥ 3 pcf], crush strength values [vary] by ±15 %" (HEX_ATTR).
  - The dynamic factor is "as much as 30 % higher" than the typical static value.
- **The 7.05–9.17 kN band in Part 2 is not enough.** At 4.5 pcf the full band is 1.79 × 0.85 × 1.0 = **1.52 MPa** to 1.79 × 1.15 × 1.30 = **2.68 MPa**, a ratio of 1.76. At 39.4 cm² that is **6.0–10.6 kN**, which fails ≤ 9.17.
- Resize options [EST]:
  | basis | σ band MPa | area for 9.17 kN | stroke for 265 J | core (0.72 t) | core g/side |
  |---|---|---|---|---|---|
  | datasheet only (±15 %, ×1.0–1.30) | 1.52–2.68 | 34.2 cm² | 51 mm | **71 mm** | 17.5 |
  | **lot crush test ±5 % + drop test rate 1.10–1.30** | 1.87–2.47 [EST] | 37.1 cm² | 38 mm | **53 mm** | 14.2 |
- **Recommendation:** buy 4.5 pcf pre-crushed with lot acceptance testing (sample crush within ±5 % of target), and measure the rate factor on the G5 drop tower. Then the core is about 61 × 61 × 53–58 mm. Without lot testing it needs **71 mm**, and the pad comes out about 90 mm proud (Arms envelope).
- **Controls should model a band, not a single value:** 6.95–9.17 kN (lot-tested case) with stroke ≤ 38–42 mm.

## B1. Mount on the shoulder-cap shell (Arms)
- **The cap shell material in the repo** is a placeholder (V5_COVER_SET "shoulder caps as placeholders"). The cover-set default is thermoformed PC 1.5 mm (P-020, R-027).
- **Inserts in that shell will not work.** The PEM IUTB-M4 brass insert in PC has **1 710 N pull-out and 5.9 N·m torque-out**, but needs a **≥ 8.91 mm deep hole** (PEM_IUTB). A 1.5 mm shell can't host it without a ≥ 9 mm boss.
- **Load path:**
  - The crush force (≤ 9.17 kN) is **compressive, toward the roll housing**.
  - On the 80 × 100 mm spreader, the bearing pressure on PC is 9 170 / 8 000 = 1.15 MPa. That's fine only if the shell is **backed solid** by structure.
  - Unbacked, a 1.5 mm PC shell spanning to the housing will not carry 9 kN in bending. That would need FEA, and I expect a fail [EST].
  - Tangential load at the 15° angle limit is 9.17 × tan 15° = **2.46 kN** shear. PC inserts can't carry it.
- **Recommendation: local 7075 doubler/bracket (cradle) between the cartridge and the roll housing**, carrying compression and shear straight to metal.
  - 4 × M4 into the bracket gives about 615 N shear per screw at 15°. Easy for steel M4 [EST: bolt grade capacity not cited].
  - The PC cap shell becomes cosmetic, with a cut-out for the cartridge face.
  - Retention against rebound and the strap is light. PEM IUTB-M4 in a PC boss (1 710 N cited) is acceptable for retention only.
  - Doubler mass [EST]: 2 mm 7075 cradle about 80 × 100 plus flanges ≈ 50 cm³?? Too heavy. Use a **1.5 mm 7075 ring frame with 4 legs to the housing, about 12–15 g/side [EST]**, sized by Arms FEA.
  - Mass is about +25–30 g per pair on top of the cartridge, so the ≤ 0.100 kg pair cap will be tight. The Arbiter must rule on whether the mount bracket counts inside the pad cap.
