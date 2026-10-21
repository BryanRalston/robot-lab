"""T&R recheck of the Thermal rev 4e outlet shroud (218a541) with the ID P-156 rev 4e geometry [EST].
Outer face = (h_i*T_mix + (4 conv + 6 rad)*Ta)/(h_i + 10)  (Thermal's balance; foil inner face removes radiation).
Exhaust at H 0.18: drive base 73.2 C at 35 C amb (Thermal); exhaust rise scaled from the rev 4d 44-62 K at base 78:
(73.2-35)/(78-35) -> 39-55 K -> exhaust 74-90 C."""
import json
Ta=35.; out={}
k=(73.2-35)/(78-35); ex=[Ta+44*k, Ta+62*k]
out["exhaust_C"]=[round(x,1) for x in ex]
for mix,lab in ((0.0,"no_dilution"),(0.5,"1to1_dilution")):
    for hi in (3.,5.):
        for e in ex:
            Tm=e-(e-Ta)*mix
            out[f"{lab}_hi{int(hi)}_ex{round(e)}"]=round((hi*Tm+10*Ta)/(hi+10),1)
out["outlet_webs_C"]=[round(e,1) for e in ex]   # webs washed both sides -> ~exhaust
json.dump(out,open('r143_rev4e.json','w'),indent=1); print(json.dumps(out,indent=1))
