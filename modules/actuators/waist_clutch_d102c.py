"""D102c (final T&R spec): waist-pitch slip clutch between CSG-25 output and the torso yoke + PU stop torso<->pelvis.
3-DOF time-domain: rotor+WG reflected Jr 0.652 (D102b) -- CSG-25-100 nonlinear stiffness (HD Table 43) -- gear output node Jo [EST]
-- friction clutch (stick: stiff spring Kc, slip at Tc, Coulomb) -- torso I (1.44 / 3.52, T&R) -- PU stop (PUR90A D575 curve x1.3 [EST]).
Contact 7.0 rad/s (Controls 1ed4d73/084af79), both directions (motor 0 / +115.4 into the stop / -115.4 away). Gate 153 J (T&R 1.5 x 102 J)."""
import math,json,os,numpy as np
Jr=0.652; Jo=1.0e-3; Kc=2.0e5; RATE=1.3; Tmot=115.4; W=7.0
T1,K1,T2,K2,K3=14,3.1e4,48,5.0e4,5.7e4
def Tg(th):
    a=abs(th)
    t=K1*a if a<=T1/K1 else (T1+K2*(a-T1/K1) if a<=T1/K1+(T2-T1)/K2 else T2+K3*(a-T1/K1-(T2-T1)/K2))
    return math.copysign(t,th)
eps=np.array([0,.02,.05,.10,.15,.20,.25]); sig=np.array([0,160,325,705,1050,1380,1690])*0.0068948
cum=np.concatenate([[0],np.cumsum(np.diff(eps)*(sig[1:]+sig[:-1])/2)])
E_gate=153.0; E25=1.1*E_gate; TH25=0.18    # rad of stop travel to 25 % strain (chosen: peak <= 2.5 kN.m at gate energy)
M25=sig[-1]*E25*0.25/(cum[-1]*TH25)   # sigma25*A*r ; A*r = V*0.25/TH25
def Mstop(x):
    if x<=0: return 0.0
    e=x/TH25*0.25
    return RATE*float(np.interp(e,eps,sig))/sig[-1]*M25 if e<=0.25 else 1e7   # 1e7 = bottomed (must not occur)
def run(I,Tc,motor=0.0,w=W,tend=0.35,dt=1e-6):
    xt=xo=xr=0.0; vt=vo=vr=w; s=0.0     # s = clutch spring deflection (stick)
    g=0;M=0;xm=0;slip=0;Eslip=0;bott=False
    for _ in range(int(tend/dt)):
        Tgear=Tg(xr-xo)
        Tcl=Kc*s
        if abs(Tcl)>Tc: Tcl=math.copysign(Tc,Tcl)
        Ms=Mstop(xt); bott|=Ms>=1e7
        ar=(motor-Tgear)/Jr; ao=(Tgear-Tcl)/Jo; at=(Tcl-Ms)/I
        vr+=ar*dt; vo+=ao*dt; vt+=at*dt; xr+=vr*dt; xo+=vo*dt; xt+=vt*dt
        dv=vo-vt; s_new=s+dv*dt
        if abs(Kc*s_new)>Tc: slip+=abs(dv*dt); Eslip+=Tc*abs(dv*dt); s=math.copysign(Tc/Kc,s_new)
        else: s=s_new
        g=max(g,abs(Tgear)); M=max(M,Ms); xm=max(xm,xt)
    return dict(gear_peak_Nm=round(g,1),stop_peak_Nm=round(M),stop_travel_mrad=round(xm*1e3,1),stop_strain=round(xm/TH25*0.25,3),
                clutch_slip_deg=round(math.degrees(slip),1),clutch_energy_J=round(Eslip,1),bottomed=bott)
Tc=170.0   # set point: > 115.4 x 1.3 = 150, < 204 with +/-10 % tolerance -> 153..187
out=dict(Jr=Jr,Jo=Jo,Kc=Kc,Tc=Tc,Tc_band=[153,187],TH25_mrad=TH25*1e3,E25_J=round(E25,1),cases={})
for I in (1.44,3.52):
    wg=math.sqrt(2*E_gate/(I+Jr))
    for lab,mot,w in (('7.0 motor 0',0,W),('7.0 motor +115 into stop',Tmot,W),('7.0 motor -115',-Tmot,W),(f'gate 153 J ({wg:.2f} rad/s)',0,wg),('7.0 no clutch',0,W)):
        r=run(I,1e9 if 'no clutch' in lab else Tc*1.1 if False else Tc,mot,w)
        r['E_kin_J']=round(0.5*(I+Jr)*w*w,1); out['cases'][f'I{I} {lab}']=r; print(I,lab,r,flush=True)
for tc in (153,187):   # tolerance band
    r=run(3.52,tc,Tmot); out['cases'][f'I3.52 7.0 motor+ Tc{tc}']=r; print('band',tc,r)
# geometry at r 110 mm [EST yoke], heat
V=E25/cum[-1]; r=110; T=TH25*r/0.25
out['PU']=dict(r_mm=r,V_cm3=round(V,1),thickness_mm=round(T,1),area_mm2=round(V*1000/T),per_end='one stack per end (-30 / +60 deg), 2 ends',PU_g_per_end=round(V*1.13),
  mass_est_kg_robot=round(2*(V*1.13/1000)*1.7,2))
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'results/waist_clutch_d102c.json'),'w'),indent=1,default=str)
print(out['PU'])
