"""R-069 mass-down pass: NEW cover trims beyond R-047 (RL Industrial Design).
Baseline = cover_set_v5.json + R-047 items + a36_vents.json.
Updates: R-075/R-079/R-080/R-081, Materials f14c29c (silpoly 71 g/m2, PA12 knee replaces B), Legs L54/R-081 C2.
All areas [EST] (measured: false)."""
import json,os
H=os.path.dirname(os.path.abspath(__file__)); L=lambda f:json.load(open(os.path.join(H,f)))
cs=L('cover_set_v5.json'); a36=L('a36_vents.json')
row={r['panel'].split(',')[0].split(' (')[0]:r for r in cs['rows']}
PC15,PC12,CF10,PA12=1.80,1.44,1.55,1.01*1.5   # PA12 1.5 mm areal kg/m2 (rho 1.01)
SILP=0.071   # Materials COVER_TRIMS_REVIEW / RBTR_SILPOLY finished ~71 g/m2
thigh=row['thigh fairing']['area_m2_side']*2; knee=row['knee cap']['area_m2_side']*2; foot=row['foot upper shell']['area_m2_side']*2
skirt=row['hip skirt']['area_m2_side']*2; boot=row['ankle boot']['area_m2_side']*2
front_kg=thigh/2*PC15+a36['pair_kg']['thigh']
knee_kg=knee*PC15+a36['pair_kg']['knee_cap']
foot_kg=foot*PC12                                    # already 1.2 mm (R-047 item 2)
# Boot extension over instep rod ends (L54/R-081 C2 condition 2): ~250 cm2/side [EST] silpoly
boot_ext_m2=2*0.025
I=[]
def add(n,kg,calc,risk,rec,status=''):
    d=dict(item=n,kg=round(kg,3),calc=calc,risk=risk,recommend=rec)
    if status: d['status']=status
    I.append(d)
add('A  CF 1.0 mm (4x0.25 twill) on the louvred thigh FRONT half (outboard stays PC 1.2)',-front_kg*(1-CF10/PC15),
 f'front skin {front_kg:.3f} x (1-1.55/1.80); R-027; Materials slot-edge rules','edge cracking -> radiused/hemmed sealed slots','YES','R-075 booked half credit')
add('B  knee cap PC 1.5 -> 1.2 mm (DROPPED)',-knee_kg*0.2,f'{knee_kg:.3f} x 0.3/1.5','Materials: FAIL dent at ~0.7 mm post-form corners','NO — dropped (Materials f14c29c / R-080)','dropped; replaced by B2')
add('B2 PA12 1.5 mm knee cap (replaces B; either-or)',-0.016,
 'Materials COVER_TRIMS_REVIEW: 0.098 x (1-1.01/1.20) = -0.016; either-or with B','kneel-fall test gate (G5)','YES (test-gated)','R-080: counts after kneel-fall')
add('C1 foot top shell 1.2 -> 1.0 mm (SUPERSEDED by C2)',-(foot_kg)*(0.2/1.2),f'{foot_kg:.3f} x 0.2/1.2','superseded','NO — superseded by C2 (R-081)','superseded')
add('C2 foot top shell DELETED + boot instep extension',-(foot_kg)+boot_ext_m2*SILP,
 f'shell skin -{foot_kg:.3f} (4 M3 inserts KEPT for boot re-anchor) + boot ext {boot_ext_m2:.3f} m2 x {SILP} silpoly = +{boot_ext_m2*SILP:.3f}; net {-(foot_kg)+boot_ext_m2*SILP:.3f}',
 'L54/R-081: re-anchor boot hem through 4 inserts; extend boot over instep rod ends; Legs R2 edges on outrigger/lugs; sole pad separate (Legs/Materials)','YES','R-081 booked -0.13 est half -> -0.065')
