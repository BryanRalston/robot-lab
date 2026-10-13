"""v3 cable routing check. Every moving joint is crossed by a clock-spring wrap on a drum coaxial with the joint
(the actuator housing for rotary joints, a dedicated PA12 drum at knee/ankle). Rule: moving cable bend radius >= 10 x d (igus chainflex/CFROBOT guidance).
Cable diameters are [EST] for 48 V pair (2 x AWG16, ~2.6 mm each) + EtherCAT (~4.0 mm) routed side by side; the largest single cable governs."""
import model, json
model.build_upper(); model.build_leg(1); model.build_leg(-1)
D=model.ACT_DIM
rows=[]
def add(j,r,d,how): rows.append(dict(joint=j,d_mm=d,r_min_mm=round(r,1),r_req_mm=10*d,route=how))
for n,(od,L) in sorted(D.items()):
    if not n.startswith('R_'):
        d=4.0 if not any(k in n for k in ('neck','wrist')) else 3.0
        add(n.replace('L_',''),od/2+3,d,'clock-spring wrap on actuator housing (+3 mm liner)')
add('knee',45,4.0,'clock-spring wrap on Ø90 drum outboard of knee clevis')
add('ankle (pitch+roll)',35,3.0,'F/T sensor cable only (Ø3 [EST]) on Ø70 drum; actuators are shank-side')
add('finger tendons (wrist idler)',4,1.0,'Dyneema 1 mm over Ø8 idlers: D/d 8 (tendon rule in hand check, not cable rule)')
rows=[r for r in rows if 'tendon' not in r['joint']]
json.dump(dict(joints=rows,rule='bend radius >= 10 x cable OD (moving)',source='IGUS'),open('out/cables.json','w'),indent=1)
L=['# v3 cable routing','',"Rule: moving bend radius ≥ 10 × cable Ø (igus). Cable Ø [EST]: 4.0 mm (EtherCAT) on leg/arm/waist joints, 3.0 mm on neck/wrist.",'','| joint | route | cable Ø | r min | r req | result |','|---|---|---|---|---|---|']
for r in rows: L.append(f"| {r['joint']} | {r['route']} | {r['d_mm']} | {r['r_min_mm']} | {r['r_req_mm']} | {'PASS' if r['r_min_mm']>=r['r_req_mm'] else 'FAIL'} |")
open('out/cables.md','w').write('\n'.join(L)); print('\n'.join(L))
