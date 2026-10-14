# RL Arms & Hands R6 (2026-10-14): forearm stack-up with D76, compaction, Controls inputs, bryan-PC job spec
model_v4 finger/thumb/lug −12 mm: commit **c6de2ce** (syntax/import check only).

## 1. Full forearm stack-up with D76 (R-057 condition "≈ 9 mm margin"): **DOES NOT FIT with cited lengths, −14.5 mm**
Elbow axis to wrist pivot: 270 mm (model_v4 `forearm`). The arrangement assumes Arms R5 §8 options 1 + 2:
- wrist roll at the elbow end, solid
- 5 DCX16 drives in the palm
- 6 flexors as one bonded ring

| item | mm | source |
|---|---|---|
| elbow housing zone (OD72 about y, forearm starts at ez − 36) | 36.0 | model_v4 |
| wrist roll, elbow end, solid: TBM2G-05008 19.84 + CSG-14 H1 18.5 + CRBH 258 8 + AksIM-2 12.45 + 2 × 2 walls [EST] | 62.8 | D76 cited lengths (same unit family as D70) |
| 6-flexor ring (6 × DCX22S+GPX22HP+ENX22 INT 70.9, +1 tol, +10 spool [EST]) | 81.9 | D68 |
| hand board stack | 13.0 | Electronics [EST] |
| D76 pitch/yaw side by side, z +28 … +90.8 above the pivot | 90.8 | D76 |
| **total** | **284.5** | |
| **margin vs 270** | **−14.5 mm** | |

- Where "9 mm" came from: Arms R5 §8 counted D73 as 112 mm above the pivot (it is 140, or 148.8 cited). Subtracting D76's 49 mm saving from that undercount gives 309.9 − 49 = 260.9, which looks like +9. **Corrected: the R5 number was wrong by 28 mm.** Arms apologises for the error.
- The R4 layout (wrist roll distal, two tiers 163.8, small drives in the forearm) is worse: 36 + 163.8 + 13 + 90.8 + 62.8 = 366.4, i.e. −96.4 mm.

### Closing the 14.5 mm, no forearm growth (R-057: lengthening off)
| step | gain mm | basis | status |
|---|---|---|---|
| a. Hand board out of the forearm, into the upper-arm tube (ID 46 × 87 mm, model_v4). Board re-laid out as a 40 × 60 × 13 rectangle: chord at 6.5 mm offset = 2·√(23² − 6.5²) = 44.1 ≥ 40 ✓, 60 ≤ 87 ✓ | +13.0 | geometry | needs Electronics re-layout (28 → 24 cm²) and leads across the elbow only (≈ 22 motor + 6 × ENX conductors, 0.144 m loop [Electronics]). Lead mass ≈ 50 × 0.45 m × 5.4 g/m ≈ **0.12 kg [EST]**, against the freeze |
| b. Spool allowance 10 → 5 mm (integrated spool on the gearhead shaft; no part cited) | +5.0 | [EST] | Actuators to cite or design |
| c. D76 start z +28 → +26.5 (cross sphere r 24.5 + 2 mm gap) | +1.5 | wrist_clash_r4 rule | CAD |
| **sum** | **+19.5 → margin +5.0 mm** | | |

Without (a) the margin is −8.0 mm, so (a) is required.

**Alternative to (a):** the board on the palm backplate. Palm inner thickness 29 mm; the DCX16 drives need 17 and the board 13, total 30, so it **fails by 1 mm** (rejected unless the board is ≤ 12).

**Inertia note:** the forearm stays 270 mm. Moving 5 × 0.053 = 0.265 kg into the palm and the board (0.035) into the upper arm shifts the arm COM distal by ≈ 0.265 × 0.12 m ≈ +0.03 kg·m [EST]. Wrist static +≈ 0.2 N·m. Controls should re-run reach/inertia with `arm_inertials_r3.json` updated (R7).

