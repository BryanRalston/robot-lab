# R-042 EPP pad face temp next to 69 C bulkhead, 35 C ambient. 1-D per m2. RL Thermal.
import json
sig=5.67e-8; Tb=69+273.15; Ta=35+273.15; kE=0.04; L=0.030; ka=0.028
res={}
for amb,ho in (('walk',15.0),('still',7.0)):          # outer h incl. radiation
  for eb,lab in ((0.85,'Al anodised/painted'),(0.05,'low-e foil')):
    for g in (0,3,5,10):
      Tf=Tb-5
      for _ in range(300):
        q=(Tf-Ta)/(L/kE+1/ho)
        if g==0: Tf=Tb-q*1e-4; continue           # contact, ~1e-4 m2K/W
        e=1/(1/eb+1/0.9-1); hr=4*e*sig*((Tb+Tf)/2)**3; hc=ka/(g*1e-3)
        Tf=Tb-q/(hc+hr)
      res[f'{amb}|{lab}|{g}mm']=round(Tf-273.15,1)
print(json.dumps(res,indent=1)); json.dump(res,open('results/r042_epp.json','w'),indent=1)
