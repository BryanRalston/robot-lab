"""Arms module fastener BOM (R14, Robot Lab request for RL Materials steel->Ti pricing). Robot totals (2 arms).
Scope: arm STRUCTURE fasteners Arms owns. Excluded to avoid double count: actuator-unit internals (Actuators FASTENER_BOM.md: flexspline,
circular spline, output flange->customer, CRB clamp, covers, readheads, Elmo mounts), pad tray M4 (ID FASTENERS_BOM.json).
Mass: ISO 4762 approx steel g = 7.85e-3 * (pi/4 d^2 L + head) [CALC]; Ti64 ratio 0.564. Counts [EST] unless a source is given."""
import json,os,math,csv
H=os.path.dirname(os.path.abspath(__file__))
def g(d,L,kind='shcs'):
    head=math.pi/4*(1.5*d)**2*d if kind!='dowel' else 0
    return 7.85e-3*(math.pi/4*d*d*L+head)
R=[ # where, size, d, L, per_side, grade, structural, reason, basis
 ('shoulder_P -> torso frame (CONTRACTS 1c)','M8x20 SHCS',8,20,8,'12.9 steel',True,'arm-to-torso joint, side-fall case','R2_OPEN_ITEMS l.152 (8xM8 12.9 BC80)'),
 ('pad stand-off flange -> roll-output hub','M4x12 SHCS',4,12,8,'12.9 steel',True,'321 N.m + 7 kN pad load','R13/R14 (PCD62)'),
 ('pad stand-off dowels','D6 m6 x10 dowel',6,10,2,'hardened steel',True,'flange shear (fitted)','ID ec12542 / R14 (PCD57)','dowel'),
 ('roll housing seat flange -> shoulder_P','M4x10 SHCS',4,10,8,'12.9 steel',True,'bearing retention, pad impact','R13 housing [EST count]'),
 ('upper-arm link -> elbow unit','M5x14 SHCS',5,14,8,'12.9 steel',True,'carry/reach bending','[EST, HD CSG-20 pattern]'),
 ('forearm tube -> elbow output / wrist node','M4x10 SHCS',4,10,12,'12.9 steel',True,'forearm bending (10 kg reach)','[EST] 6 per end'),
 ('wrist fork -> palm 7075','M3x8 SHCS',3,8,8,'12.9 steel',True,'grip/wrist torque','A32/A42 [EST]'),
 ('finger phalanx pivot screws','M2x6 shoulder',2,6,15,'A2-70 / steel',True,'finger joint pin (grip 22 N)','R9 hand [EST 5 fingers x3]'),
 ('palm tendon stops','M3x6 set',3,6,6,'steel',True,'tendon anchor (flexor tension)','A42 l.39 (palm M3 stops)'),
 ('sheath end clamps','M2x5 SHCS',2,5,12,'A2-70',False,'locates sheath; tendon load in stop not clamp','R8 clamps [EST 6 sheaths x2]'),
 ('flexor motor/encoder end-cap clamps','M2.5x6 SHCS',2.5,6,12,'A2-70',False,'thermal clamp to shell (Thermal to OK Ti)','R5/R8 ladder B clamps [EST]'),
 ('hand board (144 MHz) standoffs','M2x5 SHCS',2,5,4,'A2-70',False,'PCB mount (gap pad clamp)','R9 thermal [EST]'),
 ('DRV8874 / driver PCB','M2x5 SHCS',2,5,4,'A2-70',False,'PCB mount','[EST]'),
 ('ENX22 encoder mounts (6 flexors)','M1.6x4',1.6,4,12,'A2',False,'encoder locate, no load','maxon ENX22 [EST 2 per]'),
 ('forearm covers / wrist fairing','M2.5x6 button',2.5,6,10,'A2-70',False,'cosmetic/impact skin','R-070 fairing [EST]'),
 ('upper-arm cover / shoulder local cover','M3x8 button',3,8,8,'A2-70',False,'cover skin (ID PC 1.5)','COVER_TRIMS_R120 [EST]'),
 ('harness P-clips','M2.5x5 SHCS',2.5,5,8,'A2-70',False,'cable retention','[EST]'),
]
rows=[];tot=dict(n=0,steel=0,ns_n=0,ns_steel=0)
for r in R:
    w,sz,d,L,n,gr,st,why,src=r[:9]; k=r[9] if len(r)>9 else 'shcs'
    m=2*n*g(d,L,k); rows.append(dict(where=w,size=sz,per_side=n,per_robot=2*n,grade=gr,structural='Y' if st else 'N',reason=why,basis=src,
        steel_g_robot=round(m,1),ti64_g_robot=None if st else round(m*0.564,1),ti_candidate=not st))
    tot['n']+=2*n; tot['steel']+=m
    if not st: tot['ns_n']+=2*n; tot['ns_steel']+=m
tot={k:round(v,1) for k,v in tot.items()}; tot['ns_ti64']=round(tot['ns_steel']*0.564,1); tot['ns_saving_g']=round(tot['ns_steel']-tot['ns_ti64'],1)
json.dump(dict(rows=rows,totals=tot),open(os.path.join(H,'fastener_bom.json'),'w'),indent=1)
with open(os.path.join(H,'FASTENER_BOM.csv'),'w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
print(tot)
