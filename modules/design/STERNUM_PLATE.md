# P-052 sternum bezel (R-094)
> **Rev 2 (2026-10-21, 116 mm core): see V5_COVER_SET.md §Chest bulge.** The tapered 1.0 PC bezel/fairing rides on 4 PA66 crush posts at y ±63, z +0.157/+0.283, outside the core footprint, recessed 2 mm behind the face. The rev 1 geometry below (inserts at y ±40, face x +0.147) is superseded. P-052 = 0.072 kg.
Script `sternum_plate.py` → `sternum_plate.json`. Supersedes the R-088 / R-093 full PC plate (0.058 kg). Layout: Torso ab432da §25.1.

## Design
- **Visible skin:** the chest pad **1 mm CF face** at **x ≈ +0.147** (37 mm proud). Pad bonded to the 7075 land with structural epoxy.
- **Bezel:** 1.5 mm PC ring (≈ 15 mm radial), secondary hold + cosmetic edge. **4 captive M4s** into inserts at **(y, z) = (±0.040, +0.180 / +0.260)**.
- **Flange:** overlaps the face by **≤ 4 mm**, **no clamping preload** — 1 mm stand-off on a compliant gasket. Centre **90 × 90** free.
- **Edge:** bezel sidewall + foam edge seal (**seal does not bond to the honeycomb core walls**).
- **Film:** 0.3–0.5 mm TPU on the CF face (≈ 3–5 g).
- **Blend:** 15 mm to the surrounding chest shell.

## Service rule
A **visible dent > 1 mm deep**, or **any crush**, means **replace the pad**. The crushed face is the replace-me indicator (R-094).

## Mass (ID only)
| item | g |
|---|---|
| Bezel flange 15 mm | 11.3 |
| Bezel sidewall | 5.6 |
| Blend 15 mm to shell | 7.3 |
| 4× captive M4 | 10.0 |
| Compliant gasket 1 mm | 0.6 |
| Foam edge seal | 0.5 |
| TPU film 0.4 mm | 4.6 |
| **ID total (bezel + gasket + seal + film + blend + captives)** | **0.040 kg** |

| comparison | kg |
|---|---|
| Old full plate (R-093) | 0.058 |
| **Bezel ID vs plate** | **−0.018** |
| CF shell cut-out removed (Torso §25.1, ≈ 120×120 × 2 mm) | −0.045 |
| **Net ID added − CF shell** | **−0.005** |

R-094 ledger (Arbiter): ring +0.015 full; CF shell −0.045 at half (−0.0225); replaces R-093 +0.058 → **−0.066** booked. Script ring alone ≈ 0.017.

Not ID: 7075 land+rib (+0.030), pad core + CF face, structural epoxy.

## Conditions (R-094)
1. Face finished (clear coat or texture).
2. Torso/Materials confirm CF face for handling, UV, abrasion as outer skin.
3. Controls re-checks T-031 with skin at x ≈ +0.147.
