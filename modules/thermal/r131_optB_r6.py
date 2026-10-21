"""ID P-156 rev 6 (341ef4a): chimney section 1118 mm2 (21.5x52) + L74 notch 1323 + stack z860 + rev4e shroud. Chimney as a loss
element: entry/expansion + friction ~ K 1.0 at Cd 0.8-equivalent [EST]. Same model as r131_optB.py."""
from r131_optB import chim,Tb
H=0.217
def run(Ach,cd=0.8): return chim(H=H,exits=((Ach*1e-6,cd),(1323e-6,0.6),(3200e-6,0.6)),K=1.0)
for A in (1118,1200,900,700,500,400,300,250):
  m,dT=run(A);print(A,round(m*1e3,3),round(Tb(m),1),round(35+dT,1))
m,_=run(1118,0.6);print('1118 conservative Cd0.6',round(Tb(m),1))
