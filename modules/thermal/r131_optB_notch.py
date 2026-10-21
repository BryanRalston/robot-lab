"""Option B rev: L74 R8 notch x -34.5..-61 x y104-156 ~1320 mm2 free (legs/results/r031/p156_rev5_optionB.md), stack to z860, rev4e shroud."""
from r131_optB import chim,Tb
H=0.860-0.643
for lab,ex in (('B2n notch 1320 + shroud 3200',((1320e-6,0.6),(3200e-6,0.6))),('B3n notch 1320 + grille 1250',((1320e-6,0.6),(1250e-6,0.6)))):
  m,dT=chim(H=H,exits=ex,K=1.0);print(f'{lab}: m {m*1e3:.3f} jet {35+dT:.1f} Tb {Tb(m):.1f}')
for A in (1320,1000,800,600,500,400,350,300,250,200):
  m,dT=chim(H=H,exits=((A*1e-6,0.6),(3200e-6,0.6)),K=1.0);print(A,round(Tb(m),1),round(35+dT,1))
