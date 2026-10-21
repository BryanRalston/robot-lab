# RL Arms & Hands R11 (2026-10-21): shoulder-pad load path fix after FEA Job 1 FAIL (a556d44)
Calc: `pad_fix_r11.py` / `.json`. Image: `R11_pad_fix.png`.
Hand calcs only. Same loads and formulas as the job (Fn 8.86, Fs 2.37 kN, IKO P0 = Fr + 2M/dp + 0.44Fa, fault ×1.05). The script reproduces the FEA: s0 1.45 / 1.27 against FEA 1.45 / 1.29, Mx 567 / 773.

**Cause:**
- The pad centre sits 64 mm below the roll axis (link centre), so the normal force makes roll torque 567 N·m.
- The 87 mm standout puts Fs on a tilt lever into the small CRBH 6013.
- **Arms R7/R8 error:** the R7 s0 table left out Fs × standout, and the R8 boss mass was booked at 0.024 kg/side when a solid 62 × 62 × 10 boss is 0.108 (FEA note). Both are corrected here.

## Options (pair Δ mass [EST] unless cited)
| option | roll CRBH s0 (≥ 2.0) | roll gear (fault) | pitch bearing (D71 gate 550 N·m) | ROM / pad angle | Δ kg pair |
|---|---|---|---|---|---|
| R8 as built | 1.27 ✗ | 812 vs 369 ✗ | — | — | 0 |
| **A1** grounded carrier on shoulder_P, pad z 0.19–0.25 | bypassed | bypassed | 482 ✓ (fault 506, 1.09) | **abduction ≤ 35°** (10 mm clear) ✗. Pad angle pose-independent (side ~5–10°). | +0.2 |
| **A2** grounded, pad raised z 0.225–0.29 | bypassed | bypassed | 570–792 ✗ (needs a bigger pitch bearing) | abduction ≤ 80° | +0.2 + bearing |
| A + torso bulkhead thrust shoe | bypassed | bypassed | shoe takes Fn only after the gap closes. The pitch bearing deflects µm, so it needs a preloaded PTFE contact (friction on pitch). **Not credible in light calc.** | as A | — |
| **B (recommended)** carrier on the roll OUTPUT flange, wrapping the housing, **pad centre on the roll axis** (contact Y 115.5) + **CRBH 8016 A** (C0 43.4 kN, cited) | **2.53 at e10** (2.82 at e0; down 3.80) ✓ | axial 0. Down Fs·Y = 274, fault 288 → **CSG-25 SF 1.28 ✓** | unchanged | keeps the full ROM. Pad rotates with roll, so the R10 angles hold (tuck B side 5–10°; diagonals need waist yaw ±45°). | bearing +0.82 (2 × (0.74 − 0.33), cited); housing growth ~+0.2; carrier ~+0.14 [EST]; boss removed (−0.048 booked) → **≈ +1.1** |
| B with the CRBH 6013 kept | 1.24 ✗ | ✓ | — | — | — |
| **C** keep R8 geometry, upsize gear + bearing | 2.58 (8016) | **CSG-32-100 841 vs 812: SF 1.04** (thin); CSG-40-100 1400: 1.72 | — | OD 85 → 110 / 135 | CSG-32: 2 × 0.47 (cited) + 0.82 + housing ~0.3 → **≈ +2.1**; CSG-40 ≈ +3.7 |
| overload slip on roll (clutch) | — | — | — | — | R-057: cited clutches 1.6–4.0 kg ✗ |
| compliance / impact limit | — | — | — | — | the pad is already a 7.05–9.17 kN constant-force core; a lower plateau needs more stroke (T-030 energy) ✗ |

**Recommendation: B.**
- It is the only option that passes every gate by hand calc without a ROM cut or a gear change: CRBH s0 ≥ 2.5, CSG-25 SF 1.28 at fault.
- **Cost ≈ +1.1 kg pair [EST]**, more than the ≈ 0.38 reserve, so **the Arbiter must rule.**
- **Lighter alternative if the Arbiter accepts a ROM cut:** A1 (+0.2 kg), which limits shoulder abduction to ≤ 35°. TARGETS has no overhead task, but 35° is a big functional cut. Arms doesn't recommend it.
- Moving the pad off the roll output (A) makes the pad angle pose-independent. That fixes side falls for any tuck, including R5, but diagonals still need waist yaw. In B the R10 analysis stands.

**Gear-sizing case (if Arbiter prefers to keep the pad at the link centre):**
- Need 773 N·m nominal, **812 N·m with fault**.
- CSG-25-100 momentary 369 ✗.
- CSG-32-100: 841 (1.04×), 0.89 kg vs 0.42 (HD Table 3/8, cited), OD 110.
- CSG-40-100: 1400 (1.72×), 1.70 kg, OD 135.
- Each also needs the CRBH 8016 (s0 2.58).
- Arms advises against CSG-32: 1.04× is thinner than the 1.24× the elbow was rejected for.

**ID input needed for B:**
- Carrier: a 7075 machined cap from the roll-output flange over the housing barrel, 3 mm gap. Pad face centred on the roll axis, Y ≈ 115.5 mm from the bearing centre. No 3D printing.
- Pad stack unchanged (67.5).
- Fairing re-cut for the wider shoulder: +~15 mm radial over the roll housing.

**Heavy work queued (bryan PC Job 8 add-on):** re-run job1 FEA with geometry B (carrier, CRBH 8016, contact Y 115.5) and the abduction/fairing clash.

## Housekeeping (R11)
- **No 3D-printed parts:** the only arms PA12 use was Materials' hybrid palm skin variant (`palm_7075.py` variants, `A32_PALM_7075.md`). It is **marked DEAD**. The booked palm is all-7075 machined (R-037), so the mass is unaffected.
- No other printing appears in the arms files. Sheaths and spools are machined or molded parts [to cite].
