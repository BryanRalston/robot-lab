"""R-010 placeholder (Torso owns the pack): P45B binning yield and usable fraction at the 3.4 V/cell bus floor; runtime rerun.
Published 0.2C capacities (2.5 V cutoff): Mooch/BLF 2022 4477, 4488; ECF 2024 retest 4453, 4479; batterydesign.net C/5 4485, 4492 mAh.
Usable fraction to 3.4 V at ~0.42C (699 W / 72 V / 5P = 1.94 A/cell) [EST]: P45B datasheet/1C curves reach 3.4 V at ~91-93 % of the 2.5 V capacity;
cell IR 15 mOhm x 1.94 A = 29 mV sag and Wh-weighting (lost tail is at the lowest voltage) -> 0.91 central, 0.88 low, 0.93 high. Must be measured (bench G5)."""
import numpy as np, json, os
from math import erf, sqrt
H=os.path.dirname(os.path.abspath(__file__))
caps=np.array([4477,4488,4453,4479,4485,4492.]); mu,sd=caps.mean(),caps.std(ddof=1)
Phi=lambda z:0.5*(1+erf(z/sqrt(2)))
cases={'published n=6':(mu,sd),'lot spread x3 sd':(mu,3*sd),'conservative mean 4450 sd 50':(4450,50)}
yld={k:1-Phi((4400-m)/s) for k,(m,s) in cases.items()}
P={'1p0_half':699.0,'1p0_none':783.3,'1p2_half':841.6}
Wh_cell={'binned_min_4400':4.400*3.6,'published_mean':mu/1000*3.63}
run={}
for wk,wh in Wh_cell.items():
    for uf in (0.88,0.91,0.93):
        run[f'{wk}_uf{uf}']={k:round(100*wh*uf/p,3) for k,p in P.items()}
out=dict(caps_mAh=caps.tolist(),mean=mu,sd=sd,yield_ge_4400=yld,usable_fraction=dict(low=0.88,central=0.91,high=0.93),runtime_h=run)
json.dump(out,open(f'{H}/results/battery_bin.json','w'),indent=1); print(json.dumps(out,indent=1))
