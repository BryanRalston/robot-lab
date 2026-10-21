"""P-053 thigh collar pin access (Legs L63-R 504082f; supersedes L30 / a14_r7). Rev 2, 2026-10-20.
Legs confirmed: 8 x o7x10 radial pins, row1 az 0/90/180/270, row2 45/135/225/315 (z 8.25/25.75), ends tapped M3.
Pins are bonded fault-backup parts, extracted only on the bench with the thigh dismounted -> no on-robot tool room,
no dedicated access panel. The P-020 front + outboard fairing halves come off as whole panels for bench service;
their removal never went through the L30 sub-panel (L30 was a hatch inside the front half)."""
import json,os
H=os.path.dirname(os.path.abspath(__file__))
arc=(-90.0,180.0)   # P-020 rigid coverage at collar height: front + outboard (az -90..+180 incl. edges) [EST, no fairing CAD]
pins=[]
for z,azs in ((8.25,(0,90,180,270)),(25.75,(45,135,225,315))):
    for a in azs:
        aa=((a+180)%360)-180
        cov = 0<=aa<=135 or aa==-45
        where='under P-020 fairing' if cov else ('rear 40x50 open window (exposed)' if a==180 else 'inboard open zone (exposed, no fairing)')
        pins.append(dict(z_mm=z,az_deg=a,coverage=where,covered=cov))
old=0.018   # L30 per leg: 60x70 front hatch + 40x50 rear window panel, PA12-CF 1.5, 6 x M3 (a14_r7) -- all deleted
new=0.0     # fairing front-half skin closes the 60x70 hole; P-020 hull mass (0.443) already counted it unpierced
d=dict(P='P-053 (proposed, rev 2)',supersedes='L30 / a14_r7 thigh pin panel 60x70 + 40x50 rear panel; and P-053 rev1 218 deg band (deleted)',
 basis='Legs L63-R confirmed 2026-10-20: angles as assumed, M3-tapped ends; bench-only extraction with thigh dismounted',
 design='No dedicated access panel. L30 hatch and the rev1 218 deg band are deleted; the P-020 front half is a continuous skin over the collar. Bench service: remove the front and outboard P-020 halves (own fasteners, independent of L30), dismount thigh, extract radially with M3 extractor. Rear 40x50 window stays an open hole (no panel).',
 pins=pins,covered_count=sum(p['covered'] for p in pins),
 coverage_finding='Fairing covers 5 of 8 pin ends (0,45,90,135,315). 180 (rear window) and 225/270 (inboard) are exposed as before: P-020 never covered rear/inboard at the collar. Flush bonded pins, cosmetic only; no IP/touch issue (passive steel). Add a 2-piece rear/inboard collar cover only if Robot Lab wants all 8 hidden.',
 kg_per_leg=new,old_kg_per_leg=old,delta_kg_per_leg=round(new-old,3),delta_kg_robot=round(2*(new-old),3),
 note='[EST] until A29 CAD; fairing removal fasteners not yet defined in the repo (A29).')
json.dump(d,open(f'{H}/thigh_pin_access_p053.json','w'),indent=1); print(d['coverage_finding'],d['delta_kg_robot'])
