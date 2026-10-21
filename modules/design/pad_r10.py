"""Pad R10 per R-119: >=292 J, peak <=7.0 kN (x1.3), 15 deg shear (0.27 N), s0 hand calc."""
import math, json
C0, dp, Z, SIG, KD, ETA = 24300, 0.075, 0.064, 1.79, 1.30, 0.72  # 4.5 pcf HC plateau MPa, dyn, usable stroke
def design(F):
    t = 292*KD/(ETA*F/1000)                 # mm core height for 292 J at static plateau
    s = math.sqrt(F/KD/SIG)                  # mm core side
    Fn, Fs = F*math.cos(math.radians(15)), F*math.sin(math.radians(15)); Y = (27+t)/1000
    s0 = {f"e{e}": round(C0/(Fn+2*(Fs*math.hypot(Y, Z)+Fn*e/1000)/dp+0.44*Fs), 2) for e in (0, 5, 10)}
    m = {"core": 72*(s/1e3)**2*t/1e3, "bond": .0005, "spreader": .0052*(s/61.8)**2, "EPP": .0018*(s/61.8)**2,
         "tray": .0076, "sleeve": .0025, "boss_Arms_EST": .024}
    m = {k: round(v, 4) for k, v in m.items()}
    return dict(F_peak_N=F, core_mm=[round(s, 1), round(s, 1), round(t, 1)], energy_J=round(SIG*s*s*ETA*t/1000),
                contact_Y_mm=round(27+t, 1), s0=s0, Mx_raw_Nm={"axial": round(Fn*Z), "down": round(Fn*Z+Fs*Y)},
                Mx_clutch_Nm=307, kg_side=m, kg_pair_all=round(2*sum(m.values()), 4),
                kg_pair_ex_boss=round(2*(sum(m.values())-m["boss_Arms_EST"]), 4))
out = {"rev": "R10", "ruling": "R-119 (03fe1ca)", "pick": design(7000),
       "trade_scan": {F: design(F) for F in (6500, 6000, 5500)},
       "gates": {"energy>=292": "PASS", "peak<=7.0kN": "PASS", "s0>=2.0": "FAIL (1.81/1.70/1.60)",
                 "pair<=0.100": "PASS ex-boss 0.065 / FAIL 0.113 if Arms' 0.024 boss counted",
                 "envelope": "RISK: core 75.3 vs 60 -> +15 mm proud per side; needs check vs shoulder envelope"},
       "close_s0": "ID cannot: lowering F raises core height (energy fixed) and lever; s0 reaches 2.0 at e0 only at ~6.0 kN/88 mm core, never at e10 inside envelope. Needs Arms bearing C0 >= ~30.5 kN (e10) / ~27 kN (e0), or slip skin mu<=0.15 credited after Materials test plus e<=5 mm.",
       "skin_option": "0.25 mm PTFE skin kept as option, not credited (+0.0017/side)"}
json.dump(out, open("pad_r10.json", "w"), indent=1)
p = out["pick"]; print(p["core_mm"], p["energy_J"], p["s0"], p["Mx_raw_Nm"], p["kg_pair_all"], p["kg_pair_ex_boss"])
