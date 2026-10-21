# R-143 §2b — Knee rev 3 exposed fins: ISO 13732-1 touch-burn check (RL T&R, 2026-10-21)
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
