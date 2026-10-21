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

---
# Follow-up round (T&R after 2975e93) — PARTIAL
## (2) Head-first replay (11 seeds, deterministic rerun; `l3_headfirst_replay.json`)
Head body linear velocity in the WORLD frame via mj_objectVelocity at first head–floor contact (not cvel). Head body mass in model
(scaled to 68 kg) = **0.48 kg** [model value; looks light vs a real head+sensors — flag]. E_head = 0.5·m·v² [EST]. Upper KE = waistY..head
subtree translational + rotational KE at that instant.
| seed | t s | |v| m/s | v_normal | E_head J | upper KE J |
|---|---|---|---|---|---|
| 0 | 0.943 | 3.82 | 3.78 | 3.5 | 209 |
| 2 | 0.770 | 4.86 | 4.81 | 5.7 | 289 |
| 3 | 0.634 | 4.54 | 4.52 | 5.0 | 196 |
| 6 | 0.906 | 4.45 | 4.40 | 4.8 | 268 |
| 9 | 0.680 | 4.42 | 4.40 | 4.7 | 186 |
| 10 | 0.746 | 4.66 | 4.61 | 5.3 | 276 |
| 14 | 0.820 | **4.99** | **4.91** | **6.0** | **301** |
| 16 | 1.063 | 4.33 | 4.29 | 4.5 | 263 |
| 17 | 0.649 | 3.99 | 3.98 | 3.8 | 163 |
| 20 | 1.080 | 4.58 | 4.49 | 5.1 | 283 |
| 22 | 0.895 | 3.83 | 3.78 | 3.5 | 202 |
Worst: 4.99 m/s (4.91 normal), 6.0 J head-only [EST], 301 J upper body (seed 14, toe pivot). The head reaches the floor essentially vertically,
carrying most of the upper-body KE behind it: head-first is a real failure mode in passive (MO=0) topples, not an artefact.

## (1) Forced-25° set at 72.1 kg — NOT ACHIEVED
Searched 32 ICs (`l3_forced25.json`): knee and toe pivot × roll 0.3–0.6 rad × lean 0.15/0.3; then arms overhead (sp −2.8) / back (+1.5)
× hip pitch −0.6/−1.2 × roll 0/0.4. Pad tilt at first pad contact stayed 9.9–17.0°; with arms/hips moved, the pad mostly never touched
(hands, shanks, thigh or pelvis took the landing). **0 runs within 25±3° → no forced-25° results, second-rotation history, crush or criteria for
this set.** In this passive model a 25° chest-pad-first contact does not arise from topple ICs alone; it would need an imposed initial
angular velocity / a pivot that holds the body at 65° pitch, i.e. a prescribed-state impact, not a topple. The trunk-history logging
(pitch/roll/ω every 20 ms for 1 s after pad contact) is now in `l3_25deg_topple.py` for that run.

