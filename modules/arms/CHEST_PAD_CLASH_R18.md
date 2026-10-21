# RL Arms & Hands R18 (2026-10-21): arm clash vs the deepened chest pad (ID 341ef4a, core 100 → 116 mm)
Script `chest_pad_clash_r18.py`, results `chest_pad_clash_r18.json`, image `media/progress/2026-10-21_arms_R18_chest_pad_clash.png`.

## Method
This follows the clash_r13 approach on sim/v3 kinematics, left arm only (the right arm mirrors it). Wrist joints are held at 0.

**Arm geometry:**
- Arm surfaces are sampled from the real sim geoms: upper-arm capsule r40, forearm capsule r38, and the hand box.
- The W2 carrier and pad envelope are sampled from the `cad/r15` STL.

**Chest pad (torso frame):**
- y ±0.049 and z 0.171–0.269, plus a 2 mm bezel/trim ring [EST].
- The pad face moves from x +0.159 (100 core, R-146) to x +0.175 (116 core).

**Gate and sweep:**
- Gate: ≥ 10 mm clearance.
- 61,170 poses: pitch −120…60 / 10°, roll −15…30 / 5°, yaw ±150 / 15°, elbow −140…0 / 10°, plus a roll-127 set.
- 3,232 poses where the arm is inside the crude torso box are excluded as self-colliding anyway, leaving 57,938 feasible poses.

## Result
| | 100 core (before) | 116 core (after) |
|---|---|---|
| min clearance | **0 mm** (contact) | **0 mm** (contact) |
| feasible poses < 10 mm | 192 | **269** (+77 new) |
| contact poses | 123 | 205 |
| failing parts | hand, forearm | hand 216, forearm 53; **carrier and upper arm never fail** |

**Named poses (before → after):**

| pose | before | after | result |
|---|---|---|---|
| tuck B | 198 | 198 | pass |
| roll soft limit 127° | 142 | 142 | pass |
| worst roll-127 pose (sweep) | 10.6 | 10.6 | pass, unchanged |
| P-042 two-hand carry (−45, −10, −30, −90) | 144 | 132 | pass |
| P-042 close carry (−25, −10, −40, −110) | 69 | 55 | pass |
| hands together low | 117 | 105 | pass |
| **hands together at chest (−60, −15, −60, −100)** | 27.9 | **11.9** | pass, 1.9 mm margin |
| elbow fold, front | 191 | 191 | pass |

Hand-to-opposite-shoulder and forearm-across-chest are already torso-box collisions, so they're excluded; the pad isn't what governs them.

**Failing region (after):**
- Elbow folded ≤ −90° (deepest at −110 to −140), with inward yaw −45…−120° and forward pitch −10…−120°, at roll −15…+30.
- Yaw band by elbow:
  - el −140…−120: yaw −45…−120
  - el −110: yaw −60…−120
  - el −100: yaw −75…−105
  - el −90: yaw −90
  - el ≥ −80: no fails
- The 77 new fails all sit in this same region. The 16 mm deeper core grows a pocket that was already failing at 100 mm; it doesn't create a new one.

## Limits needed
- **No change to the shoulder roll/pitch limits, tuck B, the 127° soft limit, or W2 carrier clearance.**
- **A fixed joint-range limit would cost the cross-body/hug workspace.** For example, yaw ≥ −45° whenever elbow ≤ −90° and pitch is −10…−120°. Recommendation: Controls adds the chest pad to the self-collision model as a box at x ≤ +0.185 torso (face +0.175 plus the 10 mm gate), y ±0.061, z 0.159–0.281. That puts a keep-out zone on the hand/forearm instead of a joint limit.
- If Controls wants a hard joint-space limit instead, apply the yaw band by elbow above, mirrored for the right arm.
- **This exists at 100 mm already (123 contact poses),** so it isn't a reason to reject 116.

From Arms' side, the 116 mm core is acceptable provided Controls adopts the keep-out. ID's statement "unaffected for roll ≥ 0" holds for the shoulder and carrier, but not for folded-elbow cross-body hand poses.

**Caveats:**
- The torso box is crude, and wrist joints are held at 0. A wrist flexed toward the chest could make the hand worse.
- The cover/pad bezel is [EST]. Final check on the real cover STEP comes in the G2 full-ROM sweep.
