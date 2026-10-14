"""R-069 mass-down pass: NEW cover trims beyond R-047 (RL Industrial Design). Baseline = cover_set_v5.json + R-047 items (A35 vents, 1.2 mm outboard/foot) + a36_vents.json. All areas [EST] (measured: false)."""
import json,os
H=os.path.dirname(os.path.abspath(__file__)); L=lambda f:json.load(open(os.path.join(H,f)))
cs=L('cover_set_v5.json'); a36=L('a36_vents.json')
row={r['panel'].split(',')[0].split(' (')[0]:r for r in cs['rows']}
PC15,PC12,CF10=1.80,1.44,1.55
thigh=row['thigh fairing']['area_m2_side']*2; knee=row['knee cap']['area_m2_side']*2; foot=row['foot upper shell']['area_m2_side']*2
skirt=row['hip skirt']['area_m2_side']*2; boot=row['ankle boot']['area_m2_side']*2
front_kg=thigh/2*PC15+a36['pair_kg']['thigh']       # front half after vents (vents mostly front)
knee_kg=knee*PC15+a36['pair_kg']['knee_cap']
foot_kg=foot*PC12                                    # already 1.2 mm (R-047 item 2)
I=[]
def add(n,kg,calc,risk,rec): I.append(dict(item=n,kg=round(kg,3),calc=calc,risk=risk,recommend=rec))
add('A  CF 1.0 mm (4x0.25 twill) on the louvred thigh FRONT half (outboard stays PC 1.2: CF 1.55 kg/m2 > PC 1.2 1.44)',-front_kg*(1-CF10/PC15),
 f'front skin {front_kg:.3f} x (1-1.55/1.80); R-027 densities; R-054 prefers CF','cost ~+$0.8k Al tools (2 L/R fronts); edge cracking on impact (R-027) -> radiused/hemmed slot edges','YES')
add('B  knee cap PC 1.5 -> 1.2 mm',-knee_kg*0.2,f'{knee_kg:.3f} x 0.3/1.5','2.5:1 draw -> post-form min ~0.7 mm at corners; knee is a fall-contact zone (dent/crack); EPP pad behind it?','NO (fall zone) unless Materials dent check passes')
add('C1 foot top shell 1.2 -> 1.0 mm',-(foot_kg)*(0.2/1.2),f'{foot_kg:.3f} x 0.2/1.2','low draw (<=1.5:1) OK; foot is a kick/stub zone: dents; EPP-backed','YES (with dent check)')
add('C2 foot top shell DELETED (alternative to C1)',-(foot_kg+2*2*0.004),f'{foot_kg:.3f} + 4 inserts','instep lugs/outrigger exposed (snag, debris, looks); Legs to accept; mould M5-M6 deleted (-$2.3k)','OPTION for the Arbiter')
add('D  ankle boot: TPU-coated 210D nylon 0.30 -> silicone-coated 70D ripstop ~0.10 kg/m2',-boot*(0.30-0.10),f'{boot:.3f} m2 x 0.20 kg/m2 [EST: needs supplier TDS]','abrasion at the ankle; becomes a wear part (inspect at the 4,250 h rod-end service)','YES')
add('E  hip skirt fabric 0.30 -> 0.10 kg/m2 (same ripstop); PC rim + hem ring kept',-(skirt-2*0.0070)*(0.30-0.10),f'({skirt:.3f} - 2 x 70 cm2 exhaust open, Thermal a8811f5) m2 x 0.20 kg/m2 [EST]','flutter/pinch at the hip; the exhaust slots band needs the hem ring (kept)','YES')
add('F1 waist bellows P-024 TPE -> thin TPU-film convoluted boot 0.3 kg/m2',-0.0848*(0.60-0.30),'0.0848 m2 x 0.30 kg/m2 [EST]','fatigue at waist yaw/pitch; needs a cycle test','YES')
add('F2 waist bellows P-024 DELETED (alternative to F1)',-0.055,'cover_set_v5.json P-024','waist yoke/pinch points exposed (Optimus look lost); finger-pinch hazard at waist pitch','OPTION')
add('G  fasteners: 2 of 4 bonded inserts per rigid panel -> moulded snap hooks (8 panels)',-8*2*0.002,'8 panels x 2 x 2 g [EST]','retention after a fall; panels may pop off (that is acceptable as a fuse, but lost parts)','YES')
rec=[i for i in I if i['recommend'].startswith('YES')]
out=dict(items=I,recommended_total_kg=round(sum(i['kg'] for i in rec),3),recommended_half_credit_kg=round(sum(i['kg'] for i in rec)/2,3),
 options_extra=dict(C2_instead_of_C1=round(I[3]['kg']-I[2]['kg'],3),F2_instead_of_F1=round(I[7]['kg']-I[6]['kg'],3),B_if_dent_check_passes=I[1]['kg']))
json.dump(out,open(os.path.join(H,'cover_trims_r069.json'),'w'),indent=1)
for i in I: print(i['kg'],i['recommend'],i['item'][:60])
print(out['recommended_total_kg'],out['recommended_half_credit_kg'],out['options_extra'])
