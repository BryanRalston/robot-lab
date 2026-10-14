# D69C knee fin check (option C) vs Actuators 4366d32 / Legs L48 envelope. Hand calc, RL Thermal.
import math, json
def eta(L,t,h,k): m=math.sqrt(2*h/(k*t)); Lc=L+t/2; x=m*Lc; return math.tanh(x)/x
out={'eta':{}}
for alloy,k in (('6061-T6',167),('7075-T6',130),('A356 cast',150)):
  for t in (1.0,1.5,2.0):
    for L in (9,12,25,28,57):
      out['eta'][f'{alloy}|t{t}|L{L}']={h:round(eta(L/1e3,t/1e3,h,k),3) for h in (12,15,20)}
# winding fit from Actuators' table: T = 35 + K/(G0 + 12*A_eff)  (A_eff at their h 12, eta 1)
fit={'walk_open':(75,61),'carry_open':(101,81),'walk_vent':(63,52),'carry_vent':(84,69)}
F={}
for c,(d1,d2) in fit.items():
  G0=(d2*0.6-d1*0.3)/(d1-d2); F[c]=(G0,d1*(G0+0.3))
T=lambda c,A:round(35+F[c][1]/(F[c][0]+12*A),1)
out['fit']={c:{'G0_W/K':round(F[c][0],3),'K':round(F[c][1],1)} for c in F}
out['check_0.07_carry_open']=T('carry_open',0.07)   # Actuators: 107
# layout within envelope: housing r 45 mm [EST], length 101, active fin length 90 [EST], pitch 6.5 mm, t 1.5, 6061
r,Lf,p,t,rho=45e-3,0.090,6.5e-3,1.5e-3,2700
lay=[('rear 120-240 deg',120,25),('front 330-030',60,9),('bracket 030-060/300-330',60,0)]
A=0;m=0;Aeff={};rows=[]
for nm,deg,H in lay:
  n=int(2*math.pi*r*deg/360/p) if H>0 else 0
  a=n*2*H/1e3*Lf; mm=n*t*H/1e3*Lf*rho
  rows.append(dict(sector=nm,fin_h_mm=H,n=n,area_m2=round(a,4),mass_kg=round(mm,3),eta_h15=round(eta(H/1e3,t,15,167),3) if H else None))
  A+=a;m+=mm
  for h in (12,20): Aeff[h]=Aeff.get(h,0)+a*(eta(H/1e3,t,h,167) if H else 0)*h/12   # conductance at h, expressed as A at h 12
# base area lost under fin roots (already in G0): n*t*Lf
nroot=sum(x['n'] for x in rows); Aroot=nroot*t*Lf
out['layout']=dict(rows=rows,A_gross=round(A,4),mass_fins_kg=round(m,3),mass_with_base_thickening_kg=round(m+0.015,3),
  A_root_lost=round(Aroot,4),A_eff_h12=round(Aeff[12]-Aroot,4))
Ae=Aeff[12]-Aroot
out['temps_layout']={c:T(c,Ae) for c in F}
out['temps_their_0.05']={c:T(c,0.05) for c in F}
# needed gross area for A_eff 0.05 at 25 mm fins, eta at h12
e=eta(0.025,t,12,167); out['A_gross_for_Aeff_0.05']=round((0.05)/(e*(1-t/p)) ,4)
print(json.dumps(out,indent=1)); json.dump(out,open('results/d69c_knee_fins.json','w'),indent=1)
