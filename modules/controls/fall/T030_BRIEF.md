# T-030 brief: A44 side-fall push-fall batch (Grok Build, **bryan PC ff639f5a only, never DESKTOP-B115PVV**)
Owner: RL Controls. Gate for R-042 (A44 provisional). CPU only, MuJoCo ≥3.1, numpy. No jax, no training. Expected wall time is a few minutes per batch: smoke runs take about 0.2–0.6 s each on the box.

## 000000. R-072 + Arms R7 + R-076 (2026-10-14). **Gate batches supersede §00000**
### R-072 pad peak (Arbiter; Materials 953cd46)
- **9.17 kN is the absolute pad peak, including any initial peak** (option b). Lot cert rejects any coupon with initial peak > **1.00×** its plateau, or upper-bound×1.30 > 9.17 kN.
- **Gate T-030 on peak ≤ 9.17 kN absolute** (→ M = F × 0.064 ≤ 587 N·m at the new lever; vs CRBH 7013 A 550 N·m gate at the old 0.06 m lever — see lever note). Pitch-bearing gate kept as **F ≤ 9.17 kN** and **fs radial ≥ 1.25** at the lever in use.
- **`--spike 1.05` batches are fault-only (non-gating).** Pre-crush remains mandatory; 2.2× spike stays fault-only.

Hand estimate with **Arms R7 lever 0.064 m** to the shoulder_pitch bearing (pad on roll-yaw link):

| case | F | M = F×0.064 | vs 550 N·m @0.06 | notes |
|---|---|---|---|---|
| floor 7.31 kN, 0° | 7.31 | 468 | pass | |
| floor 15° (×0.93) | 6.80 | 435 | pass | E = 293.7 J ≥ 292 (+0.6 %, thin) |
| ceiling 9.17 kN | 9.17 | **587** | **over 550 at old 0.06; pitch moment rises with lever** | F gate still 9.17; flag to Actuators/Arms |
| 1.05× on 9.17 (fault) | 9.63 | 616 | fault-only | lot rejects >1.00× |

**Roll bearing (CRBH 6013 A, C0 24.3 kN):** e ≤ 0.010 m from pad centre to roll-bearing plane; log `CRBH_s0` (pass ≥ 2).

### Arms R7 geometry / timing
- **Pad mount:** roll-yaw link (upper_arm), not the shoulder-cap housing. Script `pad_points` uses `L/R_upper_arm`. Lever to pitch bearing **0.064 m**; e ≤ **0.010 m**.
- **Forward tuck = B (+5/0/0/0)** confirmed (96 mm behind old chest front; forearm 133 mm to torso; fairing 35 mm to pelvis; hand ~50 mm to thigh). Pitch −30 tuck **withdrawn**.
- **Hook release 0.12–0.22 s** (not 50 ms). `--release-s` default **0.22** (worst).
- **Logged outputs (pass tables):** `shoulder_pitch_gear_peak_Nm`, `CRBH_s0` (+ pass ≥2), `hand_thigh_min_m`, `outside_core` count.
- **Interim soft limit:** shoulder_roll ≤ **135°** (`limits/soft_limits.json`), pending head sweep.
- **Forearm +15 mm (R-076/R8):** re-run reach and `tuck_search` when Arms lengthens the forearm (up to +15 mm → ~285–287 mm). Sensitivity note below.

### R-076 pad crush-axis vs ground (pad on roll-yaw link)
FK tip ~85° toward impact, crouch, pad normal = upper_arm ±y:

| pose | dir | off-axis deg | vs 15° | note |
|---|---|---|---|---|
| **B** | side L/R | **~10** | **PASS (+5°)** | roll +5° is the offset |
| **B** | F | ~90 | n/a (chest pad) | shoulder pad not the forward stop |
| **B** | LF/LB/RF | **~63** | **FAIL** | needs roll offset or pad-face wedge ~50–60° |
| **R5** | side L/R | **~62** | **FAIL** | yaw −60° rotates pad off lateral |
| **R5** | F / diag | 37–120 | FAIL | R5 not for pad-on-link forward |

**Fix if side/diag exceeds 15°:** for pure side, set fall-side roll ≈ **−5°** (zeros B side angle). Diagonals need a commanded roll that aligns the pad with the impact plane, or a fixed pad-face wedge; R5 yaw must be reduced for side falls with the link-mounted pad (or keep a housing-cap mount for side only — not the R7 baseline).

