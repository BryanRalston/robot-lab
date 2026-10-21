# RL Arms & Hands R17 (2026-10-21): 7075 clevis + roll-yaw link pocketing study (R-132 §5)
Calc: `clevis_link_r17.py/.json`. Hand calcs on model_v4 EST envelopes (there's no detailed CAD). Allowables are the R-128 bands (`STOCK_GRAIN.md`). No Mg proposed. No 3D printing.

| part | now kg/side | pocketed kg/side | change | hand stress (Kt 3 EST) | limit | stock / grain |
|---|---|---|---|---|---|---|
| elbow clevis base 60×96×10 | 0.162 | 0.073 (3 mm floor, 4 mm rims, tube boss) | −0.089 | pocket web not hand-credible, so it goes to FEA | 294 | 2.5 in T651, L = Y |
| clevis lugs 2 × 50×48 | 0.108 (8 mm) | 0.097 (**9 mm**, tapered) | −0.011 | 244 MPa (8 mm would be 310: FAIL) | 294 | same |
| roll-yaw link 60×40×50 | 0.337 (solid) | 0.141 (box, 4 mm wall) | −0.196 | 35 MPa (min-gauge driven) | 308 | 2.0 in T651, L = Z |
| **total** | 0.607 | 0.311 | **−0.296/side, −0.59 pair** [CALC on EST geometry] | | | |

- **The roll-yaw link is the big item.** model_v4 draws it as a solid block, but loads are tiny, so a 4 mm-wall box holds. It must keep the yaw-housing and roll-output bolt lands solid (CAD).
- **The clevis lugs can't be thinned.** They need 9 mm (+1 mm) at Kt 3. All the clevis saving is in the base pocket.
- **Credit:** half on calc/EST, so about **−0.30 kg pair** until CAD-measured and Job 8d FEA passes.

## Job 8d spec (R7_ROUND.md §G; not launched)
