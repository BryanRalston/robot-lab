"""R-143 guard surface temperature, hand estimate [EST]. Black-anodised fins (eps 0.85) radiate to a perforated
PC guard (eps 0.9, solid fraction 0.4); guard loses heat by convection both sides (h 8, Thermal basis) + radiation out."""
import json
s=5.67e-8;out={}
for Tf in (71.5,85.0,95.8):
  for Ta in (25.0,35.0):
    for dTair in (0.0,5.0):   # warm plume air at the guard [EST]
      T=Ta+5
      for _ in range(200):
        Tk,Tfk,Tak=T+273.15,Tf+273.15,Ta+273.15
        qin=0.7*s*(Tfk**4-Tk**4)*0.8      # eff. emissivity 0.7, view of fin field 0.8
        qout=8*(T-(Ta+dTair))+8*(T-Ta)+0.9*s*(Tk**4-Tak**4)
        T+= (qin-qout)/60
      out[f"Tfin{Tf}_Ta{Ta}_plume{dTair}"]=round(T,1)
json.dump(out,open('r143_guard.json','w'),indent=1);print(json.dumps(out,indent=1))
