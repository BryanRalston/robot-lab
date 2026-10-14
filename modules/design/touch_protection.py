"""Thermal touch protection for cover outer skins (RL Industrial Design).
Origin of the +0.25 kg booking is electrical IP2X (R-076/R-079 SurLok+wire), owned by Torso/Electronics
(Electronics 7ff4cd7 inventoried 0.086 kg). This script sizes the SEPARATE thermal-touch fix for
cover skins that exceed ISO 13732-1 / IEC 62368 brief-contact plastic limits per Thermal R1_BUDGET.
"""
import json,os
H=os.path.dirname(os.path.abspath(__file__))
# Limits (cited class; Thermal R1_BUDGET.md: "touch limit ~48 C for plastics (ISO 13732-1 class, value not verified)")
# ISO 13732-1: burn threshold for plastics, short contact (~1 s) often ~60 C; for longer contact / consumer
# products IEC 62368-1 TS1 touchable plastic ~48 C is the common design target Thermal used.
LIMIT_C=48.0
LIMIT_SRC='Thermal R1_BUDGET.md (~48 C plastics, ISO 13732-1 class); IEC 62368-1 TS1-class brief touch used as design target'
# Thermal R1 cover outer skin at hip_pitch/knee, covered case, 35 C ambient: 53 C (FAIL by 5 K)
nodes=[
 dict(zone='hip_pitch cover outer skin',T_C=53,ambient_C=35,source='thermal/R1_BUDGET.md table §3',area_m2_side=0.025,sides=2,note='over hip housing / skirt zone'),
 dict(zone='knee cover outer skin (thigh fairing + cap)',T_C=53,ambient_C=35,source='thermal/R1_BUDGET.md table §3',area_m2_side=0.030,sides=2,note='P-022 + thigh over knee housing'),
]
# Strategy: (1) vents already A35 — keep; (2) 5 mm standoff ribs so outer skin sees lower cavity coupling;
# (3) thin low-e / insulating liner ONLY on hot zones still > LIMIT after vents+standoff.
# Standoff ribs: PC 1.5 strips, 5 mm tall, ~10% of hot area footprint as rib planform
PC=1.80; RIB_FRAC=0.10; RIB_H=0.005; RIB_T=0.0015
# Liner: 0.25 mm aerogel-blanket or 0.5 mm silicone foam, ~0.20 kg/m2 [EST] over remaining hot patch
LINER=0.20  # kg/m2
items=[]; tot=0
for n in nodes:
  hot=n['T_C']>LIMIT_C
  a=n['area_m2_side']*n['sides']
  # After A35 vents Thermal expects cover skin closer to OK at 25 C; at 35 C still +5 K over — apply standoff on full hot area
  rib_kg=a*RIB_FRAC*RIB_H/RIB_T*PC*RIB_T  # planform*thickness*rho... simplify: rib volume = planform_area * height * (t/spacing)
  # clearer: rib mass = (rib planform area) * thickness * density; planform = RIB_FRAC * a; use 1.5 mm thick ribs
  rib_kg=a*RIB_FRAC*0.0015*1200  # m2 * m * kg/m3
  # Assume standoff + existing vents drop skin by ~7 K [EST] -> within limit; liner only if not
  T_after_standoff=n['T_C']-7
  need_liner=T_after_standoff>LIMIT_C
  liner_a=a*0.5 if need_liner else 0.0  # half zone still hot [EST]
  liner_kg=liner_a*LINER
  kg=rib_kg+liner_kg
  tot+=kg
  items.append(dict(zone=n['zone'],T_C=n['T_C'],limit_C=LIMIT_C,margin_K=round(LIMIT_C-n['T_C'],1),
    area_m2=round(a,4),standoff_ribs_kg=round(rib_kg,4),T_after_standoff_EST=T_after_standoff,
    liner_m2=round(liner_a,4),liner_kg=round(liner_kg,4),total_kg=round(kg,4),
    source=n['source'],note=n['note']))
# Prefer vents-only path: if A35 already booked, incremental thermal-touch mass is ribs+liner only
out=dict(
 origin_of_plus_0p25=dict(booking_kg=0.25,breakdown='R-079: SurLok IP2X EST +0.21 + 16 mm2 main link +0.04',
  owners='Torso (connectors/shrouds) + Electronics (IP2X inventory); NOT Industrial Design covers',
  electronics_inventory_kg=0.086,electronics_commit='7ff4cd7',credit_vs_booking=-0.164,
  note='Electrical finger-safe IP2X is separate from thermal burn protection.'),
 thermal_limit=dict(C=LIMIT_C,citation=LIMIT_SRC),
 strategy='A35 vents first (already in cover set); 5 mm PC standoff ribs on hot outer skins; thin liner only if skin still >48 C [EST]',
 items=items,
 total_thermal_touch_kg=round(tot,3),
 vs_plus_0p25=dict(electrical_remaining_after_Electronics=0.086,thermal_ID_proposal=round(tot,3),combined=round(0.086+tot,3),delta_vs_0p25=round(0.086+tot-0.25,3)),
 needs_measurement=['cover outer skin thermocouple at hip/knee on G5 carry 35 C (Thermal R1 already asks)',
  'confirm ISO 13732-1 / IEC 62368 plastic touch threshold with Materials (48 C unverified)',
  'standoff delta-T (7 K) is [EST] — J-T1 or bench',
  'liner areal density citation if liner path needed'],
)
json.dump(out,open(os.path.join(H,'touch_protection.json'),'w'),indent=1)
print('thermal total',out['total_thermal_touch_kg'],'vs +0.25 combined',out['vs_plus_0p25'])
for i in items: print(i['zone'], i['total_kg'], 'liner', i['liner_kg'])
