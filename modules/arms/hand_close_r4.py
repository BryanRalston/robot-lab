"""RL Arms A43: loaded six-flexor close under the hand power architecture (Electronics: 2x RECOM RP40-11024SFR, split rails A/B,
each <= 40 W / firmware cap 1.67 A at 24 V; flexors 3/3; board logic on rail A). Light ODE, explicit Euler, dt 0.1 ms.
CITED (actuators/datasheets, D68): maxon DCX 22 S 24 V winding (innodrive sheet): R 3.69 ohm, Kt 18.4 mNm/A, I0 35.9 mA, J 5.55 gcm2,
  I_nom 0.869 A; GPX 22 HP 103:1 (config sheet): eta_max 0.65, J 1.191 gcm2, intermittent 3.8 N·m.
  DCX 16 S 24 V: R 83.1 ohm, Kt 36.0 mNm/A, I_nom 0.144 A. v3 used 111:1 (not in the cited configs) -> 103:1 here.
v3 geometry: spool r 4 mm, tendon stroke 30 mm, MCP arm 9 mm, contact at 65 mm.
[EST] (flagged): tendon load (return spring 10 N at full stroke + contact over the last 6 mm ramping to T4 30 N tip = 217 N tendon),
  sheath friction x1.3, board logic 4 W on rail A, ideal 24 V rails (no droop), equal power share inside a rail, finger inertia neglected,
  small drives holding at I_nom during the close (worst case), copper at 25 C resistance (hot R x1.5 case also run)."""
import json,os,numpy as np
H=os.path.dirname(os.path.abspath(__file__))
Kt,I0,Jm,Jg=0.0184,0.0359,5.55e-7,1.191e-7; V=24.0; N=103; r=0.004; S=0.030
R16,I16=83.1,0.144; P16=I16**2*R16          # small drive holding at I_nom (stall): copper only
RAILS={'A':dict(flexors=['F1 thumb flex','F2 index flex','F3 middle flex'],small=['S1 thumb rotation','S2 thumb abduction'],logic=4.0),
       'B':dict(flexors=['F4 ring flex','F5 little flex','F6 index MCP flex'],small=['S3 index abduction','S4 ring/little abduction','S5 spare/wrist-side'],logic=0.0)}
CAP=40.0
def F_tendon(x,fric): return (10.0*x/S+217.0*min(1,max(0,(x-(S-0.006))/0.006)))*fric
def close(P_avail,eta=0.65,R=3.69,fric=1.3,dt=1e-4,T=2.0):
    w=x=t=0.0; pk_m=0; i_pk=0
    while t<T:
        Tl=F_tendon(x,fric)*r/(N*eta)
        ib=(-Kt*w+np.sqrt((Kt*w)**2+4*R*P_avail))/(2*R); i=min((V-Kt*w)/R,ib)
        w=max(0.0,w+(Kt*(i-I0)-Tl)/(Jm+Jg)*dt); x+=w/N*r*dt; t+=dt
        pk_m=max(pk_m,R*i*i+Kt*w*i); i_pk=max(i_pk,i)
        if x>=S: return t,pk_m,i_pk
    return None,pk_m,i_pk
out={'rails':{}}
for case,kw in {'nominal':{},'eta0.50':dict(eta=0.5),'hotR_x1.5':dict(R=3.69*1.5),'fric_x1.6':dict(fric=1.6)}.items():
    res={}
    for rn,rl in RAILS.items():
        P_small=len(rl['small'])*P16; P_each=(CAP-rl['logic']-P_small)/len(rl['flexors'])
        t,pk,ipk=close(P_each,**kw)
        res[rn]=dict(P_per_flexor_W=round(P_each,2),P_small_W=round(P_small,2),logic_W=rl['logic'],t_close_s=None if t is None else round(t,3),
                     peak_flexor_W=round(pk,2),peak_flexor_A=round(ipk,2),rail_peak_W=round(rl['logic']+P_small+3*pk,1),rail_bus_A=round((rl['logic']+P_small+3*pk)/V,3),ok=bool(t and t<=1.0))
    out['rails'][case]=res
# hold at 30 N tip with all six flexors (continuous), per rail
for fric in (1.0,1.3):
    i30=(217*fric*r/(N*0.65))/Kt+I0; out[f'hold_30N_fric{fric}']=dict(i_per_flexor_A=round(i30,3),I_nom_A=0.869,ratio=round(i30/0.869,2),
        rail_A_W=round(4+2*P16+3*3.69*i30**2,1),rail_B_W=round(3*P16+3*3.69*i30**2,1))
out['motor_to_rail']={rn:rl['flexors']+rl['small']+(['board logic'] if rl['logic'] else []) for rn,rl in RAILS.items()}
json.dump(out,open(os.path.join(H,'hand_close_r4.json'),'w'),indent=1); print(json.dumps(out,indent=0))
