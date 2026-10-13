"""R3 structure check of the pocketed/ribbed parts by classical hand methods (NOT 3D FEA; the box has <0.5 GB free while other agents run FEA).
Methods: pin-loaded lug (net tension with Kt, bearing, shear-out; Bruhn/ESDU form), wall bending, ribbed-plate beam section. 7075-T6: Sy 503, Su 572, Se 159 MPa (5e8, per structure_fea.md).
Loads (65 kg robot, 85 kg with 20 kg carry) come from our ID runs; screw forces are the actuator maxima (conservative limit loads).
Pocketed sections: pockets assumed to remove material outside the pin-load path (webs >= 3 mm); the checked net sections are the unpocketed ligaments -> flagged."""
import json,math,os
H=os.path.dirname(os.path.abspath(__file__)); g=9.81
Sy,Su,Se=503.,572.,159.
GRF=max(json.load(open(f'{H}/results/{p}.json'))['info']['max_vertical_GRF_BW']*json.load(open(f'{H}/results/{p}.json'))['info']['mass_kg']*g
        for p in ('r2/walk_1p2','r2/walk_1p0','r2/stairs_18cm','r2/carry_20kg_r2','r3/carry_20kg_0p8','r3/carry_20kg_1p0','r2/push_recover'))
W=65*g; F3=3*W; FALL=6*W
FK=7267.4; FH=9084.3; FA=283.2/0.070        # knee/hip screw maxima (Actuators), ankle screw force at carry peak 283.2 N·m / 70 mm lever
R=[]
def rec(part,case,sig,kind,static_SF_need,note,op=None):
    sf=Sy/sig if kind!='shear' else 0.577*Sy/sig
    d=dict(part=part,case=case,stress_MPa=round(sig,1),kind=kind,SF=round(sf,2),need=static_SF_need,ok=sf>=static_SF_need,note=note)
    if op is not None:   # Goodman for 0->peak operating cycles
        sa=sm=op/2; d['goodman_SF']=round(1/(sa/Se+sm/Su),2); d['ok']=d['ok'] and d['goodman_SF']>=1.5
    R.append(d)
def lug(part,P,Wd,D,t,e,cases,kt=3.0,note=''):
    """P total pin load shared by n=len cheeks already in t (t = total thickness carrying P)."""
    for case,Pc,need,fat in cases:
        nt=kt*Pc/((Wd-D)*t); br=Pc/(D*t); so=Pc/(2*(e-D/2)*t)
        rec(part,case,nt,'net tension ×Kt %.1f'%kt,need,note,op=nt if fat else None); rec(part,case,br,'bearing',need/1.5*1.0 if False else need,note); rec(part,case,so,'shear',need,note)
# operating = worst ID GRF + screw max (colinear, conservative); fall = 6 BW (screw back-driven, not added)
OPk=GRF+FK; OPh=GRF+FH; OPa=GRF+FA
cases=lambda op:[('operating peak (ID GRF %.0f N + screw)'%GRF,op,1.5,True),('3 BW + screw',F3+(op-GRF),2.0,False),('fall 6 BW',FALL,2.0,False)]
lug('knee clevis (thigh), 2 cheeks 46×14, pin ø16',OPk,46,16,2*14,21,cases(OPk),note='bridge pocket 15 % is outside the pin path; v3 FEA scaled SF 4.80 (structure_mass.md) is the governing whole-part number')
lug('knee tongue (shank), R32 × 40, pin ø16',OPk,64,16,40,32,cases(OPk),note='pocket 15 % keeps a 12 mm ligament ring around the pin')
lug('femur upper lug → hip pivot boss, assumed bore ø32 [EST: pivot bearing unowned]',OPh,80,32,30*0.8,30,cases(OPh),note='thickness ×0.8 for the 20 % pocket; bore and bearing not defined (open linkage-table line)')
lug('ankle fork (shank), 2 walls 4 mm, assumed pin ø12 [EST]',OPa,30,12,2*4*0.85,15,cases(OPa),note='walls are only 4 mm: pocketing them (×0.85) is NOT recommended; pocket the 10 mm top plate only')
# ribbed foot plate: cantilever from the F/T sensor edge (x=30 mm) to the toe CoP extreme (x=180 mm), arm 150 mm; also heel strike (heel -60, sensor edge -30: arm 30 mm, not governing)
def sec(parts):   # list of (b,h,y_bottom) rectangles -> I, c_max
    A=sum(b*h for b,h,y in parts); yc=sum(b*h*(y+h/2) for b,h,y in parts)/A
    I=sum(b*h**3/12+b*h*(y+h/2-yc)**2 for b,h,y in parts); top=max(y+h for b,h,y in parts); return A,I,max(yc,top-yc)
solid=sec([(100,18,0)]); ribbed=sec([(100,4,0)]+[(3,14,4)]*3); boxs=sec([(100,4,0)]+[(4,10,4)]*4+[(100,4,14)])
for name,(A,I,c) in (('foot plate v3 solid 100×18',solid),('foot plate open ribbed 4 mm skin + 3 ribs 3×14 (r2 spec)',ribbed),('foot plate closed box 18: 4 mm skins top+bottom + 4 webs 4 mm (r3 spec)',boxs)):
    for case,F,need,fat in (('operating peak GRF at toe',GRF,1.5,True),('3 BW at toe',F3,2.0,False),('fall 6 BW at toe',FALL,2.0,False)):
        s=1.5*F*150/(I/c)   # Kt 1.5 rib-root fillet
        rec(name,case,s,'bending ×Kt 1.5',need,f'A {A:.0f} mm², I {I:.0f} mm⁴, c {c:.1f} mm',op=s if fat else None)
out=dict(GRF_peak_N=round(GRF,1),loads=dict(F_knee_screw=FK,F_hip_screw=FH,F_ankle_screw=round(FA,1),W3=round(F3,1),fall6=round(FALL,1)),rows=R,
         method='classical lug / beam hand methods, not FEA; R-013 credit still needs grokbuild/structure_fea.md')
json.dump(out,open(f'{H}/results/r3/structure_check.json','w'),indent=1)
L=['# R3 structure check (hand methods, not FEA)','',f"Worst ID GRF {GRF:.0f} N (all r2/r3 scenarios incl. 20 kg carry). Screw limit loads: knee {FK:.0f}, hip {FH:.0f}, ankle {FA:.0f} N. 3 BW {F3:.0f} N, fall 6 BW {FALL:.0f} N.",'',
   '| part | case | check | σ/τ MPa | SF | need | Goodman SF | ok |','|---|---|---|---|---|---|---|---|']
for r in R: L.append(f"| {r['part']} | {r['case']} | {r['kind']} | {r['stress_MPa']} | {r['SF']} | {r['need']} | {r.get('goodman_SF','')} | {'yes' if r['ok'] else '**NO**'} |")
L+=['','Notes:']+sorted({f"- {r['part']}: {r['note']}" for r in R})
open(f'{H}/results/r3/structure_check.md','w').write('\n'.join(L)+'\n')
for r in R:
    if not r['ok'] or 'net' in r['kind'] or 'bending' in r['kind']: print(r['part'][:40],r['case'][:22],r['kind'],r['stress_MPa'],r['SF'],r.get('goodman_SF'),r['ok'])
