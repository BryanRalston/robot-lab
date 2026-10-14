"""L63: A38 collar cross-pin backup check at R-110 one-screw fault 29.6 kN (Materials 04aa50b). Hand calc.
Allowables MATERIALS_DB: 7075-T6 Sy 480, shear 330, fatigue 160; 42CrMo4 Sy 990. Bearing yield 1.5*Sy=720 [EST, as R-110]. Pin shear yield 0.6*Sy."""
import math,json
F=29600.; t=1.2; Sy=480; Tbr=720; Ts7=330; Sp=990*0.6; rho=7.8e-6; Atube=183.97; Fw=0.52*8763.86; Kt=2.909
def chk(n_pins,d,planes_per,through,e,L):
    Ap=math.pi*d*d/4; nb=n_pins*(2 if through else 1)          # tube bearing faces
    tau=F/(n_pins*planes_per*Ap); brg=F/(nb*d*t); net=Atube-nb*d*t
    collar_tear=F/(nb*2*(e-d/2)*6.0)                           # collar wall 6 mm, shear-out to collar end
    return dict(pins=f"{n_pins}x ø{d}{' through' if through else ' radial'}",pin_tau=round(tau,1),SF_pin=round(Sp/tau,2),
      tube_bearing=round(brg,1),SF_bearing=round(Tbr/brg,2),collar_e_over_D=round(e/d,2),collar_tearout=round(collar_tear,1),
      SF_tearout=round(Ts7/collar_tear,2),tube_net=round(F/net,1),SF_net=round(Sy/(F/net),2),
      walk_fatigue_hole=round(Fw/net*Kt,1),SF_fatigue=round(160/(Fw/net*Kt),2),pin_mass_leg_kg=round(n_pins*math.pi*d*d/4*L*rho,4))
A=chk(2,6,2,True,8.5,62); B=chk(8,7,1,False,8.5,10)
B['mass_delta_robot_kg']=round(2*(B['pin_mass_leg_kg']-A['pin_mass_leg_kg']),4)
R=dict(current_L22=A,proposed_L63=B); json.dump(R,open('results/a38/cross_pin_backup_l63.json','w'),indent=1); print(json.dumps(R,indent=1))
