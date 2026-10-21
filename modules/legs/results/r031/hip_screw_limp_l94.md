# L94: limp first contact at the −10° adduction stop (PARTIAL, 11:20 ET hard stop), hip_screw_limp_l94.py → hip_screw_limp_l94.json
## What touches (model_v4, r116b, drives off)
- **L at −10°, R straight at 0:** first contact is **L −y hip_pitch screw BODY ↔ R +y hip_pitch screw BODY (0.0 mm)**, plus the L −y eye-stub flange ø30 [EST] on the R body (0.0). The L −y axial GE12 eye is 2.25 mm and the eye stub 4.39 mm. It is the **inboard bodies (cylinders) and the eye-end flange**, not heads or housings.
- **Both at −10 (mirrored):** body↔body, body↔rod (RV12 ø12), flanges and stubs all overlap (0.0). Already touching at **both −3** (body↔body).
- So with the hardware stop at −10, the screws hit first in every limp case. No housing↔housing or bumper↔bumper contact comes before them.

## Fix options inside modules/legs (no hip-spacing change)
1. **Sacrificial PU 95A pads on a Legs clamp band around each inboard screw body**, facing the midline, 8 mm proud of the body OD. Contact comes ≥ 3 mm before metal (the body gap changes about 6.5 mm/° near contact, so the pads touch about 1.2° earlier, at about −8.8° single). Mass about 10 g per leg [EST]. **Needs Actuators' OK** to clamp on the screw body (thermal/heat-sink face, body tolerance). It does not cover the both-adducted case beyond −3, which is software-only (L93b).
2. **Recess/counterbore:** not possible. The contact is on Actuators' body cylinders, with no Legs part in the path.
3. **Rotate/relocate the screw mount** (clock the screw pair outward about the pitch axis, or splay the inboard screw 3–5° outboard): this is the real fix but it is an **Actuators change** (screw line, lever, linkage table). Torso is not needed unless the pelvis deck mount moves.
4. **Housing-on-bumper first contact:** a PU block on the L58/L60 knee housings can't act at the hip; the knee housings are still 11.1 mm apart at single −10. A hip-level bumper would have to sit on the hip-pitch bracket web (Legs EST part at y±32.5 from the leg axis), but the web is outboard of the bodies, so it can't contact first.

## Recommendation (partial)
Option 1 as the Legs-only interim, pending Actuators' OK, plus option 3 requested from Actuators as the final fix. Not swept with the pads; needs a 3 mm re-sweep at single −10 / both −3.
