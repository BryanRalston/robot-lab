# RL Legs decision log
## Round 2 (2026-10-13)
- L1. Model at final mass: all bodies scaled uniformly 63.794 → 65.00 kg (×1.0189), with masses and inertias (`gait_lib.load`, env LEGS_MASS=65). Uniform scaling slightly under-weights the legs, because the R-001 actuator growth sits in the legs. The leg actuators are +1.43 kg over v3 (sizing.json leg_act_new 16.79 vs 15.36), so the real leg/torso split puts more mass distally. Round-2 results live in `results/r2/`.
- L2. Torque limits for forward sim = CONTRACTS R1.2 available peak (70/204/350/258/311/177 N·m). The torque limits do not enter the ID.
- L3. Round-2 gait plan `walk_1p2_r2`:
  - 0.50 s steps (0.6 m), 15 % double support, pelvis 1.02 m
  - arm swing ±0.35 rad and pelvis yaw ±0.12 rad (waist counter-rotates)
  - Result: hip-yaw peak barely changed (41.8 vs 40 N·m), while hip_pitch, knee and ankle peaks rose (longer step). It is kept as an extra scenario, not as the reference gait.
- L4. Forward sim at 1.2 m/s is still not stable with time-indexed tracking. Tried, all falling at 4–6 s: VMC gains, capture-point foot placement, CoP-limited ankle torque, stronger yaw control, the r1 plan on R1.2 limits. The failure mode is an accumulating stance-foot yaw slip/roll after about 4 s of full speed. The next step needs online replanning (LIPM-MPC footsteps + whole-body QP). It is too heavy for this box/usage, so it goes to a Grok Build brief (`grokbuild/wbc_walk_1p2.md`).
- L5. Stairs ankle: with the IK ROM margin widened to 1.0 rad, the flat-swing-foot plan reaches −74° dorsiflexion, but only in SWING (stance max −36 to −42°; walking stance max −48°). Swing dorsiflexion is a plan artifact (swing foot held flat); the swing foot can pitch freely at < 90 N·m. → proposal P-006: loaded ankle ROM need −50°, not −60°; no toe joint needed.
- L6. Structure boundary for the 4.90 kg budget: thigh = upper lug + femur tube + collars + knee clevis; shank = tibia tube + collar + ankle fork; foot = foot plate (excl. instep lever). The linkages (knee tongue + twin lever, ankle instep lever + cross, hip_pitch lever + trunnions) are counted in the R-001 linkage line, not in structure.
