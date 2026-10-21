# R-143 §2b — Knee fins: ISO 13732-1 touch-burn check (RL T&R, 2026-10-21)

## ▶ Rev 4b update (09:10 ET) — current design: fins recessed behind a fairing grille, P-154 guard DROPPED
Source: Thermal 389f91b (`thermal/R131_ELMO_MG.md` §Rev 4b, `r131_rev4_guard.py`), Robot Lab decision. D93 knee plate in the L71 thigh pocket, fins **48.6–52.7 mm inside the v5 hull, ≈ 30 mm behind the grille**. Fairing grille ≥ 104 × 52 mm, **≥ 60 % open, slots ≤ 5 mm, inner face ε ≤ 0.1**; low inlet / high outlet ≥ 1200 mm² free each; low-ε knee-housing face toward the pocket. No-guard drive base at standing duty 74–76 °C (Thermal), walking 59–72 °C; derate holds the heat-sink face ≤ 85–90 °C (R-136).

**Verdict: PASS (conditional) at the grille, with thin margin at 35 °C ambient standing.** The bare fins (≥ 71.5 °C) still fail ISO 13732-1, but they are no longer touchable. The touchable surface is now the grille and fairing, and they stay ≤ 45.6 °C in the worst estimated case.

### 1. Touch points (TP-G5-15 revised)
Grille outer face (centre, plus the top rows where exhaust air may leave), grille edges/frame (top and bottom), the fairing within 20 mm of the grille, the inlet and outlet vent grilles, and the fairing over the knee twin housing (case 90–100 °C, R131 rev 4b).

### 2. Grille temperature estimate (`r143_grille.py` → `r143_grille.json`) [EST]
Model: grille web balance, inner convection from pocket air + radiation from the fins through the low-ε face (ε_eff 0.098, view 0.5) = outer convection + ε 0.9 radiation to ambient. Pocket air: standing chimney (H 0.12 m, 1200 mm², Cd 0.4) → outlet rise ≈ 28–31 K; walking (0.3 m/s through the grille) → 6–11 K. Two bounds: mixed pocket air at the face (f 0.5) and web in the exhaust stream (f 1.0). The drive base is capped at 87.5 °C by the derate.

| case | ambient 25 °C: base / grille mixed–exhaust | ambient 35 °C: base / grille mixed–exhaust |
|---|---|---|
| walking, duty | 61 / **26.6–27.8** | 71 / **36.6–37.8** |
| walking, carry (derate-capped) | 87.5 / **27.8–29.9** | 87.5 / **37.4–39.1** |
| standing, duty | 78.3 / **31.2–36.0** | 87.5 (derate) / **41.0–45.6** |
| standing, carry/soak (derate-capped) | 87.5 / **32.0–37.3** | 87.5 / **41.0–45.6** |
- Radiation through the ε 0.1 face contributes only about 2–4 K. **The grille temperature is set by the pocket air**, which Thermal's 39 °C figure (radiation, view 0.5) did not include. The worst case is exhaust air leaving through the top grille rows while the robot stands at 35 °C ambient.
- My standing duty base, 78.3 °C at 25 °C, agrees with Thermal's 74–79 °C.
- With a **black** inner face (ε 0.9), Thermal gets 47 °C from radiation alone; adding the pocket air would push it past 48 °C. **The low-ε inner face is mandatory.**

### 3. Finger reach — CONFIRMED unreachable
- IEC 61032 probe B (jointed test finger, ø12 mm, 80 mm) cannot enter a ≤ 5 mm slot at all. Pressed against the grille, skin bulges ≤ 1–2 mm into a 5 mm slot, against ≥ 30 mm to the fin tips (≥ 48 mm to the fin roots). A small child's finger (≈ ø8–9 mm) also cannot pass 5 mm.
- Only a rigid probe (IEC 61032 probe C/13, ø2.5–4 mm pin or rod) would enter. That is a tool-access case, not a touch-burn case.
- Condition: slots must stay ≤ 5 mm after thermoforming/moulding tolerance (drawing ≤ 5.0 max), and the grille must not deflect open under a 30 N finger push (TP-G5-15 step).

### 4. ISO 13732-1 verdict with margins
Grille material is fairing plastic (v5 PA12/PC). The plastic thresholds are higher at short times. To stay conservative and material-agnostic, I check against the ≥ 1 min values, which are the same for metals and plastics at 10 min and 8 h (Table 1, verified).