## 2. D73 → D76 compaction (done by Actuators D76, adopted R-057)
- Side-by-side axial units, yaw on CSF-11-100: −49 mm vs D73 as booked, −58 mm vs cited lengths.
- Yaw margin 1.24× (11 vs 8.9 N·m). Arms check: the R3 wrist yaw need is 11.1 N·m at 1.5 × 7.4. The CONTRACTS yaw row is 8.9 (v2). **At the Arms R1 sim-based need, CSF-11 is 0.99× (11 / 11.1): fail by 1 %.** With the palm drop the yaw static is 8.58 → need 12.9, giving **0.85×, FAIL**.
  - The CONTRACTS 8.9 N·m (v2) does not include the 10 kg side-reach case (`arm_loads_r1.json` side_abduct: wrist_yaw static 7.4).
  - **Arms recommends CSG-14-100 on yaw too (36 N·m).** Cost: +2.5 mm length and +0.04 kg/side, which removes D76's −0.08. The margin then becomes +2.5 mm with steps a–c.
  - The Arbiter's call: either G3 accepts the yaw need as the CONTRACTS 8.9, or the R1 need of 11.1–12.9 applies.
- Wrist fairing about 116 mm wide (ID to accept, R-058).

## 3. Controls T-030 inputs (d43f14a)
**(1) Side-fall lever, cap-mounted pad → shoulder_pitch output bearing.**
Geometry (model_v4):
- bearing at the housing output end, ≈ y +0.20 (housing centred at shoulder_y − 5 = 0.165, L 80, output flange at +42)
- pad centre on the shoulder cap at y ≈ +0.30 (Controls), 40 mm EPP, so the outer contact face is at ≈ y +0.32
- pad centre 5 mm below the shoulder axis (ID)

A purely lateral impact (force along y) passes through the bearing axis line, so the lever is only Δz = 0.005 m. With the A44 trunk tilt φ (10–15° [EST]), the force line tilts:

lever ≈ Δz + Δy·sin φ = 0.005 + 0.12·sin φ = **0.026 m (10°) … 0.036 m (15°)**, vs 0.06 in v3.

Use **0.036 m (conservative)**. At 11.5 kN that is 414 N·m. At the 40 mm pad (−23 %, 8.86 kN) it is **319 N·m ≤ 550 gate**. The pad dome radius is not in the repo; contact scatter adds ±R_dome·sin φ in z [EST].

**(2) Hook-release time.**
- In a hook grasp the load itself opens the fingers once the tendon pays out. Extension is passive: v3 return springs plus the load.
- Pay-out is limited by the flexor no-load speed: DCX22S 24 V 12 400 rpm / 103 × 2π/60 × 4 mm spool ≈ 50 mm/s. The motor reaches it in ≈ 3 τm = 18 ms (τm 6.07 ms, datasheet).
- Unhook needs 5–10 mm of tendon pay-out [EST, edge clearance]. That gives **0.12–0.22 s**.
- **50 ms is optimistic. Use 0.2 s** (worst case 0.22 s at 10 mm). A faster drop needs a deliberate open (all six flexors reversed at full voltage). The time is speed-limited and cannot be cut by the power cap.

