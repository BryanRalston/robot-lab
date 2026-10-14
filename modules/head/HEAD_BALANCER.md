# Head as an active balance actuator: engineering study (Robot Lab, 2026-10-14)

Requested by Bryan: make the head an active balance actuator in the v4-to-v5 cycle.
Math: `head_balance.py` → `head_balance.json` (MuJoCo 3.x on `sim/v3/humanoid_v3.xml`).

## Verdict: as a balance actuator it isn't worth it. Build the neck for gaze and camera stabilization
The head and neck are 1.137 kg (head 0.647, neck yoke 0.490) out of 63.8 kg in the sim model, and the neck has only ±40° of pitch travel. The physics caps what they can do:

| Effect | Value | Compared with | Share |
|---|---|---|---|
| Whole-robot COM shift, pitch −40→+40° | 1.1 mm fore-aft | sole length ~250 mm | 0.4 % |
| Whole-robot COM shift, yaw ±80° | 0.9 mm lateral | — | negligible |
| Gravity moment swing from head pitch | 0.69 Nm | hip_pitch limit 167 Nm / waist 116 Nm | 0.4 % / 0.6 % |
| Static lean 10/20/30°, head counter-pitched −40° (MuJoCo gravity torque) | waist −0.40/−0.37/−0.33 Nm | waist static 4.6/8.7/12.5 Nm | 8.7/4.2/2.6 % of a small static load; 0.3 % of peak |
| Same, hip_pitch | 0.00 Nm (floating-base gravity term; the hip only sees the COM, max 0.69 Nm) | 167 Nm | ≤0.4 % |
| Dynamic reaction on the torso | ≤ neck servo stall, 4.1 Nm (XM430) | hip 167 / waist 116 Nm | ≤2.5 % / ≤3.5 % for ≤0.12 s, then it must reverse before the ±40° stop. Net impulse over a cycle is zero |
| Angular momentum the head can absorb | 0.42 Nms with the sim's 0.079 armature; ~0.04 Nms with real head inertia (0.0088 kg·m²) | push recovery, 66.5 kg × 0.4 m/s × 0.95 m = 25 Nms | 1.7 % upper bound, ~0.2 % realistic |

**Peak hip/waist torque reduction:** under 1 % in leans and falls, and at most 2.5–3.5 % as a transient lasting under 0.15 s during push recovery. That's within the noise of the WBC's torque tracking. Using the head to balance would also cost gaze stability (the camera swinging ±40° in a stumble is exactly when perception matters most), and it would put the stereo pair at higher risk in a fall.

**Flag: physically not worthwhile.** The honest options:
1. **Chosen: gaze + stabilization.** Active pan/tilt with IMU-driven camera stabilization. The WBC adds an *optional* head term that holds the gaze (it compensates torso rate) and counts the head's real mass and pose in subtree_com. Balance gets a minor bonus only.
2. Heavy-head concept (battery or compute in the head, ~5–8 kg): the COM shift becomes ~10× larger, but it raises the COM, adds neck torque of ~50–80 Nm (CSG-class drives), and puts the most fragile, highest-energy parts in the highest-impact location in a fall. Rejected for v5. Atlas/Optimus/Figure all carry the battery in the torso.
3. Real balance levers already exist: waist pitch/yaw (116/70 Nm) and the arms (167 Nm shoulders, ~4 kg each). Arm windmilling gives ~30–50× the head's momentum authority. That belongs in the WBC (future work).

