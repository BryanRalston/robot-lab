"""P-052 removable sternum plate (R-088). ID cover mass only; 7075 land+rib is Torso."""
import json,os
H=os.path.dirname(os.path.abspath(__file__))
RHO=1.20; T=0.15
face=12*12*T*RHO
blend=(15*15-12*12)*T*RHO + 0.5*(4*12*2.2*T*RHO)
fast=4*2.0
kg=(face+blend+fast)/1000
d=dict(P='P-052',ruling='R-088',kg=round(kg,3),
 items_g=dict(face_120x120=round(face,2),blend_15mm=round(blend,2),captive_x4=round(fast,2)),
 geometry='120x120 mm, 37 mm proud (x~+0.147), 15 mm blend, 3 mm gap to pad',
 torso_backing_not_included_kg=0.030)
json.dump(d,open(os.path.join(H,'sternum_plate.json'),'w'),indent=1)
print(d)
