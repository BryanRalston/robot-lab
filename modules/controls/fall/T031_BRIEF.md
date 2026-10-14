# T-031 brief: forward fall with permanent R5 arm tuck vs shoulder-pitch gear rating (R-057 / D77)
Grok Build, **bryan PC ff639f5a only, never DESKTOP-B115PVV**. CPU MuJoCo on sim/v3. Same script and setup as T-030 (`T030_BRIEF.md` §5): `modules/controls/fall/t030_pushfall.py --dirs F`.

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
