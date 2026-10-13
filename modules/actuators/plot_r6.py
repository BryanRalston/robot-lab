"""R6 image: A8 GE 12 C life per scenario vs T9, A5 ankle RV12x4 stroke/L10, A9 JST-GH mass sources."""
import json, os, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H=os.path.dirname(os.path.abspath(__file__)); L=json.load(open(f'{H}/results/life_r6.json')); A8,A5=L['A8'],L['A5']
fig,ax=plt.subplots(1,3,figsize=(17,5)); sc=list(L['mix'])
ax[0].bar(sc+['mix'],[A8[s]['Gh'] for s in sc]+[A8['combined']['Gh']],color=['C0']*4+['C3']); ax[0].axhline(14600,color='k',ls='--',label='T9 14 600 h')
ax[0].axhline(A8['combined']['replacement_interval_h'],color='g',ls=':',label=f"replace every {A8['combined']['replacement_interval_h']} h"); ax[0].legend(); ax[0].set_ylabel('G_h, h')
ax[0].set_title(f"A8 SKF GE 12 C hip-body eye: G_h {A8['combined']['Gh']:.0f} h → wear part"); ax[0].tick_params(axis='x',labelsize=8)
st=A5['stroke']; ax[1].barh(['need min len','Lmin (CAD)'],[st['need_min_len'],st['Lmin']],color=['0.6','C2']); ax[1].set_xlim(240,265)
ax[1].set_title(f"A5 ankle 73 mm: stroke {st['stroke']} mm, margin {st['margin']} mm\nRV12x4 L10 {A5['L10_h']/1e3:.0f}k h (≫14.6k), C0a/Fpk {A5['static_C0a_over_Fmax']:.1f}")
v=[1.2,0.5,0.384,0.32]; ax[2].bar(['R4 [EST]','R5b calc','R6 TME\nsum','R6 GAM\nsum'],v,color=['0.6','C1','C2','C2']); [ax[2].text(i,x+0.02,f'{x:.3f} g',ha='center') for i,x in enumerate(v)]
ax[2].set_title('A9 JST-GH 4-pin pair mass (×80): published distributor weights'); ax[2].set_ylabel('g per mated pair')
out='/workspace/robot-lab/media/progress/2026-10-13_actuators_r6_life_jst.png'; fig.savefig(out,dpi=105,bbox_inches='tight'); print(out)
