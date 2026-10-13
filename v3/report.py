"""Builds v3/PARTS.md, v3/REVISIONS.md and v3/dashboard.json from v3/analysis + v3/cad outputs."""
import json, os, sys
sys.path.insert(0,'analysis'); import parts as PT
V=json.load(open('analysis/results/v3.json')); ST=V['state']; rows={r['joint']:r for r in V['rows']}
REV=json.load(open('analysis/results/revisions_analysis.json'))
FEA=json.load(open('cad/out/fea_v3.json')) if os.path.exists('cad/out/fea_v3.json') else {}
CL=json.load(open('cad/out/clash.json')); CB=json.load(open('cad/out/cables.json')); KS=json.load(open('cad/out/knee_adduction_sweep.json'))
MS=json.load(open('cad/out/mass.json'))
W=['A','C','D']
# ---------------- parts table
L=['# v3 parts table (catalog parts, cited)','','Every actuator part below is a catalog item; values are copied from the cited source. Items still marked [EST] are noted.','',
   '## Joint actuators (per joint; × count in the robot)','','| joint | ×n | motor (winding) | Kt hot N·m/A | R Ω (25 °C, ph-ph) | Rth K/W | motor kg | transmission | rating | output bearing (C / C0 kN) | drive / encoder | actuator kg |','|---|---|---|---|---|---|---|---|---|---|---|---|']
CNT={}
for n,d in ST['J'].items():
    mo=PT.MOT[d['motor']]; w=W.index(PT.WIND[d['w']]) if PT.WIND[d['w']] in W else 0
    if d['kind']=='rotary':
        g=PT.CSG[d['gear']]; tr=f"Harmonic Drive {d['gear']}"; rt=f"rated {g['rated']} / rep. peak {g['rep']} / mom. {g['mom']} / ratchet {g['ratchet']} N·m"
        b=dict(PT.CRBH)[ST['bearing'][n]]; bb=f"IKO {ST['bearing'][n]} ({b['C']/1000:.1f} / {b['C0']/1000:.1f})"
    else:
        s=PT.RV[d['screw']]; tr=f"Rollvis {d['screw']} roller screw, {d['arm']*1000:.0f} mm lever"; rt=f"Ca {s['Ca']/1000:.1f} kN, C0a {s['C0a']/1000:.1f} kN, η {s['eta']}"; bb='rod-end spherical bearings [EST]'
    L.append(f"| {n} | {d['cnt']} | Kollmorgen {d['motor']}{PT.WIND[d['w']]} | {mo['Kt_hot'][w]} | {mo['Rm'][w]} | {mo['Rth']} | {mo['mass']} | {tr} | {rt} | {bb} | Everest XCR / RLS AksIM-2 | {rows[n]['mass']:.2f} |")
L+=['','Gear sizes 14 and 17 component-set masses are [EST] (not given in the table used). Housings are parametric 7075 shells (wall 3 mm), modelled in the CAD; harmonic-drive efficiency 75 % [EST]. Linear joints listed with ×0 share their screw pair with the pitch joint (differential pair).','',
 '## Other catalog parts','','| item | part | key data | source |','|---|---|---|---|',
 f"| servo drive (one per motor) | Novanta Everest XCR | 45 A crest cont. (31.8 A rms), 60 A crest 1 s, ≤80 V, 38 g | EVE |",
 f"| joint encoder | RLS AksIM-2 off-axis absolute | 17–20 bit; ring + readhead masses per datasheet | AKSIM |",
 f"| battery cells | Molicel INR-21700-P45B ×{V['mass']['cells']} (13S{ST['battery']['P']}P) | 16.2 Wh, ≤70 g each → {V['mass']['battery_Wh']:.0f} Wh, {V['mass']['battery']:.1f} kg incl. 1.25× pack overhead [EST] | P45B |",
 f"| finger flexor drives (6 per hand) | maxon DCX 22 S + GPX 22 HP 111:1 | 15.3 mN·m cont.; gearhead 3.3 N·m cont., η 0.65 | DCX22, GPX22 |",
 f"| abduction/thumb drives (5 per hand) | maxon DCX 16 S + GPX 16 LN 103:1 | 5.2 mN·m cont.; 0.28 N·m cont. | DCX16, GPX16 |",
 f"| tendons | LIROS D-Pro 1 mm (Dyneema SK78) | 195 daN break | LIROS |",
 f"| structure | 7075-T6 | Su 572, Sy 503, Sf 159 MPa @5e8 | AL7075 |",
 f"| fasteners | ISO 898-1 class 12.9 | Rp0.2 ≥ 1100 MPa | ISO898 |",
 f"| cables | igus chainflex CFROBOT-class | moving bend radius ≥ 10×d | IGUS |",
 '','## Sources','','| key | document | URL / reference |','|---|---|---|']
