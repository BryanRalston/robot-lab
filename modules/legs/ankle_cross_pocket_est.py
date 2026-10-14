"""R-069: ankle cross pocketing hand-model (CadQuery, [EST] - no FEA). model_v4: solid Ti-6Al-4V box 30(x) x 46(y) x 30(z), pitch pin
stubs y (integral, not counted here), roll pins ø12 from the foot lugs along x into the cross (bores 12 deep, ø12 + 2 mm bush wall -> ø16 bosses kept).
Pocketed form: 4 blind pockets from +-z faces between the 4 bosses, ribs/walls W mm, floor F mm at mid-plane."""
import cadquery as cq, json, os
RHO=4.43e-3
def cross(W=4.0,F=4.0):
    s=cq.Workplane('XY').box(30,46,30)
    for sx in (-1,1): s=s.cut(cq.Workplane('YZ').circle(6).extrude(12).translate((sx*15-(12 if sx>0 else 0),0,0)))   # roll pin bores
    for sz in (-1,1):
        for sx in (-1,1):
            for sy in (-1,1):
                pw=(30-3*W)/2; pl=(46-3*W)/2; d=(30-F)/2
                p=cq.Workplane('XY').box(pw,pl,d).edges('|Z').fillet(2).translate((sx*(W/2+pw/2),sy*(W/2+pl/2),sz*(15-d/2)))
                s=s.cut(p)
    return s
out={'solid_box_kg':round(30*46*30*RHO/1000,4)}
for W,F in ((4,4),(5,5),(6,6)):
    s=cross(W,F); out[f'W{W}_F{F}']=round(s.val().Volume()*RHO/1000,4)
for k,v in list(out.items()): out[k+'_7075'] = round(v*2.81/4.43,4)
os.makedirs('results/r069',exist_ok=True); json.dump(out,open('results/r069/ankle_cross_pocket_est.json','w'),indent=1); print(out)
