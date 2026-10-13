"""R5b progress image: ankle 73 mm margins, thigh clamp review, mass waterfall (linkage, harness flex) vs 66.5."""
import json, os, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); c=json.load(open(f'{H}/results/clamp_review.json')); r=json.load(open(f'{H}/results/mass_rollup_r5b.json'))
s=json.load(open(f'{H}/results/sizing.json'))['sel']['ankle_pitch']
fig,ax=plt.subplots(1,3,figsize=(17,5))
lab=['T/need\n@66.5 (314)','carry 1.0\n@66.5','rpm / 7600\n(95 % line)']; v=[s['T_out']/314,s['T_out']/(239.13*66.5/65),s['motor_rpm']/7600]
ax[0].bar(lab,v,color=['C2','C2','C1']); ax[0].axhline(1,color='k',ls='--'); ax[0].axhline(1.2,color='r',ls=':',label='carry 1.2'); [ax[0].text(i,x+0.02,f'{x:.3f}',ha='center') for i,x in enumerate(v)]
ax[0].set_title(f"ankle_pitch 73 mm: T {s['T_out']:.0f} N·m, ΔT_cad {s['dT_cad']:.0f} K"); ax[0].legend()
lab=['friction only\ntube crush','bond + clamp\nfatigue','eye GE 12 E\ns0/3','eye pin\nbending','clamp fatigue\n(Legs FEA max)']
v=[c['friction_only']['SF_tube_yield_with_scatter'],c['bonded_plus_light_clamp']['SF_fatigue'],c['eye']['s0']/3,c['pin']['SF'],c['clamp_fatigue']['SF_max']]
ax[1].bar(lab,v,color=['r' if x<1.5 else 'g' for x in v]); ax[1].axhline(1.5,color='k',ls='--',label='SF 1.5'); ax[1].tick_params(axis='x',labelsize=8); ax[1].legend(); [ax[1].text(i,x+0.05,f'{x:.2f}',ha='center') for i,x in enumerate(v)]
ax[1].set_title('Legs thigh clamp @ 2×4542 N: friction-only FAILS, bonded OK')
st=[('R-018\ncredible',r['base_R018_credible'],None),('linkage\n(eyes, 73 mm)',r['linkage_delta'],1),('harness\n(flex, O21)',r['harness_delta'],1),('R5b',r['robot'],None),('Legs A1\n(prov.)',r['legs_A1_pending'],1),('if A1',r['robot_if_A1'],None)]
lv=0
for i,(k,x,d) in enumerate(st):
    if d is None: ax[2].bar(i,x,color='0.5'); lv=x; ax[2].text(i,x+0.03,f'{x:.2f}',ha='center')
    else: ax[2].bar(i,x,bottom=lv,color='g' if x<0 else 'r'); lv+=x; ax[2].text(i,lv+0.03,f'{x:+.3f}',ha='center')
ax[2].axhline(66.5,color='r',ls='--',label='66.5 hard'); ax[2].set_ylim(65.8,67.4); ax[2].set_xticks(range(len(st))); ax[2].set_xticklabels([k for k,_,_ in st],fontsize=8); ax[2].legend(); ax[2].set_title('robot mass, kg')
out='/workspace/robot-lab/media/progress/2026-10-13_actuators_r5b_ankle_clamp_mass.png'; fig.savefig(out,dpi=105,bbox_inches='tight'); print(out)
