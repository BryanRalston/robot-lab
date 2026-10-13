"""Round-3 sensitivity sweep of the shared-bus regen model (R-009 condition: >= 77 % of modeled credit at the worst corner).
Usage: python3 regen_sweep.py [gait.npz]   (default: Legs gait-ID walk_1p2; pass Legs' forward-sim trace in regen_core format (b) when it walks)
Writes results/regen_sweep_<gait>.json. Retention = regen_W(corner) / regen_W(nominal); also the absolute check P_regen <= 729 W."""
import sys, os, json, itertools, numpy as np, regen_core as rc
H=os.path.dirname(os.path.abspath(__file__))
path=sys.argv[1] if len(sys.argv)>1 else os.path.join(H,'../legs/results/walk_1p2.npz'); tag=os.path.splitext(os.path.basename(path))[0]
GRID=dict(drive_x=[0.5,1,2], iron_x=[0.5,1,2], eta_back_x=[0.85,1,1.1], rcu_hot=[1.0,1.4,1.6], charge_A=[0,10,30],
          batt=[(3.4,1.5),(3.6,1.0),(4.0,1.0)], torque_x=[1.0,1.03,1.06], time_x=[0.9,1.0,1.1])
nom=rc.run(path); R0=nom['regen_W']; rows=[]
for combo in itertools.product(*GRID.values()):
    p=dict(zip(GRID,combo)); vc,ir=p.pop('batt'); p.update(vcell=vc,ir_x=ir)
    o=rc.run(path,p); rows.append(dict(p=p,P_noregen=o['P_noregen'],P_regen=o['P_regen'],regen_W=o['regen_W'],brake_W=o['brake_W'],retention=o['regen_W']/R0))
ret=np.array([r['retention'] for r in rows]); Pr=np.array([r['P_regen'] for r in rows])
worst=rows[int(ret.argmin())]; worstP=rows[int(Pr.argmax())]
# one-at-a-time ranges (each factor alone at its extremes, others nominal)
oat={}
for k,vals in GRID.items():
    oat[k]=[]
    for v in vals:
        p={} 
        if k=='batt': p.update(vcell=v[0],ir_x=v[1])
        else: p[k]=v
        o=rc.run(path,p); oat[k].append(dict(value=v,retention=o['regen_W']/R0,P_regen=o['P_regen'],P_noregen=o['P_noregen']))
# R-009-relevant envelope: corners with fixed walking conditions (no mass/timing change) isolate model uncertainty
model_only=[r for r in rows if r['p']['torque_x']==1.0 and r['p']['time_x']==1.0]
OUT=dict(gait=path,nominal={k:v for k,v in nom.items() if k!='trace'},n_corners=len(rows),grid={k:[list(x) if isinstance(x,tuple) else x for x in v] for k,v in GRID.items()},
    retention=dict(min=float(ret.min()),p05=float(np.percentile(ret,5)),median=float(np.median(ret)),max=float(ret.max()),
                   min_model_only=float(min(r['retention'] for r in model_only))),
    worst_retention_corner=worst,worst_power_corner=worstP,frac_corners_P_regen_le_729=float(np.mean(Pr<=729.0)),
    frac_model_only_le_729=float(np.mean([r['P_regen']<=729.0 for r in model_only])),one_at_a_time=oat)
json.dump(OUT,open(f'{H}/results/regen_sweep_{tag}.json','w'),indent=1,default=float)
print(json.dumps({k:OUT[k] for k in ['nominal','retention','frac_corners_P_regen_le_729','frac_model_only_le_729']},indent=1,default=float))
print('worst retention',worst); print('worst P',worstP)
for k,v in oat.items(): print(k,[(x['value'],round(x['retention'],3),round(x['P_regen'])) for x in v])
