# Tendon sheath rev B (RL Materials, 2026-10-14). Inputs: Arms 550ab88, Actuators D78
Inputs:
- 6 flexors at ≈ 0.20 m, thumb at 0.21 m, 11 tendons per hand.
- Tightest bend R 37.6 mm, ≥ 10 mm slack.
- Tendon: LIROS D-Pro 1 mm.
- **Stall 775 N ideal / 503 N at η 0.65 must not fail.** Working load ≈ 30 N tendon side (I²t, 0.84 A); compression and lost motion matter at the working load.
[EST] = estimate; everything else cited.

## Tendon (cited: liros.com D-Pro 1 mm, p3511)
- Breaking strength **195 daN = 1 913 N**. Dyneema SK78, 12-plait, heat-set, **working stretch < 1 %**, 0.9 g/m (hamburgertauwerk).
- **SF at 775 N = 2.47; at 503 N = 3.80.** Before freeze, derate for the 37.6 mm bend and the splice or termination [EST: typically 0.7–0.9 for splices, not cited], so SF at 775 N ≈ 1.7–2.2.
- Stretch: < 1 % at working load (LIROS). At 775 N (40 % of break) take ≈ 1 % [EST] → **≈ 2 mm over 0.2 m**. At 30 N it's negligible (< 0.1 mm [EST]).

## Plain PTFE: OUT
- PTFE tube 1.3/2.5 (3.58 mm², E 0.4–1.3 GPa, MIF) at 503 N gives 11–35 % axial strain. It crushes or buckles.
- Even at 30 N it's 0.6–2.1 % → 1.3–4.2 mm lost motion per 0.2 m.

## Compressionless coil sheaths: cited products
| product | OD / ID mm | type | mass | bend radius | source |
|---|---|---|---|---|---|
| Binder-Wöhrle 5.53.0000.002 | **4.70** (D3) / 2.60 (D1), coil OD 4.10 | flat-wire spiral, plastic cover | 61.6 g/m | not published | binder-woehrle.com, Bowden cable sheaths |
| Binder-Wöhrle 5.01.0000.135 | 4.90 / 2.20 | round-wire spiral | 64.6 g/m | not published | same |
| Shimano/Jagwire compressionless | 4–5 | long-lay strands | — | not published; Wikipedia notes long-lay housings "cannot withstand the high compression… fail by buckling" | not suitable for 775 N |

- B-W states flat-wire sheaths "absorb greater compressive forces" and are "less suitable… around corners", while round wire is "comparatively low compressive forces".
- **No cited catalog coil sheath at ≤ 2.5 mm OD was found.** Asahi Intecc, Fort Wayne Metals and Heraeus make custom medical flat-wire coils, but no published catalog part with a radius, compression or friction value could be retrieved. Custom quote needed.

## Compression and lost motion [EST, from steel E 200 GPa (MIF 4140 190) × coil metal area, ideal close-wound]
- **Option 1: B-W flat 4.70 OD**, coil metal ≈ π/4(4.10² − 2.60²) = 7.9 mm². Ideal stiffness ≈ 1 580 N/mm per metre.
  - At 503 N: 0.32 mm/m → **0.064 mm per 0.2 m tendon**. At 775 N: 0.10 mm. At 30 N: 0.004 mm.
  - Real coils add turn-contact compliance. A measured spring-sheath system gave K_s ≈ 800 N/mm (Tension Control of a Bowden-Cable Actuation System, exa.ai record). Allowing ×5 compliance [EST] gives ≈ 0.3–0.5 mm at stall and < 0.03 mm at 30 N.
  - **Fails the ø2.5 envelope** (palm bores ø2.5).
- **Option 2: custom flat-wire 304/316 coil, OD 2.4–2.5 / ID 1.6, with a PTFE liner ID 1.3** [EST geometry].
  - Coil metal ≈ π/4(2.4² − 1.6²) = 2.5 mm², so about 500 N/mm per metre ideal.
  - At 503 N: 1.0 mm/m → **0.2 mm per tendon** (×5 compliance → ≈ 1 mm). At 775 N: 0.31 mm (≈ 1.5 mm). At 30 N: 0.012 mm (< 0.06 mm).
  - Coil compressive stress at 775 N: 310 MPa. Below 304 stainless yield [EST, not cited], so it's marginal on buckling between supports. **Needs a supplier test at 775 N.**
- **Liner friction PTFE–Dyneema:** not cited. Capstan test needed (G5).

