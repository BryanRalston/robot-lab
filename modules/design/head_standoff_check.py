# P-161 standoff vs head first-contact, parametric in forward pitch theta (body frame x fwd, y up). Lowest point along floor normal hits first.
import numpy as np, json, math
v=np.array([list(map(float,l.split()[1:])) for l in open('cad/covers/head_shell.stl') if l.strip().startswith('vertex')])
cands={'chest_pad_face(x147,y1530)':[(147,1530)],
 'epaulette_E1(x125,y1680,15mm proud of cover)':[(125,1680)],
 'brow_bumper_B1(x115,y1800) on head':[(115,1800)]}
res=[]
for th in range(60,181,5):
  t=math.radians(th); h=lambda x,y: y*math.cos(t)-x*math.sin(t)  # height up (relative); lower=more negative
  hh=min(h(x,y) for x,y,z in v)
  row={'theta_deg':th}
  for k,p in cands.items(): row[k]=round(hh-min(h(x,y) for x,y in p),1)  # +ve: candidate lands first by that many mm
  res.append(row)
json.dump({'note':'margin mm = head lowest minus candidate lowest along floor normal; +ve = candidate first. Per-run orientation not in l3_headfirst_replay.json (v_world only).','rows':res},open('head_standoff_check.json','w'),indent=1)
for r in res: print(r)
