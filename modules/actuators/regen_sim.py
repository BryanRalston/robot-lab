"""RL Actuators regen sim (round 3): steady-state walking power on the shared 20S DC bus, iron loss included (iron_loss.py).
Model in regen_core.py. Run: python3 regen_sim.py -> results/regen_sim.json (+ regen_sim_trace.npz for plots).
Credit cases per R-009: no regen; half credit = no_regen - 0.5 x modeled regen; full regen. Pass line 729 W (T7, 1620 Wh x 0.9 / 2 h)."""
import json, os, numpy as np, regen_core as rc
H=os.path.dirname(os.path.abspath(__file__)); G=os.path.join(H,'../legs/results')
OUT={}
for g in ['walk_1p2','walk_1p0','walk_0p8']:
    for tag,p in [('',{}),('_no_iron',dict(iron_x=0.0)),('_eod',dict(vcell=3.4,ir_x=1.5))]:
        o=rc.run(f'{G}/{g}.npz',p); half=o['P_noregen']-0.5*o['regen_W']
        r=dict(P_noregen=o['P_noregen'],P_half=half,P_full=o['P_regen'],regen_W=o['regen_W'],iron_W=o['iron_W'],brake_W=o['brake_W'],window_s=o['window_s'])
        for Wh in (1620,1550): r[f'h_{Wh}']={k:Wh*0.9/r[k] for k in ('P_noregen','P_half','P_full')}
        r['pass_729']={k:r[k]<=729.0 for k in ('P_noregen','P_half','P_full')}
        OUT[g+tag]=r
        if tag=='': np.savez_compressed(f'{H}/results/regen_sim_trace_{g}.npz',**o['trace'])
json.dump(OUT,open(f'{H}/results/regen_sim.json','w'),indent=1,default=float)
for k,r in OUT.items(): print(k,{a:round(r[a]) for a in ('P_noregen','P_half','P_full','regen_W','iron_W')},'h1620',{a:round(b,2) for a,b in r['h_1620'].items()},'h1550',{a:round(b,2) for a,b in r['h_1550'].items()})
