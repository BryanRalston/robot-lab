# Grok Build brief — regenerate gait plans at a 16 mm CoP inset (R-102)
Run on: Bryan's "bryan" PC (ff639f5a) via Grok Interface (aa95bf5f). Do NOT use DESKTOP-B115PVV. Too heavy for the box (gait_lib + mj_inverse).
1. Pull origin main. Set the support-polygon CoP inset to 16 mm (was 8) in the gait_lib plan config. Sim foot box 18 → 21 mm, contact on the pad, E = Gent(Shore) with Shore 85A default (60A sensitivity case).
2. Regenerate ref_m12, ref_ds25, P-042 carry, push_recover, stairs. Use the same seeds and horizons as the current plans.
3. Rescore with Controls' sole_cop_r1.py (60A and 85A, 3 mm frame). Pass: every plan's min margin ≥ 0 and walk ≥ 8 mm. Also report knee/ankle peak torque changes vs the current plans (flag > +3 %).
4. Commit the outputs to modules/legs/results/r102_plans/ with a README of the numbers. Change nothing outside modules/legs.
