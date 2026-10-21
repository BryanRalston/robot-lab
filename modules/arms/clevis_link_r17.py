"""R17 (R-132 §5): pocketing study, 7075 elbow clevis + roll-yaw link (model_v4 EST geometry, 0.61 kg/side). Hand calcs vs R-128 bands.
Loads [EST]: fall 104 N.m upper-arm bending (R16); elbow cap 69 N.m; lug reaction = forearm+hand fall 2.77 kg x 187.5 m/s2 = 520 N
+ couple 78 N.m / 88 mm lug spacing; shoulder-yaw torque 70 N.m through the link. Kt 3 on hand stresses [EST]. rho 2.81 g/cc."""
import json,os
rho=2.81e-6; Kt=3.0
old=dict(clevis_base=60*96*10*rho,clevis_lugs=2*50*8*48*rho,link=60*40*50*rho)
# pocketed: base 3 mm floor + 4 mm rim + tube boss (keeps ~45 % [EST]); lugs 9 mm (8 fails Kt3: 310 vs 294), tapered to 80 % of rect [EST]; link box wall 4
new=dict(clevis_base=0.45*old['clevis_base'],clevis_lugs=2*0.8*50*9*48*rho,link=(60*40*50-52*32*42)*rho)
F_lug=520/2+78e3/88; M_lug=F_lug*48; S_lug=50*9**2/6
I_link=(60*40**3-52*32**3)/12; S_link=I_link/20
base_S=60*3**2/6+2*4*10**2/6*2  # floor + rims [EST]
st=dict(lug_MPa=round(Kt*M_lug/S_lug),lug_limit=294,link_MPa=round(Kt*104e3/S_link),link_limit=308,
        base_note='pocketed base carries 104 N.m into the lugs via rims/boss; hand calc not credible for the pocket web -> Job 8d FEA')
out=dict(old_kg={k:round(v,4) for k,v in old.items()},new_kg={k:round(v,4) for k,v in new.items()},
         saving_side=round(sum(old.values())-sum(new.values()),3),saving_pair=round(2*(sum(old.values())-sum(new.values())),3),stress=st,
         stock=dict(clevis='7075-T651 2.5 in plate, L=Y (across lugs), band 294 LT',link='7075-T651 2.0 in plate, L=Z (arm axis), band 308'))
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'clevis_link_r17.json'),'w'),indent=1); print(out)
