import math
rho=1.15;cp=1007;g=9.81;T=308;mu=1.85e-5
def chim(Q=7.5,H=0.12,Ain=1200e-6,Aout=1200e-6,Cd=0.6,Afin=650e-6,bypass=0):
  # solve dT,m: buoyancy rho g H dT_eff/T = sum losses ; dT=Q/(m cp)
  lo,hi=1e-6,0.05
  for _ in range(100):
    m=(lo+hi)/2;dT=Q/(m*cp)
    head=rho*g*H*0.8*dT/T
    Vin=m/(rho*Ain);Vout=m/(rho*Aout);Vf=m/(rho*Afin)*(1-bypass)
    loss=0.5*rho*Vin**2/Cd**2+0.5*rho*Vout**2/Cd**2+12*mu*0.1*Vf/(5e-3)**2+0.5*rho*Vf**2*1.5
    if head>loss: lo=m
    else: hi=m
  return m,dT
for lab,k in (('T&R basis Cd.4',dict(Cd=0.4)),('Cd .6',{}),('Cd.6 H.20',dict(H=0.2)),('2x area',dict(Ain=2400e-6,Aout=2400e-6)),('2x area H.20',dict(Ain=2400e-6,Aout=2400e-6,H=0.2)),('3x area H .25',dict(Ain=3600e-6,Aout=3600e-6,H=0.25))):
  m,dT=chim(**k);print(lab,round(m*1e3,2),'g/s dT',round(dT,1),'mean',round(dT/2,1))
