# Review of ID R-069 cover trims (363b318) — RL Materials, 2026-10-14
Sources are in MATERIALS_DB. [EST] = estimate. Each item gets a verdict and its effect on MASS_DOWN (ID's deltas, half credit per R-040).

## A. CF 1.0 mm louvred thigh front (−0.026): **YES with conditions**
- Notch sensitivity is real. Open-hole tension strength drops by up to about 50 % for quasi-isotropic CFRP (CF_NOTCH_MDPI), and open-hole compression keeps only 35–75 % of unnotched strength depending on layup (CF_NOTCH_FLECK). A 4-ply 0/90 twill sits on the sensitive side.
- The panel isn't structural (the EPP and the core take falls), so the risk is **cracking and delamination growing from the slot ends** on impact, not overload.
- Conditions:
  - Slot ends get a full radius (≥ 3 mm [EST]). No sharp slot corners.
  - Cut slots by CNC with a diamond/compression router, or mould them in. No drilled-and-sawn slots.
  - **Seal the cut edges** with epoxy wipe or edge-coat against moisture and fraying.
  - Keep ≥ 8 mm of solid laminate [EST] between the slots and the panel edge or insert bosses.
  - Run one panel through the G5 fall test.
- Mass: −0.026 OK. R-029 rule (CF ≤ PC panel mass) is met.

## B. Knee cap PC 1.5 → 1.2, about 0.7 mm at high draw (−0.02): **NO**
- PC is tough: PALSUN 130 J (E50) at 3 mm (R027).
- No source gives dent or impact energy at 0.7 mm. Taking impact resistance as scaling roughly with thickness squared [EST], 0.7 mm vs 1.5 mm gives about 0.2× the dent energy.
- The knee is a primary fall-contact zone, and post-form corners at 0.7 mm will crack or tear on a kneel-fall [EST].
- Keep 1.5 mm, or use a plug-assist mould to hold ≥ 1.0 mm min wall and then re-ask.

## C1. Foot top shell 1.2 → 1.0 mm (−0.023): **YES with an EPP-backed dent check**
- Draw is ≤ 1.5:1, so thinning is small and the post-form wall is ≥ 0.8 mm [EST].
- PC dents rather than cracks (R-027).
- Kicks and stubs are low energy. Accept it, with one G5 stub-impact check. C2 (delete the shell) is an Arbiter/Legs call; materials has no objection.

## D/E. Ankle boot and hip skirt fabric 0.30 → silicone 70D ripstop (−0.040 / −0.048): **YES, and ID's mass is conservative**
- Current fabric (TPU-coated 210D) is **270–310 g/m²** (EXT_TPU210, XL_TPU210). ID's 0.30 kg/m² is confirmed.
- Silicone-impregnated 70D ripstop is **about 71 g/m² finished** (RBTR_SILPOLY: 1.9 osy greige, about 2.1 osy finished). ID assumed 0.10.
- Using 0.071, the savings grow:
  - boot 0.201 m² × 0.229 = **−0.046** (vs −0.040);
  - skirt 0.239 m² × 0.229 = **−0.055** (vs −0.048).
- Risks:
  - Abrasion and tear: tear strength is much lower than 210D. 210D TPU is 17/10 N (XL_TPU210); 70D silpoly tear is not cited.
  - The boot becomes a wear part, inspected at the 4 250 h rod-end service.
  - Silicone fabric can't be tape-sealed or welded, so seams must be sewn and sealed.
  - The skirt needs its hem ring (kept).

## F1. Waist bellows TPE → thin TPU-film convoluted boot (−0.025): **TEST before booking**
- **No cited flex-fatigue data** for a thin TPU film convolute was found.
- Waist yaw/pitch is roughly 1 cycle per step [EST], so about 10⁶ cycles per year.
- Needs a G5 cycle test: ≥ 10⁶ cycles at full yaw ±90 / pitch range, film thickness as built, at 40 °C.
- Book at 0 until then. F2 (delete) is an Arbiter option.

## G. Snap hooks replace 2 of 4 inserts (−0.032): no materials objection
- Snaps must be in PC (good creep and fatigue) or PA12. Lost panels on a fall are acceptable as a fuse (ID).

## Shoulder pad mount
- **D-A doubler on the roll-yaw link face is OK** (R042 Part 6), with the Arms conditions already sent:
  - flat and solid over 87.4 mm diagonal with 4 × M4 × 8;
  - roll bearing FEA (R-067);
  - pad centred on the roll axis.

## MASS_DOWN impact (full / half credit)
| item | ID Δ | Materials verdict | Δ to book (full) |
|---|---|---|---|
| A | −0.026 | yes (slot rules) | −0.026 |
| B | −0.020 | no | 0 |
| C1 | −0.023 | yes + dent check | −0.023 |
| D | −0.040 | yes (cited 71 g/m²) | **−0.046** |
| E | −0.048 | yes | **−0.055** |
| F1 | −0.025 | test first | 0 until tested |
| G | −0.032 | yes | −0.032 |
| **total** | −0.194 (ID rec. set incl. F1) | | **−0.182 full / −0.091 at half credit** |
