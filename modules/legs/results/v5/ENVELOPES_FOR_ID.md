# Legs v5 fairing keep-outs: summary for RL Industrial Design (2026-10-14)
Source: `legs/fairings_v5.py` (model_v4 swept, left leg; mirror y for the right). Each keep-out is the convex hull of the hardware swept over the full range, plus 5 mm, expressed in its mount-segment frame (model_v4 stand coordinates, mm). Files: `results/v5/<name>_keepout.stl`, `envelopes.json`.

| envelope | frame | swept range | poses | bbox min → max (mm) | area cm² | status |
|---|---|---|---|---|---|---|
| shin_fairing | L_shank | ankle pitch −45…+40 × roll ±18 | 35 | (−20, 38, 145) → (135, 222, 473) | 1751 | **restored** (tibia saddle dropped, Thermal 9b9e169) |
| ankle_boot | L_shank | same | 35 | (−79, 47, −37) → (119, 213, 175) | 1258 | final (boot top z ≤ 170) |
| thigh_fairing | L_thigh | hip pitch −105/−74.6/0/+40 × knee 0–135 | 16 | (−181, 15, 555) → (72, 245, 885) | 2633 | final |
| knee_cap | L_thigh | knee 0–135 (shank parts r ≤ 110 about the knee axis) | 10 | (−114, 35, 386) → (101, 225, 555) | 1211 | final |
| hip_skirt | pelvis | yaw −35/0/+45 × roll −12/0/+15 × pitch −105/−74.6/0/+40 (r ≤ 150 about hip) | 36 | (−143, −19, 793) → (153, 283, 1126) | 2987 | final |
| foot_upper | L_foot | — (no screws, z 18–165) | 1 | (−65, 53, 13) → (185, 208, 113) | 1055 | final; sole 240×100 patch unchanged |

## Answers to V5_COVER_SET open question 1
- **Knee cap vs thigh fairing:** no overlap at any angle from 0 to 135° (5° steps, `knee_cap_vs_thigh_gap.json`).
  - Minimum gap between the two keep-outs is **10.2 mm at 135°**. It is 22 mm from 0 to 105°, set by the thigh fairing's lower edge at z 555.
  - With Actuators D69's ø85 knee housing (+4.5 mm radial, not yet re-CADed), expect about 5.7 mm [EST]. Recheck after the re-CAD.
- **Skin = 0.7 × hull area:** the convex hull over-states area at concave regions and includes the back and inner faces. A front/outboard trimmed panel is about 0.4–0.5 of the hull. 0.7 is conservative for full wrap only. Measure on CAD (A29).
  - foot_upper area fell from 1927 to 1055 cm²: the first run wrongly included the ankle screws. **Re-run cover_set_v5.py**, since your foot shell mass is about 45 % lower.
  - hip_skirt fell from 11317 to 2987 cm² (the first run included the whole raised thigh). knee_cap fell from 3422 to 1211.
- **3 mm extra flex gap:** reasonable for PC 1.5 on top of our 5 mm (8 mm total to hardware). Keep the 3 mm at the knee cap / thigh edge too, since the minimum there is 10.2 mm.

## New no-cover zones (Thermal D69 check)
- **Knee saddle:** tibia (axis x 14, y ±130), z 320–415, r ≤ 47, fins rear and sides. Must be in free air, with no exhaust onto the tibia collar.
- **Lower shank:** z 136–415 stays uncovered. The shin fairing reduces to nothing below the knee cap. Ankle boot only below z 170.

## Mount points (existing; no new holes in FEA'd tubes)
- **Thigh:** split collar ø64 L34 at the clamp (z ≈ tz). The L30 removable pin panel is 60×70 at collar mid, 4× M3 quarter-turn, plus a rear 40×50 window.
- **Knee cap:** knee tongue neck block (36×28×40 at x 10, z 438–478, shank). M4 inserts on its front face.
- **Ankle boot:** drawstring at z ≤ 170. Elastic hem on the foot shell.
- **Foot shell:** foot box side faces, M3 inserts into the webs. Instep lugs sit outboard on the outrigger; the shell covers them.
- **Hip skirt:** pelvis skin flange at z 1126 (rim). Elastic hem to the thigh fairing top at z 885.

## Update 2026-10-14 (Thermal 9b9e169): saddle dropped, no-cover zone moves to the thigh
- **Knee saddle and lower-shank no-cover zone: withdrawn.** The shin can be covered again (keep-out unchanged).
- **New no-cover zone: knee housing fins** (thigh frame, housing on the trunnion at x −130, z 770). The thigh fairing must be open (grille) over the housing's front and rear faces plus fins plus 5 mm. No fins on the outer ±y flanks.
- The knee cap vs thigh fairing gap is unchanged: the finned housing stays ≥ 110 mm from the knee cap keep-out.
