# O-T5 reference tasks: walk/stand split (RL Controls draft for RL Torso & Power, 2026-10-14)
**Status: [EST] draft, not a task simulation.** No task sim or logged duty exists in the repo. The durations below are arithmetic from the stated assumptions. Torso fills the power column, and the walk fraction per task falls out of the timeline. Replace this with logged sim or hardware duty once the RL policy can do the tasks.

## Assumptions (all labelled)
- **A1** Walking 1.0 m/s cruise (T7 rating speed, R-010). Accelerate/decelerate adds 1.0 s per walk segment [EST].
- **A2** Turn in place 180°: 3 s [EST] (stand-class power, steps in place).
- **A3** Pick from a surface: 6 s (reach, grasp, lift into the P-042 band) [EST]. Place: 6 s [EST]. P-042 only bounds transitions (≤ 30 s to reach the band). No cycle time is in the repo.
- **A4** Carry walking with 20 kg in the P-042 pose at 1.0 m/s (R-014 carry verified at 1.0 m/s).
- **A5** Scan/perception/alignment before a pick: 2 s stand [EST].
- **A6** Idle waits are task-specific and stated per task [EST]. Idle = standing, arms down, compute up.
- **A7** Distances are stated per task [EST layouts, not measured sites]. Agility/GXO tote-transfer is the published analogue (station-based, short walks; Torso R1 §13.5 sources).
- Phase classes for power: **walk**, **carry-walk**, **stand** (balance only), **pick/place** (stand + arm work), **idle** (stand, low compute).

## T-A Tote transfer AMR → conveyor, 5 m (station-based, GXO-like)
| # | phase | class | duration s | basis | power W (Torso) |
|---|---|---|---|---|---|
| 1 | wait for AMR | idle | 20 | A6 | |
| 2 | scan + align | stand | 2 | A5 | |
| 3 | pick tote (≤ 20 kg) | pick/place | 6 | A3 | |
| 4 | turn 180° | stand | 3 | A2 | |
| 5 | carry 5 m | carry-walk | 6 | 5/1.0 + 1 (A1, A4) | |
| 6 | place on conveyor | pick/place | 6 | A3 | |
| 7 | turn 180° | stand | 3 | A2 | |
| 8 | walk back 5 m | walk | 6 | A1 | |
| | **cycle** | | **52** | walk + carry-walk 12 s = **23 %** | |

## T-B Tote transfer, 10 m
Same as T-A, with phases 5 and 8 at 11 s each. Cycle 62 s, walk + carry-walk 22 s = **35 %**.

## T-C Tote transfer, 20 m
Same as T-A, with phases 5 and 8 at 21 s each. Cycle 82 s, walk + carry-walk 42 s = **51 %**.

## T-D Shelf picking, 4 picks per bay, bays 3 m apart, drop at a cart after 4 bays (16 picks)
| # | phase | class | duration s | basis | power W (Torso) |
|---|---|---|---|---|---|
| 1 | per pick: scan + pick + place to cart tote ×16 | stand + pick/place | 16 × (2 + 6 + 6) = 224 | A3, A5 | |
| 2 | walk between bays ×3 | walk | 3 × 4 = 12 | 3/1.0 + 1 (A1) | |
| 3 | push/walk cart to drop 15 m | carry-walk | 16 | A1, A4 (cart, not carry, [EST]) | |
| 4 | hand off, wait | idle | 30 | A6 | |
| 5 | walk back 15 + 9 m | walk | 25 | A1 | |
| | **cycle** | | **307** | walk-class 53 s = **17 %** | |

## T-E Assembly-line kitting at a fixed station (mostly stand)
| # | phase | class | duration s | basis | power W (Torso) |
|---|---|---|---|---|---|
| 1 | pick/place parts ×10 | pick/place | 10 × 12 = 120 | A3 | |
| 2 | walk to bin rack 4 m and back | walk | 2 × 5 = 10 | A1 | |
| 3 | wait for line | idle | 60 | A6 | |
| | **cycle** | | **190** | walk 10 s = **5 %** | |

## Summary for O-T5
| task | walk-class fraction |
|---|---|
| T-A 5 m tote | 23 % |
| T-B 10 m tote | 35 % |
| T-C 20 m tote | 51 % |
| T-D shelf pick | 17 % |
| T-E kitting | 5 % |
The 20 % walking share in Torso §13.5 sits between T-D and T-A. A 50 % share is only reached for 20 m tote runs. **This is still [EST]:** it rests on layout and cycle-time assumptions, not on a site study or sim. Torso picks the rating task with the Arbiter. Next steps:
1. Torso fills in power per phase class.
2. Controls replaces A2/A3 with times from the RL policy once it can turn and pick.
