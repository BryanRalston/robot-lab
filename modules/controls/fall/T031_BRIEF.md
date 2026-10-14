# T-031 brief: forward fall with permanent tuck B vs shoulder-pitch gear + chest ≤ 38 g
Grok Build, **bryan PC ff639f5a only, never DESKTOP-B115PVV**. CPU MuJoCo on sim/v3. Same script and setup as T-030 (`T030_BRIEF.md` §5): `modules/controls/fall/t030_pushfall.py --dirs F`.

## R-102 / R10 tuck (side & diagonal shared with T-030)
- Side falls use **tuck B** (R5 retired). Forward stays B. Diagonals: B + waist yaw ±45° (see `fall_config.json`).
- Tuck B τ fall ≈ **351 N·m EST** at forearm 287 mm (5% vs 369). Script logs gear peak each run.
- LB waist-slow fallback: arm pose pitch/roll/yaw/elbow = +30/−15/+30/−75 (14.5°, ~283 N·m).

## R-088 / chest rev 2 / Arms R7 (2026-10-14). **Supersedes R-070 chest numbers**
### Chest pad (Torso `T031_chest_contact_r2.md`, Materials superseded)
- **Face 98 × 98 mm**, HexWeb CR III 5052 4.5 pcf, pre-crushed, lot-certified (R-072: no initial peak > 1.00× plateau).
- **Plateau:** 17.7–22.3 kN at 0°; **16.6–20.8 kN at 15°**. Ceiling **22.35 kN** → **35.6 g at 64 kg** (34.8 g at 65.4 kg) if full mass loads the pad.
- **Stroke need at 15° floor (16.6 kN):** **62 mm** → core thickness **88 mm** (Torso used 70 % usable). Materials' earlier 78 mm / 56 mm usable was for the pre-rev2 area — **rev2 deepens the core; usable stroke = 62 mm by design. Gate FAIL if crush > 62 mm (densification).**
- **R-088:** chest front / pad outer face **+37 mm** forward of sim/v3 torso box front (half-x 0.11). Script: `--chest-standout 0.037`. Most of the 88 mm core sits inboard of the old skin line.
- **Backing** rigid ~24 MN/m (negligible vs pad). Spring proxy only if needed: **k_eq 0.53 MN/m, ζ ≈ 1.0**. Prefer `--chest-plateau`.
- **Validity:** pad must seat on a backed bulkhead/pack face (Torso O-T14), not the bare 2 mm CF shell (fails at ~1–1.5 kN).
- Log: `chest_crush_max_mm`, `chest_bottomed`, `chest_impact_angle_deg`, `chest_angle_gt15`, `torso_peak_g`, `m_eff_kg` (F/(g·peak_g); ~64 kg body at 22.35 kN is ~39 g if whole mass loads — effective mass matters).

### Arms R7 / R-070 tuck
- **Primary = tuck B (+5/0/0/0)** confirmed in sim/v3: behind chest, forearm ~133 mm to torso, fairing 35 mm to pelvis, hand ~50 mm to thigh. Pitch −30 withdrawn.
- With R-088 +37 mm chest front: behind-chest margin **~96 → ~133 mm**. Forearm lengthening to **~287 mm** (R8 +15 mm): re-run `tuck_search` / reach (sensitivity below).
- Forward tuck B pitch-gear **~343 N·m EST** vs 369 (7 % margin, crude) — T-031 measures.
- **Remedy (b) contact pads:** Arms says **not needed with tuck B**, but **(b) stays as the R-070 waiver fallback** if 38 g fails.
- Hook release **0.12–0.22 s**. Soft abduction limit roll ≤ **135°**.