## Mass, both hands (22 tendons ≈ 4.5 m total [EST from 6 × 0.20 + 0.21 + 4 × 0.20 per hand])
| option | g/m | both hands |
|---|---|---|
| plain PTFE 1.3/2.5 (out) | 7.9 | 35 g |
| **custom coil 2.5 OD + liner** | 2.5 mm² × 7.9 + liner ≈ 21 [EST] | **≈ 94 g** |
| B-W flat 4.70 OD | 61.6 | **277 g** |

## Verdict
- **Ø2.5 is feasible only as a custom flat-wire coil with a PTFE liner.** There is no catalog part. The 4.7 mm catalog part breaks the palm bore pattern and adds ≈ 0.24 kg.
- Lost motion is ≤ 0.06 mm at 30 N working load and ≈ 1–1.5 mm at stall [EST]. Tendon stretch is ≈ 2 mm at 775 N, so the tendon dominates, not the sheath.
- **Asks:**
  - **Arms/Actuators:** RFQ to Fort Wayne Metals / Asahi Intecc / Heraeus for a flat-wire 316 coil, OD ≤ 2.5, ID ≥ 1.6, with PTFE liner ID 1.3. They must state the min bend radius (need ≤ 35 mm), compression at 775 N, and turn-separation life. Book about 94 g both hands [EST], vs the earlier 26 g/hand plain PTFE: **+42 g both**.
  - **Actuators:** the termination/splice derating for the SF at stall.
  - **G5:** capstan friction test, and a 775 N proof on a 37.6 mm bend (sheath + tendon).


## Rev C (2026-10-14): 500 N firmware-capped stall, spool D/d and splice derating
**Cited derating factors:**
- **Bend over pin/spool:** E ≈ 1 − 0.5/√(D/d) (BR Ropes, "D/d ratio: rope bending loss", fixed-pin estimate for synthetic rope; no HMPE-specific test table was found):
  - D/d 10 → **0.84**; D/d 5 → **0.78**; the sheath bend R 37.6 (D/d 75) → 0.94.
  - Marlow recommends a sheave diameter ≥ 8× rope diameter for braided ropes, so **a 5 mm spool (5×) is below Marlow's minimum**.
  - Fatigue: doubling D/d roughly triples bend-fatigue life (Marlow via sail-world), so going from 10 to 5 mm costs about ⅔ of the life.
- **Splice:** a correctly made Brummel retains **80–90 %** (ropeandline, HMPE 12-plait). A Jimmy Green/Marlow test shows ≥ 80 %, with one Brummel failing at −12 %. ISO 2307 allows −10 % for splice breaks. **Use 0.80.**
- No LIROS-specific D-Pro splice figure was found.

| case (MBL 1 913 N, LIROS) | effective strength | SF at 500 N | SF at 775 N |
|---|---|---|---|
| straight | 1 913 | **3.83** | 2.47 |
| splice only (0.80) | 1 530 | 3.06 | 1.97 |
| spool 10 mm only (0.84) | 1 611 | 3.22 | 2.08 |
| spool 5 mm only (0.78) | 1 484 | 2.97 | 1.92 |
| **splice on a 10 mm spool (0.80 × 0.84)** | 1 289 | **2.58** | 1.66 |
| **splice on a 5 mm spool (0.80 × 0.78)** | 1 187 | **2.37** | 1.53 |

- Recommendation:
  - Keep the 10 mm spool if at all possible.
  - Terminate the splice off the spool, with ≥ 1.5 dead wraps so the capstan takes the load before the splice.
  - **With the 500 N firmware cap and the splice away from the spool, SF ≥ 2.97 on either spool.**
  - G5: break-test 3 assemblies on the real spool.

**Sheath at 500 N, custom coil OD 2.5 / ID 1.6 [EST, rev B method]:**
- Coil stress 500 / 2.51 mm² = **199 MPa** (vs 310 at 775 N), well clear of the coil-wire yield [EST].
- Lost motion per 0.2 m: ideal 0.20 mm; **≈ 1.0 mm with ×5 coil compliance**. At the 30 N working load it is ≤ 0.06 mm.
- Tendon stretch at 500 N ≈ 0.65 % [EST, linear from < 1 % working stretch] → **≈ 1.3 mm per 0.2 m**.
- **Total ≈ 2.3 mm at stall** (cap 500 N), ≈ 0.1 mm at working load.
