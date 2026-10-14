# V5 cover set draft (RL Industrial Design, R1, 2026-10-14)
Owner: RL Industrial Design (also owns `V5_POLISH_PLAN.md` from this round). Basis: **R-027 / P-020**: thermoformed PC 1.5 mm (ρ 1.20, 1.80 kg/m²), CF 4×0.25 twill (ρ 1.55, 1.55 kg/m²) allowed **per panel only if no heavier than its PC version**; extra coverage needs its own P-number. Numbers from `cover_set_v5.py` → `cover_set_v5.json`. Everything is **[EST]** until A29 measures panels on CAD.

## Panel list (both sides)
| panel | P | material | skin m²/side | panels | kg (PC) | kg if CF | mount |
|---|---|---|---|---|---|---|---|
| shin fairing, 2 halves | P-020 | PC 1.5 (CF option) | 0.123 | 4 | 0.457 | 0.396 | M4 inserts into existing shank clamp bosses; quarter-turn at the split; access to rod ends every 4,250 h |
| thigh fairing, 2 halves | P-020 | PC 1.5 (CF option) | 0.184 | 4 | 0.680 | 0.587 | bonded thigh collar points (no new holes in FEA'd tube) |
| foot upper shell | P-020 | PC 1.5 | 0.077 | 2 | 0.285 | — | foot box side screws; sole/contact patch unchanged |
| upper-arm shell, 2 halves | P-020 | PC 1.5 | 0.066 | 4 | 0.253 | — | **placeholder**: ø95×260 cylinder, held until Arms actuators exist |
| forearm shell, 2 halves | P-020 | PC 1.5 | 0.057 | 4 | 0.220 | — | **placeholder**: ø85×250, sized by O-A3 drive fit |
| shoulder cap | P-020 | PC 1.5 | 0.030 | 2 | 0.116 | — | placeholder |
| **knee cap** | **P-022 (proposed)** | PC 1.5 | 0.030 | 2 | 0.116 | — | shank-side, on knee lever; must stay outside thigh fairing (Legs `knee_cap` keep-out) |
| **hip skirt** | **P-023 (proposed)** | TPU-coated nylon + PC rim strip | 0.110 | 2 | 0.114 | — | rim screwed to pelvis skin flange, elastic hem to thigh fairing top |
| **waist bellows** | **P-024 (proposed)** | TPE bellows | 0.085 | 1 | 0.055 | — | clamp bands on pelvis top / torso bottom flange |
| **ankle boot** | **P-025 (proposed)** | TPU-coated nylon, zip | 0.101 | 2 | 0.098 | — | drawstring at shin fairing bottom, elastic on foot shell |

Inserts/rim doublers 4 g per rigid panel included. EPP pads (0.360) unchanged, not in table. Torso chest shell taper and head visor stay in their own lines (replace existing CFRP shell / head line, no P-020 change).

## Mass vs booked P-020
- P-020 rigid PC skin in this layout: **1.07 m² → 2.01 kg**, vs R-027 booked **0.643 m² → ~1.16 kg** (50 % coverage). **Δ ≈ +0.86 kg** if the v5 rigid coverage is kept as drawn. With CF on shin + thigh fairings: −0.15 kg (CF is lighter per m², so passes the R-027 test; costs more moulds).
- New P-numbers P-022…P-025: **+0.38 kg** total.
- Total v5 set ≈ **+1.24 kg PC / +1.09 kg CF-legs** vs booked, against reserve **1.329** (floor 0.30) → **does not fit as drawn.** Proposed trims for the Arbiter (A29): thigh/shin fairings front+outboard only (≈0.5 skin fraction instead of 0.7: −0.33 kg), arm shells deferred until Arms R2 (−0.59 kg now), foot shell top only (−0.10). Trimmed set ≈ +0.2–0.3 kg.

## Clearance assumptions
- Leg keep-outs: Legs `legs/results/v5/envelopes.json` (fairings_v5.py, model_v4 swept, convex hull + 5 mm; **uncommitted Legs WIP, not yet confirmed by Legs**). Shin: ankle pitch −45…+40 × roll ±18; thigh: hip pitch −105…+40 (incl. −74.6 sit) × knee 0–135; skirt: yaw −35/+45, roll −12/+15.
- Skin fraction 0.70 of hull area (shin/thigh), 0.40 (foot), 0.80 (boot): [EST].
- Additional 3 mm air gap inside the keep-out for PC flex under fall load [EST]; draw ratio ≤ 3:1 (LEXAN guide) assumed achievable on all rigid panels; panels split at the 3:1 limit.
- Arm/shoulder: no envelope exists; shells are placeholders (V5 plan row 6).

## Open questions
1. Legs: confirm envelopes.json as final and commit; knee-cap keep-out complement vs thigh fairing overlap.
2. Arbiter (A29): accept trimmed coverage or fund +0.86 kg on P-020; book P-022…P-025.
3. CF on shin/thigh for looks (two-tone gold/black) — cost delta vs A30 sheet.