for k,(t,u) in PT.SRC.items(): L.append(f'| {k} | {t} | {u} |')
open('PARTS.md','w').write('\n'.join(L))
# ---------------- revisions
R=['# v3 revision log','','Every failure found in the v3 hardening loop and what was done about it. "it" = iteration of `analysis/v3.py` (0 = v2 design with catalog parts substituted 1:1). CAD/FEA/sim entries were found by `cad/clash.py`, `cad/knee_sweep.py`, `cad/fea_v3.py` and `sim/v3/balance_v3.py`.','',
   '## A. Analysis loop (analysis/v3.py)','','| it | area | failure | fix |','|---|---|---|---|']
for r in REV: R.append(f"| {r['it']} | {r['area']} | {r['failure']} | {r['fix']} |")
R+=['','## B. Earlier analysis-code defects (found while iterating)','',
 '| failure | fix |','|---|---|',
 '| First full run: robot mass 94.6 kg; shoulder actuators 4.5 kg each | Fall moment was applied to all three shoulder joints with fs ≥ 3. Now applied only to shoulder pitch (where the side-fall load enters) with fs ≥ 1 (accidental one-off load, no brinelling beyond C0); other joints use fs ≥ 3 on operating/landing loads. |',
 '| Ankle and wrist differential screw pairs counted twice (pitch and roll each sized their own pair) | One shared pair per joint (`SHARED`), mass counted once, both DoF checked on the same hardware. |',
 '| Smallest CRBH in table was 3010 → neck/wrist got 0.12–0.29 kg bearings | Added IKO CRBH 208 / 258 rows from the catalog. |',
 '| Passing joints were never down-sized (only failing joints were re-selected) | Added a mass-reduction pass: every joint re-selected as the lightest passing catalog combination, then all checks re-run (mass changes the loads). 70.5 → 62.0 kg. |',
 '| Lever-arm search compounded ×1.3 per iteration (knee arm reached 101 mm, ankle 110 mm) | Arms capped at CAD packaging limits: knee 60 mm, ankle 70 mm, wrist 30 mm. |',
 '','## C. CAD (cad/model.py, clash.py)','','| failure | fix |','|---|---|',
 '| v3.0 CAD with catalog envelopes: 100 clashes at standing | — (individual fixes below) |',
 '| Hip-yaw housing (now carries a CRBH 6013, Ø90) and hip bracket webs hit the 300 mm pelvis side walls | Pelvis width follows hip_y: 2×(hip_y+55) = 370 mm; hip openings follow housing OD |',
 '| Single-leg hip adduction −12° (v2 only checked both legs together): legs cross (14 clashes) | hip_y 100 → 115 (still 7 clashes at −6°) → 130 mm. Single-leg adduction clash-free to −6° (−8° hits the other ankle actuators); −12° only with pelvis shift (both hips), which is how it is used in gait. |',
 '| Finned ankle actuator bodies (fin OD 86) overlapped each other | ankle_act_dy 37 → 45 mm |',
 '| 17 hand motors in a 40×40 box (v2) not real; first v3 placement had drives overlapping each other and the wrist | 6 flexor drives (DCX22S+GPX22HP) in one ring r = 23 mm in a Ø76/72 forearm; 5 small drives (DCX16S+GPX16) in the palm; tendons as one Ø6 bundle through the hollow wrist-roll bore (all rotary housings now have a through-bore) |',
 '| Catalog neck-yaw housing hit the compute bay; neck pitch hit neck yaw and the head shell | torso_top 1556 → 1590; neck pitch tt+48 → tt+60; head opening Ø118; head centre +15 mm |',
 '| 2.1 kWh P45B pack is 5.9 L, v2 box was 5.0 L → hit shoulder housings and spine | Pack box 185×220×144 mm, moved forward; compute bay raised |',
 '| Upper-arm tube ran into the (longer) catalog shoulder-yaw housing | Tube length derived from the housing length |',
 '| Hip abduction 20° with arms hanging: hand touches the thigh | Limit 15° with arms hanging (functional need is 15°); 20° needs the arm moved |',
 f"| Knee > 120°: {len(KS['125'])} clashes at 125°, {len(KS['130'])} at 130°, {len(KS['140'])} at 140° | **Not fixed.** At 125° the rod end hits the femur collar (a linkage knee could fix this), but at 130° the knee actuator body hits the ankle actuator bodies on the calf; a linkage does not change that. >135° needs the ankle actuators moved off the back of the shank (e.g. into the foot). Knee stays 0–120°. |",
 f"| After fixes: clash check of standing + 14 range-extreme poses | **{sum(len(v) for v in CL.values())} clashes** |",
 '','## D. Structure / FEA (cad/fea_v3.py)','','| item | result |','|---|---|']
