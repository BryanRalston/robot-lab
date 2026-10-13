"""R-022: OFFICIAL whole-robot mass rollup (single source of truth). Run from repo root.
Chain: R-020 (66.891 credible / 65.75 paper) -> R-021 A3 (a3_size.json) -> R-022 deltas (Actuators 71f3c3e, Legs 2bf99d5).
Explicit lines are the ones with an evidence trail in RULINGS; 'all other lines' is DERIVED as total minus explicit lines
(v3 rollup basis + R-015..R-020 actuator/linkage credits; not yet itemised here -> action A12)."""
import json
a3=json.load(open('modules/arbiter/a3_size.json')); h=json.load(open('modules/actuators/results/harness.json'))
lk=json.load(open('modules/actuators/results/mass_rollup_r6.json'))
hip=json.load(open('modules/legs/results/r5/hip_stop.json'))
R020_CRED, R020_PAPER = 66.891, 65.75
lines=[  # name, paper, credible, evidence, credit rule, source
 ('leg structure M2 (Legs r5 design)',4.862,5.418,'scikit-fem foot+clamp FEA; tubes/tongue/clamp sleeve hand checks','reductions on hand checks x0.5, FEA x1.0, additions x1.0 (R-019/R-020)','R-020 §4-5'),
 ('leg structure r6 add: hip-stop bumper + collar bolts over 0.04 allowance',hip['mass_both_legs']-0.04,hip['mass_both_legs']-0.04,'hand sizing, PU props [EST]','addition x1.0','Legs 2bf99d5 L25-L27, hip_stop.json'),
 ('harness M3 (Actuators)',h['total_kg'],h['total_kg'],'Belden MachFlex datasheet g/m x routed lengths; connectors distributor listings; JST-GH TME/GAM published weights (+-0.06 g/pair); sleeving 12 % [EST] already at par','datasheet/listing x1.0 (R-020 §6); sleeving no credit gained','Actuators 71f3c3e D53, harness.json'),
 ('covers M3 (Arbiter)',a3['covers_paper'],a3['covers_credited'],'HP PA12 density cited; 1.5 mm wall + 50 % coverage [EST]','saving vs 1.86 x0.5 (rests on [EST])','R-021, a3_size.json'),
 ('brain M4 (Arbiter)',a3['brain_paper'],a3['brain_credited'],'T5000/AGX301/DCM3623 cited 0.570; 0.474 [EST]','cited share x1.0, [EST] share x0.5','R-021, a3_size.json'),
 ('linkage r6 delta (GE 12 E -> GE 12 C eye)',lk['linkage_delta'],lk['linkage_delta'],'SKF GE 12 C 0.016 kg = GE 12 E 0.016 kg','datasheet x1.0','Actuators 71f3c3e LINKAGE_TABLE'),
 ('battery 20S5P P45B',8.75,8.75,'R-010','x1.0','CONTRACTS R1.1'),
]
# totals
cred=R020_CRED-(1.80-a3['brain_credited'])-(1.86-a3['covers_credited'])-(1.324-h['total_kg'])+lk['linkage_delta']+(hip['mass_both_legs']-0.04)
paper=R020_PAPER-(1.80-a3['brain_paper'])-(1.86-a3['covers_paper'])-(1.296-h['total_kg'])+lk['linkage_delta']+(hip['mass_both_legs']-0.04)
ep=sum(l[1] for l in lines); ec=sum(l[2] for l in lines)
lines.append(('all other lines (DERIVED: leg actuators+linkage, torso, arms, hands, head, thermal, pelvis; v3 basis + R-015..R-020 credits)',paper-ep,cred-ec,'see RULINGS R-015..R-020','as ruled there; to be itemised (A12)','derived'))
out=dict(status='OFFICIAL single source of truth (R-022). Module rollups must reconcile to this file line by line; any module figure that differs must cite the line and the ruling that changes it.',
 limit_kg=66.5, reserve_target_kg=0.30,
 lines=[dict(line=n,paper_kg=round(p,4),credible_kg=round(c,4),evidence=e,credit_rule=r,source=s) for n,p,c,e,r,s in lines],
 paper_kg=round(paper,3), credible_kg=round(cred,3), credible_reserve_kg=round(66.5-cred,3), paper_reserve_kg=round(66.5-paper,3),
 pending=dict(A1prime_structure_FEA=-0.596, credible_if_A1prime=round(cred-0.596,3)),
 reconciliation=dict(actuators_r6=lk['robot'], arbiter_R021=a3['credible'],
   actuators_missing_R021_brain=round(-(1.80-a3['brain_credited']),3), actuators_missing_R021_covers=round(-(1.86-a3['covers_credited']),3),
   both_missing_legs_r6_bumper_bolts=round(hip['mass_both_legs']-0.04,3), R021_missing_harness_A9=round(h['total_kg']-1.324,3), R021_missing_linkage=round(lk['linkage_delta'],4)))
assert abs(lk['robot']+out['reconciliation']['actuators_missing_R021_brain']+out['reconciliation']['actuators_missing_R021_covers']+out['reconciliation']['both_missing_legs_r6_bumper_bolts']-cred)<2e-3   # 0.001 = Actuators used 66.89 for 66.891
json.dump(out,open('modules/arbiter/mass_rollup_official.json','w'),indent=1); print(json.dumps(out,indent=1))
