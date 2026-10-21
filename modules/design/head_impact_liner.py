# P-161 head crush liner sizing (RL ID). Plateau-force model: F=sigma*A, stroke=0.7*t, E=F*stroke.
import json
m=1.104; g=9.81
runs=json.load(open('../controls/fall/l3_headfirst_replay.json'))
hv=[r['head'] for r in runs if r.get('first')=='head']
vmax=max(h['v_normal'] for h in hv); KEmax=max(h['upper_KE'] for h in hv)
E_head=0.5*m*vmax**2
mats={'LD29':(126e3,29),'EPP80':(700e3,80)}  # sigma@50% Pa (MATERIALS_DB static, no rate factor), kg/m3
rows=[]
for E in (10,20,1.5*E_head,30,40,1.5*KEmax):
  for G in (50,100,200):
    F=m*G*g; s=E/F
    for k,(sig,rho) in mats.items():
      A=F/sig; t=s/0.7; rows.append(dict(E_J=round(E,1),a_g=G,mat=k,F_N=round(F),A_cm2=round(A*1e4,1),t_mm=round(t*1e3,1),mass_g=round(A*t*rho*1e3,1)))
out=dict(m_eff_kg=m,v_normal_max=vmax,E_head_alone_J=round(E_head,1),E_gate_head_J=round(1.5*E_head,1),upper_KE_max_J=KEmax,E_gate_body_J=round(1.5*KEmax,1),table=rows)
json.dump(out,open('head_impact_liner.json','w'),indent=1)
for r in rows: print(r)
print({k:v for k,v in out.items() if k!='table'})
