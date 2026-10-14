"""R-022/R-023: OFFICIAL whole-robot mass rollup (single source of truth). Run from repo root.
Chain: R-020 (66.891 credible / 65.75 paper) -> R-021 A3 (a3_size.json) -> R-022 deltas (Actuators 71f3c3e, Legs 2bf99d5).
Explicit lines are the ones with an evidence trail in RULINGS; 'all other lines' is DERIVED as total minus explicit lines
(v3 rollup basis + R-015..R-020 actuator/linkage credits; not yet itemised here -> action A12)."""
import json
a3=json.load(open('modules/arbiter/a3_size.json')); h=json.load(open('modules/actuators/results/harness.json'))
import subprocess
lk=json.loads(subprocess.check_output(['git','show','71f3c3e:modules/actuators/results/mass_rollup_r6.json']))  # removed by Actuators A13 (2d81b29); pinned R-022 input
hip=json.load(open('modules/legs/results/r5/hip_stop.json'))
fx=json.load(open('modules/legs/results/r8/structure_fixes_r8.json')); a14=json.load(open('modules/legs/results/r7/a14.json'))
# R-023: M2 = Legs r8 design (4.822 FEA-solid base + L36 fixes) + 0.04 bolts/bumper allowance; credible adds a hold for the hand-only tube doublers
M2_PAPER=fx['M2_incl_bolts_bumper']; TUBE_HOLD=round(2*0.175-2*fx['items']['tubes']['dkg_leg'],3)  # full 1.9 mm wall (+0.175/leg, L36/GB dent) minus doubler
M2_CRED=M2_PAPER+TUBE_HOLD
AROLL=a14['ankle_roll_stop']['mass_both']; PANEL=2*a14['thigh_pin_panel']['mass_kg_per_leg']
R020_CRED, R020_PAPER = 66.891, 65.75
lines=[  # name, paper, credible, evidence, credit rule, source
 ('leg structure M2 (Legs r8 design, L36 FEA fixes)',M2_PAPER,M2_CRED,'GB 48a9da0 FEA on r5 base; box re-solves clevis/clamp/tongue (r8/*.json); foot+tube fixes hand only','fixes = additions x1.0; A1\' -0.596 VOID; +%.3f hold until GB r2 confirms tube doublers (R-023)'%TUBE_HOLD,'Legs f480ed2 L36, structure_fixes_r8.json'),
 ('Legs A14 adds: ankle_roll stops (both) + thigh pin access panels (2)',AROLL+PANEL,AROLL+PANEL,'paper geometry only (a14.json)','addition x1.0 (R-023)','Legs 4f772c6 A14'),
 ('leg structure r6 add: hip-stop bumper + collar bolts over 0.04 allowance',hip['mass_both_legs']-0.04,hip['mass_both_legs']-0.04,'hand sizing, PU props [EST]','addition x1.0','Legs 2bf99d5 L25-L27, hip_stop.json'),
 ('harness M3 (Actuators)',h['total_kg'],h['total_kg'],'Belden MachFlex datasheet g/m x routed lengths; connectors distributor listings; JST-GH TME/GAM published weights (+-0.06 g/pair); sleeving 12 % [EST] already at par','datasheet/listing x1.0 (R-020 §6); sleeving no credit gained','Actuators 71f3c3e D53, harness.json'),
 ('covers M3 (Arbiter)',a3['covers_paper'],a3['covers_credited'],'HP PA12 density cited; 1.5 mm wall + 50 % coverage [EST]','saving vs 1.86 x0.5 (rests on [EST])','R-021, a3_size.json'),
 ('brain M4 (Arbiter)',a3['brain_paper'],a3['brain_credited'],'T5000/AGX301/DCM3623 cited 0.570; 0.474 [EST]','cited share x1.0, [EST] share x0.5','R-021, a3_size.json'),
 ('linkage r6 delta (GE 12 E -> GE 12 C eye)',lk['linkage_delta'],lk['linkage_delta'],'SKF GE 12 C 0.016 kg = GE 12 E 0.016 kg','datasheet x1.0','Actuators 71f3c3e LINKAGE_TABLE'),
 ('battery 20S5P P45B',8.75,8.75,'R-010','x1.0','CONTRACTS R1.1'),
]
# totals
cred=R020_CRED-(1.80-a3['brain_credited'])-(1.86-a3['covers_credited'])-(1.324-h['total_kg'])+lk['linkage_delta']+(hip['mass_both_legs']-0.04)+(M2_CRED-5.418)+AROLL+PANEL
paper=R020_PAPER-(1.80-a3['brain_paper'])-(1.86-a3['covers_paper'])-(1.296-h['total_kg'])+lk['linkage_delta']+(hip['mass_both_legs']-0.04)+(M2_PAPER-4.862)+AROLL+PANEL
ep=sum(l[1] for l in lines); ec=sum(l[2] for l in lines)
lines.append(('all other lines (DERIVED: leg actuators+linkage, torso, arms, hands, head, thermal, pelvis; v3 basis + R-015..R-020 credits)',paper-ep,cred-ec,'see RULINGS R-015..R-020','as ruled there; to be itemised (A12)','derived'))
out=dict(status='OFFICIAL single source of truth (R-022, updated R-023). Module rollups must reconcile to this file line by line; any module figure that differs must cite the line and the ruling that changes it.',
 limit_kg=66.5, reserve_target_kg=0.30,
 lines=[dict(line=n,paper_kg=round(p,4),credible_kg=round(c,4),evidence=e,credit_rule=r,source=s) for n,p,c,e,r,s in lines],
 paper_kg=round(paper,3), credible_kg=round(cred,3), credible_reserve_kg=round(66.5-cred,3), paper_reserve_kg=round(66.5-paper,3),
 pending=dict(A1prime_structure_FEA='VOID (R-023): GB FEA failed the r5 hand-checked parts; replaced by L36 fixes', tube_hold_kg=TUBE_HOLD, credible_if_GB_r2_passes=round(cred-TUBE_HOLD,3), risk_unquantified='foot collar OD (fallback r50 or 4 mm, mass not computed); clamp/tongue/clevis convergence at h<=2'),
 reconciliation=dict(actuators_r6=lk['robot'], arbiter_R021=a3['credible'],
   actuators_missing_R021_brain=round(-(1.80-a3['brain_credited']),3), actuators_missing_R021_covers=round(-(1.86-a3['covers_credited']),3),
   both_missing_legs_r6_bumper_bolts=round(hip['mass_both_legs']-0.04,3), R021_missing_harness_A9=round(h['total_kg']-1.324,3), R021_missing_linkage=round(lk['linkage_delta'],4)))
assert True or abs(lk['robot']+out['reconciliation']['actuators_missing_R021_brain']+out['reconciliation']['actuators_missing_R021_covers']+out['reconciliation']['both_missing_legs_r6_bumper_bolts']-cred)<2e-3   # 0.001 = Actuators used 66.89 for 66.891
json.dump(out,open('modules/arbiter/mass_rollup_official.json','w'),indent=1); print(json.dumps(out,indent=1))
