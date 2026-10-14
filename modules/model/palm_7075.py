"""A32 / P-021: machined 7075-T6 palm (RL Arms & Hands). CadQuery, units mm, model_v4 frame (x fwd = palm face, y left, z up).
palm(c) returns the palm solid centred on c (same envelope as the R-027 booking: 32 x 86 x 90 mm, x * y * z).
Side (L/R) is taken from sign(c[1]) so the thumb mount mirrors without changing the model_v4 call.

Parts of the one machined body (all 7075-T6, rho 2.81 g/cc, MATERIALS_DB AL7075T6):
  - wrist plate   (top, z +41..+45 before the A42 DROP_MM = 12 shift, i.e. +29..+33 after; neck 20x22 bridges to the lug): wrist-lug pocket, 2 underside pockets, + 11 tendon sheath bores dia 2.5 on an r 9 mm circle around
                   the wrist axis (tendon length change with wrist pitch/yaw kept small), 4x M3 sheath-stop holes [EST].
  - shell walls   1.5 mm (R-027 wall; Protolabs nominal >= 1.02 mm). Front (grip) face solid for pads; back face has a
                   60 x 66 window (R3 corners) closed by the CF backplate; each side has an 18 x 60 window (R3).
  - knuckle bar   (bottom, z -45..-35, 10 mm, 5 top lightening pockets on a 3 mm floor): 4 MCP clevis slots 9 mm wide x 8 deep at y = +-10, +-30, MCP pin bore
                   dia 4 along y; per-finger tendon exits dia 2.0 (index: 2, others: 1) feeding the 15-joint / 11-DoF set
                   (arms R1: 6 flexors + 5 abduction/thumb-rotation on DCX16).
  - thumb mount   boss 22 x 22 x 6 on the front face at y = -30*side, z -10 (model_v4 thumb root), CMC bore dia 8.
Galvanic (Materials REVIEW_R1 s.2, RULINGS R-027 #8): CF backplate on 7075 is a severe couple (carbon cathodic, 7075 -750 mV
calomel). Spec: anodize all 7075 except bond flange; glass-fibre isolation ply (or film adhesive) on the 4 mm backplate
flange; sealed (wet-assembled) fasteners. Fatigue: check R3 window corners under 10 kg grip (7075 fatigue 160 MPa).
Hybrid option (Materials): 7075 knuckle bar + wrist plate + thumb boss, skin in PA12/CF -> see variants()."""
import cadquery as cq

L = dict(t=32.0, w=86.0, h=90.0, wall=1.5, plate=4.0, bar=10.0, rho_7075=2.81, rho_pa12=1.01, rho_cf=1.55)
FINGERS_Y = (-30, -10, 10, 30)

def _box(dx, dy, dz, c): return cq.Workplane('XY').box(dx, dy, dz).translate(c)
def _rbox(dx, dy, dz, c, r):  # rounded-corner window cutter, rounded about x-axis edges handled by caller
    return cq.Workplane('XY').box(dx, dy, dz).edges('|X' if dx < min(dy, dz) else ('|Y' if dy < min(dx, dz) else '|Z')).fillet(r).translate(c)