## 4. Grok Interface job spec (bryan PC; heavy, not run on the box)
- Repo: `https://github.com/BryanRalston/robot-lab.git`, branch `main`, at or after **c6de2ce** (this round's commit or later).

**Job 1, v4 audit + clash regeneration (wrist ±60/±30 + tuck):**
```
git clone https://github.com/BryanRalston/robot-lab.git && cd robot-lab && git checkout <commit>
cd modules/model
python3 -c "import model_v4 as M; M.build()"            # full CAD rebuild incl. palm_7075 DROP_MM=12 and c6de2ce finger/lug shift
# regenerate the sweep with the P-026 wrist ROM and the A44 tuck pose (sweep script that writes out/clash_v4.json; see sweep_log.txt for the command used last time)
#   wrist_pitch range -60..60 step 5, wrist_yaw -30..30 step 5 (full grid, combined), plus pose A44_tuck:
#   shoulder_roll -5, shoulder_yaw -60, shoulder_pitch -20, elbow -110 (both sides)
python3 audit_v4.py
```
Expected outputs:
- `out/clash_v4.json`, `JOINT_AUDIT.md`, `JOINT_AUDIT.json`
- **Pass criteria:**
  - wrist_pitch clear −60…60
  - wrist_yaw clear −30…30 (palm vs fork 0 clashes; sampled box check gave 4.91 mm)
  - fingers/thumb not overlapping the palm
  - tuck pose: forearm-to-torso ≥ 5 mm (box estimate 8.6 mm)

Return the files plus the run log to Arms.

**Job 2, T-030 / T-031 (Controls A44 S3 fall batch, d43f14a):** run as specified by Controls in `modules/controls/fall/` (50 pushes × 3 directions + forward-fall tuck case).
Expected outputs:
- peak shoulder pad force and share
- pitch-bearing moment using lever 0.036 m
- forward-fall pitch-gear torque with tuck (≤ CSG-25 rated / 369 momentary)

Gate: M ≤ 550 N·m (D71 7013 A), forward-fall pitch torque ≤ 369 N·m (R-057).

## 5. Industrial Design checks (cd5e88c: shoulder pad R5, wrist fairing)
**(1) Roll housing under the 8.94 kN pad load (62 × 62 mm saddle, 2.33 MPa):**
- The housing is 7075-T6 with a **2.0 mm wall** (`actuators/cad_mass.py` WALL), OD ≈ 84 (§1b).
- As a bare ring (w = 8.94 kN / 62 mm = 144 N/mm, M ≈ 0.318·w·r = 1 925 N·mm/mm), σ = 6M/t² ≈ 2.9 GPa. **The 2 mm wall alone FAILS.**
- The saddle must bear only over the stiff axial zones, the stator bond land and the CRBH bearing seat, or the cap needs its own load ring into the shoulder_P bracket.
- **Not accepted as is.** Needs G3 FEA.

**(2) 66.5 mm pad stack at y +0.30 vs upper arm (sim/v3 capsule r 40, from the roll origin y 0.282 z 0.18):**
- Pad volume y 0.267–0.333, z 0.163–0.268. **It overlaps the upper arm at every roll angle:** −7.5 mm at 0°, −22 mm at 45°, −40 mm at ≥ 90°.
- The pad must start above the arm's sweep (bottom edge ≥ z +0.19 at y ≤ 0.34), or be mounted on the roll output. **CAD/ID to re-place.**
- The A44 tuck is unaffected (the arm is adducted below the pad).

**(3) Tuck with the 124 mm wrist width:**
- At the R5 tuck (sp −20, sy −60) the wrist centre sits only 67 mm from the torso box, and the forearm 8.7 mm.
- **New tuck: shoulder_roll −5, shoulder_yaw −60, shoulder_pitch −30, elbow −110.** Forearm gap 28.0 mm. Wrist centre 89.8 mm from the torso, so 27.8 mm clear even with the 62 mm half-width facing the chest.
- Wrist roll is set so that the width lies parallel to the chest face. Controls to adopt.

**(4) Hand sweep vs wrist fairing:**
- With the sphere rule (fork/cross r ≤ 24.5) and the palm ≥ 27 mm from the pivot, the palm's highest point over pitch ±60 × yaw ±30 is ≈ z +5 above the pivot. Hand-computed from the palm top corners; confirm in the bryan-PC sweep.
- So the fairing lower edge must sit at **z ≥ +10** (≥ 5 mm gap) over |y| ≤ 62, and stay outside r 24.5 + 5 near the pivot.

## 6. Electronics §16.7 (8f4bad8)
- **Board radial fit (66 %, LQFP corner r 29.74/30, stack 12.4):** accepted on paper. A light 2D placement check is in Electronics' numbers; the CAD fit goes in the bryan-PC Job 1.
- **Axial:** 12.4 vs 13 gains 0.6 mm. **The forearm stack is still −13.9 mm (§1)**, so the board-in-upper-arm step (a) is still needed unless the spool and D76 steps find 14 mm.
- **Elbow crossing if the board stays in the forearm:** 4 power (+A, −A, +B, −B) + 2 enable, 6 conductors. Elbow loop 0.144 m (Electronics). SiF/SILI-E 0.25 mm² OD ≈ 1.7 has bend r/OD ≥ 24 on the harness drums. **OK.**
- **If step (a) moves the board to the upper arm,** the crossing becomes about 22 motor + 6 × ENX lines, about 50 conductors. That is a heavier loop; the drum fill was not checked.
- **Local motor leads:** ring (81.9 mm) → board at the distal end ≈ 0.10 m + pigtails, so **≈ 0.15 m confirmed** (board in the forearm).
- **ENX22:** the part choice is **ENX 22 EASY INT**. Its output type (TTL vs line driver) is **not cited** in the repo; D68 has its length only. Electronics: please confirm from the maxon sheet. The XMC4800 quadrature is OK with either.
- **Mass:** motor-lead booking 0.404 → 0.130 kg both, **−0.274 in the harness line** (not the arms line). The arms line is unchanged.
