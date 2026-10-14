"""R-099 sole mass-down study (hand model, [EST] where marked). Foot box 240x100 (x -60..180, y +-50), sole CoP window = whole box.
Gumlite 0.55 g/cm3, 47 Shore A (Vibram tech data); E from Gent: 2.2 MPa [EST]. PU 60A 1.24 g/cm3 [EST]. Load 1.31 BW, 65.8 kg."""
import json, math
RHO_G=0.55e-3; RHO_PU=1.24e-3; E=2.2; F=1.31*65.8*9.81
def opt(name,area,t,bump_mm3=0,lip=0,src=''):
    m=area*t*RHO_G/1e3 + bump_mm3*RHO_PU/1e3 + lip*RHO_G/1e3
    edge_strain=F/(10*100)/E; comp=edge_strain*t                       # 10 mm edge strip carrying 1.31 BW
    flat_p=F/area; Ecap=0.5*E*1e6*0.5**2*(20*100*1e-6)*(t*1e-3)          # 20x100 edge strip to 50 % strain, J
    life=max(t-1.5,0)/4.5                                                 # usable thickness vs 6 mm baseline [EST]
    return dict(option=name,t_mm=t,area_mm2=area,mass_foot_kg=round(m,4),mass_robot_kg=round(2*m,4),edge_comp_mm=round(comp,2),
                edge_strain=round(edge_strain,2),flat_stance_MPa=round(flat_p,3),edge_energy_to_50pct_J=round(Ecap,2),rel_wear_life=round(life,2),source=src)
B4=4*30*15*6.35; LIP=2*100*8   # 4 PU corner pads; toe+heel end-lip wrap 8 mm high (x t)
rows=[opt('A full 6 mm + 4 PU corners (L57 baseline)',24000,6,B4,src='Vibram Acquagum 6 mm Gumlite SKU 35002690B / #8529 12 iron 6.4 mm'),
      opt('B full 4 mm skived Gumlite + lips, no bumpers',24000,4,0,LIP*4,'skived from #8529/Acquagum [EST process]'),
      opt('C full 3 mm skived Gumlite + lips, no bumpers',24000,3,0,LIP*3,'skived [EST process]'),
      opt('D 6 mm perimeter frame 20 mm + lips, no bumpers',24000-200*60,6,0,LIP*6,'Acquagum/#8529 6-6.4 mm catalogue'),
      opt('E 4 mm perimeter frame 20 mm + lips, no bumpers',24000-200*60,4,0,LIP*4,'skived [EST process]'),
      opt('F 6 mm frame + 4 PU corners',24000-200*60,6,B4,src='catalogue')]
json.dump(dict(basis=__doc__,touchdown_EST='edge touchdown 0.5 m/s x 10 kg effective = 1.25 J [EST]',rows=rows),open('results/r081/sole_massdown_r099.json','w'),indent=1)
for r in rows: print(r['option'],r['mass_foot_kg'],r['mass_robot_kg'],r['edge_comp_mm'],r['flat_stance_MPa'],r['edge_energy_to_50pct_J'],r['rel_wear_life'])
