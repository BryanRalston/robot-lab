# Merged PA12 thigh-rear / knee-drive cover (R-087)
Script `knee_drive_panel.py` → `knee_drive_panel.json`. Owner: RL Industrial Design (merge with Electronics §18.2f item 10).

## Why
R-087: ID's drive-bay rear panels (+0.082 EST) overlapped Electronics' 41.8 g PA12 knee-drive covers. **One PA12 part per side** is the fairing skin and the drive cover.

## Geometry (per side)
| | |
|---|---|
| Planform | ~130 × 170 mm rear thigh [EST], over femur-rear drive box z 688–792 (R-062 / L51) |
| Inner pocket | **80 × 60 × 15 mm**, wall ≥ 1.5 mm PA12 (ρ 1.01), over the 26 × 52 × 104 drive box |
| Inlet (low) | **52 cm²** open, slots ≤ 10 mm, ≥ 30 % of low zone |
| Outlet (high) | **63 cm²** open, ≥ 35 % of high zone |
| Clearance | ≥ 3 mm to drive tops and cable exits; **cable exits at bottom edge** |

## Mass
| item (per side) | g |
|---|---|
| Outer skin (net of vents) | 16.1 |
| Pocket walls 80×60×15 | 6.4 |
| IP2X labyrinth baffle | 3.9 |
| 4× M2.5 bosses | 3.2 |
| 4× captive M2.5 | 4.8 |
| Stiff ribs | 0.9 |
| **Side / pair** | **35.3 g / 0.071 kg** |

| comparison | kg |
|---|---|
| Separate: ID PC panels + Electronics covers | 0.082 + 0.0418 = **0.124** |
| Merged | **0.071** (−0.053) |
| R-087 booked net | **+0.040** |
| **Merged vs booked** | **+0.031 (FLAG — reconcile)** |

## IP2X and tool removal
1. **Tool required:** 4× M2.5 **captive** screws into tabs on Legs' two G10-lined band clamps. No snap-only retention (Electronics enclosure condition C1).
2. **No femur holes:** tabs on the band clamps only. **Legs must confirm tab positions.**
3. **IP2X (IEC 60529):** jointed test finger Ø12 × 80 mm has no straight path to solder points. Inner face ≥ 8 mm from live parts **or** labyrinth baffle in front of terminals; vent slots ≤ 10 mm wide.

## Fin grille
No local bulge (rev B stays). Bulge pending Legs' rev B envelope check.
