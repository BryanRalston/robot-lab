"""P-053 thigh collar radial pin access (Legs L63/L63-R 504082f, replaces L30/a14_r7 push-through panel).
8 x o7x10 radial pins, 4/row at 90 deg, rows z 8.25/25.75 from collar bottom (collar L34, OD ~64), row 2 clocked 45 deg.
Hand sizing, [EST] throughout: no thigh fairing CAD in repo."""
import json,math,os
H=os.path.dirname(os.path.abspath(__file__))
r_col=32.0                    # collar OD 64 [EST, ENVELOPES_FOR_ID]
pin_L=10.0; pin_d=7.0
tool_d=15.0                   # extractor/drift envelope o7 + 4 each side (M3 tapped pin extractor + slide hammer, or o6.5 drift for install)
tool_radial=pin_L+30.0        # pin + extractor stud/hammer stroke -> 40 mm free radially beyond collar OD
heat='Loctite 638/648 release needs local heat ~250 C: band open gives hot-air nozzle line of sight'
r_fair=45.0                   # mean fairing inner radius at collar [EST: 3 mm at sides, ~35 mm front per L30]
rows=[8.25,25.75]
az=[[0,90,180,270],[45,135,225,315]]   # proposed clocking: row1 on x/y axes (0 = front +x, 90 = outboard)
# Fairing rigid arc at collar = front+outboard (P-020); rear + inboard open (rear window, inter-thigh gap)
arc_lo,arc_hi=-45.0,135.0
ext=math.degrees((tool_d/2+7.5)/r_fair)          # tool half-width + 7.5 mm edge margin past outer pin axes
arc=(arc_hi-arc_lo)+2*ext
h=34.0+2*8.0                                     # collar L34 + 8 mm each end; rows+tool span 0.75..33.25
L_arc=math.radians(arc)*r_fair
A_band=L_arc*h
flange=2*L_arc*8+2*h*8                           # 8 mm overlap lands on the fixed fairing
PC=1.20; t=1.5
band_g=A_band*t*PC/1000; flange_g=flange*t*PC/1000*0.5   # lands: half (joggle on fixed side only) [EST]
fast_g=6*1.2                                     # 6 x M3 captive quarter-turn (3 top, 3 bottom)
new_g=band_g+flange_g+fast_g
old_kg=0.018                                     # L30: 60x70 front panel + 40x50 rear window panel, PA12-CF, 6 x M3 (a14_r7)
pins=[]
for z,a_s in zip(rows,az):
    for a in a_s:
        aa=((a+180)%360)-180
        under= arc_lo-1e-6<=aa<=arc_hi+1e-6
        route='through P-053 band (removed)' if under else ('rear open window 40x50 (kept, unpanelled)' if a==180 else 'inboard open zone (inter-thigh gap, no fairing)')
        pins.append(dict(z_mm=z,az_deg=a,access=route,radial_free_mm=f'>={tool_radial:.0f}' ,tool_env_d_mm=tool_d))
d=dict(P='P-053 (proposed)',supersedes='L30 / a14_r7 thigh pin panel 60x70 front + 40x50 rear push-through (0.018 kg/leg)',
 basis='Legs L63-R (504082f): 8 x o7x10 42CrMo4 radial, H7/m6 bonded (638/648), rows z 8.25/25.75, row 2 at +45 deg',
 design=f'Removable 1.5 mm PC band segment of the P-020 thigh fairing, {h:.0f} mm tall centred on collar mid, {arc:.0f} deg arc (az {arc_lo-ext:.0f}..{arc_hi+ext:.0f}, 0=front, 90=outboard) at r~{r_fair:.0f}; 8 mm lands, 6 x M3 captive quarter-turn. Removing it exposes every pin under the front+outboard arc with >= {tool_radial:.0f} mm radial line-of-sight and o{tool_d:.0f} tool envelope; rear pin via the kept 40x50 window (now open, no panel); inboard pins face the open inter-thigh zone. No push-through path needed (pins are single-wall, blind).',
 tool=f'M3 tapped extractor + slide hammer, radial; heat release ({heat}); install with o6.5 drift',
 pins=pins,
 interface_asks_to_legs=['Confirm pin clocking row1 0/90/180/270, row2 45/135/225/315 (az 0 = +x front)','Pin outer end tapped M3 (or flush with chamfer) for extraction','Confirm inboard gap >= 40 mm + tool at collar height (hip y spacing) [EST]'],
 mass_g=dict(band=round(band_g,1),lands=round(flange_g,1),fasteners=round(fast_g,1),total=round(new_g,1)),
 kg_per_leg=round(new_g/1000,4),old_kg_per_leg=old_kg,delta_kg_per_leg=round(new_g/1000-old_kg,4),delta_kg_robot=round(2*(new_g/1000-old_kg),3),
 note='Same basis as L30 (panel area counted, displaced fairing skin not credited). [EST] until A29 CAD.')
json.dump(d,open(f'{H}/thigh_pin_access_p053.json','w'),indent=1); print(json.dumps({k:d[k] for k in ('design','mass_g','delta_kg_per_leg','delta_kg_robot')},indent=1))
for p in pins: print(p)
