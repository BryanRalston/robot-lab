# Fallback (c): crouch → sit back → lie back, no kneel — first attempt FAILS (for T&R / Torso review, 2026-10-21 ~10:50 ET)
`sitback_lower.py` → `sitback_lower.json`. Joint-space min-jerk segments (crouch 2.5 s → sit 2.0 s → recline 3.0 s, hold 1 s; T 8.5 s), derated PD ×0.5, knee cap ≥ 120° (50 N·m), sim/v3 + pads [EST]. **Interpretation flagged:** "sit-back chest lower" was taken as crouch → sit on the pelvis → recline onto the back. The model has **no seat/back pad**, so pelvis/torso hit the floor box-on-plane (rigid [EST]). Crouch was tuned over an 8-variant probe only (hip/ankle/sit target).

| mass | first contact (t, speed) | peak force | knee max |
|---|---|---|---|
| 65 | pelvis 3.47 s **2.75 m/s**, torso 2.22, head 1.87 | pelvis 5.35 kN, torso 2.03 kN | **135.7°** |
| 68 | pelvis 3.32 s **2.41 m/s**, torso 1.03, head 0.13 | pelvis 5.58 kN, torso 1.88 kN | 135.7° |
| 68.5 | pelvis 3.32 s **2.38 m/s**, torso 1.08, head 0.15 | pelvis 5.67 kN, torso 1.39 kN | 135.7° |
Pad tc 0.005/0.02/0.04 makes no difference (no pad involved). 0/9 acceptable (any ≤ 0.1 m/s target fails by > 20×).
- **Why:** the crouch target (knee 117°) cannot be held — under body weight the knee passes 120°, the 50 N·m cap removes its torque and the knee collapses onto the D99 stop (135.7°); the pelvis then drops ~0.3 m uncontrolled. Same mechanism as the toe kneel (KNEEL_R125.md) and pose study (b) (POSE_STUDY_B.md): **any lowering in which the knees carry body weight past 120° is incompatible with the 50 N·m stop-zone cap** in this controller.
- **Owed for acceptance:** a seat/back pad definition (Torso), a pelvis-speed-governed WBC sit-down (not joint-space), or a cap exemption / higher cap only in the controlled-lowering states (ruling).
