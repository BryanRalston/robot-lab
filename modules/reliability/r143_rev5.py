"""T&R R-143 rev 5: P-156 rev 5 (a065aa3) outboard side exit + hood. Hand model [EST], same balances as r143_rev4e.py.
Drive base Tb per case from rev 4b/4c tables; H 0.14 (was 0.18) penalty +2.5 K on standing cases [EST, Thermal to re-run].
Exhaust leaving the fins: Ta + f*(Tb-Ta), f 0.85-1.0 (fully developed channel ~ fin temp; capped at Tb).
Hood outer face = (hi*Tmix + 10*Ta)/(hi+10), foil inner face; hi 3 (good) / 5 (poor mixing).
Louvre slats + recessed exit webs: washed both sides -> T_mix (louvres, dilution 1:1 good / none poor) and exhaust (webs).
Jet at the hand: exit plume on the up/aft face, 26 mm standoff -> hand 0-30 mm away: plume core ~ T_mix."""
import json
cases={25:{"walk_duty":61.0,"carry":87.5,"stand_hot":78.3+2.5},35:{"walk_duty":71.0,"carry":87.5,"stand_hot":78.5+2.5}}
out={}
for Ta,cc in cases.items():
  for c,Tb in cc.items():
    ex=[Ta+f*(Tb-Ta) for f in (0.85,1.0)]
    good=[(3*(e-(e-Ta)*0.5)+10*Ta)/13 for e in ex]; poor=[(5*e+10*Ta)/15 for e in ex]
    lv_good=[e-(e-Ta)*0.5 for e in ex]; lv_poor=ex
    out[f"{Ta}C_{c}"]=dict(Tb=Tb,exhaust=[round(x,1) for x in ex],hood_face_good=[round(x,1) for x in good],hood_face_poor=[round(x,1) for x in poor],
      louvres_good=[round(x,1) for x in lv_good],louvres_poor=[round(x,1) for x in lv_poor],exit_webs=[round(x,1) for x in ex])
# hand geometry (sim/v3 + model_v4, standing, arm hanging, joints 0)
sh_z=1.50; hand=dict(y=(0.282-0.043,0.282+0.043),x=(-0.016,0.016),z=(sh_z-0.04-0.26-0.267-0.17,sh_z-0.04-0.26-0.267-0.03))
hood=dict(y_outer=0.261,x=(-0.084,-0.010),z=(0.780,0.815))
out["hand_box_m"]=hand; out["hood_m"]=hood
out["y_gap_hand_to_hood_mm"]=round((hand["y"][0]-hood["y_outer"])*1000,1)
out["z_overlap"]=hood["z"][0]<hand["z"][1] and hood["z"][1]>hand["z"][0]
json.dump(out,open("r143_rev5.json","w"),indent=1); print(json.dumps(out,indent=1))
