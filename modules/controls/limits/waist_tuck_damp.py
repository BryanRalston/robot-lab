"""Waist-pitch TUCK damping study (fall_mode.waist_fall_torque, ramp 20 deg before each end, D102 zero last 3 deg).
Held-backward worst cells of waist_energy_backfall + forward D99 cells (knee_stop_impact.CASES, 68 kg).
E = 0.5*(I_model + 0.24 rotor)*w^2 and with Torso P-160 I (1.44 arms down / 3.52 arms forward) + 0.24. Light CPU MuJoCo."""
import os, sys, json
from multiprocessing import Pool
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'fall')); sys.path.insert(0, H)
import waist_energy_backfall as W, knee_stop_impact as K
ROT = 0.24; IP = {'arms_down': 1.44, 'arms_fwd': 3.52}
def job(a):
    tag, kw = a
    r = W.run(**kw); r['cell'] = tag
    for e in ('lo_end', 'hi_end'):
        x = r.get(e)
        if x:
            w = x['w']; x['E_model_rot_J'] = round(0.5 * (x['I'] + ROT) * w * w, 1)
            for k, v in IP.items(): x['E_P160_' + k + '_J'] = round(0.5 * (v + ROT) * w * w, 1)
    print(r, flush=True); return r
if __name__ == '__main__':
    Bs = [None, 15.0, 40.0, 100.0]
    jobs = []
    for B in Bs:
        jobs.append(('72.1kg w+20 120Ns held', dict(mass=72.1, pose=dict(), lean=0.0, waist0=20, push=120, held=True, waist_B=B)))
        jobs.append(('72.1kg w0 60Ns held', dict(mass=72.1, pose=dict(), lean=0.0, waist0=0, push=60, held=True, waist_B=B)))
        jobs.append(('68kg w+20 120Ns held', dict(mass=68.0, pose=dict(), lean=0.0, waist0=20, push=120, held=True, waist_B=B)))
        for c in K.CASES:
            jobs.append(('D99 %s lean0.3' % c, dict(mass=68.0, pose=K.CASES[c][0], lean=0.3, waist_B=B)))
    with Pool(min(8, os.cpu_count())) as p: R = p.map(job, jobs)
    json.dump(R, open(os.path.join(H, 'waist_tuck_damp.json'), 'w'), indent=1)