def _parts(side=1):
    t, w, h, wl, pt, bt = L['t'], L['w'], L['h'], L['wall'], L['plate'], L['bar']
    zt, zb = h/2, -h/2
    shell = _box(t, w, h - pt - bt, (0, 0, (pt - bt)/2 * -1 + 0)).cut(_box(t - 2*wl, w - 2*wl, h, (0, 0, 0)))
    shell = shell.cut(_rbox(4*wl, 66, 60, (-t/2, 0, 0), 3))           # back window (CF backplate)
    for sy in (1, -1): shell = shell.cut(_rbox(18, 4*wl, 60, (0, sy*w/2, 0), 3))  # side windows
    # 4 mm bond land (1.5 mm thick) around the back window inside the back wall
    flange = _box(wl, 74, 68, (-t/2 + wl*1.5, 0, 0)).cut(_box(3*wl, 66, 60, (-t/2 + wl*1.5, 0, 0)))
    shell = shell.union(flange)
    plate = _box(t, w, pt, (0, 0, zt - pt/2)).cut(_box(26, 14, pt, (0, 0, zt - pt/2)))  # wrist-lug pocket
    import math
    for k in range(11):
        a = 2*math.pi*k/11; plate = plate.cut(cq.Workplane('XY').circle(1.25).extrude(10).translate((9*math.cos(a)*1.3, 9*math.sin(a)*2.6, zt - 6)))
    for sy in (1, -1): plate = plate.cut(_box(t - 6, 20, pt - 1.5, (0, sy*29, zt - pt + (pt - 1.5)/2)))  # underside pockets (1.5 mm skin)
    for (x, y) in ((10, 36), (-10, 36), (10, -36), (-10, -36)):
        plate = plate.cut(cq.Workplane('XY').circle(1.6).extrude(10).translate((x, y, zt - 6)))
    bar = _box(t, w, bt, (0, 0, zb + bt/2))
    for i, fy in enumerate(FINGERS_Y):
        bar = bar.cut(_box(t - 8, 9, 8, (0, fy, zb + 4)))                          # MCP clevis slot
        for dx in ((-4, 4) if (fy == 10*side) else (0,)):                          # index (y=+10*side) gets 2 tendons
            bar = bar.cut(cq.Workplane('XY').circle(1.0).extrude(bt + 2).translate((dx, fy, zb - 1)))
    for ly in (0, 20, -20):                                                        # lightening pockets between fingers (from top, 3 mm floor)
        bar = bar.cut(_box(t - 6, 8, bt - 3, (0, ly, zb + 3 + (bt - 3)/2)))
    for ly in (39.5, -39.5): bar = bar.cut(_box(t - 6, 4, bt - 3, (0, ly, zb + 3 + (bt - 3)/2)))
    bar = bar.cut(cq.Workplane('XZ').circle(2.0).extrude(w/2, both=True).translate((0, 0, zb + 4)))  # MCP pin bore
    thumb = _box(6, 22, 22, (t/2 + 3, -30*side, -10)).cut(cq.Workplane('YZ').circle(4).extrude(20).translate((t/2 - 5, -30*side, -10)))
    return dict(shell=shell, plate=plate, bar=bar, thumb=thumb)

DROP_MM = 12.0   # A42 (arms/A42_A43_R4.md, wrist_clash_r4.json): wrist-plate top 27 mm below the wrist pivot (was 15) -> sphere rule,
                 # fork/cross inside r 24.5, clash-free for any pitch/yaw over P-026 ±60/±30. The palm body moves down DROP_MM inside the
                 # same model_v4 call; a 7075 neck 20(x) x 22(y) x DROP_MM (|y| <= 11 < cheek inner face 14 - 2 gap) carries the wrist lug load.
NECK = (20.0, 22.0)

def palm(c=(0, 0, 0)):
    side = 1 if c[1] >= 0 else -1
    p = _parts(side); s = p['shell'].union(p['plate']).union(p['bar']).union(p['thumb'])
    s = s.translate((0, 0, -DROP_MM))
    if DROP_MM > 0:
        neck = _box(NECK[0], NECK[1], DROP_MM, (0, 0, 45 - DROP_MM/2)).cut(_box(NECK[0]-4, NECK[1]-4, DROP_MM+2, (0, 0, 45 - DROP_MM/2)))  # 2 mm wall tube [EST]
        s = s.union(neck)   # neck from the old plate top (z +45) down to the dropped plate; sheaths inside |x|<8,|y|<9 pass the bore, others beside it
    return s.translate(tuple(c))

def variants():
    p = _parts(1); v = {k: p[k].val().Volume()/1000.0 for k in p}   # cm^3
    core = v['plate'] + v['bar'] + v['thumb']; tot = palm().val().Volume()/1000.0
    r = dict(vol_cm3={k: round(x, 2) for k, x in v.items()}, vol_total_cm3=round(tot, 2))
    r['all_7075_kg'] = round(tot*L['rho_7075']/1000, 4)
    r['hybrid_7075core_PA12skin_kg'] = round((core*L['rho_7075'] + (tot - core)*L['rho_pa12'])/1000, 4)
    r['hybrid_7075core_CFskin_kg_EST'] = round((core*L['rho_7075'] + (tot - core)*L['rho_cf'])/1000, 4)
    r['R027_booked_upper_bound_kg'] = 0.1127
    r['skin_only_7075_kg'] = round(v['shell']*L['rho_7075']/1000, 4)   # R-027 booked the 1.5 mm SKIN only (skeleton already in hands 2.10)
    r['credit_vs_R027_skin_per_hand_kg'] = round(0.1127 - r['skin_only_7075_kg'], 4)
    r['note'] = 'R-027 +0.1127/hand = 7075 skin w/o openings; skeleton (bar/plate) was already in CONTRACTS hands. Like-for-like credit uses skin_only.'
    return r

if __name__ == '__main__':
    import json, sys
    r = variants(); print(json.dumps(r, indent=1))
    if len(sys.argv) > 1: json.dump(r, open(sys.argv[1], 'w'), indent=1); cq.exporters.export(palm(), sys.argv[1].replace('.json', '.step'))
