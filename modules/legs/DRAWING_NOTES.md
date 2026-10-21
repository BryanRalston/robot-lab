# Legs — stock form / thickness / grain notes for machined parts (R-128 §1, rev 2026-10-21)
R-128: every drawing must state stock thickness and grain direction; an unstated one takes the lowest band value (257 MPa).
[EST] = inferred by Legs, not on a drawing/CAD; Materials/Arbiter to confirm. Envelope sizes from the cited scripts/briefs.

| Part | Material / temper | Stock form & thickness | Grain direction | Single-path limit used | Source / notes |
|---|---|---|---|---|---|
| Ankle cross (job 7) | 7075-T7351 | plate ≤1.500 in (order 1.25 or 1.5 in [EST]) | plate thickness along z (30 mm); L along y (46 mm) [EST]; ST = z | L/LT 262, ST 239 (Materials 95436bf / R-125b). **R-128 308 not applied — see conflict below** | grokbuild/ankle_cross_fea_brief.md rev D |
| Femur tube | 7050-T73511 extrusion | ø50 × **1.5** wall tube (L65 proposed; was 1.2, P-047 1.6) | L = tube axis (extrusion) | 262 (R-128 §3) | model_v4 l.152 label still "T7451" (Controls/model owner to correct) |
| Tibia tube | 7050-T73511 extrusion | ø45 × **1.5** wall tube (L65 proposed; was 1.2) | L = tube axis | 262 (R-128 §3) | STRUCTURE_FEA_REPORT |
| Thigh split collar | 7075-T651 [EST temper] | plate ≥0.5 in, ID50 × 34 long, wall 6 [EST stock 2.001–2.5 in if cut with axis in-plane; ≤2.0 in if axis through-thickness] | collar axis = ST [EST] → 271 (≤2.0 in, ST) | 271 [EST] | CROSS_PIN_BACKUP.md |
| Thigh sleeve | 7075 [EST T651] | bar/tube, 47.6/43.6 × 34 [EST] | axis = L [EST] | not stated → 257 until drawn | CROSS_PIN_BACKUP.md |
| Femur tongue (ø35 press) | 7075-T651 [EST] | bar ø≥38 [EST] | L = tongue axis [EST] | not stated → 257 | results/r5/structure_r5.md |
| Knee tongue | 7075-T651 [EST] | plate, band n/a [EST] | not stated | 257 until drawn | STRUCTURE_FEA_REPORT |
| Knee fork | 7075-T651 [EST] | plate [EST] | not stated | 257 until drawn | STRUCTURE_FEA_REPORT |
| Hip clevis | 7075-T651 [EST] | plate [EST] | not stated | 257 until drawn | STRUCTURE_FEA_REPORT |
| Foot box | 7075-T651 [EST] | plate [EST] | not stated | 257 until drawn | grokbuild/fea_r5.py |
| Hip-pitch lever (r031 mw b30 d36 RC) | 7075 (per L47-R) [EST temper T651] | plate, thickness = lever width band [EST] | L along lever length [EST] | 257 until drawn (G3 uses its own gate) | actuators/cad/hip_pitch_lever_r031_mw_b30_d36_RC.step |
| Knee twin housing / fins (D69C) | 6061-T6 [EST] (fins/housing shell) | plate/billet [EST] | not stated | 6061 single-path 161 (R-128 §4) | cad/knee_twin_housing_fins_d69c_*.step |
| **Knee twin-housing centre web** (R-132 §2, L66; L67 stock fix) | **7075-T7351** (T651 not permitted: sustained ST load) | **web is integral with the one-piece housing (JOB9_KNEE_GEOMETRY: housing, web, fins one piece)**, so the stock is set by the housing envelope, measured from CAD: rev C 184.0 × 107.9 × **105.1** mm, release r116 204.8 × 115.8 × **105.1** mm (cadquery BoundingBox). 105.1 + 3 stock = 108.1 mm → **4.25 in stock required, above the R-132 §2 4.0 in plate limit → no permitted plate band.** Previous "3.501–4.0 in, ≥ ~90 mm" [EST] withdrawn. Stock form open per actuators/results/STOCK_GRAIN.md: (a) T7351/T73 hand forging with a Materials-cited allowable, (b) split nut sections to fit 3.5 in plate, (c) body ≤ 98 mm. | ST along the 105.1 mm dimension (screw axes ∥ ST, trunnion axis ∥ LT, per STOCK_GRAIN.md; supersedes the earlier trunnion-y [EST]) | **211 static** (provisional: T7351 3.501–4.0 in S-basis ST, R-132 §2 / R-135 confirmed); **317 fall** (Job 9 interim) | actuators/cad/knee_twin_housing_release_r116.step, knee_twin_housing_finned_revc.step; JOB9_SPEC (c). Sustained ST: **YES** (bearing press fit, bolt preload). **No FEA stress yet** — margins wait on JOB9-c (R-135). |
| Knee finned saddle (L45) | 6061-T6 | billet [EST] | not stated | 161 (R-128 §4) | KNEE_THERMAL_NOTE.md |
| Ankle roll stop blocks (A14) | not stated | not stated | n/a | n/a (stops) | a14_r7.py |
| Collar backup pins (L63) | 42CrMo4 | ground bar ø7 | axis | n/a (steel) | CROSS_PIN_BACKUP.md |

## Conflict — R-128 "308" vs job 7 ankle cross (not applied)
- R-128 §1 band 308 MPa = **7075-T651** plate, A-basis LT Fty ÷1.5, stock 1.001–2.0 in (single path). R-128 §2 applies it to the ankle cross.
- The ankle cross is **7075-T7351 only** (Materials a2bf811: T6/T651 barred for SCC at the press-fit bores; brief rev D l.7). Materials e98d18d/95436bf: T7351 plate 1.001–1.500 in A-basis L/LT Fty 393 MPa (MIL-HDBK-5H p.3-348) → 262; ST stand-in 239.
- 308 is a T651 value; using it on a T7351 part overstates the allowable by 46 MPa. Rev D limits (262/239, bearing 455/381/295) kept. Arbiter + Materials must either confirm R-128 §2 is void for T7351 or re-rule the temper.
