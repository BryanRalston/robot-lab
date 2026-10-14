# R-047 cover offsets: Arbiter-ready itemized list (RL Industrial Design, rev A36 / pad R8, 2026-10-14)
Scripts: `cover_trims_r047.py` → `cover_trims_r047.json` (reads `a36_vents.json`, `pad_r8.json`, `wrist_trims.json`). Areas [EST] (measured: false); covers count at half credit (R-040).

## Cover items (booked R-059: −0.117 at half credit; R-067 rebooked −0.073)
| # | item | Δ kg (full) | evidence |
|---|---|---|---|
| 1 | **P-026 vents to Thermal A35** (replaces the blanket 30 % louvres): thigh hip + knee inlets −0.026, knee-cap louvres −0.033, D69C front-fin bulge +12 mm (included in thigh), skirt hem exhaust band +0.004 | **−0.055** (was −0.154) | `a36_vents.json`; A35 per-joint open areas (≥ 50/60 cm², ≥ 30/35 %) |
| 2 | PC 1.2 mm average (min 0.9 post-form) on thigh outboard + foot top | **−0.077** | calc: (0.213 + 0.171) × 0.3/1.5; 2 ribs on the thigh outboard; **foot top later deleted by R-081 C2** |
| 3 | Hip-skirt rim strips → printed PA12 1.2 mm | **−0.013** | calc |
| | **Items 1–3** | **−0.145 → −0.073 half credit** | **shortfall +0.044 vs the booked −0.117 (FLAG)**: the A35 layout opens only over the housings, not 30 % everywhere |

## Status after R-067 / R-079 / R-081
| item | Δ kg | basis |
|---|---|---|
| Shoulder pad R8 option B 0.116 vs R-073 booked 0.092 | **+0.024** (R-079, full) | `pad_r8.json` option_B; field rebonding A rejected |
| Pad remaining credit vs R-073 (Materials f14c29c) | **−0.0044** pending FEA | after tray B booking |
| Wrist fairing trims vs R-059 +0.079 | **-0.067 → -0.034 half credit** (Arms accepted the open frame; PTFE guard contingency +0.005) | `wrist_trims.json` |
| R-069 new trims | see `COVER_TRIMS_R069.md` | A/D/E/C2 booked; B2/F1/G gated |

**Knee fin grille:** no local bulge. Rev C withdrawn (R-079/R-081); rev B stays. A ~5 mm bulge is **pending Legs' rev B envelope check** if fins again exceed the v5 thigh fairing hull.

Not included (Arbiter decision): shin add-back, deferred until D69 rev B verified; louvred CF +0.198 preferred (R-054).

## R-082 / R-087 / R-088 (cover deltas)
| item | kg | note |
|---|---|---|
| Forearm cover +17 mm (R-082) | **+0.014** pair | booked R-087; proportion 0.96 signed off |
| Merged PA12 knee-drive / thigh-rear (R-087) | **+0.071** pair | replaces +0.082 PC + 0.0418 Elec; vs booked +0.040 → +0.031 FLAG |
| P-052 sternum plate (R-088) | **+0.058** | Torso land+rib +0.030 separate |
