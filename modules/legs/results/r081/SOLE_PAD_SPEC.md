# Foot sole pad + toe/heel bumpers (Arbiter R-081), RL Legs 2026-10-14
**Basis:**
- foot = closed 7075 box 240 × 100 × 18, 3.5 mm skins, 4 webs (model_v4 l.208, fea_r5);
- sole CoP window −60…+180 mm, ±50 mm (gait_lib / README);
- max GRF 1.31 BW, stairs (r4/requirements.md); robot about 65.8 kg (R-056 era rollup).

**Gap:** nothing is defined or booked today, so the ground contacts bare 7075.

## Part list (per foot)
| # | part | catalogue source | spec | size | mass/foot |
|---|---|---|---|---|---|
| 1 | **Sole pad, baseline** | Vibram **Gumlite** compound (Vibram tech data: density 0.55 ± 0.05 g/cm³, **47 ± 3 Shore A**, abrasion < 180 mm³, compression set < 25 %). Sheet/flat sole: Vibram Acquagum 6 mm Gumlite, SKU 35002690B (Sy & Fixa, 309 SEK/pair sale, 589 list) | 6 mm, die-cut flush to 240 × 100 | 240 × 100 × 6 | **0.079 kg** [computed: 144 cm³ × 0.55] |
| 1-alt | Sole pad, wear/grip alternative | **Vibram #7174-6M "Cherry" soling sheet**, SP compound, **64–70 Shore A**, 6 mm, 579 × 909 mm sheet, **$120** (greatpairstore.com). Gives about 20 soles per sheet | 6 mm | 240 × 100 × 6 | 0.173 kg [density 1.20 EST: Vibram rubber compounds list 1.11–1.20; SP not stated] |
| 2 | **Toe + heel bumpers** | McMaster **8716K27**, tear- and abrasion-resistant PU sheet, 60A, 1/4" (6.35 mm), 6 × 6 in (price not shown in search; look it up) | wrapped strip on the toe and heel end faces | 2 × (100 × 15 × 6.35) | **0.024 kg** [computed, PU density 1.24 from the MacLellan 70A PU datasheet, EST for 60A] |

**Baseline per foot = 0.103 kg; robot = 0.206 kg** (Gumlite + PU bumpers, computed). The SP alternative is 0.197 per foot, 0.394 robot.
- Lighter option: bumpers as 4 corner pads only, 30 × 15 × 6.35, at 0.014 per foot. Gives 0.093 per foot, **0.186 robot**.

## Bond / retention
- **Sole:** this is a wear part, so it must be replaceable. Use DP490 only on the bumpers, not the sole.
  - Vibram suggests neoprene contact cement for Gumlite ("Colle de Cologne"; Rehagol + Syntic for others, Vibram tech data).
  - Prep: abrade the anodized 7075 sole skin and apply a primer (Materials to name one).
  - Replacement: peel, solvent-clean, re-cement.
- **Bumpers:** DP490 to the abraded end faces, plus 2 × M3 countersunk per bumper into the end webs [new holes in our FEA'd foot box, end zones only. Legs to confirm in fea_r5 terms].
- Materials to confirm: the primer, DP490 on PU 60A, and the Gumlite neoprene-contact bond on anodized 7075.

## Effects
- **Height:** +6.0 mm on the foot sole. Ankle axis, hip and CoM all rise 6 mm, stand height +6 mm. Controls must update the sim foot (box 18 → 24 mm, contact on the pad).
- **CoP margin (EST):**
  - Footprint unchanged (flush cut).
  - Compliance at 47A: E ≈ 2.2 MPa (Gent conversion). Flat stance at 1.31 BW: 0.035 MPa → 0.1 mm.
  - Edge loading (10 mm strip): 0.85 MPa → strain 0.39, **2.3 mm compression**. That gives about 1° of tilt at the edge, and the effective CoP edge recedes a few mm (EST).
  - The 64–70A SP (E ≈ 4.8 MPa) halves this.
  - Controls must rerun the CoP-margin / WBC_GATE cases with a compliant contact. We already ride the sole edge at 1.0–1.2 m/s (L31/L33), so the firmer SP may be preferable despite the mass.
- **Grip:** a rubber sole replaces 7075 on the floor. Rubber-on-floor friction is not measured here; G5 should do a bench μ test (dry/wet tile, ≥ 0.8 target as an EST requirement).
- **Impact:** the 6 mm pad plus 6.35 mm PU bumpers take toe-stub and heel-strike energy off the 7075 box edges. Not quantified; T&R drop test T8.

## Recommendation
- Gumlite 6 mm sole plus PU 60A corner bumpers: **0.093 per foot, 0.186 robot (computed)**. This needs a new mass line (R-081) because nothing was booked.
- If Controls' CoP rerun shows the 47A pad costs edge margin, switch to SP 64–70A (+0.094 per foot).
