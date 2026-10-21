# L3 25° topple with plateau pad (T&R 3ab7dd6) — RL Controls 2026-10-21 (PARTIAL; first pass)
`l3_25deg_topple.py` → `l3_25deg_topple.json`. 24 randomized 68 kg topples, prone_data.Sim (sim/v3 + pads), all drives MO=0 + D94 friction.
Pad: chest_pad MuJoCo contact OFF, replaced by T&R spec exactly: **9.21 kN constant normal plateau over 81.2 mm crush, then rigid wall
5.3 MN/m**; non-recovering crush (force only at max crush, while loading). Force applied as an external world-+z force at the lowest pad-face
corner. **The model has no shoulder pad geometry → shoulder pad NOT modelled** (a shoulder would show up as torso/arm contact).
Random: pivot toe (standing, even seeds) / knee (kneel, odd), lean 0.08–0.30 rad, yaw ±0.3, shoulder pitch −0.8..+0.4, friction 0.5–1.0.

## Results (24 runs)
- First contact: hand 9, shank/knee 2 (toe pivot), **head 11**, chest pad 2. 3 runs (toe, small lean) never touched the chest pad in 2.5 s (head-first, then settled).
- **Contact angle: NOT 25°.** Pad normal vs floor normal at chest contact was 0.6–19.6° (pitch 70–89°). No run reached a 25° chest landing,
  so this set does not directly answer "25°"; a 25° case needs a forced roll/yaw IC (not done).
- Chest energy ×1.5: max **489 J** (seed 18, toe, chest first); knee-pivot max 411 J. Max crush **36.5 mm of 81.2** (≥ 44.7 mm margin); **no bottoming** in any run.
  Peak pad force = plateau 9.21 kN in every crushing run (no wall).
- Pad normal speed: toe max 5.11 m/s, knee max 4.25 m/s.
## Release criteria (counts of 24)
1. Knees/hands/shoulder first (or chest within 10 ms of them) and E×1.5 ≤ 680 J: **11 pass** (all hand/knee-first). Fail: 2 chest-first (E OK, 437/489 J),
   **11 head-first** (head is not an allowed first body — flag to T&R/ID; head contact speed not logged here).
2. Pad speed ≤ 4.24 toe / ≤ 4.67 knee: **19/21 pass** among chest-contact runs; fails seeds 4 (5.11, toe) and 18 (4.92, toe) — the two chest-first runs. 3 no contact.
3. Free-body slide (feet/knees move > 20 mm): **22/24 slide**; seeds 3, 17 (knee) ~19–20 mm (borderline, pivot ~held).
Not logged: the second trunk rotation (only pitch/roll at contact and crush history every 10 ms for 0.3 s). CoM height at contact 0.10–0.16 m.

## Correction to T&R_3eacd56_REPLY (084af79), checked in this round
- Head/torso "contact speeds" there used `cvel[3:]`, which is the velocity at the subtree-CoM reference, NOT the body point. **Wrong.**
  Recheck of the "9.44 m/s" cell (68 kg, waist 0, 90 N·s, tripped): head world-frame linear speed at first contact **3.52 m/s** (vx −1.56, vz −3.15),
  t = 0.813 s, waist rate −6.01 rad/s at waist 3.2°. All torso/head contact speeds in 084af79 are void.
- Frames: chest_pad is at +x of torso (x 0.10 vs 0.0) → **+x is anatomical forward; the −x push is rearward (correct)**. Waist +0.3 rad moves the head
  +0.11 m in x → **+ waist pitch = flexion; −30° end = extension stop, +60° = flexion stop.**
- Inertia used in waist_energy_backfall: model body inertias of the waistY subtree only (incl. arms, head) about the waist axis at the impact pose;
  **no reflected rotor/armature** (Torso 0.24 or T&R 0.652 kg·m² would add on top). Arms are at their passive pose at impact (start pose arms-down), not forced down.
