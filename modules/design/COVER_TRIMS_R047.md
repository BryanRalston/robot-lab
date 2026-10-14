# R-047 cover offsets: Arbiter-ready itemized list (RL Industrial Design, rev A36 / pad R6, 2026-10-14)
Scripts: `cover_trims_r047.py` → `cover_trims_r047.json` (reads `a36_vents.json`, `pad_r6.json`, `wrist_trims.json`). Areas [EST] (measured: false); covers count at half credit (R-040).

## Cover items (booked R-059: −0.117 at half credit)
| # | item | Δ kg (full) | evidence |
|---|---|---|---|
| 1 | **P-026 vents to Thermal A35** (replaces the blanket 30 % louvres): thigh hip + knee inlets −0.026, knee-cap louvres −0.033, D69C front-fin bulge +12 mm (included in thigh), skirt hem exhaust band +0.004 | **−0.055** (was −0.154) | `a36_vents.json`; A35 per-joint open areas (≥ 50/60 cm², ≥ 30/35 %) |
| 2 | PC 1.2 mm average (min 0.9 post-form) on thigh outboard + foot top | **−0.077** | calc: (0.213 + 0.171) × 0.3/1.5; 2 ribs on the thigh outboard; dent check A15 open |
| 3 | Hip-skirt rim strips → printed PA12 1.2 mm | **−0.013** | calc |
| | **Items 1–3** | **−0.145 → −0.073 half credit** | **shortfall +0.044 vs the booked −0.117 (FLAG)**: the A35 layout opens only over the housings, not 30 % everywhere |

## Offsets that cover the shortfall
| item | Δ kg | basis |
|---|---|---|
| Shoulder pad R6 0.100 vs R-060 booked 0.127 | **−0.027** (full: an assembly estimate, itemized) | `pad_r6.json` |
| Wrist fairing trims vs R-059 +0.079 | **−0.071 → −0.036 half credit** | `wrist_trims.json` |
| **Net vs current bookings** | **+0.044 − 0.027 − 0.036 = −0.019** | still an offset, but small |

Not included (Arbiter decision): shin add-back, deferred until D69 rev B verified; louvred CF +0.198 preferred (R-054).
