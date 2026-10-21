# D104: hip_pitch inner screw bodies at the −10° limp adduction stop (reply to Legs L94, f535463)
Script `hip_screw_adduction_d104.py` → `hip_screw_adduction_d104.json`. These are hand checks with no OCC, and geometry is unchanged, so there is no STEP. Geometry sources: `legs/model_v4_l92.py` P (hip_y 130, hip_dy 69, femur ø50 at x18), `cad_mass.linear_body('TBM2G-07613',bosses='none')` (can ø82 × 43.1, nut section ø41 × 56, body 105.1 mm), the screw_unit 30 mm eye offset, and linkage_study hip_pitch_B (thigh eye x30 z−300, lever r50 clock 60). Pin-to-pin length is 325 mm.

## Decision
- **(2) splay 3–5° outboard: NOT feasible.** The inner body (y 61, OD 82) already sits **3.0 mm** [EST, hand calc] from the femur ø50 OD and thigh split collar, in the same x/z band (body z ≈ 650–755, femur z 560–864).
  - Pivoting about the lever eye moves the contact zone out 15.5 / 20.6 / 25.7 mm (3/4/5°). That is 12–23 mm *into* the femur.
  - Pivoting about the thigh eye moves it only 2.1–3.5 mm, because the contact sits next to that eye. That is useless.
  - Rotating about the pitch (y) axis does not change L/R y-separation at all.
  - For the record, torque and load-share effects would have been small: inner moment arm ×0.996–0.999 and 238–396 N lateral on the lever eye at 4542 N. The GE12 tilt would grow from ±4.1° to about 8–9°, still under 10°.
- **(1) clamp pads: allowed only as a touch/anti-fret buffer, not as the energy stop.** The screw body cannot pass impact load; see below.
- **What actually fixes it** needs a Robot Lab ruling, because it is not inside Actuators' authority:
  - (a) Legs moves the hip-roll hard adduction stop so it engages before any body contact, single and both-adducted, with the pads as backup only. Or
  - (b) a larger change: invert the inner screw (body on the hipR/lever end, where it is near the roll axis) or move the femur/inner screw outboard together. That is a rework of the hip_pitch unit, thigh clamp and linkage table, and I'm not taking it without a ruling.
  - Both-adducted contact at −3° each stays on L93b software plus pads either way.

## (1) Clamp rules (body coordinates: z = 0 at the rear cap, +z toward the nut; the thigh eye is at z −30)
- **Permitted zone:** z **14–38** on the ø82 motor can, i.e. 44–68 mm from the eye centre. Band width ≤ 12 mm. Pad on the midline sector only, ≤ 60° arc.
- **Keep-outs:**
  - z 0–12: rear cap, encoder, eye stub flange.
  - z 43–49: cone.
  - z 49–105: nut, 7202 pair, front seal/wiper at z 102–105.
  - Nothing on the RV12 rod.
  - The nut does not translate in the body; the rod does. So "nut travel" means the rod: no contact with it.
- **Heat:** the hip_pitch bodies reject heat by convection from the can. The D90/D95 heat plates are on the pelvis rear wall and are not touched. A ≤ 60° × 12 mm pad covers about 4 % of the can [EST]; that's acceptable.
- **Preload:** contact pressure **≤ 0.9 MPa**, giving radial deflection ≤ 0.01 mm against the bonded stator [EST limit]. Hoop stress is 18 MPa, and band tension is **≤ 358 N** for a 10 mm band. Bond the saddle, as in clamp_review's bonded + light clamp; don't rely on friction.

## Pad contact load
- The body plus rod is a two-force member on spherical eyes. A transverse load F at the pad is reacted 0.83 F at the thigh eye and 0.17 F at the rod-end, which bends the RV12 rod at the nut exit.
- **F_allow ≈ 210 N** per contact. This is set by rod bending of 60 MPa [EST] (Rollvis: avoid radial load). The nut radial limit, 5 % C0a [EST], allows about 1.0 kN.
- At that force a 95A pad (k ≈ 4.5 kN/mm [EST]) absorbs only **≈ 5 mJ**. A limp leg adducting (I ≈ 1.85 kg·m² [EST]) brings 0.9 / 3.7 / 8.3 J at 1 / 2 / 3 rad/s [EST].
- So the pads must never be the thing that stops the leg.

## Legs must re-sweep
1. In CAD, confirm the inner body to femur/thigh-collar clearance (3.0 mm hand calc). If it's > 30 mm, the splay reopens.
2. Find a hard-stop angle at which the stop engages ≥ 3 mm before pad contact, single and both-adducted. Pads in z 14–38, 8 mm proud.
3. Confirm the pad touches with ≤ 210 N in the sweep's static cases.
4. Both-adducted contact at −3° each stays on L93b software.
