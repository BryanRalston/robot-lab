"""ID P-156 rev 6b (baad131): stack top z840 (H 0.197), notch 1323, offset transition z831-840 to 2069 mm2 mouth (+K 0.5 offset bend [EST]),
shroud aft-only 2680 min + 710 dilution, chimney 1118. Same model as r131_optB_r6.py."""
from r131_optB import chim,Tb
for lab,H,Kx in (('rev6 ref z860',0.217,0.0),('rev6b z840 no bend',0.197,0.0),('rev6b z840 + offset bend',0.197,0.5),('rev6b z840 + bend K1.5 worst',0.197,1.5)):
  ex=((1118e-6,0.8),(1323e-6,0.6),(2069e-6,0.6),(3390e-6,0.6))
  m,dT=chim(H=H,exits=ex,K=1.0+Kx);print(f'{lab}: m {m*1e3:.3f} jet {35+dT:.1f} Tb {Tb(m):.1f}')
