"""R1.3: charge-cap runtime, clamp pulse check, mass line, updated figure -> r13_torso.json, R1_torso_power.png"""
import json, math
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
Wt, Wb, use = 1620, 1584, 0.90
P_walk, P_walk12, P_stand = 711.8, 846.0+8.4, 262.4    # R1.2 §13.5 (fan 6.12 W in full, R-032)
def rt(Wh, frac, P): return round(Wh*frac/P, 3)
res = {}
for cap, loss in [("4.20 V", 0.0), ("4.15 V, -3% [EST]", 0.03), ("4.15 V, -5% [EST]", 0.05)]:
    f = use - loss
    res[cap] = {"usable typ Wh": round(Wt*f), "usable binned Wh": round(Wb*f),
                "walk1.0 typ h": rt(Wt, f, P_walk), "walk1.0 binned h": rt(Wb, f, P_walk),
                "walk1.2 typ h": rt(Wt, f, P_walk12),
                "mixed 20/80 typ h": rt(Wt, f, 0.2*P_walk+0.8*P_stand),
                "binned 2 h pass line W": round(Wb*f/2, 1), "binned walk margin W": round(Wb*f/2 - P_walk, 1)}
# clamp pulse check (Arcol Heatsink Range Tech Info TI004/TI008: 10x/1 s, 5x/5 s, 2x/3 min; HS100 76.7 J/K 90 g; HS50 19.78 J/K 25 g)
P, t = 88**2/1.5, 400/(88**2/1.5)
k = math.log(10/5)/math.log(5)   # power-law slope through the two short tabulated points
clamp = {}
for n, W, C, g in [("HS100 1R5", 100, 76.7, 90), ("HS50 1R5", 50, 19.78, 25), ("2x HS100 0R75 series", 200, 153.4, 180)]:
    mult = P/W; pl = 10*(1/t)**k; ad = 10*1/t
    clamp[n] = dict(multiple=round(mult,1), allowed_powerlaw=round(pl,1), allowed_const_energy=round(ad,1),
                    dT_adiabatic_K=round(400/C,1), g=g, verdict="PASS" if mult<=pl else ("OPEN (between bounds)" if mult<=ad else "FAIL"))
mass = {"structure+pelvis+distribution (R1)": 4.305, "shoulder bulkhead 12 mm (§9)": 0.150, "P-030/P-044 duct fans booking": 0.040,
        "duct partition/walls + TSR (§13.4)": 0.147, "P-045 clamp (HS100 + FETs/board)": 0.145,
        "contactor LEV100 [EST 0.20] + HS25 47R 0.0125 + BSC520 + driver 0.003": 0.216}
tot = round(sum(mass.values()), 3)
out = dict(runtime=res, clamp_pulse=dict(P_W=round(P), t_ms=round(t*1000,1), parts=clamp), mass=mass, torso_total=tot, vs_alloc=round(tot-4.40,3))
json.dump(out, open("r13_torso.json","w"), indent=1); print(json.dumps(out, indent=1))
fig, ax = plt.subplots(1, 2, figsize=(15, 6.2)); a = ax[0]; a.axis("off"); a.set_xlim(0,1); a.set_ylim(0,1)
a.set_title("Power tree R1.3 (2026-10-14)")
def box(x,y,t,c): a.add_patch(plt.Rectangle((x,y),.30,.12,fc=c,ec="k")); a.text(x+.15,y+.06,t,ha="center",va="center",fontsize=6.3)
box(.01,.85,"Pack 20S5P Molicel P45B\n1620 Wh, 8.75 kg\ncharge to 4.20 V","#f7d08a")
box(.35,.85,"BMS 2x BQ79616-Q1 + host\nINA229, BQ76200\nFAULT_N x2 + CAN FD","#9fd3f7")
box(.69,.85,"Fuse L50S125 -> FETs\n6+6 IPT059N15N3 ->\ncontactor LEV100A4ANG","#f4a3a3")
box(.69,.66,"Pre-charge HS25 47R\n+ BSC520N15NS3","#f4a3a3")
box(.35,.62,"DRIVE BUS 68-84 V (ceiling 92 V)\nclamp P-045: 2x IPT059N15N3\n+ HS100 1R5, 88/86 V, bus-powered","#ddd")
box(.01,.40,"32 Elmo Gold Twitter\nVP+ and VL single-supply\n(no 24 V, O-E3)","#c9f2c0")
box(.35,.40,"DCM3623TA5N53B4T00\n-> 48 V on Thor cold plate\n(choke in brain line)","#e3c9f2")
box(.69,.40,"RP40-11012SFR/P-HC\n-> 12 V head","#e3c9f2")
box(.35,.15,"48V_BRAIN only:\nTSR 1-48120WI -> 12 V\nSunon PF40281B1 fan 6.12 W","#e3c9f2")
box(.69,.15,"LM5164 -> 5 V aux\n(BMS host, wake)","#e3c9f2")
box(.01,.15,"TMS570: STO all drives,\nfan tach, clamp OT,\nlatched manual reset","#f4a3a3")
for x1,y1,x2,y2 in [(.31,.91,.35,.91),(.65,.91,.69,.91),(.84,.85,.84,.78),(.69,.72,.65,.70),(.40,.62,.16,.52),(.50,.62,.50,.52),(.60,.62,.84,.52),(.50,.40,.50,.27),(.84,.62,.84,.27)]:
    a.annotate("",xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle="->"))
b = ax[1]; labs = ["walk1.0\ntyp","walk1.0\nbinned","walk1.2\ntyp","mixed\n20/80"]
keys = ["walk1.0 typ h","walk1.0 binned h","walk1.2 typ h","mixed 20/80 typ h"]; w = .25
for i,(cap,col) in enumerate(zip(res,["#4a4","#da4","#d44"])):
    v=[res[cap][k] for k in keys]; b.bar([j+(i-1)*w for j in range(4)], v, w, label=cap, color=col)
    for j,y in enumerate(v): b.text(j+(i-1)*w, y+.04, f"{y:.2f}", ha="center", fontsize=6.5)
b.set_xticks(range(4)); b.set_xticklabels(labs); b.axhline(2,color="k",ls="--",label="T7 2 h walk"); b.axhline(4,color="purple",ls=":",label="4 h mixed (proposed 20/80)")
b.set_ylabel("h (90 % usable at 4.20 V basis)"); b.set_title("Runtime vs charge cap (fan 6.12 W in full)"); b.legend(fontsize=7)
fig.tight_layout(); fig.savefig("R1_torso_power.png", dpi=110)