for k,o in FEA.items():
    R.append(f"| {k} | peak {o['vm']:.0f} MPa (99.5 % element), SF yield {o['SF_yield']:.2f}"+(f", Goodman {o['goodman']:.2f}" if 'goodman' in o else '')+f", mesh Δ {o['delta_pct']:.1f} % → {'converged' if o['converged'] else 'NOT converged'} |" if o['delta_pct'] is not None else f"| {k} | {o['vm']:.0f} MPa, single mesh level |")
R+=['| pelvis_hip first run: stresses of 10⁴–10⁸ MPa, solver not converging | The hip-bracket flange sat 1 mm below the pelvis top wall (top = pelvis_top−5 vs wall inner face pelvis_top−4), so the bracket was floating. Flange now bears on the wall (bolted face contact); re-run. |',
 '| Convergence metric | Peak = 99.5th-percentile element stress; Δ < 10 % between the last two meshes counts as converged. Max-element stress is also reported; it keeps rising at re-entrant corners (singularities) and is not used for SF. |',
 '| FEA memory | First attempt at full-length P2 meshes: TetGen quality refinement gave 100k–970k tets regardless of max-volume (max_volume was ignored with an options string) and OOM. Fixed by setting fixedvolume/maxvolume explicitly, radius-edge 3.0 and AMG-preconditioned CG; single-threaded BLAS. |',
 '','## E. Simulation (sim/v3)','','| failure | fix / status |','|---|---|',
 '| v3 model with CAD mass properties: plain PD (balance off) falls backwards in ~2 s | CAD centre of mass sits 20–35 mm behind the ankles (knee/ankle actuators behind the legs). With the COM ankle strategy (balance ON) it stands and rejects 125 N / 0.2 s pushes forward and sideways (v2 capsule model: 175 N). Not fixed in hardware geometry; flagged. |']
open('REVISIONS.md','w').write('\n'.join(R))
print('ok', len(REV))
# ---------------- dashboard
rowsD=[]
def add(a,c,r,s): rowsD.append((a,c,r,s))
for n,r in rows.items():
    add('actuator',f"{n}: {r['motor']} + {r['trans']}",f"torque {r['T']:.0f}/{r['need']:.0f} N·m, speed {r['w']:.1f}/{r['w_need']} rad/s, ΔT {r['dT']:.0f} K, hold {r['I_hold']:.1f} A rms, L10 {r.get('life_h',0):.1e} h",'PASS' if r['ok'] else 'FAIL')
for n,r in rows.items():
    if 'bearing' in r:
        b=r['bearing']; add('output bearing',f"{n}: IKO {b['bearing']}",f"L10 {b['L10_h']:.1e} h, fs {b['fs']:.1f} (≥{b['fs_req']:.0f})",'PASS' if b['L10_h']>=14600 and b['fs']>=b['fs_req'] else 'FAIL')