### Gate batches (R-072)
```
python $F --pad hc --hc-plateau 7310 --hc-stroke 0.0432 --dirs L,R,LB,LF --out $O/t030_hc7310_gate_tuck.jsonl                 # GATE
python $F --pad hc --hc-plateau 7310 --hc-stroke 0.0432 --dirs L,R,LB,LF --carry --out $O/t030_hc7310_gate_carry.jsonl         # GATE
python $F --pad hc --hc-plateau 9170 --hc-stroke 0.0432 --dirs L,R,LB,LF --out $O/t030_hc9170_peak.jsonl                       # GATE (absolute peak)
python $F --pad hc --hc-plateau 7310 --hc-stroke 0.0432 --dirs L,R,LB,LF --spike 1.05 --out $O/t030_FAULT_hc7310_peak105.jsonl # FAULT
python $F --pad hc --hc-plateau 9170 --hc-stroke 0.0432 --dirs L,R,LB,LF --spike 1.05 --out $O/t030_FAULT_hc9170_peak105.jsonl # FAULT
python $F --pad hc --hc-plateau 7310 --hc-stroke 0.0432 --spike 2.2 --out $O/t030_FAULT_hc7310_spike22.jsonl                   # FAULT
python $F --pad hc --hc-plateau 9170 --hc-stroke 0.0432 --spike 2.2 --out $O/t030_FAULT_hc9170_spike22.jsonl                   # FAULT
```

## 00000. Materials 48f55c3 update (2026-10-14). **Gate batches supersede §0000**
Core model: **7.31–9.17 kN at 0° (×0.93 at 15°), stroke up to 43.2 mm**. Pre-crush plus a lot cert with **no initial peak above 1.05× plateau** are mandatory.

Hand estimate (CRBH 7013 A, C0 27.7 kN, Dpw 85 mm [EST], M = F × 0.06):

| case | F | energy (× 43.2 mm) | M N·m | fs radial | vs gate |
|---|---|---|---|---|---|
| floor 7.31 kN, 0° | 7.31 kN | 315.8 J | 439 | 1.57 | pass |
| **floor at 15° (×0.93)** | 6.80 kN | **293.7 J** | 408 | 1.69 | **≥ 292 J: pass (+0.6 %, thin)** |
| ceiling 9.17 kN, 0° | 9.17 kN | 396 J | 550 | 1.25 | at the limit |
| 1.05× initial peak on 7.31 | 7.68 kN | — | 461 | 1.50 | pass |
| **1.05× initial peak on 9.17** | **9.63 kN** | — | **578** | **1.19** | **FAIL 9.17 kN / 550 N·m** |
| 2.2× spike (fault, un-pre-crushed) | 16.1–20.2 kN | — | 965–1210 | 0.71–0.57 | fail (fault case) |

**Flag:** a cert allowing 1.05× initial peak is only compatible with the 550 N·m limit if the plateau ceiling is ≤ 9.17/1.05 = **8.73 kN**, or if the peak is defined as including the initial peak. Materials/Arbiter should decide which.

