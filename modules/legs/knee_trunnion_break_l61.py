"""L61 (Thermal ec50e4e): knee trunnion -> femur thermal break, hand calc [EST unless cited].
Loads: knee peak 159.8 N.m walk_1p2, need 240 N.m (r4/requirements.md); knee lever 47.5 mm -> screw force total walk 3364 N, design 5053 N,
per trunnion side half. Screw axis ~[-0.378,0,0.926] (model_v4 housing axis), trunnion at x -130 vs femur axis x 18 -> 148 mm offset.
Materials: PEI k 0.12 W/mK, sustained <=28 MPa, fault <=76 (A37 rev B); Ti-6Al-4V k 6.7, Sy 880 [cat]; steel bolt k 40; Ti bolt k 6.7."""
import json, math
Fw=159.8/0.0475; Fd=240/0.0475
# Option 1: bolted bracket->femur band break (as Thermal asked)
Fz=0.926*Fd; M=Fz*0.148; s=0.080                 # joints spaced 80 mm along femur [EST layout]
couple=M/s
def lim_R(L,od,id_): A=math.pi*(od**2-id_**2)/4e6; return L/1e3/(6.7*A), A*1e6
RA,AA=lim_R(25,7,5.5); Rbolt=0.030/(6.7*14.2e-6)
per_bolt=1/(1/RA+1/(RA+Rbolt))
opt1={}
for n in (2,3,4,6):
    pre=4000; R=per_bolt/(2*n); slip=0.3*max(n*pre-couple,0); 
    opt1[f'{n} bolts/joint x2 joints (M5 Ti bolt, Ti limiter 7/5.5x25 @4 kN)']=dict(R_KpW=round(R,1),shear_per_joint_N=round(Fd/2),couple_N=round(couple),
        slip_capacity_N=round(slip),slip_ok=slip>Fd/2*1.25,separation_ok=n*pre>couple*1.25,limiter_stress_MPa=round(pre/AA,0))
# full-preload M6 steel with standard Ti limiters (load-capable) -> R
RAs,AAs=lim_R(10,10,6.4); Rbs=0.030/(40*20.1e-6); pb=1/(1/RAs+1/(RAs+Rbs))
opt1['6 bolts/joint x2, M6 10.9 @10 kN, Ti 10/6.4x10 (load-capable)']=dict(R_KpW=round(pb/12,1),slip_capacity_N=round(0.3*(6*10000-couple)),separation_ok=6*10000>couple*1.25)
# Option 2: PEI bushes on the knee trunnion pins (housing pivots +-6 deg on them)
d,L,t=9.0,12.0,2.0; Fs_w,Fs_d=Fw/2,Fd/2
brg_w=Fs_w/(d*L); brg_d=Fs_d/(d*L)
Rb=t/1e3/(0.12*math.pi*d*L*0.5e-6)                  # half-circumference contact
Rw=2/1e3/(0.12*0.30*math.pi*(13**2-9**2)/4*1e-6)      # 2 mm thrust washer, 30 % pads
R_side=1/(1/Rb+1/Rw); R2=R_side/2
mass2=2*(1.27e-3*math.pi*(13**2-9**2)/4*L + 1.27e-3*0.3*math.pi*(13**2-9**2)/4*2) + 2*2.7e-3*(math.pi*(18**2-13**2)/4*6)   # bushes+washers + cheek boss 20x10 extra [EST]
opt2=dict(bush=f'PEI ø{d:g}/13 x {L:g}, 2 mm wall, cheek boss ø18 x 12 (cheek 6 -> boss +6 mm)',bearing_walk_MPa=round(brg_w,1),bearing_design_MPa=round(brg_d,1),
          creep_ok=brg_w<=28,fault_ok=brg_d<=76,R_bush_side=round(Rb,1),R_washer_side=round(Rw,1),R_joint_KpW=round(R2,1),mass_knee_g=round(mass2,1),mass_robot_kg=round(2*mass2/1e3,4))
out=dict(basis=__doc__,F_walk_N=round(Fw),F_design_N=round(Fd),bracket_moment_Nm=round(M),option1_bolted=opt1,option2_trunnion_pin_PEI=opt2)
json.dump(out,open('results/r031/knee_trunnion_break_l61.json','w'),indent=1); print(json.dumps(out,indent=1)[:3000])