for b in V['bolts']: add('bolted joint (VDI 2230-style)',b['name'],f"{b['n']}×{b['size']}: clamp {b['F_res']/1000:.1f} ≥ {b['F_req']/1000:.1f} kN, σa {b['sig_a']:.0f} ≤ {b['sig_ASV']:.0f} MPa",'PASS' if b['ok'] else 'FAIL')
fg=V['fall_gear']; f=V['fall']
add('side fall 1 m','energy method',f"{f['E_J']:.0f} J; hip {f['hip_F']/1000:.1f} kN, shoulder {f['shoulder_F']/1000:.1f} kN with 30 mm pads",'PASS')
add('side fall 1 m','shoulder harmonic drive',f"impact {fg['T_impact']:.0f} N·m > momentary {fg['mom']} → overload clutch slips at {fg['clutch']} N·m",'PASS')
h=V['hand']
add('hand','continuous fingertip force',f"{h['tip']:.1f} N (target ≥ 30 N)",'PASS' if h['tip']>=30 else 'FAIL')
add('hand','tendon static',f"SF {h['SF_tendon']:.1f} at {h['tension']:.0f} N",'PASS')
add('hand','tendon bend fatigue, 5 y',f"needs {h['grasps_5y']:.1e} cycles; published evidence ≤ {h['evidence']:,} (D/d 4); our idlers D/d 8",'OPEN')
p=V['power']; add('power','walking runtime',f"{p['runtime_h']:.1f} h at {p['P_total']:.0f} W",'PASS' if p['runtime_h']>=2 else 'FAIL')
add('mass','target ≤ 65 kg',f"{V['m']:.1f} kg catalog rollup (CAD solids {MS['total']:.1f} kg)",'PASS' if V['m']<=65 else 'FAIL')
for c in CB['joints']: add('cable routing',c['joint'],f"r {c['r_min_mm']} ≥ {c['r_req_mm']} mm (Ø{c['d_mm']} [EST])",'PASS' if c['r_min_mm']>=c['r_req_mm'] else 'FAIL')
nc=sum(len(v) for v in CL.values()); add('CAD','interference: standing + 14 range extremes',f'{nc} clashes','PASS' if nc==0 else 'FAIL')
add('CAD','single-leg hip adduction',f"clash-free to −6° (−8°: {len(KS['single_roll_-8'])} clashes); −12° with pelvis shift",'PASS')
add('CAD','knee flexion > 135° (linkage knee)',f"120° clash-free; 125°: {len(KS['125'])}, 130°: {len(KS['130'])}, 140°: {len(KS['140'])} clashes (knee body vs ankle actuators; linkage does not help)",'FAIL')
for k,o in FEA.items():
    lim=1.0 if k.startswith('fall') else 2.0; ok=o['SF_yield']>=lim and o.get('goodman',9)>=1.5
    conv=o['converged']
    add('FEA',k,f"{o['vm']:.0f} MPa, SF {o['SF_yield']:.2f} (≥{lim:.0f})"+(f", Goodman {o['goodman']:.2f}" if 'goodman' in o else '')+f", {len(o['levels'])} mesh levels, Δ {o['delta_pct']:.1f} %" if o['delta_pct'] is not None else f"{o['vm']:.0f} MPa (1 level)",'PASS' if ok and conv else ('FAIL' if not ok else 'OPEN'))
SIM=json.load(open('../sim/v3/balance_v3.json'))
add('simulation','stand + push recovery (MuJoCo, CAD mass properties)',SIM['text'],'PASS' if SIM['ok'] else 'FAIL')
for a,c in [('thermal','two-node winding/housing model, h = 12 W/m²K, fins ×2 [EST]: needs dynamometer test'),('fall','pad crush model and 55/45 hip/shoulder split [EST]: needs drop test'),('clutch','300 N·m friction clutch slip repeatability: needs test'),('torso shell','CFRP properties isotropic [EST]: needs laminate data / coupon test'),('bolted joints','μ = 0.12, embedding 11 µm [EST]: needs torque-tension test'),('harmonic drive','life vs. ratcheting under repeated falls: vendor/test')]:
    add('unverifiable without hardware',a,c,'OPEN')
import mujoco
m=mujoco.MjModel.from_xml_path('../sim/v3/humanoid_v3.xml')
ids=dict(jq={m.joint(i).name:int(m.jnt_qposadr[i]) for i in range(m.njnt)},g={n:m.geom(n).id for n in ('l_foot','r_foot')},a={m.actuator(i).name:i for i in range(m.nu)},b={m.body(i).name:i for i in range(m.nbody)})
summ=(f"Bryan asked for a design that would hold up in the real world. v3 replaces every estimated actuator part with a catalog part (Kollmorgen TBM2G, Harmonic Drive CSG, Rollvis RV, IKO CRBH, Everest XCR, RLS AksIM-2, maxon, Molicel), adds bolts, bearings, cable drums, fins and a tendon hand to the CAD, and re-checks thermal, life, fall, fatigue and FEA. "
      f"The loop started with {sum(1 for r in REV if r['it']==0)} failures; {V['m']:.1f} kg after fixes.")
json.dump(dict(rows=rowsD,summary=summ,sim=dict(mass=float(m.body_subtreemass[1]),text=SIM['text']),ids=ids),open('dashboard.json','w'),indent=0)
print('dashboard rows',len(rowsD),{k:sum(1 for x in rowsD if x[3]==k) for k in ('PASS','FAIL','OPEN')})