## Neck design (real parts)
| Item | Part | Key spec | Price | Source |
|---|---|---|---|---|
| Neck yaw actuator | ROBOTIS Dynamixel **XM430-W350-R** | 4.1 Nm stall, 0.82 Nm cont. (20 %), 46 rpm, 82 g, 12 V RS485, 15′ backlash | $333.39 | https://www.robotis.us/dynamixel-xm430-w350-r/ |
| Neck pitch actuator | Dynamixel **XM430-W350-R** | same | $333.39 | same |
| (Alt. pitch, rejected) | XM540-W270-R | 10.6 Nm, 165 g; only needed for the balance duty, which is rejected | $494.39 (out of stock) | https://www.robotis.us/dynamixel-xm540-w270-r/ |
| Stereo camera (none chosen in the repo; the v1 plan only lists "2.3 MP global-shutter stereo") | Stereolabs **ZED X Mini**, 2.2 mm (ZED-311210) | 2×1920×1200 @60, global shutter, IMU, IP67, GMSL2, 94×32×37 mm, 150 g | $549 | https://www.stereolabs.com/store/products/zed-x-mini-stereo-camera |
| Yaw bearing | 6806-2RS 30×42×7 | carries head radial/moment load (servo axial limit is 20 N) | [EST] $8 | — |
| Pitch idler | 6800-2RS 10×19×5 | opposite cheek | [EST] $4 | — |
| 48→12 V converter | isolated DC-DC brick, ~30 W | servo bus | [EST] $60 | — |
| Head shell | CF prepreg 1.2 mm, laid up on a **machined aluminium mould** (no 3D printing; replaces PA12) | ~0.18 kg | [EST] $400 mould + $60/part | — |
| Neck yoke, shaft | 7075-T6 machined | — | [EST] $180 | — |
| Head deck | 6061 3 mm sheet, waterjet + bend, pocketed | — | [EST] $40 | — |

**Sizing (gaze duty):** gravity hold at pitch is 0.647×9.81×0.096 = 0.61 Nm against 4.1 Nm stall (6.7×) and 0.82 Nm continuous (1.34× continuous margin, so the continuous margin is thin). **Flag:** add a ~0.5 Nm torsion-spring gravity compensator at the pitch axis (makeable, ~10 g) for ≥3× continuous margin. Speed: 276°/s no-load is fine for tracking and stabilization (walking torso pitch rate is <60°/s) but slower than human saccades (~500°/s). Backlash of 15′ = 0.25° camera jitter, which the ZED's IMU and visual odometry absorb. **Flags:** the ZED X Mini needs a GMSL2 capture path on the brain carrier (Thor carrier support is not verified); the servo bus needs 12 V, hence the DC-DC.

## Head line (own line, not in "all other")
| Part | kg | Basis |
|---|---|---|
| 2× XM430-W350-R | 0.164 | catalog |
| ZED X Mini | 0.150 | catalog |
| CF shell 1.2 mm (0.096 m² × 1550 kg/m³) | 0.179 | calc |
| yoke + shaft 7075 | 0.110 | [EST] |
| deck 6061, pocketed | 0.070 | [EST] |
| bearings | 0.027 | [EST] |
| DC-DC + harness + fasteners | 0.100 | [EST] |
| **Head + neck total** | **0.800** | 0.314 catalog / 0.179 calc / 0.307 EST |

The sim carries 1.137 kg. The official rollup's "all other lines" carries an unknown share for the head (the v3 basis). Mass delta claimed: **0.000 kg now** (R-024 no-new-mass rule). A credit of up to −0.337 kg is possible *only* if the Arbiter's A12 itemization shows the basis carries 1.137 for head + neck. See P-019.

**Power:** servos 2 × ~1.0 W average gaze duty [EST] (0.48 W standby each, catalog 40 mA × 12 V), ZED X Mini ~2 W [EST], DC-DC loss ~0.4 W → **+4.4 W** if the camera isn't already in the 699 W budget. Runtime at 1.0 m/s goes from 2.06–2.09 h to 2.05–2.08 h (−0.6 %), so the 2 h target stays met.

## v4 → v5 tweak plan
**Done now (this commit):** in the model_v4 neck, the generic strain-wave placeholders are replaced by 2× XM430 (yaw servo on the torso top deck, horn up into the yoke), 6806 bearing, machined yoke, CF shell (was PA12), ZED X Mini envelope. The audit rows for the neck now name the real parts but stay PLACEHOLDER (brackets [EST], not module-reviewed). Clash/audit rerun, GLB and v4.html regenerated.
**Waits (v5):**
- Update the sim XML (head mass, real armature ~0.0005 instead of 0.079, ctrlrange 4.1 Nm instead of 36). Legs owns the sim, so this is a request.
- WBC: optional `head_gaze` task (hold camera orientation, weight ≪ balance). It is not a balance term.
- Gravity spring.
- GMSL2 carrier check (A11 brain).
- Arbiter A12 itemization for the credit.
- Arm-windmill push recovery as the real upper-body balance lever.