---
# Head 1.104 kg rerun (ID; CONTRACTS head+neck R-026/A23) — `l3_headfirst_replay_1104.json`, `l3_headfirst_geometry.json`, `l3_headfirst_worst_pose.json`
Head body mass 0.484 → 1.104 kg (inertia scaled ×2.28); the difference is taken off the torso (inertia scaled); total checked = 68.000 kg.
Same 11 seeds, same ICs. Speeds = head body linear velocity, world frame, at first head–floor contact. E = 0.5·1.104·v² [EST].
dz = height of the reference's lowest point minus the head's lowest point, along the floor normal (+ = head lower). Shoulder = upper_arm
geom lowest point (shoulderP has no geom). Contact order excludes feet; knee-pivot seeds list the shanks at t=0 (they start kneeling).
| seed | head-first | t s | |v| | v_n | E J | upper KE J | dz chest pad mm | dz L/R shoulder mm | 2nd (gap ms) | 3rd (gap ms) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | yes | 0.945 | 3.83 | 3.79 | 8.1 | 205 | 253 | 335/335 | L_hand (190) | R_hand (190) |
| 2 | yes | 0.774 | 4.91 | 4.85 | 13.3 | 294 | 123 | 249/249 | L_hand (83) | R_hand (83) |
| 3 | yes (after shanks) | 0.639 | 4.56 | 4.53 | 11.5 | 200 | 50 | 136/136 | — | — |
| 6 | yes | 0.907 | 4.45 | 4.40 | 10.9 | 274 | 169 | 293/293 | L_hand (129) | R_hand (129) |
| 9 | yes (after shanks) | 0.685 | 4.44 | 4.42 | 10.9 | 190 | 69 | 183/183 | — | — |
| 10 | yes | 0.748 | 4.68 | 4.63 | 12.1 | 279 | 149 | 270/272 | R_hand (99) | L_hand (100) |
| **14** | yes | 0.823 | **5.02** | **4.94** | **13.9** | **305** | 104 | 233/232 | L_hand (75) | R_hand (75) |
| 16 | yes | 1.061 | 4.31 | 4.28 | 10.3 | 258 | 191 | 308/309 | L_hand (148) | R_hand (148) |
| 17 | yes (after shanks) | 0.653 | 4.01 | 3.99 | 8.9 | 165 | 111 | 220/220 | — | — |
| 20 | yes | 1.079 | 4.55 | 4.47 | 11.4 | 281 | 155 | 285/285 | L_hand (118) | R_hand (118) |
| 22 | yes | 0.897 | 3.84 | 3.80 | 8.1 | 206 | 254 | 338/337 | L_hand (209) | R_hand (209) |
For the knee-pivot seeds 3/9/17 the order is shanks (t 0), head; 2nd/3rd after the head were not captured (log keeps the first 3 contacts).
All 11 remain head-first. The head is 50–254 mm below the chest-pad plane and 136–338 mm below the shoulders at contact: the head lands
alone, with the shoulders far off the floor, so a shoulder cover would not intercept it in these topples.
Worst seed 14: full pose at head contact in `l3_headfirst_worst_pose.json` (all body positions, torso/shoulder/upper-arm/head quats);
upper-arm lowest point 231 mm (L) / 231 mm (R) above the floor.

---
# Head-first variants (T&R hypothesis on 0ef2d9e) — `l3_headfirst_variants.json`
Same 11 seeds, head 1.104 kg (torso reduced, 68 kg total), all drives MO=0 except the holds. Hold = PD at the post-settle angle
(Kp 5000 N·m/rad, Kd 100) clipped at ±L applied as joint torque: a torque-limited stiff hold; when saturated it gives ±L, i.e. slip at L
(slip friction = L, approximated by the clip, not a separate Coulomb model). Waist L = 204 N·m output. **Knee L = 129 N·m = the sim/v3
drive peak (prone_data s.lim)**, not the D99 stop. Head speed = world frame at the head's first contact (later than first contact when not head-first).
| variant | head-first /11 | notes |
|---|---|---|
| baseline (free, 0ef2d9e) | 11 | waist flexes to +60 (flexion stop) |
| A waist 204 | **2** (seeds 0, 22) | waist slipped to −30.3/−17.5 (extension) in those 2; 9 others: hands first, waist within ±5° |
| B knees 129 | **9** | 2 knee-pivot seeds (3, 9) thigh-first; waist still flexes to 41–62° |
| C both | **3** (0, 9, 22) | seed 9 waist −6.3° yet head-first after shanks |
- **The free waist is the main cause: holding the waist cuts head-first from 11 to 2; holding the knees alone does almost nothing (9).**
- Cost: with the waist held, chest-pad energy ×1.5 rises to 518–539 J in toe runs (pad speed 5.4–5.5 m/s, above C2's 4.24 limit);
  knee-pivot runs 260–302 J at 3.4–3.9 m/s. Still ≤ 680 J (C1) and no bottoming (from previous runs' max crush; not re-logged here).
- In hand-first runs the head lands 21–24 mm *above* the chest-pad plane (dz −24) and 35–60 mm below the shoulders.
- Remaining head-first in A/C: the waist slips into extension (holding torque 204 N·m exceeded); head speed 5.26–5.59 m/s, 44–128 mm below the pad.
Per-seed first body, offsets, head speed, chest E×1.5, pad speed and waist/knee spans are in the json.