### PC batches (bryan PC ff639f5a only)
```
F=modules/controls/fall/t030_pushfall.py; O=modules/controls/fall/results
# bare shell (expected FAIL): spring proxy of unsupported CF
python $F --dirs F,LF,RF --tuck B --chest-k 46000 --chest-zeta 0.02 --out $O/t031_bare_shell.jsonl
# rev2 plateau floor (stroke / bottom-out check) — use 15° floor 16.6 kN
python $F --dirs F,LF,RF --tuck B --chest-plateau 16600 --chest-stroke 0.062 --out $O/t031_rev2_floor15.jsonl
python $F --dirs F,LF,RF --tuck B --chest-plateau 17700 --chest-stroke 0.062 --out $O/t031_rev2_floor0.jsonl
# rev2 ceiling (peak g vs 38)
python $F --dirs F,LF,RF --tuck B --chest-plateau 22350 --chest-stroke 0.062 --out $O/t031_rev2_ceil.jsonl
python $F --dirs F,LF,RF --tuck B --chest-plateau 22350 --chest-stroke 0.062 --carry --out $O/t031_rev2_ceil_carry.jsonl
# spring proxy comparison
python $F --dirs F,LF,RF --tuck B --chest-k 5.3e5 --chest-zeta 1.0 --out $O/t031_spring_proxy.jsonl
# (b) only if 38 g fails and waiver+pads defined
python $F --dirs F,LF,RF --tuck preload --chest-plateau 22350 --chest-stroke 0.062 --out $O/t031_b_preload.jsonl
```
Pass: `torso_peak_g` ≤ 38, `gear_pitch_max` ≤ 369, `chest_bottomed` = 0, `chest_angle_gt15` = 0, diagonals ≤ 369.

## R-070 update (2026-10-14): primary = tuck B, gate = chest ≤ 38 g with real chest stiffness
- **Primary forward tuck: B = arms straight down, roll +5° / yaw 0 / pitch 0 / elbow 0** (76.4 mm clearance crouched). Forward falls only; side falls keep R5. Arms confirms B with model_v4 and real covers.
- **Pass (a), both required in every run:** `torso_peak_g` ≤ **38 g** and `gear_pitch_max` ≤ 369 N·m.
  - `torso_peak_g` is new in `t030_pushfall.py`: the torso COM linear-velocity change over a 2 ms window, after fall mode starts.
  - It must be run **with real chest stiffness**: `--chest-k <N/m> --chest-zeta <ζ>`, which applies MuJoCo solref (−k, −b) on all torso geoms. Without `--chest-k`, the sim/v3 default contact is not a valid result.
- **MISSING DATA (blocks the (a) verdict):** the repo has no chest stiffness.
  - Torso R1_ARCHITECTURE gives only a CFRP 2.0 mm monocoque with no covers on the torso (R-021). There is no force–deflection, no local shell stiffness and no allowable crush.
  - Materials has the shoulder pads only (R042 EPP / honeycomb).
  - Needed from Torso, with Materials: chest-front force vs deflection at the contact patch (k in N/m, or an F–δ curve), the stroke to damage, and damping/energy loss. One number k plus ζ is enough for the first batch.
  - 38 g needs ≥ ≈ 42 mm of stopping at 5.6 m/s, so a bare 2 mm CFRP shell is unlikely to pass without a chest crush layer. That is an Arbiter item if it fails.
- **Fallback (b) preload:** allowed **only with an R-058 contact waiver and defined pads**. Arms/ID must give the forearm pad and chest pad locations (torso frame x/y/z, size), and the batch is run with those. Without them, (b) is not a candidate.
- (c) is an add-on only, with its mass going to the Arbiter.
- **Diagonals LF/RF:** `gear_pitch_max` ≤ 369 N·m in every mode (a, b, c), as a gate.
- **Batch (bryan PC ff639f5a, never DESKTOP-B115PVV), replaces the order below.** Use K = the Torso value and sweep 0.5×/1×/2×K:
```
python $F --dirs F,LF,RF --tuck B --chest-k $K        --out $O/t031_a_B_k1.jsonl
python $F --dirs F,LF,RF --tuck B --chest-k $(0.5K)   --out $O/t031_a_B_k05.jsonl
python $F --dirs F,LF,RF --tuck B --chest-k $(2K)     --out $O/t031_a_B_k2.jsonl
python $F --dirs F,LF,RF --tuck B --chest-k $K --carry --out $O/t031_a_B_carry.jsonl
python $F --dirs F,LF,RF --tuck preload --chest-k $K  --out $O/t031_b_preload.jsonl   # only once the waiver and pads are defined
```
- **Box smoke (2026-10-14, 1 run, untuned, NOT a result):** `--smoke --tuck B --chest-k 2e5` (smoke forces dir L), with k = 2e5 a placeholder. Result: torso 79.8 g, gear 721.8 N·m. This only checks that the metric and plumbing work.

