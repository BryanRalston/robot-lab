# T-030 brief: A44 side-fall push-fall batch (Grok Build, **bryan PC ff639f5a only, never DESKTOP-B115PVV**)
Owner: RL Controls. Gate for R-042 (A44 provisional). CPU only, MuJoCo ≥3.1, numpy. No jax, no training. Expected wall time is a few minutes per batch: smoke runs take about 0.2–0.6 s each on the box.

## 1. What changed since A44 (read first)
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
python $F --pad 40 --pad-model curve   --arm tuck  --out $O/t030_p40_curve_tuck.jsonl
python $F --pad 30 --pad-model curve   --arm tuck  --out $O/t030_p30_curve_tuck.jsonl
python $F --pad 40 --pad-model curve   --arm reach --out $O/t030_p40_curve_reach.jsonl
python $F --pad 40 --pad-model plateau --arm tuck  --out $O/t030_p40_plateau_tuck.jsonl    # ID 7.10 kN contrast
python $F --pad 30 --pad-model plateau --arm tuck  --out $O/t030_p30_plateau_tuck.jsonl    # v3/A44 9.17 kN contrast
python $F --pad 40 --pad-model curve   --arm tuck  --no-fallmode --out $O/t030_p40_curve_nofm.jsonl  # baseline
```
If >20 % of runs show `crouch_at_impact_m` < 0.05 or no fall, sweep `--knee 0.9,1.2,1.5` on the 40-curve-tuck case and report all three (don't tune further).

## 7. Measurements (per run, JSON line; last line = summary)
`shoulder_share` (pad work ÷ pad + all non-foot ground-contact work), `E_sh_J`, `E_other_J`, `crouch_at_impact_m` (mean leg hip→foot shortening, detection → first non-foot contact), `com_drop_at_impact_m`, `t_detect`/`t_fallmode`/`t_impact` (latency 50 ms [EST]), `pad_peak_N`, `pad_crush_max_mm`, `bottomed`, `M_bearing_Nm` (= peak × 0.06), `fs_radial`/`fs_axial` (CRBH 7013 A, C0 27.7 kN, Dpw 85 mm [EST]), `contact_centroid_mm`, `W_arm_backdrive_J`.

## 8. Pass criteria (per configuration; summary `PASS`)
- p95 `shoulder_share` ≤ **0.40**.
- min `crouch_at_impact_m` ≥ **0.15 m**.
- max `M_bearing_Nm` ≤ **550** (pad peak ≤ 9.17 kN; fs radial ≥ 1.25).
- 0 `bottomed`.
- Also report: p95 `E_sh_J` vs 74 J (curve) and 220 J (plateau); p95 |contact_centroid z| vs 30 mm.

R-042 passes only if **40-curve-tuck** or **40-curve-reach** passes. The plateau runs are contrast only.

## 9. Results to return
Commit `modules/controls/fall/results/t030_*.jsonl` plus a `results/T030_SUMMARY.md` table (one row per config: runs, fell, share p50/p95, E_sh p95, crouch min/p50, peak N max, M max, fs min, bottomed, centroid z p95, W_arm p50). Report the hash to RL Controls and Robot Lab.

## 10. Model limits (state in the summary)
- Pad = 3×3 point patch (105 mm square) on the shoulder-pitch output body, 0.152 m lateral of the joint [EST: from sim/v3 arm offset]. Forces are applied with xfrc_applied; friction 0.8 [EST].
- Partial-edge contact loads only the touching points, so peak force can be below the full-area curve.
- Scripted (untuned) fall controller with joint PD and torque caps from the MJCF.
- No waist roll DOF in sim/v3, and no shoulder-roll clutch model (the actuator cap of 164 N·m acts as the slip torque).
- sim/v3 mass 69.48 kg vs 66.36 credible (R-043), so energies are ~5 % high.
- Box smoke (2026-10-14, one 80 N·s L fall per pad, untuned): runs end-to-end. Numbers are **not results** (e.g. 40 mm curve: share 0.57, E_sh 91 J, peak 6.65 kN partial-edge, crouch 0.35 m).
