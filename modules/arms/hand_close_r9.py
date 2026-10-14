"""R-091: loaded six-flexor close with a 1.50 A SUMMED per-rail bus limit (24 V -> 36.0 W/rail) + start stagger.
Basis hand_close_r4.py (cited maxon DCX22S/GPX22HP 103:1, eta 0.65 cited max). Per-flexor motor cap 1.66 A (R-090/R-091).
Rail A: F1-F3 + S1,S2 + board logic 4.6 W hot (Thermal 55c80c1 / A43C R-089: MCU 1.2 W [Thermal], rest 3.4 W drivers/encoders/aux [EST split]).
Rail B: F4-F6 + S3-S5. Small drives hold at I_nom (copper 1.72 W each, worst case). Finished flexors hold the contact load (copper i^2 R).
Power share: rail power left after logic+small+holders split equally among still-closing flexors, each also <= 1.66 A and <= (V-Kt w)/R.
Bus-side ideal converter (no droop), drive losses neglected [EST]. Worst: hot R x1.5, eta 0.50, sheath friction x1.6 (all together)."""
import json,os,numpy as np
H=os.path.dirname(os.path.abspath(__file__))
Kt,I0,Jm,Jg=0.0184,0.0359,5.55e-7,1.191e-7; V=24.0; N=103; r=0.004; S=0.030; ICAP=1.66; P16=0.144**2*83.1
def Ft(x,f): return (10.0*x/S+217.0*min(1,max(0,(x-(S-0.006))/0.006)))*f
def run(I_rail,logic,nsmall,stag,eta=0.65,R=3.69,fric=1.3,dt=1e-4,T=3.0):
    Pr=I_rail*V-logic-nsmall*P16; w=np.zeros(3); x=np.zeros(3); done=[None]*3; t=0.0; ipk=0.0; Pbus_pk=0.0
    ih=(Ft(S,fric)*r/(N*eta))/Kt+I0
    while t<T and None in done:
        act=[k for k in range(3) if done[k] is None and t>=k*stag]; hold=sum(1 for k in range(3) if done[k] is not None)
        Pa=Pr-hold*R*ih*ih; Pe=max(0,Pa)/max(1,len(act)); Pb=hold*R*ih*ih
        for k in act:
            ib=(-Kt*w[k]+np.sqrt((Kt*w[k])**2+4*R*Pe))/(2*R); i=min((V-Kt*w[k])/R,ib,ICAP)
            Tl=Ft(x[k],fric)*r/(N*eta); w[k]=max(0.0,w[k]+(Kt*(i-I0)-Tl)/(Jm+Jg)*dt); x[k]+=w[k]/N*r*dt
            ipk=max(ipk,i); Pb+=R*i*i+Kt*w[k]*i
            if x[k]>=S: done[k]=t
        Pbus_pk=max(Pbus_pk,Pb+logic+nsmall*P16); t+=dt
    return (None if None in done else round(max(done),3)),round(ipk,2),round(Pbus_pk/V,3)
cases={'nominal':{},'hotR1.5':dict(R=3.69*1.5),'eta0.50':dict(eta=0.5),'fric1.6':dict(fric=1.6),'worst(all3)':dict(R=3.69*1.5,eta=0.5,fric=1.6)}
rails={'A':(4.6,2),'B':(0.0,3)}; out={'basis':__doc__,'rail_limit_A':{}}
for IR in (1.50,):
    for st in (0.0,0.05,0.10,0.15,0.20):
        for c,kw in cases.items():
            for rn,(lg,ns) in rails.items():
                t,ipk,ib=run(IR,lg,ns,st,**kw); out['rail_limit_A'].setdefault(f'{IR}',{}).setdefault(f'stagger_{int(st*1000)}ms',{}).setdefault(c,{})[rn]=dict(t_close_s=t,flexor_i_pk_A=ipk,bus_A_pk=ib,ok=bool(t and t<=1.0))
# rail current needed to pass worst case (rail A, logic on), best stagger
need={}
for st in (0.0,0.05,0.10):
    for IR in np.arange(1.40,3.01,0.02):
        t,_,_=run(IR,4.6,2,st,R=3.69*1.5,eta=0.5,fric=1.6)
        if t and t<=1.0: need[f'stagger_{int(st*1000)}ms']=dict(I_rail_A=round(float(IR),2),t=t); break
out['worst_railA_need']=need
json.dump(out,open(os.path.join(H,'hand_close_r9.json'),'w'),indent=1)
for st,v in out['rail_limit_A']['1.5'].items(): print(st,{c:(v[c]['A']['t_close_s'],v[c]['B']['t_close_s'],v[c]['A']['bus_A_pk']) for c in v})
print('need',need)
