# R-110: bond temp vs knee trunnion break value; no lever-eye sleeve, tine ø22 (26 K/W) || rod path 58 K/W. Conservative superposition, h12 attenuation 0.28.
import json
par=lambda *r:1/sum(1/x for x in r); Rb=par(26,58); att=0.28; Rnode=2.9
cases={'A35 design':(50,60),'vents short':(62.6,68)}   # hip case dT, knee case dT
out={}
for lab,Rtr in (('unbroken 2.5',2.5),('unbroken/5',5),('10',10),('15',15),('33 (L61)',33)):
  r={}
  for cl,(dTh,dTk) in cases.items():
    for Rc in (8,14):
      thk=dTk*Rnode/(Rtr+Rnode); r[f'{cl}|Rc{Rc}']=round(35+dTh*Rc/(Rb+Rc)+att*thk,1)
  out[lab]=r; print(lab,r)
json.dump(out,open('results/a38_r110.json','w'),indent=1)