## R-065 update (2026-10-14): remedy order (a) → (b) → (c), diagonals, gate ≤ 369 N·m everywhere
Candidate search: `tuck_search.py` → `tuck_search.json` (sim/v3 FK + mj_geomDistance, standing and FALL-mode crouch).
- **R5 tuck:** forearm/hand front at torso x 272 mm vs chest front 110 mm (≈ 160 mm proud), clearance 8.6 mm. Fails R-058 and the outline.

### (a) Tuck inside the chest outline (primary, zero mass)
175 adducted poses (roll ≤ +5°) in a coarse grid pass "front ≤ 110 mm and ≥ 10 mm clear of torso/pelvis/thighs/head". Picks:

| id | roll / yaw / pitch / elbow (deg, L; R mirrors roll & yaw) | front x mm | min clearance mm (crouched) |
|---|---|---|---|
| A | 0 / 0 / 0 / 0 (arms straight down at the sides) | 38 | 57.5 |
| **B** | **+5 / 0 / 0 / 0** | 38 | **76.4** |
| D | +5 / −30 / +10 / −20 | 37 | 74.1 |

- **Arms must confirm all three** with model_v4 plus the real covers. sim/v3 has no wrist fairing (R-059: wide axis parallel to chest, ~124 × 70–76 mm), no R5 pad cartridge, no carry hardware. Ranges are fine (pitch +60, roll −15…+180 L).
- **Side-fall conflict:** in a side fall these poses put the hanging forearm/hand lateral of the hip, so it lands under the hip and loads shoulder roll. Use (a) for forward falls only and R5 for side. The diagonal needs whichever passes both, and T-031 must check it.
- **Hand estimate (a):** the chest lands first, so the arm only sees its own inertia.
  - Gear torque ≈ ½·m_arm·a·r_com + ½·τ_motor (reflected rotor 0.441 ≈ arm I ≈ 0.43 kg·m² [EST]). m_arm 6.05 kg, r_com ≈ 0.25 m hanging, motor peak ~167.
  - **≤ 369 needs torso deceleration ≤ ≈ 38 g**, i.e. ≥ ≈ 42 mm of chest stopping distance at 5.6 m/s.
  - No chest crush element exists, so this **depends on the chest contact** and T-031 measures it. Likely marginal.

### (b) Forearm preload against the chest (intentional contact on defined pads)
R5 angles plus a commanded adduction/elbow bias (`--tuck preload --preload-Nm 30` [EST]). Ground force on the forearm then goes through the pad into the chest. Gear torque ≈ the preload plus the arm's own inertia share (as in (a)), **estimated ≤ ≈ 200–250 N·m [EST]**. Needs Arms/ID to define the forearm and chest contact pads, and R-058 waived for that intentional contact.

### (c) Forearm crush element (last, mass to Arbiter)
Gear torque = F_c × 0.15 m lever, so **F_c ≤ 2.46 kN**. The energy it can take is small (2.46 kN × 30 mm ≈ 74 J). On its own it only delays (b): after it bottoms out the forearm rests on the chest. Modelled as `--forearm-crush-N 2400 --forearm-crush-stroke 0.030` (native forearm/hand contacts disabled).

### Batches (bryan PC, in this order; 50 runs × each direction F, LF, RF; impulse 40–80 N·s)
```
python $F --dirs F,LF,RF --tuck B       --out $O/t031_a_B.jsonl
python $F --dirs F,LF,RF --tuck A       --out $O/t031_a_A.jsonl
python $F --dirs F,LF,RF --tuck D       --out $O/t031_a_D.jsonl
python $F --dirs F,LF,RF --tuck B --carry --out $O/t031_a_B_carry.jsonl
python $F --dirs F,LF,RF --tuck preload --out $O/t031_b_preload.jsonl
python $F --dirs F,LF,RF --tuck R5 --forearm-crush-N 2400 --out $O/t031_c_crush.jsonl
python $F --dirs F,LF,RF --tuck R5      --out $O/t031_R5_ref.jsonl
```
(all with `--pad hc --hc-plateau 7310 --hc-stroke 0.0432`, per Materials 48f55c3.)
- Pass: `gear_pitch_max` ≤ 369 N·m in every run. Stop at the first remedy that passes, but run its carry variant too.
- **Box smoke** (one 80 N·s run each, untuned, **not results**): F/A 417, F/preload 269, F/crush 1281, F+LF+RF/B 1566 N·m. That's noisy and the controller is untuned, so the PC batch decides.