| criterion | limit | worst grille (35 °C amb, standing) | margin | worst at 25 °C amb | margin |
|---|---|---|---|---|---|
| 1–10 s (metal spread, most severe material) | 55–70 | 45.6 | **≥ +9.4** | 37.3 | ≥ +17.7 |
| 1 min (metal 51 / plastic 60) | 51 | 45.6 | **+5.4** | 37.3 | +13.7 |
| 10 min (all materials) | 48 | 45.6 | **+2.4** | 37.3 | +10.7 |
| 8 h (all materials, < 10 % skin) | 43 | 45.6 | **−2.6 (FAIL)** | 37.3 | +5.7 |
| Thermal's own 45 °C face limit (rev 4b) | 45 | 45.6 | −0.6 | 37.3 | +7.7 |
- **PASS against T&R's touch target** (≤ 48 °C at 35 °C ambient; ≤ 43 °C at 25 °C, R143 original spec) in every case. Margins are 2.4 K at 35 °C standing and 5.7 K at 25 °C.
- The 8 h / 43 °C value is exceeded only at 35 °C ambient with the robot standing hot for long periods. ISO 13732-1 limits that value to sustained contact (leaning or sitting against the robot for hours), which is not a credible case at 35 °C. Recorded as a residual risk, not a fail.
- **Conditions for the PASS:** (a) grille inner face ε ≤ 0.1 (foil/bare or a metallised film); (b) slots ≤ 5.0 mm max; (c) low inlet + high outlet each ≥ 1200 mm² free, so the exhaust is not forced through the face grille (route the outlet away from the main touch zone, aft/outer, above z 792); (d) firmware derate active (75/85/90 °C, R-136); (e) the fairing over the knee housing measured as a touch point (90–100 °C case behind it, not modelled here).
- **Mass:** P-154 guard dropped, −0.041 kg (Thermal). Any grille/foil mass belongs to ID/Legs (fairing line), not T&R.

The original rev 3 analysis below is kept for the record; its guard spec is superseded.

---

**Verdict: FAIL.** At 71.5 °C (duty, h 8) the bare black-anodised 6061 fins are above the ISO 13732-1 burn threshold at **every** contact time from 1 s up, and they reach 95.8 °C in continuous carry before the derate. **A perforated guard is required** (R-143 §2b). Spec below; Thermal must re-check UA with the guard.

## Inputs (repo)
- Fins: knee plate rev 3 (Actuators D91, `actuators/results/DRIVE_HEAT_PLATES.md` §Rev 3; R-143): 6061-T6, **black-anodised** outer face, 8 fins × 13 mm × 1 mm at 6 mm pitch (5 mm gaps), 100 mm long, protruding 13 mm beyond the L51 box; thermal basis h 8 needs ≥ 10 mm of clear air (Thermal R131 rev 2).
- Temperatures: **71.5 °C duty (h 8)**; 73.8 °C at the 12 mm fin minimum; continuous carry **95.8 °C at h 8** (held by the R-096 duty limit + firmware derate from 75 °C, 50 % at 85, off at 90 heat-sink, R-136) and 76.1 at h 12. Fin efficiency 0.995, so the tips are at the base temperature.

## ISO 13732-1:2006 thresholds (cited honestly)
| contact time | uncoated metal threshold | source / certainty |
|---|---|---|
| 1 s | spread ≈ **65–70 °C** | Fig. 2 is a graph, not a table; values read from the figure as widely quoted [UNCERTAIN ±1–2 °C] |
| 4 s | ≈ **58–61 °C** | read from Fig. 2 [UNCERTAIN] |
| 10 s | ≈ **55–56 °C** | read from Fig. 2 [UNCERTAIN] |
| 1 min | **51 °C** | Table 1 (verified: ISO 13732-1 preview text; CENELEC Guide 29 Table A.1; BAuA Tab. 5.1-1) |
| 10 min | **48 °C** | Table 1 (verified) |
| 8 h+ | **43 °C** | Table 1 (verified; applies only if < 10 % of skin touches) |
- Rough metal: up to +2 °C above the upper spread limit (§4.2.1.2). Black anodise (typ. 10–25 µm) is thinner than the thinnest coating the standard credits (lacquer 50 µm, Fig. 3), so **no coating rise is credited: treat as uncoated metal.** Table 1 gives the same values for coated metal at ≥ 1 min.
- Sources: ISO 13732-1:2006 §4.2 (preview, standards.iteh.ai / previewnorm); CENELEC Guide 29 Annex A; BAuA "Heiße Medien/Oberflächen" (DIN EN ISO 13732-1 table).

