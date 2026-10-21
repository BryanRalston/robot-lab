"""R-146(b) hands-first kneel -> chest lower, Arms R19 (3de759b) plant-posture candidate, DR sweep.
Candidate: straight-arm plant (elbow -7.5 deg, wrist pitch -55 deg, wrist yaw 0), hands 0.40 m ahead of the toes,
CoM 0.06 m behind the toe line while reaching, elbow budget 49 N.m in kneel/lower only (Arms R19 [EST], Arbiter proposal;
38 N.m derate elsewhere). Fingers / heel plant are not modelled (single hand geom)."""
import os, sys, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chest_lower_wbc as CL, kneel_toe_wbc as K
CAND = dict(H_ELBOW=-0.13, H_WRIST=-0.96, K_ELBOW=None, HAND_X_TOE=0.40, COM_BACK=0.06)
LIM = dict(hand_N=875.0, hand_mps=0.23, chest_mps=0.10, chest_N=8800.0, line_elbow_mm=25.0, line_shoulder_mm=55.0)

def one(mass, tc, elbow_nm):
    for k, v in CAND.items(): setattr(K, k, v)
    CL.ELBOW_KNEEL_NM = elbow_nm
    r = K.run(mass, tc); c = r.get('chest') or {}
    ph = r['phase_times_s']; T = round(sum(ph.values()) + (c.get('t_d94_flag_mo0_s') or 0.0), 3) if c else None
    return dict(mass=mass, pad_tc=tc, elbow_cap_Nm=elbow_nm or 38.0, fell=r['fell'], phase_times_s=ph, chest_to_mo0_s=c.get('t_d94_flag_mo0_s'), T_s=T,
                hand_peak_N=r['hand_peak_force_per_hand_N'], hand_speed_mps=r['hand_contact_speed_per_hand_mps'], hand_posture=r['hand_plant_posture'],
                knee_contact_mps=r.get('knee_contact_speed_mps'), knee_peak_N=r['knee_peak_force_N'],
                chest_contact_mps=c.get('chest_contact_speed_mps'), chest_peak_N=c.get('peak_chest_N'),
                elbow_peak_Nm=max(r['peak_tau_Nm']['elbow'], (c.get('peak_tau_Nm') or {}).get('elbow', 0.0)))

if __name__ == '__main__':
    out = dict(candidate=CAND, limits=LIM, runs=[one(ms, tc, e) for e in (49.0, None) for ms, tc in [(68.0, 0.02)] + list(itertools.product((65.0, 68.0, 68.5), (0.005, 0.02, 0.04)))])
    json.dump(out, open(os.path.join(HERE, 'kneel_toe_r19_dr_results.json'), 'w'), indent=1, default=float)
    for r in out['runs']:
        print(r['elbow_cap_Nm'], r['mass'], r['pad_tc'], r['fell'] and r['fell']['phase'], r['phase_times_s'], r['T_s'], r['hand_peak_N'], r['hand_speed_mps'], r['knee_contact_mps'], r['knee_peak_N'], r['chest_contact_mps'], r['chest_peak_N'], r['elbow_peak_Nm'],
              [(p['elbow_deg'], p['wrist_pitch_deg'], p['wrist_yaw_deg'], p['line_to_elbow_mm'], p['line_to_shoulder_mm']) for p in r['hand_posture'].values()])
