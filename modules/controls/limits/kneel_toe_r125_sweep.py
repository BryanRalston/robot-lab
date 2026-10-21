"""Robot Lab (on 976eca8): hands-first toe kneel with knee <= 125 deg in every phase, 50 N.m cap from 120 deg, D99 stop 130.
Sweep of the R19 candidate (kneel_toe_r19_dr.CAND) with KNEE_MAX_RAD 2.09 (119.7 deg soft upper limit on q_des),
CoM height at the end of A (COMZ_A), hand target ahead of the toes, hand descent speed scale; elbow cap 38 / 49 N.m [49 unruled].
68 kg, pad tc 0.02. Writes kneel_toe_r125_sweep.json. Result: no variant meets knee <= 125 (see KNEEL_R125.md)."""
import os, sys, itertools, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kneel_toe_r19_dr as R, kneel_toe_wbc as K, chest_lower_wbc as CL
rows = []
for el in (38.0, 49.0):
    CL.ELBOW_KNEEL_NM = None if el == 38.0 else el
    for k, v in R.CAND.items(): setattr(K, k, v)
    K.KNEE_MAX_RAD = 2.09
    for cz, hx, hs in itertools.product((0.68, 0.74), (0.40, 0.55), (1.0, 0.4)):
        K.COMZ_A, K.HAND_X_TOE, K.H_SPEED_SCALE = cz, hx, hs
        r = K.run(68.0, 0.02); c = r.get('chest') or {}
        km = max(r['knee_max_deg_by_phase'].values())
        row = dict(elbow_cap=el, COMZ_A=cz, HAND_X_TOE=hx, H_SPEED_SCALE=hs, fell=r['fell'] and r['fell']['phase'], phase_times_s=r['phase_times_s'],
                   knee_max_deg_by_phase=r['knee_max_deg_by_phase'], knee_max_deg=km, hand_peak_N=r['hand_peak_force_per_hand_N'],
                   hand_speed_mps=r['hand_contact_speed_per_hand_mps'], chest_mps=c.get('chest_contact_speed_mps'), chest_N=c.get('peak_chest_N'),
                   pass_=bool(not r['fell'] and km <= 125 and max(r['hand_peak_force_per_hand_N'].values()) <= 875 and (c.get('chest_contact_speed_mps') or 9) <= 0.1))
        rows.append(row); print(json.dumps(row), flush=True)
json.dump(rows, open(os.path.join(HERE, 'kneel_toe_r125_sweep.json'), 'w'), indent=1, default=float)