## Check
| contact | threshold | fins 71.5 °C | fins 95.8 °C (carry) |
|---|---|---|---|
| 1 s (brush-past) | 65–70 (max 72 rough) | **FAIL** (above the upper limit for smooth metal; at the rough-surface ceiling) | FAIL |
| 4 s (hand on knee) | ~58–61 | FAIL | FAIL |
| 10 s (steadying/helping the robot) | ~55–56 | FAIL | FAIL |
| 1 min / 10 min / 8 h | 51 / 48 / 43 | FAIL | FAIL |
Relevant contact times for people around a walking humanoid: accidental brush 0.5–1 s; deliberate hand on the leg (assist, catching, a child touching) 4–10 s; leaning or sitting against a standing robot ≥ 1 min. Even the most lenient case fails at duty. Fins also have 5 mm gaps: a finger enters between them (two-sided contact, worse than a flat plate).

## Guard spec (required)
- **Material:** thermoformed **PC 1.5 mm** (the cover-set material, P-020/R-029; Tg ≈ 147 °C, fine at 96 °C fin radiation), black or cover colour. Plastic contact thresholds are higher (Table 1: 60 °C at 1 min), but the target below is set on the 10 min value anyway.
- **Geometry:** a perforated cap over the fin field, open at both ends along the leg axis (fin channels run axially, so walking flow passes through).
  - **≥ 10 mm clear air between the fin tips and the guard inner face** (Thermal's h 8 basis), wall 1.5 → guard outer face ≈ 24.5 mm beyond the L51 box (was 13). Side walls ≥ 10 mm from the outer fins.
  - Openings: longitudinal slots **≤ 5 mm wide**, ≥ 3 mm webs, **≥ 60 % open area** on the face. With the 10 mm gap, the IEC 61032 test finger (probe B, ø12 mm) cannot reach a fin.
  - Mounting: 4 bosses on the **thigh shell/structure, not the heat plate**, with PC or PEEK spacers (no metal bridge from the plate). Snap or 4 × M3 nylon/steel into shell inserts.
- **Touchable-surface target:** guard outer face **≤ 48 °C** (ISO 13732-1 10 min, any material) at 35 °C ambient and the worst fin case, and **≤ 43 °C** at 25 °C ambient at duty (8 h value, the robot can be leaned on).
  - Hand estimate (`r143_guard.py` → `r143_guard.json`, radiation + both-side convection h 8, warm plume +5 K) [EST]: duty 71.5 °C → **34 °C** at 25 ambient / **43 °C** at 35 ambient; carry 95.8 °C (derate-limited) → 40 / **48 °C**. **Passes, but with 0 margin at 35 °C ambient + continuous carry.** At standstill (natural convection h ≈ 4) the guard runs warmer: firmware must keep the derate active, and G5 TP-G5-15 measures it.
- **Mass:** about 18 g per knee [EST: face 110 × 60 + sides 2 × 110 × 25 mm, 1.5 mm PC at 1.20 g/cm³, 60 % open on the face, + bosses] → **+0.04 kg robot**, booked at full per R-143 §2b.
- **Effect on fin cooling (Thermal must re-check UA, R-143 §2b):**
  - Convection: keeping ≥ 10 mm clear and open ends preserves Thermal's h 8 basis for the fin channels, but the slotted cap adds flow resistance. With 60 % open area the cross-flow component drops [EST 10–20 %].
  - Radiation: the guard intercepts about 40 % of the fin field's view to ambient (solid fraction) and radiates back at ~35–48 °C.
  - **Expected UA loss 5–10 % [EST] → 0.203 → ~0.183–0.193 W/K vs 0.185 needed.** That is marginal: rev 3 has only 1.2 K margin at 12 mm fins. If Thermal's re-check fails, the options are: longer fins (protrusion grows), h 12 vent flow credit, or a lower duty limit.
- **Knock-on:** the protrusion grows by about 11.5 mm. R-143 §2a (ID/Legs ROM sweep with ≥ 3 mm, knee 0–145°, leg-to-leg, seated, kneeling) and §2c (fall/side impact) must be run **on the guarded envelope**. The guard should be the sacrificial fall part (PC deforms, fins protected), which may help §2c.

## Actions
- Thermal: UA re-check with the guard (geometry above) — R-143 §2b.
- Actuators/ID: guard CAD on the thigh shell; Legs/ID: §2a/§2c sweeps on the guarded envelope.
- Arbiter: book +0.04 kg at full when the CAD lands.
- T&R: G5 TP-G5-15 (below and in G5_TEST_PLAN.md).
