"""RL Torso & Power R1 check: pack, mass line, waist_pitch static load, runtime vs T7.
-> r1_torso.json + R1_torso_power.png. [EST] = estimate. Sources: CONTRACTS R1.3, actuators/results/sizing.md,
sim/v3/humanoid_v3.xml, arms/R1_ARCHITECTURE.md, electronics/R1_ARCHITECTURE.md, Molicel P45B datasheet (v3/PARTS.md)."""
import json, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
g = 9.81
S, P = 20, 5   # P45B: 4.5 Ah typ, 3.6 V, 16.2 Wh, <=70 g, 45 A cont
pack = dict(S=S, P=P, cells=S*P, Vmin=S*3.4, Vnom=S*3.6, Vmax=S*4.2, Ah=P*4.5, Wh=S*P*16.2, Wh_binned=S*P*4.4*3.6,
            I_cell_60A=60/P, I_cell_100A=100/P)
pack_mass = {"cells 100 x 0.070 (datasheet max)": 7.000, "busbars/tabs [EST]": 0.250, "cell holders + foam [EST]": 0.300,
             "enclosure CFRP 1.5 mm + 6061 caps/latch [EST]": 0.750, "BMS + FET/precharge board + fuse + connector [EST]": 0.300,
             "gap filler [EST]": 0.150}
pack["kg"] = round(sum(pack_mass.values()), 3)
struct = {"torso shell CFRP 2.0 mm, 0.55 m2 [EST]": round(0.55*0.002*1550, 3), "shoulder bulkhead 7075 [EST]": 0.45,
          "waist ring 7075 [EST]": 0.25, "pack rails + latch [EST]": 0.20, "pelvis 7075 machined [EST]": 1.45,
          "power distribution board, busbars, branch fuses, 5 V aux [EST]": 0.25}
struct_kg = round(sum(struct.values()), 3)
m_t, z_t, m_arm, z_sh, x_arm = 18.762, 0.169, 9.54, 0.30, 0.10   # sim torso; catalog arm/side; [EST] geometry
cases = {}
for n, lean, pay, x in [("stand", 0, 0, 0), ("lean 30", 30, 0, 0), ("carry 20 kg upright", 0, 20, 0.30),
                        ("carry 20 kg lean 15", 15, 20, 0.30), ("10 kg reach lean 30", 30, 10, 0.60)]:
    s, c = math.sin(math.radians(lean)), math.cos(math.radians(lean))
    cases[n] = round(g*(m_t*z_t*s + 2*m_arm*(z_sh*s + x_arm*c) + pay*(x*c + z_sh*s)), 1)
need = round(1.5*max(cases.values()), 1)
add = {"BMS + host always-on [EST]": 1.0, "FET conduction 2 mOhm x 9.8^2": 0.2, "distribution/fuses [EST]": 0.3}
A = sum(add.values()); use = 0.90
w10, w12 = 703.4 + A, 846.0 + A
stand = 254 + 40   # rest of robot (sizing.md) + standing copper [EST]
mixed = 0.5*w10 + 0.5*stand
rt = {"walk1.0 typical": round(pack["Wh"]*use/w10, 2), "walk1.0 binned": round(pack["Wh_binned"]*use/w10, 2),
      "walk1.2 typical": round(pack["Wh"]*use/w12, 2), "mixed 50/50 typical": round(pack["Wh"]*use/mixed, 2)}
out = dict(pack=pack, pack_mass=pack_mass, struct=struct, struct_kg=struct_kg, waist_pitch_static_Nm=cases,
           waist_pitch_need_Nm=need, P_add_W=add, P_walk10_W=round(w10, 1), P_mixed_W=round(mixed, 1), runtime_h=rt)
json.dump(out, open("r1_torso.json", "w"), indent=1); print(json.dumps(out, indent=1))
fig, ax = plt.subplots(1, 3, figsize=(17, 5.8)); a = ax[0]; a.axis("off"); a.set_xlim(0, 1); a.set_ylim(0, 1)
a.set_title("Power tree: 20S5P 68-84 V + 48 V intermediate rail")
def box(x, y, t, c): a.add_patch(plt.Rectangle((x, y), 0.30, 0.13, fc=c, ec="k")); a.text(x+.15, y+.065, t, ha="center", va="center", fontsize=6.5)
box(.01, .84, "Pack 20S5P Molicel P45B\n1620 Wh, 22.5 Ah, 8.75 kg", "#f7d08a")
box(.35, .84, "BMS 2x TI BQ79616-Q1\nBQ76200 FET driver\nINA229 low-side shunt", "#9fd3f7")
box(.69, .84, "Fuse Littelfuse L50S125\nB2B FETs 6+6x IPT059N15N3\nprecharge 47R", "#f4a3a3")
box(.69, .60, "MOTOR BUS 68-84 V\nclamp/chopper <=90 V", "#ddd")
box(.01, .36, "Legs/arms/waist drives\nElmo Gold Twitter VP+", "#c9f2c0")
box(.35, .36, "Vicor DCM3623TA5N53B4T00\n43-154 V -> 48 V, 240 W\n(brain rail, RL Electronics)", "#e3c9f2")
box(.69, .36, "RECOM RP40-11012SFR/P-HC\n43-160 V -> 12 V, head", "#e3c9f2")
box(.35, .10, "AGX301 + Thor (36-60 V in)\n48 V -> 24 V POL for drive VL\n(O-E3 open)", "#e3c9f2")
box(.69, .10, "TI LM5164 (6-100 V)\n-> 5 V aux: BMS host,\ne-stop logic", "#e3c9f2")
box(.01, .10, "E-stop: STO star (TMS570)\nthen BMS FETs open", "#f4a3a3")
for x1, y1, x2, y2 in [(.31, .905, .35, .905), (.65, .905, .69, .905), (.84, .84, .84, .73), (.69, .66, .16, .49),
                       (.74, .60, .50, .49), (.84, .60, .84, .49), (.50, .36, .50, .23), (.95, .60, .95, .23)]:
    a.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->"))
b = ax[1]; k = list(cases); b.barh(k, [cases[i] for i in k], color="#7aa6d6")
b.axvline(116, color="r", ls="--", label="v3 waist_pitch avail 116"); b.axvline(need, color="k", ls=":", label=f"need 1.5x = {need}")
b.axvline(204, color="g", ls="--", label="CSG-25-100 rep. peak 204"); b.set_xlabel("static waist_pitch N·m [EST geometry]")
b.set_title("Waist pitch static load"); b.legend(fontsize=7)
c = ax[2]; v = list(rt.values()); c.bar([x.replace(" ", "\n") for x in rt], v, color=["#6c6", "#6c6", "#e88", "#e88"])
c.axhline(2, color="k", ls="--", label="T7 2 h walk"); c.axhline(4, color="purple", ls=":", label="T7 4 h mixed")
for i, y in enumerate(v): c.text(i, y+.05, f"{y:.2f} h", ha="center")
c.set_ylabel("h, 90 % usable [EST]"); c.set_title("Runtime vs T7"); c.legend(fontsize=8)
fig.suptitle("RL Torso & Power R1 (2026-10-14)"); fig.tight_layout(); fig.savefig("R1_torso_power.png", dpi=110)
