"""Robot Lab job1 (a556d44) 'forearm-roll' torque check -> results/FOREARM_ROLL_TORQUE.{md,json}.
Sources: hd_csf_csg_catalog.txt Table 3 (CSG ratings), Table 6 (CSG ratcheting), Table 8 (OD A, length B),
component weight row (l.1101); hd_shg_2uh_engineering.pdf Tables 13.2/15.1 (SHG); iko_crb_catalog.txt l.802-804;
job1 REPORT/results.json; RULINGS R-119/R-120/R-121; arms/R13_STANDOFF_7013.md."""
import json
# size: (OD A, length B, component mass kg); ratio: (repeated, momentary, ratchet)
CSG={25:(85,37.0,0.42,{50:(127,242,580),80:(178,332,880),100:(204,369,650),120:(217,395,610)}),
     32:(110,44.0,0.89,{50:(281,497,1200),80:(395,738,1800),100:(433,841,1300),120:(459,892,1200)}),
     40:(135,53.0,1.70,{50:(523,892,2300),80:(675,1270,3600),100:(738,1400,2700),120:(802,1530,2400)})}
SHG_2SO={25:1.31,32:2.9,40:5.1}   # SHG unit weights incl. output bearing (SHG-2SO), same TR/TM as CSG
FAULT=1.05
cases={'job1 R8B axial (Z-64, 6013)':566,'job1 R8B down (Z-64, 6013)':773,
       'R-120/R13 adopted (Z-20, 7013, 15 deg)':321,'R-120 mu0.15 sens.':239}
base=CSG[25]
rows=[]
for s,(od,L,m,rat) in CSG.items():
    for N,(rep,mom,rat_t) in rat.items():
        rows.append(dict(gear=f'CSG-{s}-{N}',OD=od,B=L,mass=m,rep=rep,mom=mom,ratchet=rat_t,
            d_mass_pair=round(2*(m-base[2]),2),d_OD=od-base[0],d_B=L-base[1],
            SF_773=round(mom/(773*FAULT),2),SF_566=round(mom/(566*FAULT),2),SF_321=round(mom/(321*FAULT),2)))
# bearing (s0, from job1 results.json and R-120/R13, IKO P0 = Fr + 2M/dp + 0.44Fa)
bearing={'CRBH 6013 A C0 24.3 kN, job1 Z-64':{'axial_e0':1.45,'axial_e10':1.29,'down_e0':2.63,'down_e10':2.09},
         'CRBH 7013 A C0 27.7 kN, R-120 Z-20':{'e0':2.31,'e5':2.16,'e10':2.04}}
out=dict(cases_Nm=cases,gears=rows,shg_2so_mass=SHG_2SO,bearing_s0=bearing,
         clutch_needed_below=round(369/FAULT,1))
json.dump(out,open('results/forearm_roll_torque.json','w'),indent=1)
for r in rows: print(r)
