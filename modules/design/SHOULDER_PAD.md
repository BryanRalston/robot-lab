# Shoulder impact pad: R8 option B adopted (R-079), RL Industrial Design, 2026-10-14
**P-number: P-051 (proposed).** **R-079 adopts option B** (replaceable 0.5 mm 7075 tray on Arms' integral 62x62x10 boss): **0.116 kg pair, +0.024 vs the R-073 0.092 booking, full credit.** Field rebonding on the arm link (option A, 0.096 pair) is **rejected** — it puts a structural link at risk on every cartridge swap. Materials remaining credit vs R-073: **-4.4 g** (pending FEA job 1 + link-face qualification). Numbers from `pad_r8.py` -> `pad_r8.json`.

## R8 CURRENT (R-079): option B — replaceable tray
- **Why:** the roll-yaw link face is only 60 x 50 (78 mm diagonal), too small for D-A. Arms provides a solid 7075-T6 link with an integral 62 x 62 x 10 boss, 4 x M4 x 8 tapped, +0.024/side [EST]. The boss replaces the D-A doubler.
- **Service:** cartridge swaps in minutes (tray tabs on boss M4); no field rebond.
- **Pad centre on the CRBH 6013 plane** (e <= 10 mm). Abduction soft limit <= 135 deg.

**Option B (ADOPTED): replaceable 0.5 mm 7075 tray + sleeve**
| item (per side) | kg |
|---|---|
| core_61p8x61p8x60 | 0.0165 |
| bond_DP490 | 0.0005 |
| spreader_Al_0p5 | 0.0052 |
| EPP80_face_6mm_integral_skin | 0.0018 |
| link_boss_7075_Arms_EST | 0.024 |
| replaceable_tray_7075_0p5_with_lips_tabs | 0.0076 |
| sleeve_TPU_film | 0.0025 |
| **per side** | **0.0581** |
| **pair** | **0.1162 (booked 0.092 -> +0.024; R-079)** |

**Option A (REJECTED for field service): direct bond** — 0.096 pair; cartridge replacement = debond + re-prep + 24 h cure on the structural link.

**FEA case (bryan PC):** solid 7075 link with integral boss + tray + bonded core pressure patch 61.8^2, pad centre at e = 0 and e = 10 mm; 9.17 kN at 15 deg; pass criteria unchanged (link/boss <= 480/1.5 MPa, bond <= 23/3, CRBH s0 >= 2.0, deflection <= 1 mm, M4 no slip).

## R8 design detail (superseded pick narrative; B is adopted above)
- **Why:** the roll-yaw link face is only 60 × 50 (78 mm diagonal), too small for D-A. Arms proposes a solid 7075-T6 link with an integral 62 × 62 × 10 boss, 4 × M4 × 8 tapped, +0.024/side [EST]. **The boss replaces the D-A doubler**: the core is bonded straight to the boss face (−15.5 g/side), net ≈ +0.0085/side vs R7.
- **Bond:** 15° shear 2.37 kN → 0.62 MPa on the footprint; DP490 (23 MPa) SF 37; core shear SF 3.8 (Materials, residual-after-crush test at G5). Prep the machined 7075 boss face per `legs/BOND_SPEC.md` (grit-blast, solvent, primer).
- **Lips/guides:** not needed when bonded (Materials Part 4: lips only locate; the bond carries shear). A 62 boss leaves no wall for a pocket around a 61.8 core, so **locate with a bonding jig**. A 0.5 mm rim would need a 64 × 64 boss (+7 g).
- **Pad centre on the CRBH 6013 plane** (axial offset e ≤ 10 mm, target 0; Arms s0 2.45 at 0, 1.98 at 10 mm, 1.25 at 40 mm). **Contact band** z ±15 mm about the centre: 15.9 mm margin to the core edges; T-030 smoke fore-aft centroid −10/−12 mm: 19 mm margin in x. Abduction clears to 90° roll; interim soft limit ≤ 135° pending the bryan-PC sweep.

**Option A (recommended for mass): direct bond, EPP face with integral skin (no sleeve)**
| item (per side) | kg |
|---|---|
| core_61p8x61p8x60 | 0.0165 |
| bond_DP490 | 0.0005 |
| spreader_Al_0p5 | 0.0052 |
| EPP80_face_6mm_integral_skin | 0.0018 |
| link_boss_7075_Arms_EST | 0.024 |
| **per side** | **0.048** |
| **pair** | **0.096** (booked 0.092 → **+0.004**; cap 0.100 → −0.004) |

**Service flag (A):** replacing a spent cartridge means debonding the core from the arm link, re-prepping and re-bonding (24 h cure). That's a field-service burden. **Option B:** replaceable 0.5 mm 7075 tray (lips + tabs on the boss M4) + sleeve = **0.1162 pair, over the cap by 0.016**; tray tabs OK (0.5 mm tabs: bearing 307 MPa (SF 1.56 vs 480), tear-out 154 MPa (SF 2.1 vs 330)). **R-079 pick: B adopted** (+0.024 vs booking). A rejected.

**FEA case (bryan PC, updated):** solid 7075 link with integral boss + bonded core pressure patch 61.8², pad centre at e = 0 and e = 10 mm; 9.17 kN at 15° (8.86 normal + 2.37 tangential, applied axial along the roll axis = worst for CRBH P0, and downward); arm tuck self-weight; fixed at the shoulder_P bracket through the CRBH 6013 (stiffness element). Pass: link/boss ≤ 480/1.5 MPa, bond-line ≤ 23/3 MPa, CRBH s0 ≥ 2.0, deflection ≤ 1 mm at the pad, M4 no slip.

## R7 (R-068), superseded by R8. Core frozen by Materials (48f55c3 Part 5), not re-sized
**Core:** 4.5 pcf, 61.8 × 61.8 × 60, pre-crushed, ±3 % lot cert. **Peak 9.15 kN** (upper bound × 1.30) ≤ 9.17; **293 J at 15° on the floor** (× 0.93, lower bound × 1.10) ≥ 292; 315 J at 0°. Standout **67.5 mm** (doubler 1.0 + core 60 + spreader 0.5 + EPP 6).

### Mount decision: ROLL OUTPUT (R6 location) carrying Materials' D-A doubler
| criterion | D-A on the housing face (fixed, at the R5 location y 0.267–0.335, z 0.163–0.268) | R6 roll output (on the roll-yaw link lateral face, moves with roll) |
|---|---|---|
| upper arm, all roll angles (sim/v3 capsule r 40 from y 0.282, z 0.18) | **overlaps −8.5 … −41 mm** (Arms −7.5…−40 at 66.5, +1 mm at 67.5). Raising to z ≥ +0.19 takes it off the housing face, so D-A can't be both | **no overlap**: the pad rides on the arm |
| abduction | clears | pad rotates with the arm; at 90° it faces up, outboard of the cap. **Arms to confirm vs head/cap at max abduction** |
| A44 tuck (roll −5, pitch −30) | fixed pad above the adducted arm; lateral-most surface may become the arm → out-of-footprint risk | pad is on the arm's lateral face, which **is** the lateral-most surface; not between arm and torso (27.8 mm tuck clearance unaffected) |
| vent inlet z +0.14 | ~1.6 mm (Materials) | pad on the arm, outboard of the bay vents; does not cover them. **Re-check in crushed-state CAD (R-059)** |
| contact band ±15 mm (Controls) | covered only if the arm doesn't reach the ground first | centred by construction (pad on the contact face) |
| load path | axial into the housing face, but the bare 2 mm ring fails (Arms), so it needs a stiff end face | 9.17 kN lateral → link → roll output → roll bearing (radial; small moment if the pad is centred on the roll axis) → shoulder_P bracket; bare housing ring not loaded |
**Pick: roll output.** It is the only option that clears the upper arm at every roll angle without leaving the seat, and it covers the band by construction. Materials' **D-A plate (15.5 g) fits it** if the roll-yaw link lateral face is flat and solid over the 87.4 mm diagonal; otherwise the R6 ribbed doubler (25.7 g → pair 0.105, over the cap).

| item (per side) | kg |
|---|---|
| core_4p5pcf_61p8x61p8x60 | 0.0165 |
| doubler_7075_DA_plate1p0_lips0p8_tabs | 0.0155 |
| bond_film_DP490 | 0.0005 |
| spreader_Al_0p5 | 0.0052 |
| EPP80_face_6mm | 0.0018 |
| sleeve_TPU_film | 0.0025 |
| **per side** | **0.042** |
| **pair** | **0.084 (booked 0.100 → -0.016)** (Materials 0.087 with their 4 g sleeve) |

### Single doubler FEA case (bryan PC)
- **Model:** roll-yaw link (actual CAD) + D-A 7075-T6 plate (1.0 mm base, 0.8 × 6 mm lips, 4 tabs 8 × 10 × 1.5) + 4 × M4 class 8.8 (preload 2 kN each) + bonded core as a uniform pressure patch 61.8 × 61.8, + roll output and roll bearing (CRBH) as a spring/bearing element; fixed at the shoulder_P bracket.
- **Load:** peak 9.17 kN at 15°: normal 8.86 kN (2.32 MPa on the footprint) + tangential 2.37 kN, applied **downward (hip-first lean)**, plus arm self-weight at the tuck (roll −5, pitch −30, elbow −110) and the roll gear held (brake/backdrive torque off).
- **Outputs/pass:** plate and link von Mises ≤ 480/1.5 MPa; M4 shear ≤ 0.6 × 640 MPa and no slip/separation; roll bearing combined radial + moment ≤ the CRBH static rating / 1.5 (R-067); link deflection ≤ 1 mm at the pad.

### Must confirm
- **Arms/Actuators (D1–D3):** a flat, solid lateral face on the roll-yaw link ≥ 87.4 mm diagonal with 4 × M4 × 8; abduction sweep vs head/cap with the 67.5 mm pad; the roll bearing rating for the case above.
- **Materials:** D-A on the link face (alloy unknown) and the bonded-core residual shear (G5); OK with the 2.5 g film sleeve.
- **Controls:** the 15° limit holds across the roll ROM, since the pad orientation moves with roll (Materials D1).

## R6 (R-060, Arms c64ab91 R6 §5), superseded by R7
- **Decision: mount on the ROLL OUTPUT** (the upper-arm lateral face at shoulder height), not on the cap.
  - Raising the cap pad to bottom ≥ z +0.19 would technically keep the band inside the core (10 mm below / 21 mm above), but the upper arm would then sit only ≈ 11 mm inboard of the pad face. A 10–15° hip-first lean could land on the arm, which is an out-of-footprint hit (an R-059 fail).
  - On the roll output the pad moves with the arm: no overlap at any roll angle (Arms' −7.5…−40 mm overlap is gone), and the band stays centred.
  - **Fallback:** shoulder_P-bracket load ring (Materials fd46ad8 ring frame) with the pad raised to z ≥ +0.19.
- **Load path, kept out of the bare 2 mm housing ring (Arms: ≈ 2.9 GPa bare-ring bending, FAIL):** core → 7075 doubler (flat 1.5 mm top plate, 4 ribs landing on the roll-output flange, integral 0.8 mm lips replace the guide posts) → 4 × M4 into the roll-output flange (615 N shear each at 15°) → roll output → roll bearing → shoulder_P bracket. **The 7075 doubler REPLACES the PC saddle.**
- **Core:** 4.5 pcf pre-crushed, lot-tested ±5 %, **60.9 × 60.9 × 55 mm** (61 nominal, 60.9 max). σ band 1.87–2.47 MPa (Materials, incl. rate 1.10–1.30). **Peak 9.16 kN = 550 N·m ≤ 9.17 kN / 550: PASS. Energy at min σ 275 J ≥ 265: PASS.**
- **Doubler checks:** top plate between ribs at 20 mm pitch, σ 329 MPa vs 7075 ~500 (SF 1.52); rib bearing 25.1 MPa; 15° shear 2.46 kN into the 4 M4.
- **Trims vs R5:** no guide posts (doubler lips), 0.3 mm face plate, 4 mm EPP face, TPU film sleeve, aramid strap + 2 M3 in the lips.

| item (per side) | kg |
|---|---|
| core_HC_4p5pcf_61x61x55_lot_tested | 0.0147 |
| face_plate_Al_0p3 | 0.003 |
| doubler_7075_plate_ribs_lips | 0.0256 |
| retention_aramid_strap_plus_2_M3_in_doubler_lips | 0.003 |
| EPP80_face_4mm | 0.0012 |
| face_sleeve_TPU_film | 0.0025 |
| **per side** | **0.05** |
| **pair** | **0.1 (R-060 booked 0.127 → -0.027; cap 0.100 → at cap)** |

**R-059 conditions (recorded):** T-030 logs impact points and counts hits outside the core footprint, or beyond 15° (R-060), as a fail; G5 drop test on the cartridge (also measures the rate factor for lot qualification, R-060); the 1.5 mm vent clearance must hold in the crushed-state CAD (re-check at the roll-output location).
**Bryan-PC jobs:** (1) FEA of doubler + roll-output flange + roll bearing at 9.17 kN, 0–15°; (2) crushed-state CAD clearance; (3) Arms/Controls re-check of the contact band and abduction sweep with the pad on the roll output.
**Open for Arms:** roll-output flange face ≥ 61 mm, flat, with 4 × M4 available; roll bearing capacity for the 9.17 kN lateral load.

## R5: relocated to the shoulder cap (superseded by R6) (Arms: R4 on the bulkhead face covers the ø96 shoulder-pitch housing and flange, so not viable). CURRENT DESIGN
R-054 accepted R4 at 0.100 (booked). Same core: **5052 HexWeb CR III 4.5 pcf, pre-crushed, 62 × 62 × 57 → 8.94 kN at ×1.3 (537 N·m) / 282 J at ×1.0: PASS.**
- **Location:** outboard of the shoulder roll housing, y ≈ +0.30 (Arms: abduction clears, arm gap about 32 mm at roll −5°, A44 tuck clears the torso by 8.6 mm). **Arms to re-confirm with the R5 stack of 66.5 mm** (saddle 3 + core 57 + plate 0.5 + EPP 6).
- **Minimal carrier (shells deferred):** 3 mm PC conformal saddle on the roll-housing outer face, retained by a bonded aramid band + 2 bonded M4 inserts of its own (the bulkhead's 8 × M8 are taken). **Load path:** ground → EPP → plate → core → saddle → **roll housing (2.33 MPa bearing, compression)** → shoulder structure. The future cosmetic cap carries no load. **Arms to confirm the roll housing takes 8.94 kN lateral in bearing over 62 × 62.**
- **Vent inlet z +0.14:** core centre moved 4 mm up → about 1.5 mm clear (was 2.5 mm overlap). **Coverage:** ±15 mm contact band stays 12 mm (bottom) / 20 mm (top) inside the core edges.
- **Off-centre face-plate check (R4 80 × 100 plate, 8.94 kN):** under a flat-ground hit the EPP loads the whole plate (1.12 MPa mean). The 19 mm overhang beyond the core is a cantilever, M ≈ 202 N·m/m: 0.5 mm σ ≈ 4.8 GPa (SF 0.06) **FAIL**; 0.8 mm σ ≈ 1.9 GPa (SF 0.15) **FAIL**, so **the +0.008 for 0.8 mm does not fix it**; a flat plate would need 2.1 mm 6061 (+0.035/side). **Fix: plate and EPP face cut to the 62 × 62 core**, so the plate is in pure compression (2.33 MPa) with no bending; an off-centre resultant only tilts the crush, held by the side posts. Coverage comes from placing the core on the band.
- Thermal: the pad is now off the 69 °C bulkhead; **Thermal to give the roll-housing surface temperature** (R4's gap/foil dropped unless needed, +0.001).

| item (per side) | kg |
|---|---|
| HC 4.5 pcf core 62×62×57 | 0.0158 |
| Al 0.5 mm face plate 62×62 | 0.0052 |
| 4 PC side-guide posts | 0.0040 |
| PC 3 mm conformal saddle (replaces backing) | 0.0138 |
| bonded aramid band + 2 bonded M4 inserts | 0.0040 |
| EPP 80 face 6 mm 62×62 | 0.0018 |
| face sleeve | 0.0040 |
| **per side** | **0.0486** |
| **pair** | **0.097 (R-054 booked 0.100 → −0.003)** |

## R4 (Materials 8a3cc66, R-049), superseded by R5
R3 fails R-049 against the cited HexWeb CR III data (3.1 pcf 0.896 MPa, ×1.30 dynamic → 9.79 kN; 239 J at ×1.0). The EPP face is in series and gets no energy or peak credit.
- **Core: 5052 HexWeb CR III 4.5 pcf (1.79 MPa cited), pre-crushed, 62 × 62 × 57 mm** (63 × 63 gives 9.24 kN at ×1.3, over the limit).
  - **Peak at ×1.30: 8.94 kN = 537 N·m ≤ 9.17 kN / 550: PASS.**
  - **Energy at ×1.0: 1.79 MPa × 38.4 cm² × 0.72 × 57 mm = 282 J ≥ 265: PASS.**
- Cartridge: PC backing (62 × 62, M4 inserts) → core in 4 PC corner-post side guides → **Al 0.5 mm ribbed spreader / face plate 80 w × 100 h**, centre 5 mm below the shoulder axis → 6 mm EPP 80 cosmetic face → face sleeve. Replaceable, single-use.
- Coverage (Controls ±15 mm contact band): ≥ 35 mm inside the plate top/bottom edges; the contact centre stays ≤ 15 mm off the core centre (16 mm inside the core edge). **Open: spreader bending check for a 15 mm off-centre load on a 0.5 mm ribbed plate** (Materials/ID; go to 0.8 mm, +0.0065/side, if it fails).
- Thermal: ≥ 5 mm air gap vented top and bottom, low-e foil on the bulkhead, pad face about 47–50 °C (Thermal). Stack 70 mm from the bulkhead (+12 vs R3).

| item (per side) | kg |
|---|---|
| HC 4.5 pcf core 62×62×57 | 0.0158 |
| Al 0.5 mm ribbed spreader 80×100 | 0.0108 |
| 4 PC corner-post side guides | 0.0040 |
| PC 1.5 backing 62×62 + M4 inserts | 0.0069 |
| EPP 80 face 6 mm 80×100 | 0.0038 |
| face sleeve TPU-nylon | 0.0050 |
| low-e foil + 4 standoffs | 0.0010 |
| **per side** | **0.0473** |
| **pair** | **0.095 (cap 0.10, −0.005)** |

Materials estimated about 0.068 pair; the difference is the enlarged face plate (needed for the edge margin), the face sleeve and the foil/standoffs. R-047 item 4 = **−0.005**.

## R3 (Controls 03fc980), superseded: design energy 265 J, not 220. Re-sized
- Peak force fixed at 8.3 kN design → 9.13 kN (548 N·m ≤ 550), so the **area stays 84 cm²**. Stroke 265/8.3 = 31.9 mm → **honeycomb 44 mm** (was 37).
- Plain (b2) at 265 J = 0.103 kg pair (+0.003 over the cap). **R3 pick: 5052 honeycomb 3.1 pcf, 80 w × 105 h mm (84 cm²) × 44 mm, EPP face 10 → 6 mm, 0.5 mm Al spreader, PC backing, sleeve: 0.1004 kg pair, i.e. AT the 0.10 cap with zero margin.** Stack 58 mm from the bulkhead (+3 vs R2; Controls: width OK, about 1° more lean).
- Coverage: Controls says contact lands at or slightly above the centre, and 10–15 mm below it when leaning hip-first. A 105 mm tall pad with its centre 5 mm below the shoulder axis keeps the ±15 mm contact band ≥ 37 mm inside the top/bottom edges. The spreader carries an off-centre load into the core. OK.
- (b1) 4.5 pcf (0.067) rejected now: its 68 mm square pad leaves only about 19 mm edge margin with the offset contact.
- **Arbiter:** item 4 of R-047 moves from −0.005 to **0.000**. If Materials' cited 3.1 pcf crush strength comes in below about 0.90 MPa, the pair goes over 0.10 → re-rule (2.3 pcf fallback 0.130, +0.030; R-047 total still −0.19 / −0.095 half-credit). Other options at 265 J: EPP (a) 143 mm, 0.160; hybrid (d) 0.111; 3003 3.1 pcf 0.111.

## R2 re-size (Materials 5f8f149, `materials/R042_EPP_SHOULDER.md`): R1 40 mm EPP 80 FAILS
R1 assumed a constant 0.65 MPa crush. On the real ARPRO 5170 curve (0.50/0.70/1.60 MPa at 25/50/75 %, rate ×1.45) 220 J peaks at about 19.5 kN → **≈ 1.17 kN·m vs 550 allowed**. Re-sized in `shoulder_pad.py` → `shoulder_pad.json`.
Requirement: 220 J at peak F ≤ 550/0.060 = **9.17 kN**. EPP: force checked at RT × rate, stroke at hot (40 °C pad face, ×0.70) × rate, up to 65 % strain. Honeycomb: pre-crushed, constant crush, stroke 0.72 t, rate ×1.10, designed at 8.3 kN → 9.13 kN peak (548 N·m). All masses include the PC backing (8 g, Materials), sleeve and 5 mm air gap to the 69 °C bulkhead in the stack. Honeycomb crush strengths are [EST] catalog-class values: **Materials to cite**.

| option | element | area cm² | thick mm | stack from bulkhead mm | pair kg | vs 0.10 cap | peak / moment | notes |
|---|---|---|---|---|---|---|---|---|
| R1 | EPP 80, 40 mm | 109 | 40 | 47 | 0.116 | +0.016 | ~19.5 kN / 1.17 kN·m | **FAIL** |
| (a) | EPP 80 | 51 | **119** | 126 | 0.136 | +0.036 | 9.17 / 550 | passes but +80 mm proud per side (shoulder width +160 mm): unacceptable envelope; single-use > 50 % strain |
| (b1) | 5052 HC 4.5 pcf + 10 mm EPP + 0.5 mm Al spreader | 46 | 37 (+10) | 55 | **0.061** | −0.039 | 9.13 / 548 | lightest; small footprint (~68 mm sq), weak to oblique hits > ~15° |
| **(b2)** | **5052 HC 3.1 pcf + 10 mm EPP + spreader** | **84** | **37 (+10)** | **55** | **0.095** | **−0.005** | **9.13 / 548** | **recommended**: ~92 mm sq covers the tuck contact; replaceable cartridge after a hard fall |
| (b3) | 5052 HC 2.3 pcf | 122 | 37 | 55 | 0.122 | +0.022 | 9.13 / 548 | over cap |
| (b4) | 5052 HC 1.6 pcf | 243 | 37 | 55 | 0.200 | +0.100 | 9.13 / 548 | over cap |
| (b5) | 3003 HC 3.1 pcf | 91 | 37 | 55 | 0.103 | +0.003 | 9.13 / 548 | marginal over |
| (c) | EPP 80 for 80 J (Controls cut) | 51 | 43 | 50 | 0.062 | −0.038 | 9.17 / 550 | needs Controls to cut shoulder energy 220 → 80 J (−64 %); not credible from A44 today |
| (d) | HC 3.1 core (200 J) + 15 mm EPP | 84 | 48 | 56 | 0.103 | +0.003 | 9.13 / 548 | EPP outer is multi-hit for small knocks; marginal over |

**Recommendation: (b2) 5052 honeycomb 3.1 pcf, 84 cm² × 37 mm, pre-crushed, in a replaceable cartridge (PC backing, 0.5 mm Al spreader, 10 mm EPP 80 cosmetic face, sewn sleeve), 0.095 kg pair (−0.005 vs cap).** Peak 9.13 kN = 548 N·m: it meets 550 with the only margin being the 10 % design factor. (b1) is the fallback if mass is tight and Controls confirms near-normal impact. Envelope: 55 mm proud of the bulkhead vs 47 mm in R1 (+8 mm per side).
- **Arbiter re-rule: not needed** if (b2) holds ≤ 0.10. It needs an Arbiter note that the pad is **single-use** (cartridge swap after a hard fall, T8 "replaceable pads"), and Materials must cite the honeycomb crush strength. If the cited 3.1 pcf crush strength is below about 0.85 MPa the area grows and the pair goes over 0.10 → re-rule.
- **Controls energy cut: not needed** for (b). Only option (c) needs it. Controls still has to confirm in T-030 that shoulder energy ≤ 220 J and that the impact is within about 15° of the pad axis.

## R1 analysis (superseded, kept for record)
## Basis (Controls A44, `controls/fall/A44_side_fall.md`)
- Side fall from standing at 66.21 kg: E = m·g·0.98 = **637 J**. With the A44 strategy (knee drop, arm tuck, hip-first lean), shoulder energy is capped at **220 J**.
- Constant-force crush over s = 0.7·t + 3 mm (v3 `fall_model`). Bearing moment = F × 60 mm.
- 30 mm pad: s 24 mm → F 9.17 kN → **550 N·m**. **40 mm pad: s 31 mm → F 7.10 kN → 426 N·m**, i.e. **−22.6 %** at the same energy (R-042 asks for about 23 %). That is a CRBH 7013 radial SF of about 1.28 × 550/426 ≈ **1.65** if T-030 confirms the 220 J.

## Foam choice (pad sized so plateau stress × area = 7.10 kN)
| foam | ρ kg/m³ | plateau MPa [EST] | area cm² | kg/pad |
|---|---|---|---|---|
| EPP 45 | 45 | 0.30 | 237 | 0.043 |
| EPP 60 | 60 | 0.45 | 158 | 0.038 |
| **EPP 80 (pick)** | 80 | 0.65 | **109** | **0.035** |
| EVA 100 closed-cell | 100 | 0.55 | 129 | 0.052 |
| PORON-class PU 240 | 240 | 0.50 | 142 | 0.136 |

Why EPP 80: lightest per joule of the options, flat crush plateau (so the constant-force model holds), and it **recovers** for multi-hit use (T8: ≥ 1 fall/day on replaceable pads). PORON and EVA are comfort/vibration foams: too heavy, and they bottom out early. A pad bigger than 109 cm² would stop it reaching the plateau: crush force stays near 7.1 kN only if the area is right.

## Geometry and mounting (minimal carrier; arm shells deferred to Arms R2)
- Pad: 40 mm EPP 80, about 105 × 105 mm footprint (109 cm²), domed outer face, on the lateral face of the shoulder roll housing / bulkhead. It sits in the A44 arm-tuck footprint (the upper arm sits inside it).
- Carrier: **no rigid shell.** A sewn TPU-coated nylon sleeve (0.03 m², 9 g) with the pad moulded around 2× M4 inserts (6 g incl. a 25 mm hook-strap anchor), bolted to existing bulkhead tapped holes. No new holes in FEA'd parts; bulkhead hole pattern to be confirmed with Torso.
- It must not cover the shoulder-bay vents (≥ 25 cm² in/out, Electronics/Thermal A43) or press on the RP40 gap-pad strap.
- Replaceable in about 2 min (2 screws). Pads are a wear part after a hard fall (R-021 basis).

## Mass
Foam 0.035 + sleeve 0.009 + inserts/anchor 0.006 = **0.050/side, 0.100 kg pair = at the R-042 cap (0.10)**. **No margin:** if Materials' EPP 80 plateau comes in below about 0.6 MPa, or the sleeve is heavier, the pair goes over 0.10 and returns to the Arbiter. Fallback: EPP 60 at 158 cm² (0.038/pad) gives 0.106 pair. Listed in `cover_set_v5.json` as its own row, outside the P-020/P-022..025 delta.

## Questions for RL Materials (89a94197)
1. EPP grade: the cited compressive plateau for EPP 80 g/L (ARPRO / Neopolen) at 25–60 % strain, and the densification strain (the model needs about 78 %).
2. Multi-hit: recovery and plateau loss after 10 / 100 hits at 220 J; strain-rate factor at about 3–4 m/s impact.
3. Moulded-in M4 inserts in EPP 80: pull-out strength, or do we need a bonded PC backing plate (+about 8 g)?
4. Temperature: plateau at 0 °C vs 40 °C next to a shoulder bulkhead at about 69 °C (A43). Is EPP OK at that contact temperature?
5. Add EPP 80 (and the sleeve fabric) to MATERIALS_DB; EPP grade is [UNKNOWN] there today.

## Questions for RL Controls (c5cee5de)
1. T-030: please model the pad as 40 mm, s = 31 mm, constant force 7.10 kN (109 cm² × 0.65 MPa), and report the shoulder share and peak bearing moment against 550 N·m.
2. Is the contact point during the arm tuck on the lateral shoulder face (pad centre) or higher on the deltoid? If it's higher, the pad moves.
3. Does the 40 mm pad (about 10 mm more lateral) change the topple geometry or the knee-drop timing?
4. What sensitivity to shoulder energy above 220 J should we design for (worst-case push)?

## R9 (2026-10-21): response to job1 FAIL (a556d44)
- **Failing interface: CRBH 6013 static s0 (Arms' roll bearing)**, axial-shear cases 1.45 @0 / 1.29 @10 mm. The tray and M4s pass (tab bearing SF 1.62, no slip 593 < 825 N). No tray/washer/doubler change can fix s0: it is set by pad force and lever arm.
- ID-side fix (pad_r9.py/.json): core **55.3 × 55.3 × 60** 4.5 pcf (peak 7.0 kN at ×1.3, was ~9 kN) + **0.25 mm PTFE-faced slip skin** on the EPP face (μ ≤ 0.15 caps tangential shear). Tray, boss, 4× M4 unchanged; core centred on tray.
- Hand-calc s0 (same P0 as fea_job1.py): **2.32 @ e0, 2.13 @ e5, 1.97 @ e10**. Reaching 2.0 at e10 needs Arms (qualify e ≤ 5 mm or a bearing with C0 ≳ 27 kN). Proposed to Arms; not imposed.
- Energy 237 J ≥ 220 J (A44 cap) but < 265 J R3 design energy: needs the 220 J basis confirmed.
- Roll torque Mx 448 (axial) – 539 (down) N·m, still > CSG-25 369 N·m momentary peak (was 566–773). Driven by the 64 mm pad-centre offset from the roll axis: raised with the Arbiter.
- Mass: −0.007 kg pair [EST] (core −3.5 g, spreader −1.1, EPP −0.4, PTFE +1.7 per side).
- Rerun: fea/job1_pad_r9/CASE.md.

## R10 (2026-10-21): per R-119 (03fe1ca) — supersedes R9
- Core **54.8 × 54.8 × 75.3 mm** 5052 HC 4.5 pcf (1.79 MPa), peak **7.0 kN** at ×1.3, energy **292 J** (0.72 stroke, static plateau). Contact face Y = 102.3 mm (was 87). Tray, boss, 4× M4 unchanged. PTFE skin: option only, not credited.
- s0 (15° case, shear 0.27 N): **1.81 @ e0, 1.70 @ e5, 1.60 @ e10 — FAIL**. Roll Mx raw 433 (axial) / 618 (down) N·m; clutch-limited ≤ 307 (R-119).
- Mass: pair **0.065 kg ex Arms' boss** (≤ 0.100 PASS); 0.113 if the 0.024/side boss is counted in the pad cap (FAIL). Core mass is fixed by energy (~16 g/side regardless of F).
- Envelope: core +15 mm vs R8 (+15 mm proud per side): needs check.
- Trade: lowering F does not close s0 (core grows to hold 292 J, lever grows): 6.0 kN → 88 mm core, s0 2.04/1.91/1.80. 7.0 kN is the best trade (shortest, lightest proud). **Closes only with Arms: bearing C0 ≥ 26.8 kN (e0) / ≥ 30.4 kN (e10) vs CRBH 6013 24.3**, or Materials-credited μ ≤ 0.15 skin plus e ≤ 5 mm.
- Rerun: fea/job1_pad_r10/CASE.md.

## R10 status per R-120 (12f68a4)
- **Booked: R10 pad pair 0.065 kg PASS** vs 0.100 cap (cap = pad assembly incl tray/sleeve/fasteners; stand-off outside it, Arms ledger). +15 mm/side envelope accepted provisionally pending Arms clash check.
- s0 path (R-120): R10 core + Arms stand-off (pad centre Z −20) + CRBH 7013 A + e ≤ 5 mm: s0 2.31/2.16/2.04, Mx 321 N·m, CSG-25 SF 1.10. R-119 clutch basis withdrawn.

## R10 stand-off layout proposal (Arms-owned part) — pad_r10_standoff.py/.json
- Machined 7075-T6, replaces the 62×62×10 boss. **ID layout only; Arms owns and finalizes it** (roll-output bolt interface, sizing, drawing).
- Roll flange ring OD 60 / ID 40 × 4 mm on the roll output (bolt pattern TBD Arms) → 2 ribs 5 × 30 mm, Y 0–23, spanning Z 0 to −20 → pad face plate 62 × 62 × 4 (Y 23–27, rear pocketed, 2 mm floor) with 4× M4 tapped bosses on ±24 mm. Tray (0.5 mm) and R10 core 54.8 sq centred unchanged; mount face Y 27 keeps contact Y 102.3.
- Mass **0.051 kg/side, 0.102 pair [EST]** (plate 0.019, ribs 0.018, flange 0.014); R-120 booked 0.050/side.
- Arms to confirm: roll-output bolt pattern on CRBH 7013 A; rib/flange sizing under 7.0 kN at 15° (Job 8 add-on); e ≤ 5 mm tolerance stack; clash check (pad + stand-off + 7013 housing through abduction ROM, tuck, cover set); Y datum 27.
