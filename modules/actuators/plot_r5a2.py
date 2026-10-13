"""R5 A2 progress image: routed harness lengths per run + harness mass R4 model / R-018 credit / R5 datasheet model."""
import json, os, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); h=json.load(open(f'{H}/results/harness.json')); m=json.load(open(f'{H}/results/mass_rollup_r5a2.json'))
rows=[r for r in h['rows'] if 'route_m' in r]
fig,ax=plt.subplots(1,2,figsize=(16,6),gridspec_kw=dict(width_ratios=[1.4,1]))
nm=[r['item'][:34] for r in rows]; ax[0].barh(nm,[r['route_m'] for r in rows],label='routed straight ×1.15'); ax[0].barh(nm,[r['loops_m'] for r in rows],left=[r['route_m'] for r in rows],label='clock-spring loops + pigtails',color='C1')
ax[0].invert_yaxis(); ax[0].tick_params(axis='y',labelsize=7); ax[0].set_xlabel('length per run, m (v3 CAD coordinates)'); ax[0].legend(); ax[0].set_title('O16 routed harness runs')
lab=['R4 model\n[EST]','R-018\ncredited','R5 model\n(datasheet+routed)','R5 under strict\nR-018 EST rule']; val=[0.821,1.344,h['total_kg'],m['harness_strict_R018']]
b=ax[1].bar(lab,val,color=['0.6','C3','C2','C1']); [ax[1].text(i,v+0.02,f'{v:.3f}',ha='center') for i,v in enumerate(val)]
ax[1].axhline(1.46,ls='--',color='k',label='M3 target 1.46'); ax[1].legend(); ax[1].set_ylabel('harness kg')
ax[1].set_title(f"credit {m['claim_credit']:+.3f} kg → robot {m['robot_claim']:.2f} kg vs 66.5 (strict {m['robot_strict']:.2f})")
out='/workspace/robot-lab/media/progress/2026-10-13_actuators_r5a2_harness.png'; fig.savefig(out,dpi=110,bbox_inches='tight'); print(out)
