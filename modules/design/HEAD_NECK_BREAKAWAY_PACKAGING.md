# Head-side packaging for the neck breakaway + bypass (Robot Lab ruling after P-161; mechanism owner: Actuators) — RL ID, 2026-10-21
Existing geometry only: head_shell.stl (x −83.5…+104.7, y 1699.2…1875, z ±94.9; frame x fwd, y up), torso_cover.stl top y 1610, HEAD_BALANCER.md parts, P-161.

## Envelopes
| item | value |
|---|---|
| Head shell outer | 188.2 (x) × 175.8 (y) × 189.8 (z) mm |
| Shell wall | 1.5 mm general, 2.0 mm under the P-161 liner patches |
| Head interior (inside 1.5 wall) | ≈ 185 × 173 × 187 mm; P-161 crown/brow liner (25 mm LD29) is added **outside** the existing interior (shell grows +27 mm at crown/brow), so interior is unchanged |
| ZED X Mini | 94 × 32 × 37 mm, 150 g, front of head behind the visor; its window + FOV cone are a Head-module keep-out — no breakaway part forward of the camera's rear face (x ≈ +60 [EST]) |
| XM430-W350 ×2 | 28.5 × 46.5 × 34 mm each; yaw servo on torso top deck (horn up), pitch servo in the yoke at the cheek; 6806 yaw (ø42×7) + 6800 pitch idler (ø19×5) |
| Neck gap, torso cover top → head shell bottom | 1699.2 − 1610 = **89 mm** vertical |
| Neck opening at torso top | ø90 (r 45) |
| Free annulus in the neck around the yaw servo (servo diagonal ≈ 44 → r 22) | **r 22…45, ~23 mm radial × 89 mm tall** — space for a fuse ring/shear pins on the yaw output or the yoke base |
| Free space in head below the pitch axis, behind the ZED | ≈ x −80…+60, y 1700…1760, minus the yoke and servo [EST] — for the head-side fuse seat |

## Suggested bypass path (head side)
1. Fuse sits at the yoke base, between the yaw output/6806 and the head yoke (inside the neck annulus above).
2. Head shell carries an internal **neck collar**: CF ring ø110 OD / ø92 ID, 3 mm, bonded to the shell skirt at y ≈ 1700, lower face **10 mm above** a torso **neck land** ring (Torso/Actuators-owned) around the ø90 opening.
3. When the fuse lets go, the head drops ≤ 10 mm and the collar seats on the land through a 5 mm LD29/TPU ring; crown load then goes liner → shell → collar → torso land, and the servos, horns and bearings carry no load.
4. Honest load note: the bypass moves the body-KE force into the torso; it doesn't absorb it. With 25 mm liner (17.5 mm usable) + ~3 mm ring, 457 J (1.5 × 305 J) means ~22 kN average through the collar/land. Torso and Actuators must rate the land, or add stroke there. The head shell skirt bond (≈ 345 mm perimeter × 10 mm) is Materials' check.
5. Collar ring ≈ 0.012 kg [EST]; land ring is on the torso side.

## Cover / visor rules
- No cover part may bridge the fuse: the fabric neck sleeve stays non-structural, with ≥ 15 mm slack so a 10 mm drop + tilt doesn't tear it.
- Visor stays recessed ≥ 20 mm behind the rim (P-161) and replaceable; no fuse or collar part in the ZED FOV.
- Head shell stays one piece; service access to the fuse is through the neck (sleeve off, head off the yoke at 4 screws [EST]).
- Liner patches are not structural for the bypass (shell + collar are).

## Open items for Actuators
1. Fuse type and break load (shear pins / ball detent) vs the neck's normal loads: gravity 0.61 Nm pitch, gaze dynamics.
2. Confirm the fuse fits r 22…45 × 89 mm and clears the XM430 cable and RS485/12 V routing.
3. Neck land on the torso top: rating for ~22 kN average (or more stroke), and the 10 mm drop gap.
4. Re-home / inspection after a break; encoder offset.
5. Head mass change (collar +0.012 [EST]) to the Arbiter with P-161.
