# Grok Build brief: stable 1.2 m/s forward-sim walking (Legs, round 2)

**Why it's here:** the box has about 1 GB RAM and limited compute. Every ID-feedforward + PD + virtual-model controller variant tried falls at 4.5–5.8 s (DECISIONS L4).

## Goal
The MuJoCo v3 humanoid (`modules/legs/gait_lib.load()`, LEGS_MASS=65, LEGS_LIMITS=r1, i.e. CONTRACTS R1.2 torque limits) walks the `walk_1p2_r2` plan (or an online re-plan of it) at a mean of ≥ 1.15 m/s for ≥ 20 s on flat ground without falling. It must also:
- survive a 60 N·s lateral push at mid-stance
- repeat the walk with a 20 kg torso payload (`carry_20kg_r2`)

## Known failure mode (from our runs)
- The stance foot drifts in yaw (~21°).
- The foot rolls onto its edge, then ankle_roll saturates.
- Capture-point foot placement (fp 0.5/1.0) and the CoP clamp did not fix it (results/r2/fsim/*.json).

## Required method
1. A whole-body QP at 1 kHz:
   - centroidal momentum tasks, foot wrench cones (μ 0.8, CoP inside the sole, yaw-torque limit)
   - torque limits = R1.2 ctrlrange
   - joint velocity limits from `results/r2/requirements.md`
2. LIPM / centroidal MPC at 50–100 Hz with online footstep position and timing adaptation, including step width and yaw.
3. Swing-foot yaw and roll tracking, with toe-roll timing taken from the plan.
4. CPU only is acceptable. A multi-core box with ≥ 8 GB RAM is recommended.

## Repro of the current state
```
cd modules/legs
LEGS_OUT=r2 LEGS_MASS=65 LEGS_LIMITS=r1 python3 scenarios.py walk_1p2_r2
LEGS_OUT=r2 LEGS_MASS=65 LEGS_LIMITS=r1 python3 fsim.py walk_1p2_r2 --kc 10 --kr 8 --record 0.5 --tag _kr8   # falls ~5.5 s
```

## Acceptance (report every number, fabricate none)
- Fall time, mean speed and touchdown count.
- Per-joint peak and RMS torque against R1.2 avail, and the time spent saturated (%).
- Peak CoP margin (mm).
- The same metrics for the push and the 20 kg carry.
- A GIF of the walk to media/progress/YYYY-MM-DD_legs_wbc_walk1p2.gif.
- Code in modules/legs/wbc/.
- Do not edit CONTRACTS.md or actuator selections.
