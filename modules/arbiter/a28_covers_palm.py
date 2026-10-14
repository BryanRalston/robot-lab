"""R-027: cover-set material trade (replaces PA12 MJF covers M3 line) + PA12 palm -> machined. Run from repo root.
Same coverage basis as R-021: 1.285 m2 limb convex-hull area (v3 CAD), 50 % coverage [EST], EPP pads 0.360 [EST] carried.
Credit rule (R-021): saving vs v3 1.86 credited x0.5 (rests on [EST] wall/coverage); a net addition vs 1.86 counts x1.0."""
import json
A=1.285; F=0.50; EPP=0.360; V3=1.86; PA12_CRED=1.622; PA12_PAPER=1.384
# name, density kg/m3 (source), wall m (source), fasteners/inserts kg [EST], fall dS (fraction, [EST]), cost USD [EST]
OPT=[
 ('CF prepreg 2x2 twill, 4 plies x 0.25 mm on machined Al moulds',1550,'1.51-1.54 g/cc laminate, Toray 3900 TDS (toraycma.com/wp-content/uploads/3900-Prepreg-System.pdf); 1.55 +-0.05 twill sheet TDS (cnccarbonfiber.com); conservative vs Easy Composites XC110 1.152',
  1.0e-3,'4 x 0.25 mm consolidated ply (Easy Composites XC110/XC130 210 g 2x2 twill); 3 plies (0.75 mm) judged too thin for edge impact [EST]',0.070,0.00,3800,'brittle edge cracking on impact; panels replaceable'),
 ('Thermoformed PC sheet 1.5 mm (vacuum-formed on machined tooling-board/Al moulds)',1200,'1.20 g/cc ASTM D792, Palram PALSUN TDS; SABIC LEXAN 1.20 ISO 1183',
  1.5e-3,'heavy-gauge thermoforming 1.5 mm+ (Select Plastics ABS thermoforming guide); draw <=3:1 (LEXAN forming guide)',0.050,+0.05,1300,'ductile; 130 J falling-weight E50 at 3 mm (PALSUN TDS); dents rather than cracks'),
 ('Formed 5052 Al sheet 0.8 mm',2680,'5052 2.68 g/cc (handbook)',0.8e-3,'0.8 mm formed sheet [EST]; Protolabs machined min nominal 1.02 mm would be heavier',0.050,-0.05,2400,'permanent dents on every fall; sharp edges'),
 ('Injection-moulded PC/ABS 1.5 mm',1150,'PC/ABS ~1.15 g/cc [EST, typical grades]',1.5e-3,'1.5 mm typical moulded wall [EST]',0.050,+0.03,24000,'tough; but ~8 hard tools [EST $3k each] for qty 1-2 robots'),
]
res=[]
for n,rho,rs,t,ts,fa,dfall,cost,fn in OPT:
    shell=A*F*t*rho; paper=shell+fa+EPP
    cred=paper if paper>=V3 else V3-0.5*(V3-paper)
    dcred=cred-PA12_CRED
    s_mass=-(dcred/66.5)*0.15; s_fall=dfall*0.13*0.5   # TARGETS weights T2 0.15, T8 0.13; [EST] evidence x0.5
    res.append(dict(option=n,density_kg_m3=rho,density_src=rs,wall_mm=t*1e3,wall_src=ts,shell_kg=round(shell,3),fasteners_kg=fa,epp_kg=EPP,
        paper_kg=round(paper,3),credited_kg=round(cred,3),d_paper_vs_PA12=round(paper-PA12_PAPER,3),d_cred_vs_PA12=round(dcred,3),
        fall_note=fn,cost_usd_EST=cost,score=round(s_mass+s_fall,5)))
res.sort(key=lambda r:-r['score'])
# V5 plan extra coverage (CF shin/thigh fairings, skirt): 75 % coverage at CF 1.0 mm, for reference only
cf75=A*0.75*1.0e-3*1550+0.070+EPP
# palm: model_v4 palm envelope box 32 x 86 x 90 mm ('7075 skeleton + PA12', modules/model/model_v4.py l.261).
# The 7075 skeleton is unchanged; the PA12 skin (wall 1.5 mm, R-021 PA12 basis) becomes a machined 7075 skin at the same 1.5 mm
# (Protolabs: >=0.51 mm features, >=1.02 mm nominal; 1.5 mm kept for 3:1 wall height and grip loads [EST]).
dx,dy,dz=32e-3,86e-3,90e-3; S=2*(dx*dy+dx*dz+dy*dz); t=1.5e-3
pa=S*t*1010; al=S*t*2810; al6061=S*t*2700
palm=dict(envelope_mm=[32,86,90],skin_area_m2=round(S,5),wall_mm=1.5,pa12_kg_per_hand=round(pa,4),al7075_kg_per_hand=round(al,4),al6061_kg_per_hand=round(al6061,4),
  delta_per_hand=round(al-pa,4),delta_both=round(2*(al-pa),3),basis='skin = envelope surface x wall (upper bound: no openings); [EST] geometry, x1.0 as an addition')
out=dict(ruling='R-027',coverage_basis=dict(area_m2=A,fraction=F,epp_kg=EPP),options=res,winner=res[0]['option'],
  cf_at_75pct_coverage_paper=round(cf75,3),palm=palm)
json.dump(out,open('modules/arbiter/a28_covers_palm.json','w'),indent=1); print(json.dumps(out,indent=1))
