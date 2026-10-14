# A44: side-fall strategy, shoulder_pitch load ≤ 550 N·m (R-039 / D71)

Owner: RL Controls. Script: `a44_side_fall.py` → `a44_results.json` (analytic model, runs in under 1 s, no sim).

## Where 690 N·m comes from
- `v3/analysis/v3.py` `fall_model()`: side fall from standing, rigid topple about the foot edge, COM height zc = 0.98 m, E = m·g·zc = 613 J (`v3.json` fall.E_J).
- Shoulder share 0.45 [EST, v3 "55/45 hip/shoulder split"], 30 mm EPP pad crushed at constant force over s = 0.7·30 + 3 = 24 mm. That gives F = 0.45·613/0.024 = 11.5 kN (`v3.json` shoulder_F).
- Moment at the shoulder_pitch output bearing: M = F × 0.06 m (v3.py line 99) = **690 N·m**. See also D71 and Torso R1_ARCHITECTURE.

## Bearing: IKO CRBH 7013 A (R-039 D71)
- IKO CAT-57151 dims table: d 70, D 100, B 13 mm; C 20.1 kN; **C0 27.7 kN**; 0.38 kg. IKO publishes **no separate moment rating** for CRBH. Moment enters through the static equivalent load P0r = Fr + 2M/Dpw + 0.44Fa (CAT-57151 eq. 2), and fs = C0/P0r.
- Dpw = (d+D)/2 = 85 mm [EST] (roller pitch diameter isn't published; R-039 (a) asks Actuators for it).
- At pure moment, fs = 1 at M = C0·Dpw/2 ≈ 1177 N·m. With the coupled impact force F = M/0.06 at the radial worst case, **M = 550 N·m → F 9.17 kN → P0r 22.1 kN → fs 1.25**. That matches R-039 (b). At 690 N·m the result is fs 1.00 radial / 1.30 axial, which reproduces D71.

## Finding: the baseline is already worse at the current mass
At R-039 credible mass 66.21 kg (v3 used 63.8), the same fall gives **716 N·m** (fs 0.96 radial). A44 has to cover 716 → 550, a 23 % cut in shoulder-site energy. Max shoulder impact energy = 550/0.06 × 0.024 = **220 J**.

## Results (model above, m = 66.21 kg)
| case | zc m | shoulder share | M N·m | fs radial / axial | ≤550 |
|---|---|---|---|---|---|
| baseline (v3 mass 63.8) | 0.98 | 0.45 | 690 | 1.00 / 1.30 | no |
| baseline @ 66.21 kg | 0.98 | 0.45 | 716 | 0.96 / 1.25 | no |
| S1 crouch 0.20 m only | 0.78 | 0.45 | 570 | 1.21 / 1.57 | no |
| S2 hip-first only | 0.98 | 0.35 | 557 | 1.24 / 1.61 | no |
| **S3 proposed: crouch 0.15 m + hip-first (share 0.40)** | 0.83 | 0.40 | **539** | **1.28 / 1.66** | **yes** |
| S3, hip-first not achieved (0.45) | 0.83 | 0.45 | 607 | 1.14 | no |
| S3, crouch only 0.08 m | 0.90 | 0.40 | 585 | 1.18 | no |

Required shoulder share for ≤550: ≤0.346 with no crouch, ≤0.408 with a 0.15 m crouch.

## Proposed strategy (S3): "drop, tuck, hip-first"
1. **Detect** (WBC fall predictor: capture point outside the support polygon laterally plus base roll rate over threshold). Abort balance and enter FALL mode. Disable the step planner.
2. **Knee drop / crouch (0–~250 ms):** command both knees and hips to a deep squat as fast as the joints allow, lowering COM ≥ 0.15 m before ground contact. The energy model treats a lowered COM as less potential energy at impact. Energy the legs absorb during the drop is counted as dissipated, not stored [ASSUMPTION].
3. **Arm tuck (fall side):** shoulder_roll adduct, elbow flex ~−110°, forearm across the chest. This keeps the hand and forearm out of the ground path, so no gear-path torque goes through the arm. The 300 N·m roll clutch is untouched. The upper arm sits inside the shoulder pad footprint.
4. **Hip-first lean:** waist roll/pitch toward the fall side so the pelvis/hip pad lands first, with the trunk still tilted ~10–15° up [EST]. This shifts the share to hip ≥ 60 %. The hip side has margin (fall_hip_bracket FEA SF 15.3).
5. **Post-contact roll:** after hip contact, let the trunk roll back (waist pitch compliant/backdrivable, low-gain) to spread the shoulder contact over time. This isn't credited in the 539 N·m number.
6. **Shoulder compliance at impact:** shoulder_pitch/roll go to low-gain/backdrive at contact. This **does not reduce the bearing moment**: 690/550 is a lateral force × 60 mm offset carried as bearing moment about x, not pitch-gear torque (D71). So it's not credited.

## Assumptions (all to verify)
- The 30 mm pad, 70 % usable crush + 3 mm, constant-force crush, and the 0.06 m lever are all from v3.py, unchanged.
- The share 0.40 under hip-first lean is **[EST, not measured]**. It is the single biggest driver; the margin is only 11 N·m (2 %).
- A ≥0.15 m COM drop inside the fall window is **[EST]**. A standing side topple takes ~0.5–0.7 s by the v3 rigid model; joint speed limits and the predictor latency are not modelled.
- Rigid single-body topple; no sliding. Fall from standing only (walking at 1.2 m/s adds lateral KE, not covered).
- Dpw 85 mm [EST]; C0 is from the catalog.

## Recommendations / next steps
- The margin is thin. A cheap extra lever is a **thicker shoulder pad** (40 mm → s 31 mm → −23 % force at the same energy). Torso/Arms decide the mass/packaging. Not booked.
- **Heavy verification (bryan PC, Grok Interface brief, not run on the box):** a MuJoCo sim/v3 side-push fall batch with the S3 FALL-mode script, contact force at the shoulder pad geom, 50 pushes × 3 directions. Output: peak shoulder pad force and share. Gate: F ≤ 9.17 kN (M ≤ 550).
- A pitch-axis (forward) fall component is still unquantified (D71 last line).

## Update 2026-10-14 (after R-042, ID d80df32, Materials 5f8f149)
The constant-force pad model used above is **superseded for EPP**. With the ARPRO 5170 curve ×1.45, the S3 shoulder energy of 216–220 J gives **~19 kN, ~1150 N·m, radial SF 0.60** on the 40 mm/109 cm² pad. That fails 550. See `T030_BRIEF.md` §2 and `epp_pad_estimate.py`. The 539 N·m above holds only for an ideal constant-force crush element (honeycomb or crush tube).
