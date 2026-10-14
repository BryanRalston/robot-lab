# V5 cover set (RL Industrial Design, 2026-10-14; baseline = trimmed set per R-029)
Owner: RL Industrial Design (also owns `V5_POLISH_PLAN.md` from this round). Basis: **R-027 / P-020**: thermoformed PC 1.5 mm (ρ 1.20, 1.80 kg/m²), CF 4×0.25 twill (ρ 1.55, 1.55 kg/m²) allowed **per panel only if no heavier than its PC version**; extra coverage needs its own P-number. Numbers from `cover_set_v5.py` → `cover_set_v5.json`. Everything is **[EST]** until A29 measures panels on CAD.

## Baseline: trimmed set (R-029 approved basis; `cover_set_v5.json`)
Trims: shin/thigh fairings front + outboard only (skin fraction 0.70 → 0.50 of hull), arm shells + shoulder cap deferred to Arms R2, foot shell top only (0.40 → 0.26).

| panel | P | material | skin m²/side | panels | kg (PC) | kg if CF | mount |
|---|---|---|---|---|---|---|---|
| shin fairing, front + outboard, 2 pieces | P-020 | PC 1.5 (CF option) | 0.088 | 4 | 0.331 | 0.287 | M4 inserts into existing shank clamp bosses; quarter-turn at the split; rod-end access every 4,250 h |
| thigh fairing, front + outboard, 2 pieces | P-020 | PC 1.5 (CF option) | 0.132 | 4 | 0.490 | 0.424 | bonded thigh collar points (no new holes in FEA'd tube) |
| foot top shell | P-020 | PC 1.5 | 0.050 | 2 | 0.188 | — | foot box side screws; sole/contact patch unchanged |
| knee cap | P-022 (booked R-029) | PC 1.5 | 0.030 | 2 | 0.116 | — | shank-side on knee lever; outside thigh fairing |
| hip skirt | P-023 (booked R-029) | TPU-coated nylon + PC rim strip | 0.110 | 2 | 0.114 | — | rim to pelvis skin flange, elastic hem to thigh fairing |
| waist bellows | P-024 (booked R-029) | TPE bellows | 0.085 | 1 | 0.055 | — | clamp bands, pelvis top / torso bottom flange |
| ankle boot | P-025 (booked R-029) | TPU-coated nylon, zip | 0.101 | 2 | 0.098 | — | drawstring at shin fairing, elastic on foot shell |

Inserts/rim doublers 4 g per rigid panel included; EPP pads (0.360) unchanged, not in table. Torso taper and head visor stay in their own lines.

**Mass (trimmed):** P-020 rigid PC skin 0.539 m² → **1.009 kg** vs booked 1.157 (**−0.148**); P-022…P-025 **+0.383**; **net +0.236 kg vs booked** (R-029 holds 0.30). With CF shin + thigh fairings: **+0.126 kg**. Arm shells return as a P-020 change at Arms R2 (untrimmed estimate +0.589 kg).

## Option: untrimmed set (`python3 cover_set_v5.py --untrimmed` → `cover_set_v5_untrimmed.json`)
Full-wrap shin/thigh fairings (0.70 hull), foot shell 0.40, upper-arm (ø95×260) + forearm (ø85×250) shells + shoulder caps as placeholders. P-020 1.073 m² → 2.012 kg (+0.855 vs booked) + P-022…P-025 0.383 → **+1.238 kg**. Rejected by R-029 against the 1.329 kg reserve / 0.30 floor; kept for reference only.

## Clearance assumptions
- Leg keep-outs: Legs `legs/results/v5/envelopes.json` (hull areas snapshotted into `cover_set_v5.py`) (fairings_v5.py, model_v4 swept, convex hull + 5 mm; **uncommitted Legs WIP, not yet confirmed by Legs**). Shin: ankle pitch −45…+40 × roll ±18; thigh: hip pitch −105…+40 (incl. −74.6 sit) × knee 0–135; skirt: yaw −35/+45, roll −12/+15.
- Skin fraction 0.50 of hull area (shin/thigh, trimmed; 0.70 untrimmed), 0.26 (foot top; 0.40 untrimmed), 0.80 (boot): [EST].
- Additional 3 mm air gap inside the keep-out for PC flex under fall load [EST]; draw ratio ≤ 3:1 (LEXAN guide) assumed achievable on all rigid panels; panels split at the 3:1 limit.
- Arm/shoulder: no envelope exists; shells are placeholders (V5 plan row 6).

## Open questions
1. Legs: confirm envelopes.json as final and commit; knee-cap keep-out complement vs thigh fairing overlap.
2. A29 now owned by Industrial Design (R-029): panel layout + mould list on v4 CAD; measured delta must stay ≤ 0.30 kg.
3. CF on shin/thigh for looks (two-tone gold/black) — cost delta vs A30 sheet.