add('D  ankle boot: TPU 210D 0.30 -> silicone 70D ripstop 0.071 kg/m2',-boot*(0.30-SILP),
 f'{boot:.3f} m2 x {0.30-SILP:.3f} kg/m2 (Materials cited ~71 g/m2)','wear part: replaceable; inspect at 4,250 h rod-end service','YES','R-075 booked; R-080 silpoly delta')
add('E  hip skirt fabric 0.30 -> 0.071 kg/m2; PC rim + hem ring kept',-(skirt-2*0.0070)*(0.30-SILP),
 f'({skirt:.3f} - 2x70 cm2 exhaust, Thermal a8811f5) m2 x {0.30-SILP:.3f}; was -0.045 at 0.10 assumed','flutter/pinch; hem ring kept','YES','R-079 E updated; R-080 silpoly')
add('F1 waist bellows P-024 TPE -> thin TPU-film convoluted boot 0.3 kg/m2',-0.0848*(0.60-0.30),'0.0848 m2 x 0.30 kg/m2 [EST]','fatigue; cycle test gate','YES (test-gated)','R-075: counts after cycle test')
add('F2 waist bellows P-024 DELETED',-0.055,'cover_set_v5.json P-024','ingress/pinch','NO — rejected (R-075)','rejected')
add('G  fasteners: 2 of 4 bonded inserts per rigid panel -> moulded snap hooks',-8*2*0.002,'8 panels x 2 x 2 g [EST] (C2 drops M5-M6: if 6 rigid panels left, -0.024)','retention/fall test gate','YES (test-gated)','R-075: counts after retention/fall')
# Booked / gated sets
booked=[i for i in I if i.get('status','').startswith('R-075 booked') or i.get('status','').startswith('R-081') or (i['item'].startswith('D ') or i['item'].startswith('E ') or i['item'].startswith('A '))]
# cleaner: A,D,E booked; C2 booked; B2/F1/G gated
A=next(i for i in I if i['item'].startswith('A '))
D=next(i for i in I if i['item'].startswith('D '))
E=next(i for i in I if i['item'].startswith('E '))
C2=next(i for i in I if i['item'].startswith('C2'))
B2=next(i for i in I if i['item'].startswith('B2'))
F1=next(i for i in I if i['item'].startswith('F1'))
G=next(i for i in I if i['item'].startswith('G '))
booked_full=A['kg']+D['kg']+E['kg']+C2['kg']
gated_full=B2['kg']+F1['kg']+G['kg']
out=dict(items=I,
 silpoly_kg_m2=SILP,
 pad_R8_option_B=dict(kg_pair=0.1162,booked_R073=0.092,delta_vs_booking=0.024,remaining_credit_vs_R073_kg=-0.0044,note='Materials f14c29c: -4.4 g remaining vs R-073; R-079 adopts B at +0.024 full'),
 booked_ADE_C2_full_kg=round(booked_full,3),
 booked_half_credit_kg=round(booked_full/2,3),
 test_gated_B2_F1_G_full_kg=round(gated_full,3),
 C2_net=dict(shell_skin_deleted_kg=round(-foot_kg,3),inserts_kept=4,boot_extension_m2=boot_ext_m2,boot_extension_kg=round(boot_ext_m2*SILP,3),net_full_kg=C2['kg'],arbiter_R081_half_credit=-0.065),
 notes=['F2 rejected R-075','B dropped Materials/R-080; B2 PA12 either-or','C1 superseded by C2 R-081','sole pad + toe/heel bumpers required separately (R-081, Legs/Materials)'])
json.dump(out,open(os.path.join(H,'cover_trims_r069.json'),'w'),indent=1)
for i in I: print(f"{i['kg']:+.3f}  {i.get('status','')[:40]:40s}  {i['item'][:70]}")
print('booked full/half',out['booked_ADE_C2_full_kg'],out['booked_half_credit_kg'],'gated',out['test_gated_B2_F1_G_full_kg'])
print('C2 net',out['C2_net'])
