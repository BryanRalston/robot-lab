import cadquery as cq, model, json, math, sys
model.build_upper(); model.build_leg(1); model.build_leg(-1)
P=model.PARTS
for p in P:
    v=p['solid'].val().Volume(); p['vol']=v
    p['m']=p['mass'] if p['mass'] is not None else v*model.MAT[p['mat']]
print(len(P),'parts; CAD mass %.1f kg'%sum(p['m'] for p in P))
