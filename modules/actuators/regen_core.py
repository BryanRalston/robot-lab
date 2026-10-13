"""Shared-DC-bus energy model used by regen_sim.py (nominal) and regen_sweep.py (sensitivity). Round 3.
Gait input (any source): an .npz with either
  (a) Legs gait-ID format: t [N], TAU [N,nq], V [N,nq], va [12] (column of each leg joint, order LEG left then right), or
  (b) generic: t [N], tau [N,12], omega [N,12] (joint-output torque N·m and speed rad/s, LEG order left 0-5 then right 6-11).
Legs' forward-sim 1.2 m/s gait drops in by saving format (b) and passing its path."""
import json, math, os, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(H,'../..')
LEG=['hip_yaw','hip_roll','hip_pitch','knee','ankle_pitch','ankle_roll']
SEL=json.load(open(f'{H}/results/sizing.json'))['sel']
FE=json.load(open(f'{H}/results/iron_loss.json'))
MOTKEY={j:SEL[j]['d']['motor']+'ACD'[SEL[j]['d']['w']] for j in LEG}
# back-drive (generating) efficiency of each transmission: Rollvis RV12 'indirect' efficiency 0.88 (datasheet p.24) x 0.95 bearings (v3 rule);
# Harmonic Drive back-drive efficiency [EST] 0.65 (HD catalog efficiency curves fall at reverse drive/low load; no table value)
ETA_BACK={j:(0.88*0.95 if SEL[j]['d']['kind']=='linear2' else 0.65) for j in LEG}
NOM=dict(drive_x=1.0, iron_x=1.0, eta_back_x=1.0, eta_fwd_x=1.0, rcu_hot=1.4, charge_A=30.0, vcell=3.6, ir_x=1.0, torque_x=1.0, time_x=1.0,
         ns=20, np_=5, p_other=120+40+26*3.3+8.0)
import functools
@functools.lru_cache(maxsize=8)
def load(path):
    d=np.load(path); t=d['t'].astype(float)
    if 'TAU' in d: va=d['va']; tau=np.stack([d['TAU'][:,va[k]] for k in range(12)],1); om=np.stack([d['V'][:,va[k]] for k in range(12)],1)
    else: tau=d['tau']; om=d['omega']
    return t,tau.astype(float),om.astype(float)
def steady_window(t,om):
    """steady walking = from 1 s after hip_pitch first exceeds 1 rad/s to 1 s before it last does"""
    hp=np.abs(om[:,[2,8]]).max(1); idx=np.where(hp>1.0)[0]
    return (t>=t[idx[0]]+1.0)&(t<=t[idx[-1]]-1.0)
def run(path,p=None,window='steady'):
    q=dict(NOM); q.update(p or {})
    t,tau,om=load(path); tau=tau*q['torque_x']; om=om*q['time_x']; t=t/q['time_x']   # time_x>1 = faster cadence (same path)
    dt=np.gradient(t); W=steady_window(t,om) if window=='steady' else np.ones_like(t,bool)
    Pj=[]; FEsum=0
    for k in range(12):
        j=LEG[k%6]; s=SEL[j]; N,n=s['ratio'],s['nmot']; ef=min(s['eta']*q['eta_fwd_x'],0.99); eb=min(ETA_BACK[j]*q['eta_back_x'],0.99)
        Km=s['Km']/math.sqrt(q['rcu_hot']); Kt=s['Kt']; fe=FE[MOTKEY[j]]
        x=tau[:,k]; w=om[:,k]; mot=x*w>=0
        tm=np.where(mot,x/(N*ef),x*eb/N)/n; wm=w*N
        I=np.abs(tm)/Kt; krpm=np.abs(wm)*60/(2*math.pi)/1000
        Pfe=n*(fe['a_W_per_krpm']*krpm+fe['b_W_per_krpm2']*krpm**2)*q['iron_x']
        Pdrv=n*(28/49.5**2*I**2+28/49.5*I)*q['drive_x']
        FEsum=FEsum+Pfe
        pe=n*tm*wm+n*(tm/Km)**2+Pdrv+Pfe; Pj.append(pe)
    Pj=np.array(Pj); NS,NP=q['ns'],q['np_']; OCV=NS*q['vcell']; RP=NS*0.015/NP*q['ir_x']
    def batt(Pbus,Ich_max):
        I=np.where(Pbus>=0,(OCV-np.sqrt(np.maximum(OCV**2-4*RP*Pbus,0)))/(2*RP),0.0)
        Pch=np.minimum(-np.minimum(Pbus,0),Ich_max*(OCV+Ich_max*RP)); Ich=(-OCV+np.sqrt(OCV**2+4*RP*Pch))/(2*RP)
        return np.where(Pbus>=0,OCV*I,-OCV*Ich*0.99), -np.minimum(Pbus,0)-Pch
    mean=lambda x:float(np.sum((x*dt)[W])/np.sum(dt[W]))
    PA=np.maximum(Pj,0).sum(0)+q['p_other']; PB=Pj.sum(0)+q['p_other']
    cA,_=batt(PA,0); cC,bC=batt(PB,q['charge_A'])
    no,rg=mean(cA),mean(cC)
    return dict(P_noregen=no,P_regen=rg,regen_W=no-rg,brake_W=mean(bC),window_s=(float(t[W][0]),float(t[W][-1])),
                iron_W=mean(FEsum),trace=dict(t=t,PA=PA,PB=PB))
def runtime(P,Wh): return Wh*0.9/P
