import numpy as np,math
R=25;y=np.linspace(-24,24,481)
def hgap(s0,dT=30):
  s=(s0+R-np.sqrt(R**2-y**2))*1e-3
  Ra=9.81/330*dT*s**4/(1.7e-5*2.4e-5*0.1)
  Nu=np.maximum(Ra/24*(1-np.exp(-35/Ra))**0.75,1.0); return (Nu*0.027/s).mean()
sig=5.67e-8
def hr(e1,e2,T=60):return 4*sig*(273+T)**3/(1/e1+1/e2-1)
m=math.sqrt(16/(167e-3));eta=math.tanh(m*0.0135)/(m*0.0135);print('eta',eta)
A=0.0256
# outer UA cases
s=5e-3;Ra=9.81/330*36*s**4/(1.7e-5*2.4e-5*0.1);Nu=Ra/24*(1-math.exp(-35/Ra))**0.75;hn=Nu*0.027/s
rad_env=hr(0.85,0.9,55)*0.0048*1.3
UA_stand=hn*A*eta+rad_env
def walk(vc):
  mcp=7*5e-3*13e-3*vc*1.15*1007;hA=20*A*eta;ntu=hA/mcp;return mcp*(1-math.exp(-ntu))+rad_env
print('hn',hn,'UA stand',UA_stand,'walk .2/.4',walk(.2),walk(.4))
Gf=(hgap(7)+hr(0.1,0.05))*0.0045;Gint=3*0.004;Gsh=0.2*0.002*0.296*math.sqrt(16/0.0004)/(1+0.2*0.002*0.296*200*20)
print('Gf',Gf,'Gint',Gint,'Gshell',Gsh)
Tf=45
for name,UA in (('h8 claim',0.203),('walk lo',walk(.2)),('walk hi',walk(.4)),('stand',UA_stand),('h12',0.203*1.5)):
  for Q,c in ((7.2,'duty'),(12,'cont')):
    Tp=(Q+(UA+Gint+Gsh)*35+Gf*Tf)/(UA+Gint+Gsh+Gf); print(name,c,round(Tp+Q/2*.3,1),'femurW',round(Gf*(Tp-Tf),2),'shellW',round(Gsh*(Tp-35),2))
