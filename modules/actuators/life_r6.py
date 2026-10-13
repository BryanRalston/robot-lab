"""R6 (R-020) A8 + A5 life checks vs T9 14 600 h, from Legs' gait-ID time series (modules/legs/results/*.npz: TAU, Q; MJCF order,
left leg = TAU cols 6..11 / Q cols 7..12), scaled to the 66.5 kg limit. Duty mix [EST]: walk 1.0 60 %, walk 1.2 15 %, carry 20 kg 15 %, stairs 10 %.
A8: maintenance-free hip-body eye SKF GE 12 C (steel/PTFE sintered bronze; C 11.4 kN, C0 28.5 kN, K 100, dk 18, 0.016 kg, SKF product page),
    SKF method: p = K P / C, v = 5.82e-7 dk beta f (f in min^-1, beta = half oscillation angle), G_h = b1 b2 1400 / (p^1.3 v), b1 0.2 (alternating, > 0.5 Hz), b2 1 (< 80 C).
A5: ankle RV12x4 (Rollvis tables: Ca 17.2 kN, C0a 27.2 kN, lead 4): per-screw force F = tau_p/(2 a) + tau_r/(2 r_roll), a 0.073, r_roll 0.040 (differential pair, size.py),
    screw speed n = (a w_p +- r_roll w_r)/lead; L10 = (Ca / Fm)^3 1e6 rev, Fm = cubic mean weighted by revolutions (ISO 3408-5)."""
import json, os, math, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); LG=f'{H}/../legs/results'; LIFE=14600.0; M=66.5
MIX={'walk_1p0':0.60,'walk_1p2':0.15,'carry_20kg':0.15,'stairs_18cm':0.10}
def load(s):
    d=np.load(f'{LG}/{s}.npz'); m=json.load(open(f'{LG}/{s}.json'))['info'].get('mass_kg',63.794); k=M/m
    t=d['t']; dt=np.gradient(t); return t,dt,d['TAU'][:,6:12]*k,d['Q'][:,7:13],d['V'][:,6:12]
# ---- A8 eye
C,K,dk,b1,b2=11400,100,18,0.2,1.0
def body_angle(th_deg):   # hp_clearance geometry, hip pitch sign as Legs CAD (flexion negative)
    a=np.radians(60-th_deg); E=np.stack([-50*np.sin(a),-50*np.cos(a)],-1); u=E-np.array([30,-300.]); return np.degrees(np.arctan2(u[...,0],u[...,1]))
A8={}; inv=0
for s,w in MIX.items():
    t,dt,TAU,Q,V=load(s); th=-np.degrees(Q[:,2]); F=np.abs(TAU[:,2])/0.050/2/0.77   # screw force incl. K_HIP slider-crank factor (size.py)
    ba=body_angle(th); Tst=json.load(open(f'{LG}/{s}.json'))['info'].get('Tstep',0.47); f=60/(2*Tst)
    beta=(np.percentile(ba,99)-np.percentile(ba,1))/2
    P=(np.sum(F**1.3*dt)/np.sum(dt))**(1/1.3); p=K*P/1000/(C/1000); v=5.82e-7*dk*beta*f; G=b1*b2*1400/(p**1.3*v)
    A8[s]=dict(share=w,F_peak=float(F.max()),P_eq_N=float(P),p_Nmm2=float(p),beta_deg=float(beta),f_min=f,v_ms=v,Gh=float(G)); inv+=w/G
Gh=1/inv; interval=math.floor(0.5*Gh/250)*250
A8['combined']=dict(Gh=Gh,T9=LIFE,ok=bool(Gh>=LIFE),replacement_interval_h=interval,replacements_over_life=math.ceil(LIFE/interval)-1,
  note='b1 0.2 is the SKF value for alternating load > 0.5 Hz at 25 < p < 40 N/mm2; applied at lower p as well (conservative). Interval = 50 % of G_h (rating life is a mean wear life, not L10).')
# steel/steel GE 12 E re-check with correct f units (D46 used f = 1 min^-1 -> overstated 54x)
# ---- A5 ankle roller screw
Ca,C0a,lead,a,rr=17200,27200,0.004,0.073,0.040
A5={}; inv=0; Fmax=0
for s,w in MIX.items():
    t,dt,TAU,Q,V=load(s)
    for sg,nm in ((1,'in'),(-1,'out')):
        F=np.abs(TAU[:,4]/(2*a)+sg*TAU[:,5]/(2*rr)); n=np.abs(a*V[:,4]+sg*rr*V[:,5])/lead   # rev/s
        rev=np.sum(n*dt); Fm=(np.sum(F**3*n*dt)/max(rev,1e-9))**(1/3); rph=rev/np.sum(dt)*3600
        L10=(Ca/Fm)**3*1e6/rph; Fmax=max(Fmax,F.max())
        A5[f'{s}_{nm}']=dict(share=w,F_peak=float(F.max()),Fm=float(Fm),rev_per_h=float(rph),L10_h=float(L10))
for nm in ('in','out'):
    A5[f'combined_{nm}']=1/sum(A5[f'{s}_{nm}']['share']/A5[f'{s}_{nm}']['L10_h'] for s in MIX)
A5['L10_h']=min(A5['combined_in'],A5['combined_out']); A5['ok']=bool(A5['L10_h']>=LIFE); A5['static_C0a_over_Fmax']=float(C0a/Fmax); A5['L10_h']=float(A5['L10_h'])
stroke=json.load(open(f'{H}/results/ankle_stroke_73.json'))
A5['stroke']=stroke['73mm L_ankle actuator in']
json.dump(dict(A8=A8,A5=A5,mix=MIX,mass_kg=M),open(f'{H}/results/life_r6.json','w'),indent=1)
print(json.dumps(A8['combined'],indent=1)); [print(s,{k:round(v,3) for k,v in A8[s].items()}) for s in MIX]
print('A5 L10',round(A5['L10_h']),'static',round(A5['static_C0a_over_Fmax'],2)); [print(k,{kk:round(vv,1) for kk,vv in v.items()}) for k,v in A5.items() if isinstance(v,dict) and 'L10_h' in v]
