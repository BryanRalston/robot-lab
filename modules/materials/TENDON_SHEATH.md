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
