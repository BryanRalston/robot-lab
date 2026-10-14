# T-031 brief: forward fall with permanent R5 arm tuck vs shoulder-pitch gear rating (R-057 / D77)
Grok Build, **bryan PC ff639f5a only, never DESKTOP-B115PVV**. CPU MuJoCo on sim/v3. Same script and setup as T-030 (`T030_BRIEF.md` §5): `modules/controls/fall/t030_pushfall.py --dirs F`.

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