Batches (replace the §0000 gate lines; directions L,R,LB,LF):
```
python $F --pad hc --hc-plateau 7310 --hc-stroke 0.0432 --dirs L,R,LB,LF --out $O/t030_hc7310_gate_tuck.jsonl                 # GATE
python $F --pad hc --hc-plateau 7310 --hc-stroke 0.0432 --dirs L,R,LB,LF --carry --out $O/t030_hc7310_gate_carry.jsonl         # GATE
python $F --pad hc --hc-plateau 7310 --hc-stroke 0.0432 --dirs L,R,LB,LF --spike 1.05 --out $O/t030_hc7310_peak105.jsonl       # GATE (1.05x initial peak)
python $F --pad hc --hc-plateau 9170 --hc-stroke 0.0432 --dirs L,R,LB,LF --out $O/t030_hc9170_peak.jsonl                       # GATE (peak load)
python $F --pad hc --hc-plateau 9170 --hc-stroke 0.0432 --dirs L,R,LB,LF --spike 1.05 --out $O/t030_hc9170_peak105.jsonl       # GATE (expected to fail, see flag)
python $F --pad hc --hc-plateau 7310 --hc-stroke 0.0432 --spike 2.2 --out $O/t030_FAULT_hc7310_spike22.jsonl                   # FAULT, non-gating
python $F --pad hc --hc-plateau 9170 --hc-stroke 0.0432 --spike 2.2 --out $O/t030_FAULT_hc9170_spike22.jsonl                   # FAULT, non-gating
```
The 2.2× runs in §000 are relabelled **fault cases (non-gating)**. T-031 batches use `--hc-plateau 7310 --hc-stroke 0.0432` (the pad doesn't drive the forward-fall result).

## 0000. R-065 update (2026-10-14). Supersedes earlier gates where they differ
- **Pad energy gate: ≥ 292 J at worst case AND at the 15° limit** (≥ 10 % over 265 J).
  - Capacity = F_low × 0.93 × stroke. At 6.95 kN that requires **stroke ≥ 292 / (6.95 kN × 0.93) = 45.2 mm** (44.3 mm if the 0.93 is normalised to the 0.98 head-on ratio).
  - The current 38 mm gives 245.6 J (×0.93), so it fails the gate until ID/Materials' longer core lands.
  - The stroke is parameterised: `--hc-stroke <m>`. Summary fields: `E_cap_worst15_J`, `E_cap_gate_ok`. Peak stays ≤ 9.17 kN / 550 N·m.
- **Shoulder-pitch ≤ 369 N·m momentary is now a pass criterion in every mode** (`gear_pitch_max`).
- **Diagonals added:** LB (rear-left) was already in; LF (front-left) added.
- **Gate batches (stroke placeholder 0.045 until ID's number lands):**
```
python $F --pad hc --hc-plateau 6950 --hc-stroke 0.045 --dirs L,R,LB,LF --out $O/t030_hc6950_gate_tuck.jsonl
python $F --pad hc --hc-plateau 6950 --hc-stroke 0.045 --dirs L,R,LB,LF --carry --out $O/t030_hc6950_gate_carry.jsonl
python $F --pad hc --hc-plateau 9170 --hc-stroke 0.045 --dirs L,R,LB,LF --out $O/t030_hc9170_peak_tuck.jsonl
```
- The side-fall tuck stays R5. A/B/D (T-031) put the forearm under the hip in a side fall, so they're not used for side falls until T-031 picks a pose.
- **Box smoke** (single untuned runs, not results): LF with R5 logged 374 N·m on the pitch gear, which is above 369. The diagonal is a real risk.

## 000. R-057 + Materials fd46ad8 update (2026-10-14). **Supersedes §00 and §0 where they differ**
- **Reach mode and all clutch-slip credit removed (R-057, D77: no shoulder clutch).** The R5 tuck is permanent for every fall, and hands-first braces are not allowed. `--arm` now accepts only `tuck`. Forward falls move to **T-031** (`T031_BRIEF.md`).
- **Honeycomb (Materials R042_EPP_SHOULDER.md Part 3):**
  - Lot-tested, pre-crushed 2–3 mm cores give no start spike (assumed). Modelled band: **6.95–9.17 kN, 38–42 mm stroke**. The datasheet band (6.0–10.6 kN) fails.
  - Off-axis plateau ratio: 0.98 at 0°, 0.93 at 15°, 0.73 at 25°. The script scales the plateau by ratio(θ)/0.98, interpolated linearly. Above 25° it holds 0.73 and flags `angle_beyond_25_unknown` (= fail).
  - **Angle limit: p95 `impact_angle_deg` ≤ 15°** (pass criterion).
- **Hand estimate** (CRBH 7013 A, M = F × 0.06):

| case | F | stroke | energy | vs 265 J | M N·m | fs radial |
|---|---|---|---|---|---|---|
| **gate: 6.95 kN, 38 mm** | 6.95 kN | 38 | **264 J** | **−0.4 %: marginal, technically 1 J short** | 417 | 1.66 |
| gate at 15° off-axis (×0.93/0.98) | 6.60 kN | 38 | 251 J | −5 %: fails the design point | 396 | 1.74 |
| peak: 9.17 kN, 42 mm | 9.17 kN | 42 | 385 J | ×1.45 | 550 | 1.25 |
| un-pre-crushed, 2.2× start spike, 6.95 kN | 15.3 kN | n/a | n/a | n/a | 917 | 0.75: **FAIL** |
| un-pre-crushed, 2.2× spike, 9.17 kN | 20.2 kN | n/a | n/a | n/a | 1210 | 0.57: **FAIL** |

  - **Plainly:** the worst-case lot-tested cartridge stores 264 J. That's 1 J below the 265 J design point at 0°, and 14 J below at the 15° angle limit. The design point is not met with margin in the worst corner. The 220 J A44 nominal is still covered (×1.20).
  - Pre-crush plus the lot check are mandatory: a start spike breaks the bearing limit regardless of the controller.
- **Batches (replace §6 primary):**
```
python $F --pad hc --hc-plateau 6950 --hc-stroke 0.038 --out $O/t030_hc6950_s38_tuck.jsonl          # GATE (worst case)
python $F --pad hc --hc-plateau 6950 --hc-stroke 0.038 --carry --out $O/t030_hc6950_s38_tuck_carry.jsonl   # GATE (carry)
python $F --pad hc --hc-plateau 9170 --hc-stroke 0.042 --out $O/t030_hc9170_s42_tuck.jsonl          # peak load
python $F --pad hc --hc-plateau 6950 --hc-stroke 0.038 --spike 2.2 --out $O/t030_hc6950_spike22.jsonl  # sensitivity: un-pre-crushed
python $F --pad hc --hc-plateau 9170 --hc-stroke 0.042 --spike 2.2 --out $O/t030_hc9170_spike22.jsonl  # sensitivity
```
  - The `--arm reach` lines in §6 are void. The EPP contrast and no-fall-mode baseline stay.
  - **Gate (R-057/R-058/R-059):** hc6950_s38 tuck AND carry pass all of: stroke ≤ 38 mm, peak ≤ 9.17 kN, p95 angle ≤ 15°, 0 angle-unknown, p95 |centroid| ≤ 15 mm (the core footprint, R-059), 0 bypass, share p95 ≤ 0.40, crouch ≥ 0.15 m.
  - The spike batches are reported, not gating.
- New log fields: `shoulder_pitch_gear_peak_Nm` (|motor − armature·q̈ + limit-constraint| on both shoulder-pitch DOFs), `hc_stroke_mm`, `spike`, `angle_beyond_25_unknown`.
- **Box smoke** (single untuned run per config, not results): side and LB runs run end to end. One LB run logged 438 N·m shoulder-pitch gear peak with no pad contact. That's a hint that side/diagonal falls also need the pitch torque checked. T-031 covers it on forward falls, and the T-030 summary must also report `gear_pitch_max` against 369.

## 00. R-054 update (2026-10-14): ID pad R4 + Arms R5 tuck. **Supersedes §0 geometry**
- **Element = ID R4 cartridge (329a79a, accepted R-054):**
  - Core: HexWeb CR III 4.5 pcf, pre-crushed, 62 × 62 × 57 mm, 38.4 cm². Usable stroke = 0.72 × 57 = **41.0 mm**.
  - Face plate: Al 0.5 mm ribbed spreader, 80 w × 100 h, centre 5 mm below the shoulder axis, plus a 6 mm EPP cosmetic face (no energy credit). Stack about 63.5 mm.
  - Plateau: 1.79 MPa × 38.4 cm² = **6.88 kN at ×1.0, 8.94 kN at ×1.3**. Pair mass **0.095 kg**.
- **Mount:** the shoulder-cap shell outboard of the roll housing, about y +0.30 in the torso frame (Arms R5 7f0ff7a §3). In sim that's 0.13 m outboard of the shoulder-pitch joint, on the pitch-output body.
- **Lever:** the 0.06 m impact-to-bearing lever is **unchanged** because Arms R5 gives no new value. **But the cap mount moves the load path outboard of the roll housing, so Arms/Actuators must confirm the lever** before G3.
- **Hand estimate (CRBH 7013 A, C0 27.7 kN, Dpw 85 mm [EST], M = F × 0.06):**

| plateau | energy (× 41.0 mm) | vs 265 J | M N·m | fs radial / axial |
|---|---|---|---|---|
| 6.88 kN (R4 ×1.0) | 282 J | ×1.06 | 413 | 1.67 / 2.17 |
| **7.05 kN (gate batch)** | 289 J | ×1.09 | 423 | 1.63 / 2.12 |
| 8.94 kN (R4 ×1.3) | 367 J | ×1.38 | 536 | 1.28 / 1.67 |
| 9.17 kN (limit) | 376 J | ×1.42 | 550 | 1.25 / 1.63 |

  - The 7.05 kN batch stays the gate (R-054). The R4 ×1.0 plateau is 6.88 kN, about 2 % lower, so an extra 6.88 kN batch is added as a check.
  - Contact band: the contact centre must stay ≤ 15 mm from the core centre (ID R4). That is the pass limit on `contact_centroid_mm`.
- **Tuck (Arms R5, 8.6 mm clear):** shoulder_roll −5°, shoulder_yaw −60°, shoulder_pitch −20°, elbow −110° (mirrored for the right arm). Yaw −90° and pitch 0° clash. Implemented in the script.
- **Carry (P-042):** FALL-mode sequence is detect → **release the hook load** → arm tuck (legs start the knee drop immediately).
  - `--carry` models 20 kg as 98 N down at each hand until release.
  - `--release-s` defaults to 0.05 s [EST]; Arms to confirm.
  - `t_release` is logged.
- **Forward falls: tuck, no brace** (a hand brace above ~605 N exceeds the CSG-25 369 N·m). `--arm reach` is applied **only on pure side directions (L, R)**. LB is always tucked. `arm_used` is logged.
- **Motor map check:** `controls/thermal/winding_model.py` already uses shoulder_yaw 06008C, elbow 05013C, wrist_roll 05008C, so no fix is needed. The iron-loss coefficients for 05013/05008 use the 06008 values as a proxy [EST].
- **Box smoke** (one 80 N·s L fall, untuned, sim mass 69.5 kg): with the cap mount the element is the first contact. In that one run it took 98 % share, 325 J, bottomed past 41 mm, and peaked at 13.1 kN. With carry: release at +50 ms, 400 J, bypass contact. **Not results**, but a warning: the controller must actually move energy off the shoulder (crouch, hip-first), otherwise even 289 J is exceeded.

## 0. R-049 update (geometry superseded by §00) (2026-10-14): honeycomb crush element is primary
- Arbiter R-049 adopted a constant-force crush element. RL Materials (8a3cc66): **4.5 pcf pre-crushed 5052 Al honeycomb, ≈63 × 63 × 57 mm per side, plateau 7.05–9.17 kN, usable stroke ≤ 41 mm, pair ≈ 0.068 kg.** Strength drops off-axis, so impact-point scatter and angle across the 63 mm face are logged.
- **Hand estimate:**

| plateau | energy capacity (× 41 mm) | vs 265 J design point | bearing M | CRBH 7013 A fs radial / axial |
|---|---|---|---|---|
| 7.05 kN | **289 J** | ×1.09 | 423 N·m | 1.63 / 2.12 |
| 9.17 kN | **376 J** | ×1.42 | 550 N·m | 1.25 / 1.63 |

  - A44's S3 energy (216–220 J) uses 24–31 mm of stroke at 7.05 kN and 24 mm at 9.17 kN. The 289 J floor still covers the 265 J design point, with only 9 % margin at the low plateau.
  - Moment is set by the plateau, not the energy, as long as the stroke stays ≤ 41 mm. So the share ≤ 0.40 gate now matters mainly to keep the energy ≤ 289 J.
  - **Assumptions:** the plateau is assumed flat over the full 41 mm, with no peak at crush onset because the core is pre-crushed (Materials). The off-axis strength loss isn't quantified yet (Materials to supply a limit). The rate effect is taken as covered by the 7.05–9.17 kN band.
- **Roll-clutch slip gets credit only if T-030 shows it** (R-049). `W_arm_backdrive_J` is logged for that.
- **EPP data past 75 % strain is unknown** (Materials 8a3cc66). Any EPP run crushing past 75 % is flagged `beyond_data_unknown` and counts as **FAIL/UNKNOWN**. The script holds force at the 75 % value there; it does not extrapolate. (§2's EPP sizing table used an extrapolation beyond 75 %. Treat the 120 mm / 83–85 mm figures as indicative only.)

## 1. What changed since A44 (EPP history, contrast only) (read first)
| pad model | source | 40 mm pad at 220 J (shoulder) | bearing M | CRBH 7013 A fs radial |
|---|---|---|---|---|
| constant 7.10 kN plateau, s 31 mm | ID SHOULDER_PAD.md (d80df32) | 7.10 kN | 426 N·m (−22.6 % vs 550, arithmetic checks) | 1.65 |
| **ARPRO 5170 curve 0.50/0.70/1.60 MPa @ 25/50/75 %, ×1.45 rate, 109 cm²** | Materials R042_EPP_SHOULDER.md (5f8f149) | **≈19.1 kN** at 64 % strain | **≈1150 N·m** | **0.60** (axial 0.78) |

The curve is authoritative. ID's 426 N·m is valid only for a constant-force element.

## 2. Hand estimate with the curve (`epp_pad_estimate.py` → `epp_pad_estimate.json`)
- **40 mm, 109 cm², at the A44 S3 energy (215.6 J, i.e. the "539 N·m" case): F ≈ 18.8 kN, M ≈ 1129 N·m, fs 0.61 radial / 0.79 axial. FAIL.** At 220 J: 19.1 kN, 1149 N·m, fs 0.60.
- Energy the 40 mm pad takes before the 9.17 kN gate (M = 550) is **≈ 74 J** (35 % strain). At 80 J: 9.39 kN → 563 N·m, fs 1.22, just over the limit. Materials' "≈7 kN to ≈80 J" is the quasi-static figure; with ×1.45 it's ≈9.4 kN. So **the controller target is ≤ ≈74 J**, not 80.
- At 7.10 kN the pad takes only ≈32 J.
- **Pad needed for 220 J at ≤ 9.17 kN (EPP 80 curve):** about **83–85 mm thick at 60–80 cm²**, 120 mm at 109 cm². At ≤ 7.10 kN: 107 mm at 60 cm², 136 mm at 80 cm². That's 2–3× ID's 40 mm. The volume (and mass, ×~2) breaks the R-042 0.10 kg cap.
- **Bearing alternative with the 40 mm pad kept at 220 J:** fs 1.25 radial needs C0 ≈ 57.7 kN. CRBH 8016 A (43.4 kN) is **not enough**. The next IKO size meeting it is CRBH 10020 A (C0 72.2 kN, 1.45 kg per the CAT-57151 table): **not credible** for the budget.
- **Better hardware path:** a constant-force crush element (aluminium honeycomb / crush tube, Materials + ID R2). A44's 539 N·m then holds as computed.

## 3. Can the controller cut the shoulder energy to ≈74 J (80 J)?
E_sh = share × m·g·zc with m 66.36 kg (R-043), m·g = 651 N.
- **Need share × zc ≤ 0.114 m** (0.123 for 80 J).
  - Crouch to zc 0.83 (A44, 0.15 m drop): share ≤ **0.14** (0.15).
  - Crouch to zc 0.68 (0.30 m drop): share ≤ **0.17** (0.18).
  - Crouch to zc 0.60 (0.38 m): share ≤ **0.19** (0.20).
- **Geometry says shoulder-first, not hip-first** (sim/v3 bodies): the shoulder lateral face (upper-arm capsule outer edge at y 0.322 + pad) sits **0.177 m + pad** further out than the pelvis side (0.185). Hip contact first needs the trunk leaned **≥ ~28° (30 mm pad) / ~29° (40 mm)** away from the fall side, relative to the pelvis, at a 0.34 m hip-to-shoulder height. v3 has **no waist roll DOF**: only hip roll (12–15° range) can do it. **A share of 0.14–0.19 from crouch plus lean alone is not plausible in a ~0.5–0.7 s fall** [EST]. A 0.30–0.38 m crouch is also beyond the A44 ≥0.15 m assumption.
- **Staged arm contact is the only controller lever large enough:** the fall-side arm abducted, hand/forearm landing first, with the shoulder_roll output backdriving or slipping at a capped torque (v3 300 N·m roll clutch; the sim actuator cap is 164 N·m).
  - Dissipation ≈ τ_slip × Δθ. **Taking 216 → 74 J needs ≈142 J ≈ 300 N·m × 0.47 rad** (0.87 rad at 164 N·m).
  - Geometrically possible (an abducted arm has ~1.3 rad to sweep) [EST].
  - Costs: the hand/wrist takes ≈ 300/0.6 m ≈ 500 N, clutch slip life is unverified (v3 "UNVERIFIED clutch"), and pitch-gear load needs checking.
  - This reverses A44's "keep the arm out of the ground path". **T-030 tests it (`--arm reach`).**
- Bottom line: ≈74 J is **not credible from crouch/lean alone**. Possible only with staged arm-clutch dissipation, unproven until T-030. Recommended plan: run T-030 for both arm modes, and in parallel ask Materials/ID for a constant-force crush element.

## 4. Questions answered (from ID and Materials)
1. **Contact point during the arm tuck:** in sim/v3 the upper-arm body sits 0.112 m lateral of the shoulder-pitch joint (capsule r 0.04). The lateral-most surface is the **upper-arm/roll-housing face at shoulder-joint height (z ≈ 1.46–1.50 m standing)**, so a tucked arm does not move inside the pad. My geometric estimate: contact lands **at or slightly above the pad centre** on the lateral face. With the trunk tilted 10–15° toward the hip (hip-first), the domed face first touches about 10–15 mm **below** centre (toward the hip), 52 mm × sin 12° [EST]. The smoke run logged centroid offsets of ≈ −10/+12 mm (x/z), consistent with near-centre contact, but it's one untuned run. **T-030 logs `contact_centroid_mm` per run** (pad-local x fore-aft, z up). If |z| > 30 mm in the p95, the pad moves.
2. **+10 mm width:** the topple pivot is the foot edge, unchanged. Final rotation at contact is ≈ 0.4° less (10 mm at ~1.5 m). Impact comes ≈ 1.6 ms earlier at ~6.4 m/s, and potential energy changes < 1 %. Knee-drop timing is effectively unchanged. But it adds ~1° to the trunk lean needed for hip-first.
3. **Design margin above 220 J:** a 60 N·s side push on 66.36 kg gives Δv 0.90 m/s → +27 J translational KE, ×0.40 share → **+11 J on the shoulder** (more if lateral walking velocity adds, ~0.1–0.2 m/s sway [EST], +0.3–1.3 J). Walking forward at 1.2 m/s is mostly orthogonal to a side fall; a twisting/diagonal fall is covered by direction LB below. Model uncertainty (rigid topple, share) is larger. **Recommend designing for 265 J (220 × 1.2, covering +11 J push and ±~10 % model error).** With the EPP curve that is irrelevant until §3 is solved.

## 5. Setup (bryan PC)
```
cd <robot-lab clone> && git pull origin main          # needs commit with modules/controls/fall/t030_pushfall.py
python -m venv .venv-t030 && .venv-t030\Scripts\activate   # (Linux/mac: source .venv-t030/bin/activate)
pip install "mujoco>=3.1" numpy
python modules/controls/fall/t030_pushfall.py --smoke       # one fall, must print a JSON line + summary
```

## 6. Runs (each 50 push-falls × 3 directions L, R, LB(45° rear-left); impulse uniform 40–80 N·s on pelvis over 0.1 s; seed 0)
```
F=modules/controls/fall/t030_pushfall.py; O=modules/controls/fall/results
# PRIMARY: R4 cartridge. Gate = 7050. Reach only applies on L/R.
python $F --pad hc --hc-plateau 7050 --arm tuck  --out $O/t030_hc7050_tuck.jsonl
python $F --pad hc --hc-plateau 7050 --arm reach --dirs L,R --out $O/t030_hc7050_reach.jsonl
python $F --pad hc --hc-plateau 7050 --arm tuck  --carry --out $O/t030_hc7050_tuck_carry.jsonl
python $F --pad hc --hc-plateau 6880 --arm tuck  --out $O/t030_hc6880_tuck.jsonl
python $F --pad hc --hc-plateau 8940 --arm tuck  --out $O/t030_hc8940_tuck.jsonl
python $F --pad hc --hc-plateau 8940 --arm reach --dirs L,R --out $O/t030_hc8940_reach.jsonl
# CONTRAST: EPP 80 curve (ARPRO 5170 x1.45, no data past 75 %) and plateau models
python $F --pad 40 --pad-model curve   --arm tuck  --out $O/t030_p40_curve_tuck.jsonl
python $F --pad 30 --pad-model curve   --arm tuck  --out $O/t030_p30_curve_tuck.jsonl
python $F --pad 40 --pad-model plateau --arm tuck  --out $O/t030_p40_plateau_tuck.jsonl
# BASELINE: no fall mode
python $F --pad hc --hc-plateau 7050 --arm tuck --no-fallmode --out $O/t030_hc7050_nofm.jsonl
```
If >20 % of runs show `crouch_at_impact_m` < 0.05 or no fall, sweep `--knee 0.9,1.2,1.5` on hc7050-tuck and report all three (don't tune further).

## 7. Measurements (per run, JSON line; last line = summary)
`shoulder_share` (pad work ÷ pad + all non-foot ground-contact work), `E_sh_J`, `E_other_J`, `crouch_at_impact_m` (mean leg hip→foot shortening, detection → first non-foot contact), `com_drop_at_impact_m`, `t_detect`/`t_fallmode`/`t_impact` (latency 50 ms [EST]), `pad_peak_N`, `pad_crush_max_mm`, `bottomed`, `M_bearing_Nm` (= peak × 0.06), `fs_radial`/`fs_axial` (CRBH 7013 A, C0 27.7 kN, Dpw 85 mm [EST]), `contact_centroid_mm`, `W_arm_backdrive_J`.

## 8. Pass criteria (per configuration; summary `PASS`)
- **Stroke:** max `pad_crush_max_mm` ≤ **41 mm** (honeycomb). For EPP: ≤ 75 % strain, else UNKNOWN = fail.
- **Peak force:** max `pad_peak_N` ≤ **9.17 kN**, so `M_bearing_Nm` ≤ 550 and fs radial ≥ 1.25.
- **Impact within the face:** `bypass_contact` = 0, i.e. no torso, upper-arm or shoulder body touches the ground while the element is loaded. Also log `impact_angle_deg` / `peak_angle_deg` (element normal vs vertical) and `contact_centroid_mm` (x, z on the 63 mm face). Report p95 angle and p95 |centroid|. The angle limit is pending Materials' off-axis knockdown; the run fails if p95 |centroid| > **15 mm** from the core centre (R4).
- **Shoulder share:** p95 `shoulder_share` ≤ **0.40** (R-042).
- **Crouch:** min `crouch_at_impact_m` ≥ **0.15 m**.
- **Arm credit:** `W_arm_backdrive_J` counts only if the reach mode passes everything above.

R-042/R-049/R-054 passes if **hc7050-tuck AND hc7050-tuck-carry** pass (the worst-case low plateau has the least stroke margin), or if **hc7050-reach** passes with the arm credit shown. EPP and plateau runs are contrast only.

## 9. Results to return
Commit `modules/controls/fall/results/t030_*.jsonl` plus a `results/T030_SUMMARY.md` table (one row per config: runs, fell, share p50/p95, E_sh p95, crouch min/p50, peak N max, M max, fs min, bottomed, centroid z p95, W_arm p50). Report the hash to RL Controls and Robot Lab.

## 10. Model limits (state in the summary)
- Honeycomb = 3×3 point patch over the 63 mm face, outer face 57 mm proud, flat plateau to 41 mm then a stiff stop (2e6 N/m) [EST]; off-axis knockdown not modelled. EPP pad = 3×3 point patch (105 mm square) on the shoulder-pitch output body, 0.152 m lateral of the joint [EST: from sim/v3 arm offset]. Forces are applied with xfrc_applied; friction 0.8 [EST].
- Partial-edge contact loads only the touching points, so peak force can be below the full-area curve.
- Scripted (untuned) fall controller with joint PD and torque caps from the MJCF.
- No waist roll DOF in sim/v3, and no shoulder-roll clutch model (the actuator cap of 164 N·m acts as the slip torque).
- sim/v3 mass 69.48 kg vs 66.36 credible (R-043), so energies are ~5 % high.
- Box smoke hc 9.17 kN tuck (one 80 N·s L fall, untuned): runs end-to-end. Stroke 14.7 mm, angle 7.4°, centroid −12/+6 mm, share 0.74, crouch 0.35 m. **Not results.**
- Earlier box smoke (2026-10-14, one 80 N·s L fall per pad, untuned): runs end-to-end. Numbers are **not results** (e.g. 40 mm curve: share 0.57, E_sh 91 J, peak 6.65 kN partial-edge, crouch 0.35 m).
