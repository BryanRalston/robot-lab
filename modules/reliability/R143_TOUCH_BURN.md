# R-143 §2b — Knee fins: ISO 13732-1 touch-burn check (RL T&R, 2026-10-21)

## ▶ Rev 4e update (09:40 ET) — outlet shroud + "no-sustained-contact" class: **CONFIRMED WITH CONDITIONS**
Sources: Thermal 218a541 (rev 4e shroud, H 0.18 → drive base 73.2 °C standing); ID P-156 rev 4e (`design/V5_COVER_SET.md` §P-156 rev 4e, `cad/covers/thigh_knee_vents.json`): shroud = v5 skin swelled +6 mm, 1.0 mm PC, outlet slot face recessed to x −71.5 → **17 mm standoff**, y 96–164, z 815–865, **closed bottom**, **open up (68 × 17 = 1156 mm²) and both upper sides (1530 mm²)**, outlet webs 28 mm behind the shroud skin. Knee-housing fairing slots 5 × 4.0 ± 0.3 × 20 per end (≤ 4.3 mm): the rev 4d IP2X gap is **closed**. Housing low-ε callout removed (foil on the fairing only), which resolves the rev 4d conflict. T&R recheck: `r143_rev4e.py` → `r143_rev4e.json`.

### 1. Shroud temperature recheck (35 °C ambient, standing hot, H 0.18)
Exhaust at H 0.18 ≈ 74–90 °C (the rev 4d 44–62 K rise scaled to the 73.2 °C base) [EST].

