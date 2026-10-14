"""R-089 / Electronics §18.2l: per-rail summed-current limit (I_rail = sum D_i*I_i <= 1.50 A, 10 kHz loop) + flexor stagger
(one flexor accelerating per rail, >= 20 ms apart). Does a full-hand close still meet T4 0.64-0.68 s, and does the rail stay < 2.5 A hiccup?
Physics and constants copied from arms/hand_close_r4.py [REPO: DCX22S R 3.69, Kt 18.4 mNm/A, I0 35.9 mA, J 5.55+1.191 gcm2,
GPX22HP 103:1 eta 0.65, spool r 4 mm, stroke 30 mm, tendon load ramp to 217 N x fric 1.3; DCX16S 83.1 ohm, I_nom 0.144 A].
[EST]: ideal 24 V rail, current-mode bridge (current = min(setpoint, (V-Kt w)/R)), bridge eff 0.95, small drives holding at I_nom,
acceleration phase = until w reaches 90 % of its running value or contact begins; hold after full stroke at 0.952 A (30 N)."""
import json, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__))
Kt, I0, J, V, N, r, S, R = 0.0184, 0.0359, 5.55e-7+1.191e-7, 24.0, 103, 0.004, 0.030, 3.69
eta, fric, CAP, RAIL, HOLD = 0.65, 1.3, 1.66, 1.50, 0.952
small = {'A': 2, 'B': 3}; I16, R16 = 0.144, 83.1
def Ftend(x): return (10*x/S + 217*min(1, max(0, (x-(S-0.006))/0.006)))*fric
def run(nsmall, Rm=None, stagger=0.020, rail_lim=True, rail=None, gate=True, dt=1e-5, Ts=1e-4, T=1.5):
    global R
    R = Rm or 3.69
    w = np.zeros(3); x = np.zeros(3); start = np.array([0.0, stagger, 2*stagger]); done = np.full(3, np.nan)
    accel_done = np.zeros(3, bool); scale = 1.0; pkstate = None; t = 0.0; nxt = 0.0; pk = 0.0; pk1ms = 0.0; buf = []
    Is = I16*nsmall*(I16*R16/V)                     # small drives' rail current (D*I)
    while t < T:
        if t >= nxt:                                 # 10 kHz loop: compute scale from last sample
            nxt += Ts
            sp = np.zeros(3)
            for k in range(3):
                if t < start[k]: continue
                # stagger: k may only start accelerating once k-1 has finished accelerating (and >= stagger offset)
                if gate and k > 0 and not accel_done[k-1] and np.isnan(done[k-1]): start[k] = max(start[k], t+Ts); continue
                sp[k] = HOLD if not np.isnan(done[k]) else CAP
            ib = np.minimum(sp, np.maximum((V-Kt*w)/R, 0)); D = np.clip((R*ib+Kt*w)/V, 0, 1)
            Ir = (D*ib).sum()/0.95 + Is
            scale = min(1.0, max(0.0, ((rail or RAIL)-Is))/max(Ir-Is, 1e-9)) if rail_lim else 1.0
            cmd = ib*scale   # scale the achievable current, not the (saturated) setpoint
        i = np.minimum(cmd, np.maximum((V-Kt*w)/R, 0))
        Tl = np.array([Ftend(xx) for xx in x])*r/(N*eta)
        acc = (Kt*np.maximum(i-I0, 0) - Tl)/J
        w = np.maximum(0, w + np.where(np.isnan(done), acc, 0)*dt)
        x = np.minimum(S, x + w/N*r*dt)
        for k in range(3):
            if np.isnan(done[k]) and x[k] >= S: done[k] = t; w[k] = 0
            if not accel_done[k] and t > start[k] + 2*Ts and (acc[k] < 0.1*Kt*CAP/J or x[k] > S-0.006): accel_done[k] = True
        D = np.clip((R*i+Kt*w)/V, 0, 1); Ir = (D*i).sum()/0.95 + Is
        if Ir > pk: pk = Ir; pkstate = (round(t,4), np.round(i,3).tolist(), np.round(w,0).tolist(), round(scale,3))
        buf.append(Ir)
        if len(buf) >= 100: pk1ms = max(pk1ms, np.mean(buf)); buf = []
        t += dt
        if not np.isnan(done).any() and t > np.nanmax(done)+0.05: break
    return dict(t_close_each_s=[round(float(d), 3) for d in done], t_full_close_s=round(float(np.nanmax(done)), 3),
                rail_peak_A=round(pk, 3), peak_state_t_i_w_scale=pkstate, rail_peak_1ms_A=round(pk1ms, 3), starts_s=[round(float(s), 3) for s in start])
out = {}
for rail in 'AB':
    out[rail] = dict(staggered_limited=run(small[rail]), simultaneous_limited=run(small[rail], stagger=0.0, gate=False),
                     simultaneous_unlimited=run(small[rail], stagger=0.0, rail_lim=False, gate=False),
                     fixed20ms_nogate_limited=run(small[rail], gate=False),
                     staggered_rail1p60=run(small[rail], rail=1.60),
                     fixed20ms_rail1p60=run(small[rail], gate=False, rail=1.60),
                     R097_50ms=run(small[rail], stagger=0.050, gate=False),
                     R097_150ms_max=run(small[rail], stagger=0.150, gate=False),
                     R097_50ms_hotR1p5=run(small[rail], stagger=0.050, gate=False, Rm=3.69*1.5),
                     R097_150ms_hotR1p5=run(small[rail], stagger=0.150, gate=False, Rm=3.69*1.5))
# 10 kHz adequacy: worst rail-current change between two 100 us samples from back-EMF build-up (setpoint held)
dwdt = Kt*CAP/J; out['dI_rail_per_100us_A'] = round(CAP*Kt*dwdt/V*1e-4, 4)
json.dump(out, open(os.path.join(H, 'rail_stagger_sim.json'), 'w'), indent=1); print(json.dumps(out, indent=1))
