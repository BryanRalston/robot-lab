"""RL Thermal O-A2: arm hold transient (20 kg two-hand carry). Single- and two-node lumped models. -> results/oa2_arm_hold.json"""
import json, math, os, sys
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,f'{H}/../../v3/analysis'); import parts as P
EST=dict(eta=0.75, rcu_hot=1.4, h=12.0, fins=2.0, cp_motor=460.0, cp_al=900.0, cp_steel=460.0)
J={'shoulder_pitch':dict(m='TBM2G-07608',T=61.3,N=100,D=96,L=80,act=1.52,gear_steel=0.40),   # CSG-25 set ~0.40 kg [EST]
   'elbow':dict(m='TBM2G-05013',T=40.1,N=100,D=70,L=75,act=0.90,gear_steel=0.22)}            # CSG-20 set ~0.22 kg [EST]
def sim(Pcu,Rwh,Rha,Cw,Ch,lim=100.0,tmax=36000,dt=0.5):
    Tw=Th=0.0; t=0
    while t<tmax:
        q=(Tw-Th)/Rwh; Tw+=dt*(Pcu-q)/Cw; Th+=dt*(q-Th/Rha)/Ch; t+=dt
        if Tw>=lim: return t/60
    return None
out={}
for j,d in J.items():
    m=P.MOT[d['m']]; Km=m['Km'][1]/math.sqrt(EST['rcu_hot']); res={}
    for eta in (EST['eta'],1.0):
      tm=d['T']/(d['N']*eta); Pcu=(tm/Km)**2
      area=(math.pi*d['D']*d['L']+2*math.pi/4*d['D']**2)*1e-6
      Rwh=0.6*m['Rth']; Cw=m['mass']*EST['cp_motor']
      Ch=d['gear_steel']*EST['cp_steel']+(d['act']-m['mass']-d['gear_steel']-0.022)*EST['cp_al']   # rest of actuator ~Al
      for hx in (0.7,1.0,1.3):
        Rha=1/(EST['h']*hx*area*EST['fins']); ss=Pcu*(Rwh+Rha)
        t1=-Rwh*Cw*math.log(1-100/(Pcu*Rwh))/60 if Pcu*Rwh>100 else None   # single node, winding only on Rwh (housing held at amb)
        tau1=(Rwh+Rha)*(Cw+Ch); t1b=-tau1*math.log(1-100/ss)/60 if ss>100 else None   # single node, whole actuator
        res[f'eta{eta}_h{hx}']=dict(tm_Nm=tm,Tc130=m['Tc130'][1],Pcu_W=Pcu,ss_dT=ss,Rwh=Rwh,Rha=Rha,Cw=Cw,Ch=Ch,tau_1node_min=tau1/60,
            t100_1node_min=t1b,t100_winding_only_min=t1,t100_2node_min=sim(Pcu,Rwh,Rha,Cw,Ch))
    out[j]=res
json.dump(dict(EST=EST,J=J,res=out),open(f'{H}/results/oa2_arm_hold.json','w'),indent=1)
for j,r in out.items():
    for k,v in r.items(): print(j,k,{a:(round(b,2) if isinstance(b,float) else b) for a,b in v.items()})
