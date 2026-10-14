"""v4 audit fixes (D59-D62): actuator-owned mass deltas vs the pre-v4 CAD (git 9447a9d cad_mass.json), both legs. Updates results/actuator_deltas.json."""
import json, math, os, subprocess
H=os.path.dirname(os.path.abspath(__file__))
old=json.loads(subprocess.check_output(['git','show','9447a9d:modules/actuators/results/cad_mass.json'],cwd=H)); new=json.load(open(f'{H}/results/cad_mass.json'))
d=lambda k:new[k]['mass']-old[k]['mass']
pin12=math.pi/4*12**2*30*7.85e-6; spacer=math.pi/4*(20**2-12**2)*4.5*7.85e-6
L={ 'hip_pitch body: unused trunnion bosses removed (x2/leg)':2*d('hip_pitch_body_x1'),
    'knee twin housing: inner bosses -> shared web (x2 halves/leg)':2*d('knee_body_x1'),
    'ankle body: bosses -> axial top eye lug (x2/leg)':2*d('ankle_body_x1'),
    'ankle top eye SKF GE 12 C 0.017 (x2/leg)':2*0.017,
    'ankle top eye pin ø12x30 steel (x2/leg)':2*pin12,
    'ankle trunnion pin pairs retired (-2/leg)':-2*old['trunnion_pins_pair']['mass'],
    'ankle bottom rod end: high-misalignment PTFE (QA1 MGF12T class) vs GE 12 C rod end, +0.010 [EST] (x2/leg)':2*0.010,
    'ankle bottom spacer ø20/12 x4.5 steel (x2/leg)':2*spacer,
    'ankle rod anti-rotation key + rod flat [EST] (x2/leg)':2*0.006}
per_leg=sum(L.values()); out=dict(lines_per_leg={k:round(v,5) for k,v in L.items()},per_leg_kg=per_leg,both_legs_kg=2*per_leg,
    status='pending Arbiter ruling (P-018); not in the official rollup',
    not_included='Legs-side changes (ankle clevis replacing trunnion cheeks/pins/centre plate, raised bracket +40 mm, instep lug +5 mm outboard) are Legs mass')
json.dump(out,open(f'{H}/results/v4_deltas.json','w'),indent=1)
A=json.load(open(f'{H}/results/actuator_deltas.json')); A['v4_audit_fixes_pending']=dict(both_legs_kg=round(2*per_leg,4),source='results/v4_deltas.json',status=out['status'])
json.dump(A,open(f'{H}/results/actuator_deltas.json','w'),indent=1); print(json.dumps(out,indent=1))
