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

## A29 panel layout and mould list (owner: Industrial Design per R-029)
Status: layout from Legs keep-out hulls + model_v4 dims, **not yet measured on v4 CAD** (areas [EST]). Delta check: itemized `modules/design/cover_set_v5.json` = **+0.236 kg ≤ 0.30 cap: PASS** (+0.126 with CF shin/thigh).

| # | panel (per side unless noted) | split / layout | draw [EST] | mould (L/R separate) | process |
|---|---|---|---|---|---|
| M1–M2 | shin front piece | front of shank, ankle pitch −45…+40 swept; split on sagittal line to outboard piece | ≤ 2:1 | 2 tools | PC vacuum-form, CNC trim (or CF prepreg on same geometry, Al tool) |
| M3–M4 | shin outboard piece | lateral face, overlaps front 8 mm at quarter-turn joint | ≤ 1.5:1 | 2 | PC vacuum-form |
| M5–M6 | thigh front piece | taper 140→105 mm; ends above knee-cap keep-out | ≤ 2:1 | 2 | PC / CF option |
| M7–M8 | thigh outboard piece | lateral face, clears hip-pitch screw | ≤ 1.5:1 | 2 | PC / CF option |
| M9–M10 | foot top shell | top of 240×100 box only, hides instep lugs | ≤ 1.5:1 | 2 | PC vacuum-form |
| M11–M12 | knee cap (P-022) | shank-mounted, sweeps 0–135° outside thigh fairing | ≤ 2.5:1 | 2 | PC vacuum-form |
| M13 | hip skirt rim strip (P-023) | flat-formed strip, both sides from one tool | ≤ 1:1 | 1 | PC strip former |
| P1 | hip skirt fabric (P-023) | 2 sewn panels from flat pattern | — | cut pattern | sewn TPU-nylon |
| M14 | waist bellows (P-024, 1 off) | single band, convolutions over yoke | — | 1 dip/rotational mould, or catalog bellows if one fits ø300 × 90 | TPE |
| P2 | ankle boot (P-025) | flat pattern + zip | — | cut pattern | sewn TPU-nylon |

Rigid thermoform tools: **12** (vs 16 [EST] in COVER_COST.md; A30 cost sheet to be updated) + 1 strip tool + 1 bellows mould; 2 sewing patterns. Trim fixtures: one per rigid tool (12). Next: measure panel areas on model_v4 CAD and confirm draw ratios; re-run `cover_set_v5.py` with measured areas.

## Area measurement status (R-030)
Not measured yet. Measuring trimmed panel areas needs the build123d model_v4 rebuild plus the Legs keep-out STLs (not on main), which is a heavy CAD job. Route it to Bryan's PC. Until then `cover_set_v5.json` areas stay [EST] (`measured: false`). Re-rule trigger: any panel measuring > 10 % over its estimate.

## A36 / P-026 vent panels (stub, waiting on Thermal A35)
R-030 P-026: no closed PC over hip-pitch or knee. The knee cap, hip skirt and thigh panels must be louvred (≥ 30 % open area) or made of CF/aluminium. Thermal's A35 per-joint open-area and airflow spec is **not on main** yet; only `thermal/R1_BUDGET.md` recommends ≥ 30 % louvred/perforated panels.
- Expected direction: louvres in PC remove material, so mass goes down (≈ −30 % on the affected panels: thigh 0.490, knee cap 0.116 → ≈ −0.18 kg [EST]), minus the rim/rib stiffening at the louvres (≈ +0.03 [EST]). Al 0.8 mm instead of PC would be heavier (+49 % per m²): **flag to the Arbiter if chosen.**
- The hip skirt is fabric (P-023); a mesh insert at the hip-pitch zone meets the intent with no mass change [EST].
- Draft to be done when A35 lands.

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
