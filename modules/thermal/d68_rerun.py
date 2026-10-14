"""RL Thermal: rerun O-A2 arm hold and R1 leg joint margins with Actuators D68 inputs (ded9c2d):
R(T)=R25*(234.5+T)/259.5 (R155 = 1.501*R25), Kt linear from Kt25 = Kt155/0.89 to Kt155, limit 155 C, HD eta 0.84. -> results/d68_rerun.json"""
import json, math, os
H=os.path.dirname(os.path.abspath(__file__))
R155={'TBM2G-07608C':0.477,'TBM2G-05013C':0.690}; KT155={'TBM2G-07608C':0.096,'TBM2G-05013C':0.061}
Rf=lambda T:(234.5+T)/259.5                       # R(T)/R25
Ktf=lambda T:1/0.89-(1/0.89-1)*(T-25)/130         # Kt(T)/Kt155
def Pcu(mot,Tm,T):                                # 3-phase sinusoidal: 1.5*I^2*R_LL
    I=Tm/(KT155[mot]*Ktf(T)); return 1.5*I*I*R155[mot]/1.501*Rf(T)
O=json.load(open(f'{H}/results/oa2_arm_hold.json'))
def sim(mot,Tm,Rwh,Rha,Cw,Ch,Ta,dt=0.5,tmax=36000):
    Tw=Th=Ta; t=0; t100=t155=None
    while t<tmax:
        P=Pcu(mot,Tm,Tw); q=(Tw-Th)/Rwh; Tw+=dt*(P-q)/Cw; Th+=dt*(q-(Th-Ta)/Rha)/Ch; t+=dt
        if t100 is None and Tw>=Ta+100: t100=t/60
        if t155 is None and Tw>=155: t155=t/60
        if t100 and t155: break
    return t100,t155
def ss(mot,Tm,Rtot,Ta):
    T=Ta+50
    for _ in range(200):
        Tn=Ta+Pcu(mot,Tm,T)*Rtot
        if Tn>600: return float('inf')
        T=Tn
    return T
arm={}
for j,mot,Tout in [('shoulder_pitch','TBM2G-07608C',61.3),('elbow','TBM2G-05013C',40.1)]:
    b=O['res'][j]['eta0.75_h1.0']; arm[j]={}
    for eta in (0.84,0.76):
      for hx in (0.7,1.0,1.3):
        Rha=b['Rha']/hx; Tm=Tout/(100*eta); Tss=ss(mot,Tm,b['Rwh']+Rha,40.0); t100,t155=sim(mot,Tm,b['Rwh'],Rha,b['Cw'],b['Ch'],40.0)
        arm[j][f'eta{eta}_h{hx}']=dict(Tm=Tm,P_start=Pcu(mot,Tm,40),T_ss=Tss,t100_min=t100,t155_min=t155,
            t120_note='advisory trip 120-130 C')
# legs: scale R1 copper (computed at constant Rcu x1.4, Km cold) to temperature-dependent R and Kt
R1=json.load(open(f'{H}/results/r1_budget.json')); E=R1['EST']
legs=[]
for r in R1['legs']:
    cu25=r['copper_W']/1.4; fe=r['iron_W']; n=r['motors']
    sc=lambda T:Rf(T)/Ktf(T)**2*(1/0.89**2)   # P(T)/P25 ; P25 uses Kt25
    Rwh_n=(r['dT_wind_open']-r['dT_case_open'])/(r['copper_W']/n)        # per-motor winding->case
    Rha_o=r['dT_case_open']/(r['copper_W']+fe); Rha_c=r['dT_case_cov']/(r['copper_W']+fe)
    out={}
    for Ta in (25.0,35.0):
      for tag,Rha in (('open',Rha_o),('cov',Rha_c)):
        T=Ta+60
        for _ in range(300):
            cu=cu25*sc(T); Tn=Ta+cu/n*Rwh_n+(cu+fe)*Rha
            if Tn>800: Tn=float('inf'); break
            T=Tn
        out[f'{tag}_{int(Ta)}']=T
    # A35: max case-air R and min h at 35 C for winding 155 (and 130 advisory)
    for lim in (155.0,130.0):
        cu=cu25*sc(lim); dTc=lim-35-cu/n*Rwh_n; Rmax=dTc/(cu+fe); out[f'hmin_{int(lim)}']=E['h_air']*Rha_o/Rmax; out[f'case_dT_max_{int(lim)}']=dTc
    out['joint']=r['joint']; legs.append(out)
json.dump(dict(arm=arm,legs=legs),open(f'{H}/results/d68_rerun.json','w'),indent=1,default=str)
for j,v in arm.items():
    for k,x in v.items(): print(j,k,{a:(round(b,1) if isinstance(b,float) else b) for a,b in x.items()})
for o in legs: print({a:(round(b,1) if isinstance(b,float) else b) for a,b in o.items()})
