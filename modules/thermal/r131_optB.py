"""R-143 Option B: rear/up exit through L60 top-plate cut-out (52x40=2080 mm2 gross).
Geometry from repo: chimney/duct z 643..837 (legs/p156_vent_check_l72.py), L60 plate z 816-824 +1.5 (DECISIONS L60) -> 817.5-825.5,
cut-out y 104-156 (R143 s5). Same chimney model as r131_rev4d_chimney.py; Tb=a+b/m fitted to rev4e table (H .12/.18/.20)."""
rho=1.15;cp=1007;g=9.81;T=308;mu=1.85e-5
def chim(Q=7.5,H=0.12,Ain=1440e-6,exits=((1200e-6,0.6),),Afin=650e-6,K=0.0):
  lo,hi=1e-6,0.05
  for _ in range(100):
    m=(lo+hi)/2;dT=Q/(m*cp);rh=rho*T/(T+dT)
    head=rho*g*H*0.8*dT/T;Vf=m/(rho*Afin)
    loss=0.5*rho*(m/(rho*Ain))**2/0.36+sum(0.5*rh*(m/(rh*A))**2/c**2 for A,c in exits)+12*mu*0.1*Vf/(5e-3)**2+0.5*rho*Vf**2*1.5+K*0.5*rh*(m/(rh*2080e-6))**2
    lo,hi=(m,hi) if head>loss else (lo,m)
  return m,dT
Tb=lambda m:47.2+3.97e-3/m
z_in=0.643
cases=[('B1 exit at plate top z825.5, grille 60% (1250 free)',0.8255-z_in,((2080e-6,0.6),(1250e-6,0.6)),1.0),
 ('B2 + stack to z860, shroud 2600+600',0.860-z_in,((2080e-6,0.6),(3200e-6,0.6)),1.0),
 ('B3 stack to z860, grille only 1250',0.860-z_in,((2080e-6,0.6),(1250e-6,0.6)),1.0)]
for lab,H,ex,K in cases:
  m,dT=chim(H=H,exits=ex,K=K);print(f'{lab}: H {H:.3f} m {m*1e3:.3f} g/s exhaust dT {dT:.1f} K jet {35+dT:.1f} C Tb {Tb(m):.1f} C')
for d in (600e-6,1200e-6):  # dilution mixing of jet with ambient entrained via slots (ratio by area, [EST])
  m,dT=chim(H=0.217,exits=((2080e-6,0.6),(3200e-6,0.6)),K=1.0);r=d/2080e-6
  print('dilution',d*1e6,'mixed jet',round(35+dT/(1+r*1.5),1))
