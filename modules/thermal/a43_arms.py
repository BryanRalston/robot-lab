"""RL Thermal A43: (1) shoulder_pitch 07608C band/cap with D68 model; (2) hand motor/converter burst duty. -> results/a43_arms.json"""
import json, math, os
H=os.path.dirname(os.path.abspath(__file__))
O=json.load(open(f'{H}/results/oa2_arm_hold.json'))['res']['shoulder_pitch']['eta0.75_h1.0']
Rwh,Rha,Cw,Ch=O['Rwh'],O['Rha'],O['Cw'],O['Ch']; Ta=40.0; ETA=0.84; N=100
Rf=lambda T:(234.5+T)/259.5; Ktf=lambda T:1/0.89-(1/0.89-1)*(T-25)/130
P=lambda Tout,T:1.5*((Tout/(N*ETA))/(0.096*Ktf(T)))**2*0.477/1.501*Rf(T)
def steady(Tout,hx=1.0):
    Tw=Th=Ta
    for _ in range(4000):
        p=P(Tout,Tw); Th=Ta+p*Rha/hx; Tn=Th+p*Rwh
        if Tn>400: return float('inf'),None
        Tw=0.5*Tw+0.5*Tn
    return Tw,Th
def run(Tout,Tw,Th,secs,dt=0.2):
    t=0; tt={}
    while t<secs:
        p=P(Tout,Tw); q=(Tw-Th)/Rwh; Tw+=dt*(p-q)/Cw; Th+=dt*(q-(Th-Ta)/Rha)/Ch; t+=dt
        for lim in (120,130,145,155):
            if Tw>=lim and lim not in tt: tt[lim]=round(t/60,2)
    return Tw,Th,tt
r={'steady':{}, 'cap':{}}
for T in (40,43.45,47,50.2,54,55,58,61.3):
    for hx in (0.7,1.0,1.3): r['steady'][f'{T}_h{hx}']=steady(T,hx)[0]
Tw0,Th0=steady(54)
for T in (55,61.3,80,100,120,167):
    Tw,Th,tt=run(T,Tw0,Th0,600); r['cap'][str(T)]=dict(T_after_10min=Tw,crossings_min=tt)
# hand: maxon datasheets (actuators/datasheets): DCX22S 24V R 3.69, Inom 0.869, Rth 7+16, tau_w 20 s, tau_m 528 s, Tmax 125;
# DCX16S 24 V [EST winding] R 19.2, Inom 0.299, Rth 9.9+23.5, tau_w 9.63 s, tau_m 227 s, Tmax 100
M={'DCX22S':dict(R=3.69,In=0.869,Rwh=7,Rha=16,tw=20,tm=528,Tmax=125),'DCX16S':dict(R=19.2,In=0.299,Rwh=9.9,Rha=23.5,tw=9.63,tm=227,Tmax=100)}
hand={}
for k,m in M.items():
    Cw=m['tw']/m['Rwh']; Ch=(m['tm']-m['tw'])/m['Rha']
    Icont=m['In']*math.sqrt((m['Tmax']-Ta)/(m['Tmax']-25))     # nominal current rated at 25 C ambient
    hand[k]=dict(Cw=Cw,Ch=Ch,I_cont_40C=Icont)
    for Ib in (0.56,1.0,1.67,3.33):
        Pb=Ib*Ib*m['R']*Rf(100)                              # hot R at ~100 C [EST]
        dT1=Pb/Cw*1.0                                        # adiabatic 1 s
        dmax=min(1.0,(Icont/Ib)**2)                          # rms duty limit
        hand[k][f'Ib{Ib}']=dict(P_W=Pb,dT_1s_adiabatic=dT1,max_duty=dmax,min_period_s_for_1s=1/dmax)
r['hand']=hand
json.dump(r,open(f'{H}/results/a43_arms.json','w'),indent=1,default=str)
print(json.dumps(r,indent=1,default=lambda o:round(o,2)))
