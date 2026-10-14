"""Arms R1 wrist downsize ask (e1032af, arms/R1_ARCHITECTURE.md: wrist pair 4.3x oversized). Differential twin screw, arm r 25 mm (unchanged).
Needs (Arms R1): pitch 11.1 N·m, yaw 11.1 N·m (1.5 x 7.4 static), 6 rad/s; RMS = 7.4 N·m static hold (10 kg reach).
Motor: TBM2G-05008 (smallest TBM2G; Tp 0.72, Tmc1 0.27 / Tmc2 0.20 N·m, 0.111 kg; tbm2g_manual.pdf §9.2.1) - kept.
Screw: RV12x4 roller (Ca 17.2 kN) -> THK BNK1004-2.5 miniature ball screw ø10 lead 4 (Ca 2.1 / C0a 2.7 kN; nut ø26, flange ø46, L 34; lead 10 BNK0810 fails RMS 0.76x; thk_bnk_lmsystems.html)."""
import json, math, os
H=os.path.dirname(os.path.abspath(__file__)); r=0.025; eta=0.9; lead=0.004; Tp,Tmc2=0.72,0.20; NRATED=4900   # winding B rated speed at bus (manual table)
Fpk=Tp*2*math.pi*eta/lead; Fcont=Tmc2*2*math.pi*eta/lead
need_axis=11.1/r/2; need_both=(11.1+11.1)/(2*r); rms=7.4/r/2
v=6*r; rpm_axis=v/lead*60; rpm_both=2*v/lead*60
L10_h=(2100/rms)**3*1e6/(rpm_axis*60*0.25)   # 25 % duty at 6 rad/s mean [EST]
unit=dict(housing_7075=0.0789,motor_TBM2G05008=0.111,screw_shaft_ø10x110=math.pi/4*100*110*7.85e-6,nut_BNK1004=0.060,support_bearings_2x7000=0.038,hub=0.016,fasteners=0.0236,rod_end_GE_misc=0.037)
pair=2*sum(unit.values())
out=dict(F_pk_N=Fpk,F_cont_N=Fcont,need_per_axis_N=need_axis,SF_per_axis=Fpk/need_axis,need_pitch_plus_yaw_N=need_both,SF_simultaneous=Fpk/need_both,
 rms_N=rms,SF_rms=Fcont/rms,rpm_axis=rpm_axis,rpm_pitch_plus_yaw=rpm_both,rpm_rule_95pct=rpm_both<=0.95*NRATED,L10_h_EST=L10_h,
 unit_kg={k:round(x,4) for k,x in unit.items()},pair_kg=pair,old_pair_kg=1.55,delta_per_side_kg=pair-1.55,delta_both_kg=2*(pair-1.55),
 cost=dict(BNK1004_EST_usd='150-250 each [EST, no public THK price]',RV12x4_EST_usd='no public price (SOURCES row 32); planetary roller screws typically several x a miniature ball screw [EST]'),
 note='nut mass, rod end/misc [EST]; housing from cad_mass.linear_body geometry scaled to ø56 can / ø32 nut section')
json.dump(out,open(f'{H}/results/wrist_r1.json','w'),indent=1); print(json.dumps({k:(round(v,3) if isinstance(v,float) else v) for k,v in out.items() if k not in('unit_kg','cost')}))
