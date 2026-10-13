# Grok Build brief: WBC walk/push/carry fix (r6)
The box diagnosis is in DECISIONS L28. Contact-model changes made the falls worse. The failure is in the planner.
1. Replace the open-loop slice playback in `_plan_mpc` with closed-loop footstep placement: sagittal and lateral DCM/capture-point stepping, a bounded step-timing adapt, and stance-yaw feedback through `yaw_off` and the swing-foot yaw.
2. Make `--cruise` actually scale the plan. Today 0.5 and 0.8 give identical runs.
3. Raise double support from 3.3 % (DS_FRAC 0.15), and damp touchdown so the 7 % airborne bounce goes away (swing-down velocity / impedance at TD).
4. Pass criteria are unchanged: walk ≥ 20 s at 1.2 m/s, push recover, carry 20 kg. Report CoP margin, yaw and roll traces.
Keep the default contact (condim 3, box foot 240×100). Re-sim is cheap: about 11 s wall per 5 s of sim on a 1 GB box.