| mixing under the shroud | h_i 3 (lazy plume) | h_i 5 (plume attached to the inner face) |
|---|---|---|
| **1:1 dilution** (Thermal's ≥ 600 mm² low/side slots) | 39.5–41.4 | 41.5–44.2 |
| **no dilution** (ID's closed bottom, no low slots) | 44.0–47.7 | **48.0–53.4 FAIL** |
- Thermal's 41–43 °C is **confirmed only with the dilution slots**: worst 44.2 °C → **+3.8 K vs 48**, −1.2 vs 43.
- **ID's rev 4e drawing has a closed bottom and no dilution slots. That contradicts Thermal's spec, and the poor-mixing case fails 48.** The foil inner face (ε ≤ 0.05) is also not on ID's drawing (1.0 mm PC only). Without it, radiation from the 74–90 °C webs adds about 2–4 K.

### 2. IP2X / probe B reach — **FAIL as drawn**
- The open top (68 × 17 mm) and upper sides take the ø12 mm finger (the 50 mm sphere cannot enter the 17 mm gap). **Probe B's 80 mm reach does reach the outlet webs 28 mm behind the skin** (ID's json says so). The webs are washed on both sides by exhaust, so they sit **≈ 74–90 °C** (polymer). That exceeds IEC 62368-1 TS1 plastic for > 1 s (77) at the top of the range, and every ISO 13732-1 ≥ 10 s limit.
- **Fix (condition):** close the up/side openings with louvres or slots **≤ 5.0 mm** (4.5 nominal, same as the inlet), keeping ≥ 2600 mm² free. Or recess the outlet webs so probe B, through the opening, cannot touch any surface > 48 °C. Dilution slots ≤ 5 mm (Thermal) are fine.

### 3. Is the 10 min / 48 °C gate defensible for a "no sustained contact" zone? — **YES, with conditions**
- ISO 13732-1:2006 asks the assessor to take the **contact period that is reasonably foreseeable**, and gives thresholds per period: 1 s (unintentional touch with reflex withdrawal), up to 10 s (graph spread), 1 min 51, 10 min 48, 8 h 43 (Table 1). The **43 °C / 8 h** value is for prolonged contact, and the standard limits it to < 10 % of skin. It is not a default for occasional touch.
- **IEC 62368-1 Table 37 (TS1)**, the IEC 60950/60065 successor, uses exactly this banding for accessible surfaces: "surfaces that do not have to be touched (< 1 s)" metal 70 / plastic 94; "touched occasionally for very short periods (> 1–10 s)" 60 / 77; "held for short periods or touched occasionally (> 10 s–1 min)" 51 / 60; **"held or touched in normal use (> 1 min–< 8 h)" 48 / 48**; 43–48 only for **body-worn** devices > 8 h. CENELEC Guide 29 Annex A reproduces the ISO 13732-1 data and Table A.1 (51/48/43) for the same purpose.
- So gating a non-hand-hold zone at **48 °C** is the *1 min–8 h normal-use* limit in IEC 62368-1. It is conservative compared with the "touched occasionally" limits (51–77 °C), and 43 °C is the body-worn value. **Defensible.**
- **Caveats (become conditions):** ISO 13732-1's data are for healthy adult skin. Children, the elderly, or a person who cannot withdraw (pinned or fallen against the robot) can have longer contact; ISO 13732-1 and Guide 29 both warn about this. A robot that falls or sits on someone, or that a person leans against, turns "brief" into "sustained". This is why the zone has to be shown to be outside every handling/hold/lean case, and why 48 °C (not 51–77) is the right gate.

### 4. Is the upper-rear knee outlet zone outside the handling points? — **NOT DEFINED in the repo (gap)**
- Searched ID, Legs, Arms, Controls, CONTRACTS and the carry docs: **there is no handling / hand-hold / lift-point / rescue-grip map.** ID's rev 4e json says "away from the front/side hand-hold zones", but no document defines those zones.
- The T5/P-042 carry is the robot's own hook grasp of a payload (`arms/R5_ROUND.md`); it involves no human grip on the robot. Nothing designates the thigh as a carry or lift point.
- Foreseeable human contact at the upper-rear thigh: assisting a robot that is kneeling or prone, especially the **R-146 safe-sit prone end state** (rear thigh faces up and is the natural lift grip for a person righting it); a person beside a seated robot; being stepped against in a crowd.
- **Condition:** ID + Controls publish a handling map (lift/rescue grips, shove/assist zones, "no-hold" hot zones) in CONTRACTS or V5_COVER_SET, with the upper-rear thigh outlet marked **no-hold**, a lift/right-a-fallen-robot procedure that avoids it, and the hot-surface symbol (ISO 7000-0535 / IEC 60417-5041) on the shroud. After a prone fallback (MO = 0) the drives stop heating; TP-G5-15 measures the cool-down to ≤ 43 °C before rescue.

### Verdict and conditions
**CONFIRM** the "no-sustained-contact" class for the upper-rear knee outlet zone, gated at **48 °C** (ISO 13732-1 10 min; IEC 62368-1 TS1 > 1 min–8 h), **target 43 °C**, subject to:
1. Thermal's shroud spec built as written: **≥ 600 mm² low/side dilution slots (≤ 5 mm)**, **Al foil inner face ε ≤ 0.05**, ≥ 15 mm standoff (ID 17 ✓), ≥ 2600 mm² free (ID 2686 ✓). ID's closed-bottom, no-foil rev 4e drawing must change.
2. **IP2X:** up/side openings louvred ≤ 5.0 mm (or recessed) so probe B cannot touch the 74–90 °C outlet webs or any surface > 48 °C.
3. **Handling map** published with this zone marked no-hold, plus a hot-surface label. A rescue/lift procedure for the R-146 prone state avoids the zone.
4. **TP-G5-15** measures the shroud face, upper-side edges and webs (via probe), standing hot at 35 °C (≤ 48 °C, target 43), and the cool-down after a prone fallback.
5. If conditions 1–3 are not met, the zone reverts to the 43 °C gate, and the current drawing fails it (44–53 °C).

---
## Rev 4d update (09:25 ET) — CURRENT: baffle + aft/up outlet, foil under the knee-housing fairing, P-156 grille 4.5 mm slots
Sources: Thermal ec7b49d (rev 4d) and eef2728 (rev 4c, D94 plate), `thermal/R131_ELMO_MG.md`, `thermal/r131_rev4d_chimney.py`; ID P-156 a0b2aea (`design/cad/covers/thigh_knee_vents.*`, V5_COVER_SET.md). T&R recheck: `r143_rev4d.py` → `r143_rev4d.json` (same energy-balance approach as `r143_grille.py`) [EST].
Geometry:
- **Grille:** in the v5 rear skin at x −82.5, 104 × 52 mm, 8 slots **4.5 × 98 mm (≤ 5.0 incl. tolerance)**, 65 % open, Al liner ε ≤ 0.1 inside.
- **Fins and baffle:** fin tips at x −53.0, **29.5 mm** behind the grille inner face. Baffle 1 mm PC with Al tape on the fin side, at fin tips + 3 mm (≈ 26.5 mm behind the grille).
- **Inlet** z 643–681 and **outlet** z 799–837, 8 slots 4.5 × 36 each (1296 mm² free), with the outlet routed aft/up ≥ 30 mm from the grille top edge.
- **Knee-housing fairing:** 0.05 mm Al foil inside, gap ≥ 10 mm, ≥ 300 mm² slots top and bottom.
- **Basis:** Thermal rev 4c standing vented basis is **35 °C ambient**, drive base 76.2–78.5 °C (my rev 4b table wrongly took 35 °C as derate-capped at 87.5; corrected here). Pocket air mean +28–31 K, outlet air +44–62 K (Thermal's rev 4d table). Knee housing case 90–100 °C.

### 1. Independent temperature recheck
| touch point | Thermal | T&R recheck, 25 °C amb | T&R recheck, 35 °C amb | agree? |
|---|---|---|---|---|
| grille outer face (with baffle) | 37–39 | 27.3–28.6 | **37.2–38.5** | **yes** |
| baffle (not touchable, 26.5 mm behind the slots) | — | 43.7–47.2 | 53.9–57.3 | n/a |
| inlet grille webs (draw ambient air) | not given | 25.9 | **35.9** | — |
| **outlet grille webs (washed by exhaust air +44–62 K)** | **not evaluated** | **44.6–52.3** | **54.0–61.4** | **DISAGREE: new finding** |
| fairing over the knee housing (foil + ≥ 10 mm vented gap) | 40–41.5 | 31.6–32.5 | **40.6–41.5** | **yes** |
Model notes: grille = baffle radiation through ε 0.1 + cavity air (cavity breathing through the grille, exchange h 2–5); outlet webs = h 8 from exhaust inside, h 4 + ε 0.9 radiation outside; housing fairing = housing radiation through foil (ε_eff 0.049) + gap air (chimney through 300 mm², H 0.10).

### 2. IP2X / test-finger reach (P-156 geometry) — CONFIRMED for the grille, inlet and outlet; one gap at the knee-housing fairing
- IEC 60529 IP2X / IEC 61032 probe B (ø12 mm jointed finger, 80 mm reach) **cannot enter a 4.5 mm slot (≤ 5.0 with tolerance)**. Skin bulge ≤ 1–2 mm into the slot.
  - Grille: hot parts behind it are the baffle at ≈ 26.5 mm and the fin tips at 29.5 mm (fin roots ≥ 48 mm). **Unreachable.**
  - Inlet and outlet: same 4.5 mm slots in the same skin plane; the fin ends and duct sit ≥ 29.5 mm inboard (x −53 vs skin −82.5). **Unreachable.**
  - The 50 mm sphere of IP2X can't enter either. A rigid ø2.5–4 mm pin (probe C/13) would enter any slot: tool access, not a burn case.
- **Knee-housing fairing slots: width is not specified** in ec7b49d ("≥ 300 mm² slots"). The housing (90–100 °C) is only ≥ 10 mm behind them, so the finger must not enter. **Requirement: those slots ≤ 5.0 mm wide incl. tolerance** (4.5 nominal like P-156). Otherwise IP2X fails at the housing.

### 3. ISO 13732-1 verdict per touch point (worst case = 35 °C ambient, standing hot)
Limits as in the rev 3 section: 1–10 s metal spread 55–70 [graph, uncertain]; 1 min 51 (metal) / 60 (plastic); 10 min 48; 8 h 43 (Table 1, verified). The outer skins are plastic (PC/PA12, cover colour). I gate on the ≥ 1 min metal values (conservative) and give the plastic 1 min margin as well.

| touch point | worst T (35 °C amb) | vs 10 min 48 | vs 8 h 43 | vs 1 min 51 metal / 60 plastic | at 25 °C amb vs 43 | verdict |
|---|---|---|---|---|---|---|
| grille | 38.5 | **+9.5** | +4.5 | +12.5 / +21.5 | +14.4 | **PASS** |
| inlet | 35.9 | +12.1 | +7.1 | +15.1 / +24.1 | +17.1 | **PASS** |
| **outlet** | **54.0–61.4** | **−6.0 to −13.4** | −11 to −18.4 | −3 to −10.4 / +6 to −1.4 | −1.6 to −9.3 | **FAIL** |
| knee-housing fairing | 41.5 | +6.5 | **+1.5** | +9.5 / +18.5 | +10.5 | **PASS (thin vs 8 h)**, conditional on the slots ≤ 5 mm |

**Outlet fix (required; Thermal/ID to size):** the exhaust leaves at about 79–97 °C at 35 °C ambient, and fully developed channel flow leaves near fin temperature (Thermal rev 4d). Any touchable surface washed by it fails. Options:
- (a) Recess the outlet slots under an outer shroud, ≥ 10 mm standoff, open aft/up and ≥ 2 × the free area. The shroud entrains ambient air (about 1:1 dilution → web ≈ 44–48 °C at 35 °C [EST]). About +4 g/knee [EST].
- (b) A low-conductivity outlet screen of thin PC at h_i reduced by a stagnant standoff. Unproven.
- (c) Put the outlet where it can't be touched (under the fairing lip toward the knee pit, facing aft/down into the stream). That conflicts with chimney "high outlet" unless it is ducted.
- **T&R recommends (a), and the outlet webs ≤ 48 °C measured in TP-G5-15.** The exhaust air itself (≈ 80–97 °C, low velocity) on skin is outside ISO 13732-1 (surfaces only). Flagged for Thermal/ID: keep the outlet jet away from the hand-hold zones.

### 4. Other disagreements / conditions
- **Knee-housing low-ε face conflict:** P-156 (and Thermal rev 4b item 3) asks for a low-ε (≤ 0.1) knee housing face toward the pocket. Thermal rev 4d says **do not foil the housing** (its radiation is part of the knee rev B fin cooling, 4.7 K margin) and puts the foil on the fairing instead. **Thermal and ID must reconcile.** For touch, the fairing-foil route (rev 4d) is the one checked here.
- **Standing drive base margin is only 1.5–3.8 K** (76.2–78.5 vs 80 °C, rev 4c). TP-G5-15 now measures it inside the closed fairing. The baffle should not change it (Thermal: lost radiation ≈ 0), and that has to be verified.
- Mass (not T&R's line): baffle +0.014, fairing foil +0.012 (Thermal); P-156 +0.006 pair; outlet shroud (a) ≈ +0.008 pair [EST] if adopted.

---
## Rev 4b update (09:10 ET) — SUPERSEDED by rev 4d above: fins recessed behind a fairing grille, P-154 guard DROPPED
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
