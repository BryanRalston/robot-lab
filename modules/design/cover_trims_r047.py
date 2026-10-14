"""R-047 cover offsets, rev A36/R6 (RL Industrial Design). Item 1 now from a36_vents.json (Thermal A35 layout) replacing the blanket 30 % louvre assumption."""
import json,os
H=os.path.dirname(os.path.abspath(__file__)); L=lambda f:json.load(open(os.path.join(H,f)))
cs=L('cover_set_v5.json'); a36=L('a36_vents.json'); r6=L('pad_r6.json'); wr=L('wrist_trims.json')
row={r['panel'].split(',')[0].split(' (')[0]:r for r in cs['rows']}
thigh=row['thigh fairing']['area_m2_side']*2*1.5e-3*1200; foot=row['foot upper shell']['area_m2_side']*2*1.5e-3*1200
items=[
 dict(item='P-026 vents to A35 (thigh hip+knee inlets, knee-cap louvres, fin bulge +12 mm, skirt hem exhaust)',kg=a36['pair_kg']['total'],evidence='a36_vents.json: thigh %.3f, knee cap %.3f, skirt %+.3f'%(a36['pair_kg']['thigh'],a36['pair_kg']['knee_cap'],a36['pair_kg']['hip_skirt'])),
 dict(item='PC 1.2 mm avg (min 0.9) on thigh outboard + foot top',kg=round(-(thigh/2+foot)*0.2,3),evidence='calc (thigh outboard %.3f + foot %.3f) x 0.3/1.5; ribs on thigh outboard; dent check A15 open'%(thigh/2,foot)),
 dict(item='hip-skirt rim strips -> printed PA12 1.2 mm',kg=-0.013,evidence='calc 0.040 x (1-1.01*1.2/(1.20*1.5))'),
 dict(item='shoulder pad R6 vs R-060 booked 0.127',kg=r6['delta_vs_booked'],evidence='pad_r6.json'),
]
tot=round(sum(i['kg'] for i in items),3)
out=dict(items=items,total_kg=tot,total_half_credit_kg=round(tot/2,3),booked_R059_half=-0.117,shortfall_vs_booked_half=round(tot/2+0.117,3),
 wrist_trims_available_pair=wr['trim_pair'],shin_addback_option=dict(PC=0.300,PC_louvred=0.227,CF=0.260,CF_louvred=0.198,preferred='CF louvred (R-054)'))
json.dump(out,open(os.path.join(H,'cover_trims_r047.json'),'w'),indent=1)
for i in items: print(i['kg'],i['item'])
print(tot,tot/2,out['shortfall_vs_booked_half'])
