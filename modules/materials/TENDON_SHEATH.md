# Tendon sheath Ø2.5: search result (RL Materials, 2026-10-14; for Arms R5 §9 and Actuators D78)
Requirement:
- Ø2.5 OD, PTFE-lined or PEEK, for a LIROS D-Pro 1 mm Dyneema tendon (so ID ≥ about 1.2 mm [EST]).
- **Published** minimum bend radius ≤ 35 mm (used at 37.6 mm).
- 11 sheaths at the wrist.
- RINGSPANN at 51 mm is already rejected.

## What I found (cited)
| candidate | ID / OD | published min bend radius | compressionless? | source |
|---|---|---|---|---|
| Zeus PTFE Industrial-wall 1/16″ ID × 0.030″ wall | 1.59 / 3.11 mm | **17.5 mm** (0.688″, ≥ 36″ length test) | no (plain PTFE) | ZEUS_BEND |
| Zeus PTFE Industrial-wall 1/32″ ID × 0.015″ wall | 0.79 / 1.59 mm | 8.4 mm | no; **ID too small** for 1 mm tendon | ZEUS_BEND |
| Zeus PEEK extruded 0.080 × 0.125″ | 2.03 / 3.18 mm | not published (Zeus: "tight radius bends … catheter") | stiffer | ZEUS_PEEK |
| Optinova PEEK 1.59/3.18 mm, 1.0/1.59 mm | — | **< 50 mm** (not ≤ 35) | stiffer | OPTINOVA_PEEK |
| Shimano PTFE compressionless housing | 5 mm OD | none published | yes | retailer listings (no datasheet) |
| Alligator PTFE-lined Bowden sheath | 1.8 / 5 mm | none published | coil | mofakult listing |

- **No catalog Ø2.5 OD sheath with a published bend radius ≤ 35 mm was found.** That covers PTFE-lined coil, catheter coil, bike housing (smallest standard 4 mm, no radius published) and PEEK.
- A research hand (arXiv 2512.24657) used a 2 mm ID PTFE liner in a 3.2 mm OD stainless spring, with no radius stated.
- **Closest cited path:** Zeus PTFE. Their table shows the radius scaling with OD and wall: 8.4 mm at 1.59 OD and 17.5 mm at 3.11 OD. A custom **Zeus PTFE ID 1.3 × OD 2.5 mm** (wall 0.6 mm ≈ 0.024″) falls inside that range, so I expect about 12–15 mm [EST: interpolation, needs a Zeus quote or sample bend test]. That is well under 35 mm.

## Friction against UHMWPE (Dyneema)
- **Not found in a cited source** for PTFE or PEEK against Dyneema. Bulk PTFE has the lowest friction of the candidates (MIF lists it as a fluoroplastic; no µ value fetched).
- A capstan test is needed (G5): tendon over a 37.6 mm radius, 67° wrap, 5–30 N, measure µ. That gives the A42 "sheath friction ×1.3" figure.

## Compression under load (lost motion) [EST from cited moduli]
- The sheath carries the tendon tension in compression. Plain PTFE tube, OD 2.5 / ID 1.3: A = 3.58 mm², E ≈ 0.4–1.3 GPa (MIF flex).
- At **30 N** (T4 grip) over a 300 mm sheath [EST length]: strain 0.6–2.1 %, so **1.9–6.3 mm lost motion per tendon**. That's too much for finger position control unless it is calibrated or tensioned.
- PEEK at E ≈ 4 GPa (MIF lower bound) gives about 0.6 mm, but has no published radius ≤ 35 mm at 2.5 OD.
- **Recommendation:**
  1. Short term: Zeus custom PTFE 1.3/2.5 as a liner, with lost motion compensated by motor-side encoder plus tension sensing. Request a Zeus sample and bend radius quote.
  2. Better: PTFE liner (Zeus thin-wall, ID 1.2 / OD about 1.6) inside a **flat-wire stainless coil to 2.5 OD**, which is compressionless. That is a custom catheter-coil supplier part, and the radius still has to be quoted. Cite on receipt.
  3. Keep the RINGSPANN rejection (51 mm).
- Actuators/Arms: book an [EST] mass of about 11 × 0.3 m × 3.6 mm² × 2.2 g/cm³ ≈ **26 g per hand** for plain PTFE (more with a coil).

## Asks
- **Arms + Actuators:** accept a "custom Zeus PTFE 1.3/2.5, R ≈ 12–15 mm [EST]" placeholder until a sample or quote arrives. Supply the sheath lengths and the max tendon load for the lost-motion budget.
- **G5:** capstan friction test (µ PTFE–Dyneema) and lost-motion test at 30 N.