## Rating (limit to show)
- Shoulder pitch: CSG-25-100 (v3/analysis/parts.py: rated 87, repeated peak 204, **momentary peak 369 N·m**, ratchet 650). One-off fall = momentary.
- **Pass: max shoulder-pitch gear torque ≤ 369 N·m** in every run. Also report the count above 204 (repeated peak) for life, and above 650 (ratcheting).
- Gear torque = |motor torque − reflected armature (0.441 kg·m², sim/v3 MJCF) × q̈ + joint-limit constraint|, both arms.

## Hand estimate (now) [EST unless cited]
- **Geometry, sim/v3 FK at the R5 tuck** (roll −5°, yaw −60°, pitch −20°, elbow −110°):
  - Forearm and hand reach torso-frame x ≈ 0.21–0.24 m against a chest front at x 0.11. So **the tucked forearm/hand sits 100–130 mm ahead of the chest and is the first forward contact**.
  - Contact sits 70–150 mm below the pitch axis (the axis is at torso z 0.22; forearm end at z 0.07, hand at 0.11–0.15).
- **Static:** 369 N·m is reached at a ground force of **2.5 kN on the forearm** (0.15 m lever) or **5.3 kN at the hand** (0.07 m). That is below any credible arrest force for a 66 kg forward fall.
- **Backdrive bound:**
  - If the forearm is stopped while the torso keeps going at v ≈ 5.6 m/s (v3 rigid topple, ω 4.28 rad/s × 1.3 m chest height), the arm is driven back through the ~110 mm gap: about 0.73 rad at a 0.15 m lever.
  - The gear must spin the reflected rotor plus arm, J ≈ 0.441 + ~0.1 ≈ 0.54 kg·m².
  - With α ≈ (v/r)²/(2θ) ≈ 940 rad/s², **τ ≈ 510 N·m > 369** (below the 650 ratchet). The end-stop impact on the chest at about 37 rad/s comes on top of that.
- **Conclusion: the R5 tuck most likely fails T-031 by about 1.4×** unless the controller lowers the impact speed (crouch, knee drop to kneel first) or the arm meets the chest before the ground.
  - One untuned box smoke run (80 N·s forward) logged 255 N·m. That is a single run, not evidence.
  - **The R5 tuck clearance of 8.6 mm is also below R-058's ≥10 mm requirement.**

## Runs (bryan PC)
```
F=modules/controls/fall/t030_pushfall.py; O=modules/controls/fall/results
python $F --pad hc --hc-plateau 6950 --hc-stroke 0.038 --dirs F --runs 50 --out $O/t031_fwd_tuck.jsonl
python $F --pad hc --hc-plateau 6950 --hc-stroke 0.038 --dirs F --runs 50 --carry --out $O/t031_fwd_tuck_carry.jsonl
python $F --pad hc --hc-plateau 6950 --hc-stroke 0.038 --dirs F --runs 50 --knee 1.5 --out $O/t031_fwd_tuck_k15.jsonl   # deeper knee drop
```
Impulse 40–80 N·s forward at the pelvis, seed 0.

## Measurements
`shoulder_pitch_gear_peak_Nm` (p50/p95/max), runs > 204 / > 369 / > 650, `t_impact`, `crouch_at_impact_m`, `com_drop_at_impact_m`, `t_release` (carry). Also the first contact body (from the jsonl: add a note if it isn't the forearm/hand).

## Pass / return
- PASS: max ≤ 369 N·m in all three batches.
- If it fails: report the margin and return to the Arbiter (R-057). Candidates for the Arbiter, not tested here:
  - a tuck that keeps the forearm inside the chest silhouette (an Arms clash check is needed)
  - a forearm-to-chest preload (zero gap) so the load bypasses the gear
  - a forearm crush element
- Results go in `results/t031_*.jsonl` + `results/T031_SUMMARY.md`.

## Model limits
Same as T-030 §10. The forward contact is modelled with MuJoCo native capsule/box contacts (no forearm cover compliance). There's no chest crush element, and sim mass is 69.5 kg vs 66.36 kg.
