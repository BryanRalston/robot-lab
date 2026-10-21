import numpy as np
R=25;y=np.linspace(-24,24,481)
def hgap(s0):
  s=(s0+R-np.sqrt(R**2-y**2))*1e-3
  # natural conv Elenbaas parallel plate, dT 30, L .1 ; floor Nu=1 (conduction)
  Ra=9.81/330*30*s**4/(1.7e-5*2.4e-5*0.1)
  Nu=np.maximum(Ra/24*(1-np.exp(-35/Ra))**0.75,0)
  Nu=np.maximum(Nu,1.0) # conduction to femur
  return (Nu*0.027/s).mean()
for s0 in (2,3,3.5,4,6):print(s0,round(hgap(s0),1))
# fin channel
s=1.17e-3;Ra=9.81/330*35*s**4/(1.7e-5*2.4e-5*0.1);print('Ra fin',Ra, Ra/24*0.027/s)
def T(h,Q,s0,Tf,eps=0.85,ad=0.0065):
  hr=4*5.67e-8*eps*0.85/(eps+0.85-eps*0.85)*((273+60)**3)
  Gf=(hgap(s0)+hr)*0.0045
  # solve h*ad*(T-35)+Gf*(T-Tf)=Q
  Tp=(Q+h*ad*35+Gf*Tf)/(h*ad+Gf); return round(Tp+Q/2*0.3,1)
for s0 in (3.5,4):
 for Tf in (40,50):
  for h in (8,12):
   print(s0,Tf,h,'duty',T(h,7.2,s0,Tf),'cont',T(h,12,s0,Tf))
print('bare(eps .1)',T(8,7.2,4,45,eps=0.1))
